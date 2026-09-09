"""Robustness results with lie-activity accounting."""
import argparse
import json
from pathlib import Path

import numpy as np

from study_v4_robust import DIRECTORY, make_manifest, read_stage
from v4_robust import ARMS, GRIDS
from v4_robust_policy import (KEYS, SEEDS, digest, interval, metric_values,
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
                    if record['kind'] not in ('window', 'exponential', 'graded'):
                        raise ValueError('invalid memory kind')
                    if arm == 'sgd':
                        if record['kind'] != 'exponential' or any(record[f] is not None for f in (
                                'width_mean', 'width_final', 'width_min', 'width_max', 'total_discarded')) or indices:
                            raise ValueError('SGD has no finite window')
                    elif arm in ('graded', 'adwin_gated'):
                        if record['kind'] != 'graded':
                            raise ValueError('invalid memory kind')
                        for reset in record['resets']:
                            if reset.get('kind') not in ('delayed', 'false'):
                                raise ValueError('unclassified alarm')
                        if type(record['alarm_total']) is not int or record['alarm_total'] != len(indices):
                            raise ValueError('alarm accounting mismatch')
                        if not all(type(g) is int and g >= 0 for g in record['gain_levels']):
                            raise ValueError('invalid gain levels')
                    else:
                        if record['kind'] != 'window':
                            raise ValueError('invalid memory kind')
                        check_widths(record)
                fields = ('excess_mse', 'post_mse', 'stable_mse', 'adaptation_latency')
                c = {f: None if values[0]['coordinates'][coord][f] is None else float(np.mean([
                    v['coordinates'][coord][f] for v in values])) for f in fields}
                c.update(resets_total=sum(v['reset_count'] for v in memory), events={})
                for field in ('width_mean', 'width_final', 'total_discarded'):
                    c[field] = None if arm in ('sgd', 'graded', 'adwin_gated') else float(np.mean([v[field] for v in memory]))
                c['alarm_total'] = float(np.mean([v['alarm_total'] for v in memory])) if arm in ('graded', 'adwin_gated') else None
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
        result['decisions'] = {'graded': performance_decision(rows, 'graded'),
                               'adwin_gated': performance_decision(rows, 'adwin_gated')}
        result['status'], result['closed'] = result['decisions']['graded']['status'], True
        result['absolute'] = absolute_summary(rows)
    return result


def number(value):
    return '—' if value is None else f'{value:.6f}'


def markdown(summary):
    lines = ['# V4 robustness under frozen lies', '', f'Disposition: **{summary["status"]}** (graded arm).', '',
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
              'The ADWIN-gated arm uses the selected graded config on observed alarms; it is diagnostic only.', '',
              *screen['reasons']]
    if summary['absolute']:
        lines += ['', '## Independent primary performance', '', '| Policy | Finite seeds | Primary MSE | 95% interval |', '| --- | ---: | ---: | --- |']
        for arm, row in summary['absolute'].items():
            m = row.get('metrics', {}).get('primary')
            lines.append(f'| {arm} | {row["finite_seeds"]} | {number(m["mean"] if m else None)} | {m["interval95"] if m else "unavailable"} |')
    for arm, decision in summary['decisions'].items():
        lines += ['', f'## {arm}: {decision["status"]}' + ('' if arm == 'graded' else ' (diagnostic; authorizes nothing)'), '',
                  'All45 comparisons against window/SGD/ADWIN are required for the graded arm; '
                  'the ADWIN-gated arm is reported with the same instrument for comparison only.', '',
                  '| Contrast | Control | Policy | Delta | 95% interval | Pass |',
                  '| --- | ---: | ---: | ---: | --- | --- |']
        for key, cell in decision['cells'].items():
            lo, hi = cell['interval95']
            lines.append(f'| {key} | {cell["control"]:.6f} | {cell["candidate"]:.6f} | {cell["delta"]:.6f} | [{lo:.6f}, {hi:.6f}] | {cell["pass"]} |')
        if 'reason' in decision: lines += ['', decision['reason']]
    if summary['absolute']:
        lines += ['', '## Absolute errors and alarms', '',
                  '| Policy/fixture/coordinate | Excess MSE | Post MSE | Stable MSE | Recovery latency | Mean vector update norm | Total alarms | Mean width |',
                  '| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |']
        for arm, row in summary['absolute'].items():
            for name, data in row.get('fixtures', {}).items():
                for coord, c in data['coordinates'].items():
                    fields = [c['excess_mse'], c['post_mse'], c['stable_mse'], c['adaptation_latency'],
                              data['update_norm_mean'], c['resets_total'], c['width_mean']]
                    lines.append(f'| {arm}/{name}/{coord} | '+' | '.join(number(v) for v in fields)+' |')
        lines += ['', 'Alarm counts include delayed true events and false alarms; their kinds are recorded '
                  'per alarm in the raw evidence. SGD uses exponential weights and has no literal window.', '']
    lines += ['', '## Measured execution time', '', '| Stage | Family | Seconds |', '| --- | --- | ---: |']
    for stage, families in summary['elapsed_seconds'].items():
        lines += [f'| {stage} | {a} | {seconds:.2f} |' for a, seconds in families.items()]
    lines += ['', 'Configuration budgets are equal, not CPU costs. Times exclude archive writes and share '
              'cached fixtures.', '', '## Scope and reproduction', '',
              'ADWIN2 is independently implemented from the paper: practical Eq.(3.1), five buckets per size, '
              'minimum subwindow5. Gaussian observations violate the bounded-input premise; no corresponding '
              'formal guarantee or library-release parity is claimed. All policies see unchanged raw observations.', '',
              'The lie profile is frozen at registration and was never tuned. No schedule outcome overrides '
              'the advancement gate. All outcomes close this registration.', '',
              'Intervals resample whole seeds10000 times with seed185000. Finite menus and synthetic fixtures '
              'do not establish global optimizer superiority, population guarantees or general neural-memory utility. '
              'Every reached row and source is archived; prior studies remain intact.', '',
              '`python check_v4_robust.py --evidence results/v4-robust --reproduce` regenerates every '
              'reached row and scientific manifest/summary at rtol1e-11/atol1e-13. '
              '`python report_v4_robust.py --check` verifies both generated reports.', '']
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
