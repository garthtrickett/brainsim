"""Complete discovery results with learning, discovery-gate and oracle accounting."""
import argparse
import json
from pathlib import Path

import numpy as np

from study_v3_discovery import DIRECTORY, make_manifest, read_stage
from v3_discovery import ARMS, GRIDS
from v3_discovery_policy import (KEYS, SEEDS, discovery_decision, digest, interval,
                                 metric_values, performance_decision)
from v3_persistent import FIXTURES


def absolute_summary(rows):
    result = {}
    for arm in ARMS:
        valid = [rows[f'{arm}/{s}'] for s in SEEDS['confirmation'] if rows[f'{arm}/{s}']['status'] == 'ok']
        if not valid:
            result[arm] = {'finite_seeds': 0}
            continue
        metrics = [metric_values(r) for r in valid]
        result[arm] = {'finite_seeds': len(valid), 'metrics': {k: {
            'mean': float(np.mean([m[k] for m in metrics])), 'interval95': interval([m[k] for m in metrics])}
            for k in metrics[0]}, 'fixtures': {}}
        for name in FIXTURES:
            values = [r['fixtures'][name] for r in valid]
            item = {'update_norm_mean': float(np.mean([v['update_norm_mean'] for v in values])), 'coordinates': {}}
            for coord in values[0]['coordinates']:
                memory = [r['memory'][name][coord] for r in valid]
                kinds = {m['kind'] for m in memory}
                if len(kinds) != 1:
                    raise ValueError('mixed memory kinds')
                kind = kinds.pop()
                if kind == 'conditional':
                    for m in memory:
                        if not (np.isfinite(m['sigma_mean']) and np.isfinite(m['sigma_final']) and 0.0 <= m['hat_mean'] <= 1.0):
                            raise ValueError('invalid conditional memory')
                elif kind == 'window':
                    for m in memory:
                        if not (1 <= m['width_min'] <= m['width_mean'] <= m['width_max'] <= 6000):
                            raise ValueError('invalid width range')
                        if type(m['width_final']) is not int or not 1 <= m['width_final'] <= 6000 or m['total_discarded'] != 6000 - m['width_final']:
                            raise ValueError('discard accounting mismatch')
                fields = ('excess_mse', 'post_mse', 'stable_mse', 'adaptation_latency')
                c = {f: None if values[0]['coordinates'][coord][f] is None else float(np.mean([
                    v['coordinates'][coord][f] for v in values])) for f in fields}
                c['memory_kind'] = kind
                if kind == 'conditional':
                    c['sigma_mean'] = float(np.mean([m['sigma_mean'] for m in memory]))
                    c['hat_mean'] = float(np.mean([m['hat_mean'] for m in memory]))
                elif kind == 'window':
                    c['width_mean'] = float(np.mean([m['width_mean'] for m in memory]))
                    c['width_final'] = float(np.mean([m['width_final'] for m in memory]))
                item['coordinates'][coord] = c
            result[arm]['fixtures'][name] = item
    return result


def summarize(directory):
    tuning = read_stage(directory, 'tuning')
    manifest = json.loads((directory / 'manifest.json').read_text())
    if manifest != make_manifest(tuning):
        raise ValueError('manifest differs from tuning')
    screen = manifest['screen']
    status = 'awaiting_confirmation' if screen['status'] == 'eligible' else screen['status']
    result = {'status': status, 'closed': status != 'awaiting_confirmation', 'protocol': manifest['protocol'],
        'manifest_digest': digest(manifest), 'screen': screen,
        'counts': {'tuning': len(KEYS['tuning']), 'confirmation': 0}, 'decisions': {}, 'absolute': {},
        'elapsed_seconds': {'tuning': {a: float(sum(r.get('seconds', 0.) for k, r in tuning.items()
                                                   if k.startswith(a + '/'))) for a in GRIDS}}}
    if (directory / 'confirmation.json').exists():
        if screen['status'] != 'eligible':
            raise ValueError('forbidden confirmation stage')
        rows = read_stage(directory, 'confirmation')
        result['counts']['confirmation'] = len(KEYS['confirmation'])
        result['elapsed_seconds']['confirmation'] = {a: float(sum(r.get('seconds', 0.) for k, r in rows.items()
                                                                  if k.startswith(a + '/'))) for a in ARMS}
        result['decisions'] = {a: performance_decision(rows, a) for a in ('discover', 'oracle', 'oracle_matched')}
        result['decisions']['discovery_gate'] = discovery_decision(rows)
        gate = result['decisions']['discovery_gate']['status']
        learn = result['decisions']['discover']['status']
        result['status'] = 'learning_positive' if (gate == 'discovery_pass' and learn == 'learning_positive') else (
            'discovery_negative' if gate != 'discovery_pass' else learn)
        result['closed'] = True
        result['absolute'] = absolute_summary(rows)
    return result


def number(value):
    return '—' if value is None else f'{value:.6f}'


def markdown(summary):
    lines = ['# V3 interference-as-discovery', '', f'Disposition: **{summary["status"]}**.', '',
             '| Stage | Rows |', '| --- | ---: |']
    lines += [f'| {k} | {v} |' for k, v in summary['counts'].items()]
    lines += ['', '## Finite-menu tuning', '', 'Each searched family: 12 configurations × 8 seeds × 5 fixtures. '
              'Same objective: half primary post-switch MSE plus half mean of 14 retention metrics.', '',
              '| Family | Index | Configuration | Tuning objective | Menu endpoint fields |', '| --- | ---: | --- | ---: | --- |']
    screen = summary['screen']
    for arm, i in screen['indices'].items():
        config, endpoints = screen['selected'][arm], []
        for field, value in config.items():
            options = sorted({json.dumps(c[field], sort_keys=True) for c in GRIDS[arm]})
            if len(options) > 1 and json.dumps(value, sort_keys=True) in (options[0], options[-1]):
                endpoints.append(field)
        lines.append(f'| {arm} | {i} | `{json.dumps(config)}` | {screen["objectives"][arm][i]:.6f} | {", ".join(endpoints) or "none"} |')
    lines += ['', 'Endpoint choices remain in the registered finite menu; no extension or global-optimum claim. '
              'Matched oracle/random/shuffled/nocontext use the discover configuration without extra search.']
    lines += ['', *screen['reasons']]
    if summary['absolute']:
        lines += ['', '## Independent primary performance', '', '| Policy | Finite seeds | Primary MSE | 95% interval |', '| --- | ---: | ---: | --- |']
        for arm, row in summary['absolute'].items():
            m = row.get('metrics', {}).get('primary')
            lines.append(f'| {arm} | {row["finite_seeds"]} | {number(m["mean"] if m else None)} | {m["interval95"] if m else "unavailable"} |')
    for arm, decision in summary['decisions'].items():
        if arm == 'discovery_gate':
            lines += ['', f'## Discovery gate (ground truth): {decision["status"]}', '',
                      'Polarity-invariant AUC* = max(AUC, 1-AUC) of pre-update cue score vs true hidden context, '
                      'mean over four switching coordinates. MSE cannot pass this gate.', '',
                      '| Cell | Mean | 95% interval | Pass |', '| --- | ---: | --- | --- |']
            for key, cell in decision['cells'].items():
                lo, hi = cell['interval95']
                lines.append(f'| {key} | {cell["mean"]:.6f} | [{lo:.6f}, {hi:.6f}] | {cell["pass"]} |')
            if 'reason' in decision:
                lines += ['', decision['reason']]
            continue
        lines += ['', f'## {arm}: {decision["status"]}', '',
                  'Privileged diagnostic: cannot authorize candidate advancement.' if arm != 'discover' else
                  'All 90 candidate comparisons plus the discovery gate are required.', '',
                  '| Contrast | Control | Policy | Delta | 95% interval | Pass |', '| --- | ---: | ---: | ---: | --- | --- |']
        for key, cell in decision['cells'].items():
            lo, hi = cell['interval95']
            lines.append(f'| {key} | {cell["control"]:.6f} | {cell["candidate"]:.6f} | {cell["delta"]:.6f} | [{lo:.6f}, {hi:.6f}] | {cell["pass"]} |')
        if 'reason' in decision:
            lines += ['', decision['reason']]
    if summary['absolute']:
        lines += ['', '## Absolute errors and memory', '',
                  '| Policy/fixture/coordinate | Excess MSE | Post MSE | Stable MSE | Recovery latency | Mean update norm | Memory kind | Sigma/width mean |',
                  '| --- | ---: | ---: | ---: | ---: | ---: | --- | ---: |']
        for arm, row in summary['absolute'].items():
            for name, data in row.get('fixtures', {}).items():
                for coord, c in data['coordinates'].items():
                    extra = c.get('sigma_mean', c.get('width_mean'))
                    lines.append(f'| {arm}/{name}/{coord} | {number(c["excess_mse"])} | {number(c["post_mse"])} | '
                                 f'{number(c["stable_mse"])} | {number(c["adaptation_latency"])} | {data["update_norm_mean"]:.6f} | '
                                 f'{c["memory_kind"]} | {number(extra)} |')
    lines += ['', '## Measured execution time', '', '| Stage | Family | Seconds |', '| --- | --- | ---: |']
    for stage, families in summary['elapsed_seconds'].items():
        lines += [f'| {stage} | {a} | {seconds:.2f} |' for a, seconds in families.items()]
    lines += ['', 'Each searched family consumes 5,184,000 coordinate observations. Configuration budgets are equal, not CPU costs.', '',
              '## Scope and reproduction', '',
              'Cues are evaluator-generated noisy observations of the hidden context (SEP=0.5, unit cue noise; '
              'single-sample AUC ≈ 0.76). y bytes are identical to the forgetting fixtures at equal seeds. '
              'Perfect context is privileged, not perfect prediction: conditionals must still learn each '
              'regime mean. No oracle or discovery outcome overrides candidate learning performance; MSE '
              'cannot pass the discovery gate either. Candidate success requires the gate plus all 90 '
              'comparisons, including >= 10% primary improvement and every retention bound. Oracle arms each '
              'have 45 comparisons. All outcomes close this registration.', '',
              'Intervals resample whole seeds 10000 times with seed 95000. Finite menus and synthetic fixtures '
              'do not establish global optimizer superiority, population guarantees or general neural-memory utility. '
              'Every reached row and source is archived; prior studies remain intact.', '',
              '`python check_v3_discovery.py --evidence results/v3-discovery --reproduce` regenerates every '
              'reached row and scientific manifest/summary at rtol1e-11/atol1e-13. '
              '`python report_v3_discovery.py --check` verifies both generated reports.', '']
    return '\n'.join(lines)


def publish_report(directory, check=False):
    summary = summarize(directory)
    for name, content in {'summary.json': json.dumps(summary, indent=2, sort_keys=True) + '\n', 'report.md': markdown(summary)}.items():
        if check:
            if (directory / name).read_text() != content:
                raise ValueError('stale report ' + name)
        else:
            (directory / name).write_text(content)
    print('RESULT', summary['status'], summary['counts'], flush=True)
    return summary


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--directory', type=Path, default=DIRECTORY)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    publish_report(args.directory, args.check)
