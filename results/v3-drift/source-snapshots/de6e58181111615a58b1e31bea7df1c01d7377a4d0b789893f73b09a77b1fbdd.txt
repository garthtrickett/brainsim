"""Complete retention results with dual-state memory and strict-veto accounting."""
import argparse
import json
from pathlib import Path

import numpy as np

from study_v3_retention import DIRECTORY, make_manifest, read_stage
from v3_retention import ARMS, GRIDS
from v3_retention_policy import (KEYS, SEEDS, digest, interval, metric_values,
                                 performance_decision)
from v3_persistent import FIXTURES


def check_widths(record, prefix=''):
    mean, final = record[prefix+'width_mean'], record[prefix+'width_final']
    if not 1 <= record[prefix+'width_min'] <= mean <= record[prefix+'width_max'] <= 6000:
        raise ValueError('invalid width range')
    if type(final) is not int or not 1 <= final <= 6000 or record[prefix+'total_discarded'] != 6000-final:
        raise ValueError('discard accounting mismatch')


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
                for record in memory:
                    indices = [r['index'] for r in record['resets']]
                    if record['reset_count'] != len(indices) or indices != sorted(set(indices)) or any(type(i) is not int or not 0 <= i < 6000 for i in indices):
                        raise ValueError('invalid reset records')
                    if record['kind'] not in ('window', 'exponential', 'dual'):
                        raise ValueError('invalid memory kind')
                    if arm == 'sgd':
                        if record['kind'] != 'exponential' or any(record[f] is not None for f in (
                                'width_mean', 'width_final', 'width_min', 'width_max', 'total_discarded')) or indices:
                            raise ValueError('SGD has no finite window')
                    else:
                        if record['kind'] != ('dual' if arm in ('retain', 'random_fallback') else 'window'):
                            raise ValueError('invalid memory kind')
                        check_widths(record)
                        for reset in record['resets']:
                            if any(type(reset[f]) is not int for f in ('width_before', 'width_after', 'discarded')) or not (
                                    reset['width_before']+1-reset['discarded'] == reset['width_after'] and
                                    0 <= reset['width_before'] <= reset['index'] and 1 <= reset['width_after'] <= reset['index']+1 and reset['discarded'] >= 0):
                                raise ValueError('invalid reset conservation')
                        if record['kind'] == 'dual':
                            check_widths(record, 'adwin_')
                            share = record['regime_fast_share']
                            if type(share) is not float or not 0. <= share <= 1.:
                                raise ValueError('invalid regime share')
                fields = ('excess_mse', 'post_mse', 'stable_mse', 'adaptation_latency')
                c = {f: None if values[0]['coordinates'][coord][f] is None else float(np.mean([
                    v['coordinates'][coord][f] for v in values])) for f in fields}
                c.update(resets_total=sum(v['reset_count'] for v in memory), events={})
                for field in ('width_mean', 'width_final', 'total_discarded'):
                    c[field] = None if arm == 'sgd' else float(np.mean([v[field] for v in memory]))
                dual = arm in ('retain', 'random_fallback')
                for field in ('adwin_width_mean', 'adwin_width_final', 'adwin_total_discarded', 'regime_fast_share'):
                    c[field] = float(np.mean([v[field] for v in memory])) if dual else None
                kinds = [e['kind'] for e in memory[0]['events']]
                for kind in kinds:
                    events = [[e for e in v['events'] if e['kind'] == kind] for v in memory]
                    if any(len(e) != 1 for e in events):
                        raise ValueError('missing/duplicate reset event')
                    events = [e[0] for e in events]
                    if any(type(e['hit']) is not bool or type(e['latency']) is not int or not (
                            0 <= e['latency'] < 100 if e['hit'] else e['latency'] == 100) for e in events):
                        raise ValueError('invalid reset event')
                    c['events'][kind] = {'hits': sum(e['hit'] for e in events), 'total': len(valid),
                        'latency': float(np.mean([e['latency'] for e in events])),
                        'latency_interval95': interval([e['latency'] for e in events])}
                item['coordinates'][coord] = c
            result[arm]['fixtures'][name] = item
    return result


def summarize(directory):
    tuning = read_stage(directory, 'tuning')
    manifest = json.loads((directory/'manifest.json').read_text())
    if manifest != make_manifest(tuning):
        raise ValueError('manifest differs from tuning')
    screen = manifest['screen']
    status = 'awaiting_confirmation' if screen['status'] == 'eligible' else screen['status']
    result = {'status': status, 'closed': status != 'awaiting_confirmation', 'protocol': manifest['protocol'],
        'manifest_digest': digest(manifest), 'screen': screen,
        'counts': {'tuning': len(KEYS['tuning']), 'confirmation': 0}, 'decisions': {}, 'absolute': {},
        'elapsed_seconds': {'tuning': {a: float(sum(r.get('seconds', 0.) for k, r in tuning.items()
                                                   if k.startswith(a+'/'))) for a in GRIDS}}}
    if (directory/'confirmation.json').exists():
        if screen['status'] != 'eligible': raise ValueError('forbidden confirmation stage')
        rows = read_stage(directory, 'confirmation')
        result['counts']['confirmation'] = len(KEYS['confirmation'])
        result['elapsed_seconds']['confirmation'] = {a: float(sum(r.get('seconds', 0.) for k, r in rows.items()
                                                                   if k.startswith(a+'/'))) for a in ARMS}
        result['decisions'] = {'retain': performance_decision(rows)}
        result['status'], result['closed'] = result['decisions']['retain']['status'], True
        result['absolute'] = absolute_summary(rows)
    return result


def number(value):
    return '—' if value is None else f'{value:.6f}'


def markdown(summary):
    lines = ['# V3 oracle-schedule retention', '', f'Disposition: **{summary["status"]}**.', '',
             '| Stage | Rows |', '| --- | ---: |']
    lines += [f'| {k} | {v} |' for k, v in summary['counts'].items()]
    lines += ['', '## Finite-menu tuning', '', 'Each searched family: 12 configurations ×8 seeds ×5 fixtures. '
              'Same objective: half primary post-switch MSE plus half mean of14 retention metrics.', '',
              '| Family | Index | Configuration | Tuning objective | Menu endpoint fields |', '| --- | ---: | --- | ---: | --- |']
    screen = summary['screen']
    for arm, i in screen['indices'].items():
        config, endpoints = screen['selected'][arm], []
        for field, value in config.items():
            options = sorted({c[field] for c in GRIDS[arm]})
            if len(options) > 1 and value in (options[0], options[-1]): endpoints.append(field)
        lines.append(f'| {arm} | {i} | `{json.dumps(config)}` | {screen["objectives"][arm][i]:.6f} | {", ".join(endpoints) or "none"} |')
    lines += ['', 'Endpoint choices remain in the registered finite menu; no extension or global-optimum claim. '
              'Oracle_nofallback is the fixed fast base without slow state. Random_fallback uses the selected delta/H.']
    if 'random_frequency' in screen:
        f = screen['random_frequency']
        lines += ['', f'Frozen random p={f["probability"]:.12f}, from {f["starts"]} requests / '
                  f'{f["coordinate_time"]} tuning coordinate-updates, 16-update suppression, opportunities from t0. '
                  'Expected pooled frequency is matched, not actual counts or memory age.']
    lines += ['', *screen['reasons']]
    if summary['absolute']:
        lines += ['', '## Independent primary performance', '', '| Policy | Finite seeds | Primary MSE | 95% interval |', '| --- | ---: | ---: | --- |']
        for arm, row in summary['absolute'].items():
            m = row.get('metrics', {}).get('primary')
            lines.append(f'| {arm} | {row["finite_seeds"]} | {number(m["mean"] if m else None)} | {m["interval95"] if m else "unavailable"} |')
    for arm, decision in summary['decisions'].items():
        lines += ['', f'## {arm}: {decision["status"]}', '',
                  'All75 comparisons are required: >=10% primary improvement over window/sgd/adwin/random_fallback, '
                  'primary preservation against oracle_nofallback, every retention bound, and strict improvement on '
                  'the8 stable/noise cells against oracle_nofallback.', '',
                  '| Contrast | Mode | Control | Policy | Delta | 95% interval | Pass |',
                  '| --- | --- | ---: | ---: | ---: | --- | --- |']
        for key, cell in decision['cells'].items():
            lo, hi = cell['interval95']
            lines.append(f'| {key} | {cell["mode"]} | {cell["control"]:.6f} | {cell["candidate"]:.6f} | {cell["delta"]:.6f} | [{lo:.6f}, {hi:.6f}] | {cell["pass"]} |')
        if 'reason' in decision: lines += ['', decision['reason']]
    if summary['absolute']:
        lines += ['', '## Absolute errors and memory', '',
                  '| Policy/fixture/coordinate | Excess MSE | Post MSE | Stable MSE | Recovery latency | Mean vector update norm | Total requests | Fast mean width | Fast final width | Fast discarded | ADWIN mean width | Fast share |',
                  '| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |']
        for arm, row in summary['absolute'].items():
            for name, data in row.get('fixtures', {}).items():
                for coord, c in data['coordinates'].items():
                    fields = [c['excess_mse'], c['post_mse'], c['stable_mse'], c['adaptation_latency'],
                              data['update_norm_mean'], c['resets_total'], c['width_mean'], c['width_final'], c['total_discarded'],
                              c['adwin_width_mean'], c['regime_fast_share']]
                    lines.append(f'| {arm}/{name}/{coord} | '+' | '.join(number(v) for v in fields)+' |')
        lines += ['', 'Width counts retained observations, not physical storage. SGD uses exponential weights '
                  'and has no literal window. Fixed windows evict routinely without reset flags; ADWIN flags '
                  'window shrinkage, and the ADWIN slow state manages its own shrinkage untouched by requests. '
                  'Discarded totals include routine cap evictions. Vector norms repeat per fixture. Fast share is the '
                  'post-burn fraction of predictions taken from the fast window.', '',
                  '## Actual request timing', '',
                  '| Policy/fixture/coordinate/event | Hits/finite seeds | Censored latency |', '| --- | --- | ---: |']
        for arm, row in summary['absolute'].items():
            if arm in ('window', 'sgd', 'adwin'): continue
            for name, data in row.get('fixtures', {}).items():
                for coord, c in data['coordinates'].items():
                    for kind, e in c['events'].items():
                        lines.append(f'| {arm}/{name}/{coord}/{kind} | {e["hits"]}/{e["total"]} | {e["latency"]:.6f} |')
    lines += ['', '## Measured execution time', '', '| Stage | Family | Seconds |', '| --- | --- | ---: |']
    for stage, families in summary['elapsed_seconds'].items():
        lines += [f'| {stage} | {a} | {seconds:.2f} |' for a, seconds in families.items()]
    lines += ['', 'Each searched family consumes 5,184,000 coordinate observations. Times exclude archive '
              'writes and share cached fixtures. Configuration budgets are equal, not CPU costs.', '', '## Scope and reproduction', '',
              'ADWIN2 is independently implemented from the paper: practical Eq.(3.1), five buckets per size, '
              'minimum subwindow5. Gaussian observations violate the bounded-input premise; no corresponding '
              'formal guarantee or library-release parity is claimed. All policies see unchanged raw observations.', '',
              'Perfect timing is privileged, not perfect segmentation: retaining K_fast=4 at the true event may '
              'retain old-regime data. In stationary fixtures the candidate reduces to ADWIN2 by construction; '
              'that is not reported as a discovery. No schedule outcome overrides candidate performance. '
              'Candidate success requires all75 comparisons. All outcomes close this registration.', '',
              'Intervals resample whole seeds10000 times with seed105000. Finite menus and synthetic fixtures '
              'do not establish global optimizer superiority, population guarantees or general neural-memory utility. '
              'Every reached row and source is archived; prior studies remain intact.', '',
              '`python check_v3_retention.py --evidence results/v3-retention --reproduce` regenerates every '
              'reached row and scientific manifest/summary at rtol1e-11/atol1e-13. '
              '`python report_v3_retention.py --check` verifies both generated reports.', '']
    return '\n'.join(lines)


def publish_report(directory, check=False):
    summary = summarize(directory)
    for name, content in {'summary.json': json.dumps(summary, indent=2, sort_keys=True)+'\n', 'report.md': markdown(summary)}.items():
        if check:
            if (directory/name).read_text() != content: raise ValueError('stale report '+name)
        else: (directory/name).write_text(content)
    print('RESULT', summary['status'], summary['counts'], flush=True)
    return summary


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--directory', type=Path, default=DIRECTORY)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    publish_report(args.directory, args.check)
