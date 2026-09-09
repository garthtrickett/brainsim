"""Registered burst results, timing controls and full condition-level accounting."""
import argparse
import json
from pathlib import Path

import numpy as np

from study_v3_burst import DIRECTORY, make_manifest, read_stage
from v3_burst import ARMS, GRIDS
from v3_burst_policy import (KEYS, SEEDS, detector_decision, digest, interval,
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
                activity = [r['activity'][name][coord] for r in valid]
                for record in activity:
                    starts = record['starts']
                    if record['start_count'] != len(starts) or starts != sorted(set(starts)) or any(type(i) is not int or not 146 <= i < 6000 for i in starts):
                        raise ValueError('invalid start records')
                    if type(record['active_updates']) is not int or not 0 <= record['active_updates'] <= 5854 or abs(record['duty_cycle']-record['active_updates']/5854) > 1e-14:
                        raise ValueError('invalid duty record')
                fields = ('excess_mse', 'post_mse', 'stable_mse', 'adaptation_latency')
                c = {f: None if values[0]['coordinates'][coord][f] is None else float(np.mean([
                    v['coordinates'][coord][f] for v in values])) for f in fields}
                c.update(starts_total=sum(v['start_count'] for v in activity),
                         active_updates_mean=float(np.mean([v['active_updates'] for v in activity])),
                         duty_cycle_mean=float(np.mean([v['duty_cycle'] for v in activity])), events={})
                kinds = [e['kind'] for e in activity[0]['events']]
                for kind in kinds:
                    events = [[e for e in v['events'] if e['kind'] == kind] for v in activity]
                    if any(len(e) != 1 for e in events):
                        raise ValueError('missing/duplicate pulse event')
                    events = [e[0] for e in events]
                    if any(type(e['hit']) is not bool or type(e['latency']) is not int or not (
                            0 <= e['latency'] < 100 if e['hit'] else e['latency'] == 100) for e in events):
                        raise ValueError('invalid pulse event')
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
        'manifest_digest': digest(manifest), 'threshold': manifest['threshold'], 'screen': screen,
        'counts': {'tuning': len(KEYS['tuning']), 'confirmation': 0}, 'decisions': {}, 'absolute': {},
        'elapsed_seconds': {'tuning': {a: float(sum(r.get('seconds', 0.) for k, r in tuning.items()
                                                  if k.startswith(a+'/'))) for a in GRIDS}}}
    if (directory/'confirmation.json').exists():
        if screen['status'] != 'eligible':
            raise ValueError('forbidden confirmation stage')
        rows = read_stage(directory, 'confirmation')
        result['counts']['confirmation'] = len(KEYS['confirmation'])
        result['elapsed_seconds']['confirmation'] = {a: float(sum(r.get('seconds', 0.) for k, r in rows.items()
                                                                  if k.startswith(a+'/'))) for a in ARMS}
        result['decisions'] = {a: performance_decision(rows, a) for a in ('burst', 'oracle', 'oracle_matched')}
        result['decisions']['detector_diagnostic'] = detector_decision(rows)
        result['status'], result['closed'] = result['decisions']['burst']['status'], True
        result['absolute'] = absolute_summary(rows)
    return result


def number(value):
    return '—' if value is None else f'{value:.6f}'


def markdown(summary):
    lines = ['# V3 bounded burst-controller experiment', '', f'Disposition: **{summary["status"]}**.', '',
             '| Stage | Rows |', '| --- | ---: |']
    lines += [f'| {k} | {v} |' for k, v in summary['counts'].items()]
    lines += ['', f'Frozen strict detector threshold: {summary["threshold"]:.16f}.', '',
              '## Finite-menu tuning', '', 'All searched families: 12 configurations × 8 seeds × 5 fixtures. '
              'Objective: half primary post-switch MSE plus half mean of 14 retention metrics.', '',
              '| Family | Index | Configuration | Tuning objective | Menu endpoint fields |', '| --- | ---: | --- | ---: | --- |']
    screen = summary['screen']
    for arm, i in screen['indices'].items():
        config = screen['selected'][arm]
        endpoints = []
        for field, value in config.items():
            options = sorted({c[field] for c in GRIDS[arm]})
            if len(options) > 1 and value in (options[0], options[-1]):
                endpoints.append(field)
        lines.append(f'| {arm} | {i} | `{json.dumps(config)}` | {screen["objectives"][arm][i]:.6f} | {", ".join(endpoints) or "none"} |')
    lines += ['', 'Endpoints are reported, not expanded: these are fixed menus, not global optima. '
              'oracle_matched and random use burst settings exactly, with no additional tuning.']
    if 'random_frequency' in screen:
        f = screen['random_frequency']
        lines += ['', f'Frozen random opportunity probability: **{f["probability"]:.9f}**, from '
                  f'{f["starts"]} candidate starts / {f["coordinate_time"]} tuning coordinate-updates. '
                  'Expected pooled frequency is matched; realized per-condition counts and movement are not.']
    for reason in screen['reasons']:
        lines += ['', reason]
    if summary['absolute']:
        lines += ['', '## Independent primary performance', '', '| Policy | Finite seeds | Primary MSE | 95% interval |',
                  '| --- | ---: | ---: | --- |']
        for arm, row in summary['absolute'].items():
            m = row.get('metrics', {}).get('primary')
            lines.append(f'| {arm} | {row["finite_seeds"]} | {number(m["mean"] if m else None)} | {m["interval95"] if m else "unavailable"} |')
    for arm, decision in summary['decisions'].items():
        if arm == 'detector_diagnostic':
            continue
        lines += ['', f'## {arm}: {decision["status"]}', '',
                  'Candidate alone decides advancement. Both oracle arms are privileged diagnostics.' if arm != 'burst' else
                  'All 60 candidate comparisons are required; no selected success overrides a failed cell.', '',
                  '| Contrast | Control | Policy | Delta | 95% interval | Pass |', '| --- | ---: | ---: | ---: | --- | --- |']
        for key, cell in decision['cells'].items():
            lo, hi = cell['interval95']
            lines.append(f'| {key} | {cell["control"]:.6f} | {cell["candidate"]:.6f} | {cell["delta"]:.6f} | [{lo:.6f}, {hi:.6f}] | {cell["pass"]} |')
        if 'reason' in decision:
            lines += ['', decision['reason']]
    if 'detector_diagnostic' in summary['decisions']:
        decision = summary['decisions']['detector_diagnostic']
        lines += ['', f'## Raw detector diagnostic: {decision["status"]}', '',
                  'Twelve cells, one signal. These diagnostics do not veto or establish learning performance.', '',
                  '| Cell | Count/total | Rate | Censored latency | Pass |', '| --- | --- | ---: | ---: | --- |']
        for key, cell in decision['cells'].items():
            lines.append(f'| {key} | {cell["count"]}/{cell["total"]} | {cell["rate"]:.6f} | {number(cell.get("latency"))} | {cell["pass"]} |')
    if summary['absolute']:
        lines += ['', '## Absolute errors and actual activity', '',
                  '| Policy/fixture/coordinate | Excess MSE | Post MSE | Stable MSE | Recovery latency | Mean vector update norm | Total starts | Mean active updates | Duty |',
                  '| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |']
        for arm, row in summary['absolute'].items():
            for name, data in row.get('fixtures', {}).items():
                for coord, c in data['coordinates'].items():
                    fields = [c['excess_mse'], c['post_mse'], c['stable_mse'], c['adaptation_latency'],
                              data['update_norm_mean'], c['starts_total'], c['active_updates_mean'], c['duty_cycle_mean']]
                    lines.append(f'| {arm}/{name}/{coord} | '+ ' | '.join(number(v) for v in fields)+' |')
        lines += ['', 'Vector update norm is repeated across coordinates of its fixture. Zero burst activity '
                  'for continuous/Adam/SGD does not mean zero learning. Duty excludes the fixed startup period.', '',
                  '## Actual burst starts near events', '',
                  '| Policy/fixture/coordinate/event | Hits/finite seeds | Censored start latency |', '| --- | --- | ---: |']
        for arm, row in summary['absolute'].items():
            if arm in ('continuous', 'adam', 'sgd'):
                continue
            for name, data in row.get('fixtures', {}).items():
                for coord, c in data['coordinates'].items():
                    for kind, e in c['events'].items():
                        lines.append(f'| {arm}/{name}/{coord}/{kind} | {e["hits"]}/{e["total"]} | {e["latency"]:.6f} |')
    lines += ['', '## Measured row execution time', '',
              '| Stage | Family | Seconds |', '| --- | --- | ---: |']
    for stage, families in summary['elapsed_seconds'].items():
        lines += [f'| {stage} | {a} | {seconds:.2f} |' for a, seconds in families.items()]
    lines += ['', 'Each searched family executes 5,184,000 learner coordinate-updates. '
              'Times exclude archive writes and share a causal signal cache: the first family '
              'pays cache initialization. These are observed times, not equal CPU-cost claims.', '',
              '## Scope and evidence', '',
              'Rate caps do not cap realized Adam update norms. Perfect timing is privileged and is not a '
              'mathematical upper bound. The separately tuned oracle tests this finite controller menu; '
              'the matched oracle holds candidate parameters fixed. Random scheduling matches expected '
              'pooled frequency only, so actual activity and per-condition differences remain visible.', '',
              'Candidate advancement requires >=10% primary improvement over Adam, SGD, continuous and random '
              'with paired upper delta <0, plus every retention upper delta <=max(.002,.1*control). '
              'No oracle or alarm score overrides that decision. A positive result would warrant only '
              'a separately authorized broader supervised benchmark; all outcomes close this registration.', '',
              'Whole-seed intervals: 10,000 resamples, seed75000. The archive retains every reached row, '
              'tuning score, source snapshot, event start and candidate event-error/recovery record. '
              'Small synthetic fixtures and finite menus do not establish global optimizer superiority '
              'or a scalable reference-gradient mechanism. Every earlier study remains unchanged.', '',
              '`python check_v3_burst.py --evidence results/v3-burst --reproduce` regenerates every reached '
              'row and manifest/summary at rtol1e-11/atol1e-13. `python report_v3_burst.py --check` '
              'checks both generated reports.', '']
    return '\n'.join(lines)


def publish_report(directory, check=False):
    summary = summarize(directory)
    outputs = {'summary.json': json.dumps(summary, indent=2, sort_keys=True)+'\n', 'report.md': markdown(summary)}
    for name, content in outputs.items():
        if check:
            if (directory/name).read_text() != content:
                raise ValueError('stale report '+name)
        else:
            (directory/name).write_text(content)
    print('RESULT', summary['status'], summary['counts'], flush=True)
    return summary


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--directory', type=Path, default=DIRECTORY)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    publish_report(args.directory, args.check)
