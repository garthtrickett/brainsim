"""Separate-reference results: native decisions, explanatory diagnostics, independent learning."""
import argparse
import json
from pathlib import Path

import numpy as np

from study_v3_reference import DIRECTORY, diagnostic_result, make_manifest, read_stage
from v3_reference import DETECTORS, FIXTURES
from v3_reference_policy import (KEYS, SEEDS, detector_decision, digest, interval, performance_decision)

EVENT_COORDINATES = (('core', 'switch_quiet'), ('core', 'switch_noisy'),
                     ('mixed', 'increase_first'), ('mixed', 'decrease_first'))


def explanatory_summary(rows):
    result = {}
    for arm in DETECTORS:
        valid = [rows[f'{arm}/{s}'] for s in SEEDS['diagnostics'] if rows[f'{arm}/{s}']['status'] == 'ok']
        if not valid:
            result[arm] = {'n': 0}
            continue
        for mode in ('fixed', 'closed'):
            for name, coord in EVENT_COORDINATES:
                for kind in ('target_down', 'target_up'):
                    misses, recovered, measurements = [], [], []
                    for row in valid:
                        raw = row['explanatory_events'][mode][name][coord]
                        if len(raw) != 2 or {e['kind'] for e in raw} != {'target_down', 'target_up'}:
                            raise ValueError('missing/duplicate explanatory event')
                        event = next(e for e in raw if e['kind'] == kind)
                        alarms = row['modes'][mode][name][coord]['events']
                        alarm = [e for e in alarms if e['kind'] == kind]
                        if len(alarm) != 1 or alarm[0]['index'] != event['index']:
                            raise ValueError('unmatched explanatory/diagnostic event')
                        latency, success = event['recovery_latency'], event['recovery_success']
                        if type(success) is not bool or type(latency) is not int or not (
                                0 <= latency <= 990 if success else latency == 1000):
                            raise ValueError('invalid recovery record')
                        if type(event['recovered_within_100']) is not bool or event['recovered_within_100'] != (success and latency+10 <= 100):
                            raise ValueError('inconsistent recovery window')
                        misses.append(int(not alarm[0]['hit']))
                        recovered.append(int(event['recovered_within_100']))
                        measurements.append(event)
                    intersections = [m*r for m, r in zip(misses, recovered)]
                    count = sum(misses)
                    item = {'n': len(valid), 'missed_count': count, 'recovered_count': sum(recovered),
                            'missed_and_recovered_count': sum(intersections),
                            'recovered_fraction_among_missed': sum(intersections)/count if count else None,
                            'miss_rate_interval95': interval(misses), 'recovery_rate_interval95': interval(recovered),
                            'joint_rate_interval95': interval(intersections)}
                    for field in ('q_max100', 'error_at_event', 'mse_before100', 'mse_after20',
                                  'mse_after100', 'mse_after200', 'recovery_latency'):
                        values = [m[field] for m in measurements]
                        item[field] = {'mean': float(np.mean(values)), 'interval95': interval(values)}
                    result[f'{arm}/{mode}/{name}/{coord}/{kind}'] = item
    return result


def learning_summary(rows, stage):
    result = {}
    arms = DETECTORS if stage == 'diagnostics' else tuple(sorted({k.split('/')[0] for k in rows}))
    for arm in arms:
        valid = [rows[f'{arm}/{s}'] for s in SEEDS[stage] if rows[f'{arm}/{s}']['status'] == 'ok']
        if not valid:
            result[arm] = {'n': 0}
            continue
        modes = ('fixed', 'closed') if stage == 'diagnostics' else ('closed',)
        for mode in modes:
            fixtures = [r['learning'][mode] if stage == 'diagnostics' else r['fixtures'] for r in valid]
            for name in FIXTURES:
                for coord in fixtures[0][name]['coordinates']:
                    metrics = [r[name]['coordinates'][coord] for r in fixtures]
                    item = {'n': len(valid), 'update_norm_mean': float(np.mean([r[name]['update_norm_mean'] for r in fixtures]))}
                    for field in ('excess_mse', 'post_mse', 'stable_mse', 'adaptation_latency', 'gate_settled'):
                        values = [m[field] for m in metrics]
                        if any(v is None for v in values) and not all(v is None for v in values):
                            raise ValueError('inconsistent optional learning metric')
                        item[field] = None if values[0] is None else float(np.mean(values))
                    result[f'{arm}/{mode}/{name}/{coord}'] = item
    return result


def summarize(directory):
    calibration = read_stage(directory, 'calibration')
    manifest = json.loads((directory/'manifest.json').read_text())
    if manifest != make_manifest(calibration):
        raise ValueError('manifest differs from calibration')
    reached, decisions, common, events, learning = ['calibration'], {}, {}, {}, {}
    status = 'calibration_inconclusive'
    if manifest['status'] == 'eligible':
        status = 'awaiting_diagnostics'
        if (directory/'diagnostics.json').exists():
            reached.append('diagnostics')
            rows = read_stage(directory, 'diagnostics')
            native = diagnostic_result(directory, manifest)
            if native != json.loads((directory/'diagnostic-decision.json').read_text()):
                raise ValueError('stale detector decision')
            decisions['diagnostics'] = {a: detector_decision(rows, a) for a in DETECTORS}
            common = {a: detector_decision(rows, a, common=True) for a in DETECTORS}
            events = explanatory_summary(rows)
            learning['diagnostics'] = learning_summary(rows, 'diagnostics')
            # This invariant does not count as independent evidence in two modes.
            for seed in SEEDS['diagnostics']:
                row = rows[f'separate/{seed}']
                if row['status'] == 'ok' and row['modes']['fixed'] != row['modes']['closed']:
                    raise ValueError('separate-reference gate depends on learner')
            status = native['status']
            if status == 'detector_pass':
                status = 'awaiting_performance'
                if (directory/'performance.json').exists():
                    reached.append('performance')
                    rows = read_stage(directory, 'performance')
                    decisions['performance'] = performance_decision(rows)
                    learning['performance'] = learning_summary(rows, 'performance')
                    status = decisions['performance']['status']
    for stage in KEYS:
        if (directory/(stage+'.json')).exists() != (stage in reached):
            raise ValueError('forbidden/missing stage '+stage)
    if 'diagnostics' not in reached and (directory/'diagnostic-decision.json').exists():
        raise ValueError('unexpected diagnostic decision')
    return {'status': status, 'closed': not status.startswith('awaiting_'), 'protocol': manifest['protocol'],
            'manifest_digest': digest(manifest), 'thresholds': manifest.get('thresholds', {}),
            'configs': manifest['configs'], 'counts': {s: len(KEYS[s]) if s in reached else 0 for s in KEYS},
            'reached': reached, 'decisions': decisions, 'common_threshold_diagnostics': common,
            'explanatory_events': events, 'learning_summaries': learning}


def detector_table(lines, arm, decision):
    lines += ['', f'### {arm}: {decision["status"]}', '',
              '| Cell | Count/total | Rate | 95% interval | Censored latency | Pass |',
              '| --- | --- | ---: | --- | ---: | --- |']
    for key, cell in decision['cells'].items():
        lo, hi = cell['interval95']
        latency = f'{cell["latency"]:.3f}' if 'latency' in cell else '—'
        lines.append(f'| {key} | {cell["count"]}/{cell["total"]} | {cell["rate"]:.5f} | '
                     f'[{lo:.5f}, {hi:.5f}] | {latency} | {cell["pass"]} |')
    if 'reason' in decision:
        lines += ['', decision['reason']]


def number(value):
    return '—' if value is None else f'{value:.6f}'


def markdown(summary):
    lines = ['# V3 separate-reference experiment', '', f'Disposition: **{summary["status"]}**.', '',
             '| Stage | Rows |', '| --- | ---: |']
    lines += [f'| {s} | {n} |' for s, n in summary['counts'].items()]
    lines += ['', '## Fixed configurations and native thresholds', '',
              '| Policy | Configuration | Fixed threshold | Active threshold |', '| --- | --- | ---: | ---: |']
    for arm, config in summary['configs'].items():
        t = summary['thresholds'].get(arm, {})
        lines.append(f'| {arm} | `{json.dumps(config)}` | {number(t.get("fixed"))} | {number(t.get("closed"))} |')
    if 'diagnostics' in summary['decisions']:
        lines += ['', '## Native detector decisions: authoritative advancement gate']
        for arm, decision in summary['decisions']['diagnostics'].items():
            detector_table(lines, arm, decision)
        lines += ['', '## Common-threshold diagnostics: explanatory only', '',
                  'Every unchanged gate sequence is scored at separate/fixed calibration threshold. '
                  'These cells do not select settings or permit advancement; stationary failures remain visible.']
        for arm, decision in summary['common_threshold_diagnostics'].items():
            detector_table(lines, arm, decision)
        lines += ['', '## Missing alarms and prediction recovery: diagnostic data only', '',
                  'Recovery within 100 requires all ten consecutive predictions with absolute error <.2 '
                  'to fit within the first 100 observations. Ratios condition on missed alarms only when '
                  'that denominator is nonzero. These records do not establish independent learning gains.', '',
                  '| Setup/mode/fixture/coordinate/event | Seeds | Missed | Recovered | Both | Recovered/missed | Post-100 MSE | Post-200 MSE | Max q mean |',
                  '| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |']
        for key, row in summary['explanatory_events'].items():
            if row['n'] == 0:
                lines.append(f'| {key} | 0 | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable |')
                continue
            lines.append(f'| {key} | {row["n"]} | {row["missed_count"]} | {row["recovered_count"]} | '
                         f'{row["missed_and_recovered_count"]} | {number(row["recovered_fraction_among_missed"])} | '
                         f'{row["mse_after100"]["mean"]:.6f} | {row["mse_after200"]["mean"]:.6f} | {row["q_max100"]["mean"]:.6f} |')
        lines += ['', 'The summary JSON also includes seed-bootstrap intervals for miss, recovery and joint rates, '
                  'q maxima, signed event error, pre-event MSE, post-20/100/200 MSE and censored recovery latency. '
                  'The conditional recovered/missed ratio is descriptive; its denominator is shown explicitly.']
    if 'performance' in summary['decisions']:
        decision = summary['decisions']['performance']
        lines += ['', '## Independent performance: all 90 required contrasts', '',
                  '| Contrast | Control | Separate | Difference | 95% interval | Pass |',
                  '| --- | ---: | ---: | ---: | --- | --- |']
        for key, cell in decision['cells'].items():
            lo, hi = cell['interval95']
            lines.append(f'| {key} | {cell["control"]:.6f} | {cell["candidate"]:.6f} | {cell["delta"]:.6f} | '
                         f'[{lo:.6f}, {hi:.6f}] | {cell["pass"]} |')
        if 'reason' in decision:
            lines += ['', decision['reason']]
    for stage, rows in summary['learning_summaries'].items():
        lines += ['', f'## Absolute learning metrics: {stage}', '',
                  '| Setup/mode/fixture/coordinate | Finite seeds | Excess MSE | Post-200 MSE | Stable MSE | Adaptation latency | Mean update norm | Settled q |',
                  '| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |']
        for key, row in rows.items():
            if row['n'] == 0:
                lines.append(f'| {key} | 0 | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable |')
                continue
            fields = ('excess_mse', 'post_mse', 'stable_mse', 'adaptation_latency', 'update_norm_mean', 'gate_settled')
            lines.append(f'| {key} | {row["n"]} | '+ ' | '.join(number(row[f]) for f in fields)+' |')
        lines += ['', 'Update norms are for the fixture vector, repeated across its coordinates for context. '
                  'Finite-seed counts expose failed trajectories; missing required performance rows cannot pass.']
    lines += ['', '## Limits', '',
              'Separate observes a fixed zero reference. Its fixed/active gate sequences are identical by construction; '
              'their two sets of cells are not independent replications. The toy exposes supervised observations; '
              'this does not establish an efficient reference-gradient mechanism for a general neural model.', '',
              'Native detector criteria remain >=80% target detection and <=5% false alarms in every registered '
              'cell, including mixed changes. All 90 performance contrasts must pass for positive. Settings are '
              'fixed/transferred, not globally optimized; matching mean q does not match realized update norms. '
              'A common-threshold improvement cannot repair the native decision. Diagnostic prediction metrics '
              'cannot substitute for the independent performance partition.', '',
              'Intervals use 10,000 whole-seed bootstrap resamples, seed 65000. Point screens and degenerate '
              'zero/one-rate bootstrap intervals are not population guarantees. No agent/default integration follows. '
              'Every old experiment remains intact.', '',
              'Reproduce every reached row and summary with `python check_v3_reference.py --evidence '
              'results/v3-reference --reproduce`; check this report with `python report_v3_reference.py --check`. '
              'Numerical tolerance is rtol 1e-11/atol 1e-13, excluding only timing and regenerated input hashes.', '']
    return '\n'.join(lines)


def publish_report(directory, check=False):
    summary = summarize(directory)
    outputs = {'summary.json': json.dumps(summary, indent=2, sort_keys=True)+'\n', 'report.md': markdown(summary)}
    for name, content in outputs.items():
        path = directory/name
        if check:
            if path.read_text() != content:
                raise ValueError('stale report '+name)
        else:
            path.write_text(content)
    print('RESULT', summary['status'], summary['counts'], flush=True)
    return summary


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--directory', type=Path, default=DIRECTORY)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    publish_report(args.directory, args.check)


if __name__ == '__main__':
    main()
