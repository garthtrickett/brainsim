"""Derived persistent-detector report, including every control and failed cell."""
import argparse
import json
from pathlib import Path

import numpy as np

from study_v3_persistent import DIRECTORY, diagnostic_result, make_manifest, read_stage, write
from v3_persistent import DETECTORS
from v3_persistent_policy import KEYS, SEEDS, detector_decision, digest, performance_decision


def summarize(directory):
    calibration = read_stage(directory, 'calibration')
    manifest = json.loads((directory/'manifest.json').read_text())
    if manifest != make_manifest(calibration):
        raise ValueError('manifest differs from calibration')
    reached, decisions, descriptions = ['calibration'], {}, {}
    status = 'calibration_inconclusive'
    if manifest['status'] == 'eligible':
        status = 'awaiting_diagnostics'
        if (directory/'diagnostics.json').exists():
            reached.append('diagnostics')
            rows = read_stage(directory, 'diagnostics')
            candidate = diagnostic_result(directory, manifest)
            if candidate != json.loads((directory/'diagnostic-decision.json').read_text()):
                raise ValueError('stale detector decision')
            decisions['diagnostics'] = {a: detector_decision(rows, a) for a in DETECTORS}
            status = candidate['status']
            for arm in DETECTORS:
                valid = [rows[f'{arm}/{s}'] for s in SEEDS['diagnostics'] if rows[f'{arm}/{s}']['status'] == 'ok']
                if not valid:
                    descriptions[arm] = {'n': 0}
                    continue
                for mode, fixtures in valid[0]['modes'].items():
                    for name, coordinates in fixtures.items():
                        for coord in coordinates:
                            metrics = [r['modes'][mode][name][coord] for r in valid]
                            descriptions[f'{arm}/{mode}/{name}/{coord}'] = {
                                'n': len(valid), 'gate_initial': float(np.mean([m['gate_initial'] for m in metrics])),
                                'gate_mean': float(np.mean([m['gate_mean'] for m in metrics])),
                                'point_alarm_rate': float(np.mean([m['point_count']/m['point_total'] for m in metrics])),
                                'block_alarm_rate': float(np.mean([m['block_count']/m['block_total'] for m in metrics]))}
            if status == 'detector_pass':
                status = 'awaiting_performance'
                if (directory/'performance.json').exists():
                    reached.append('performance')
                    decisions['performance'] = performance_decision(read_stage(directory, 'performance'))
                    status = decisions['performance']['status']
    for stage in KEYS:
        if (directory/(stage+'.json')).exists() != (stage in reached):
            raise ValueError('forbidden/missing stage ' + stage)
    if 'diagnostics' not in reached and (directory/'diagnostic-decision.json').exists():
        raise ValueError('unexpected diagnostic decision')
    return {'status': status, 'closed': not status.startswith('awaiting_'),
            'protocol': manifest['protocol'], 'manifest_digest': digest(manifest),
            'thresholds': manifest.get('thresholds', {}), 'configs': manifest['configs'],
            'counts': {s: len(KEYS[s]) if s in reached else 0 for s in KEYS},
            'reached': reached, 'decisions': decisions, 'descriptive_diagnostics': descriptions}


def markdown(summary):
    lines = ['# V3 persistent detector experiment', '', f"Disposition: **{summary['status']}**.", '',
             'Four fixed detector policies; no hyperparameter selection. Calibration precedes fresh '
             'confirmation. All 24 candidate cells must pass before independent performance.', '',
             '| Stage | Rows |', '| --- | ---: |']
    lines += [f'| {stage} | {count} |' for stage, count in summary['counts'].items()]
    lines += ['', '## Fixed policies and thresholds', '', '| Policy | Configuration | Fixed threshold | Closed threshold |',
              '| --- | --- | ---: | ---: |']
    for arm, config in summary['configs'].items():
        thresholds = summary['thresholds'].get(arm, {})
        lines.append(f'| {arm} | `{json.dumps(config)}` | {thresholds.get("fixed", "—")} | {thresholds.get("closed", "—")} |')
    for arm, decision in summary['decisions'].get('diagnostics', {}).items():
        lines += ['', f'## Detector: {arm} — {decision["status"]}', '',
                  '| Cell | Count/total | Rate | Seed-bootstrap 95% interval | Censored latency | Pass |',
                  '| --- | --- | ---: | --- | ---: | --- |']
        for name, cell in decision['cells'].items():
            lo, hi = cell['interval95']
            latency = f'{cell["latency"]:.3f}' if 'latency' in cell else '—'
            lines.append(f'| {name} | {cell["count"]}/{cell["total"]} | {cell["rate"]:.5f} | '
                         f'[{lo:.5f}, {hi:.5f}] | {latency} | {cell["pass"]} |')
        if 'reason' in decision:
            lines += ['', decision['reason']]
    if summary['descriptive_diagnostics']:
        lines += ['', '## All descriptive detector conditions', '',
                  '| Arm/mode/fixture/coordinate | Finite seeds | Startup gate | Settled gate | Point alarms | Block alarms |',
                  '| --- | ---: | ---: | ---: | ---: | ---: |']
        for key, row in summary['descriptive_diagnostics'].items():
            if row['n'] == 0:
                lines.append(f'| {key} | 0 | unavailable | unavailable | unavailable | unavailable |')
                continue
            lines.append(f'| {key} | {row["n"]} | {row["gate_initial"]:.6f} | {row["gate_mean"]:.6f} | '
                         f'{row["point_alarm_rate"]:.6f} | {row["block_alarm_rate"]:.6f} |')
    if 'performance' in summary['decisions']:
        decision = summary['decisions']['performance']
        lines += ['', '## Independent performance', '', '| Contrast | Control | Candidate | Difference | 95% interval | Pass |',
                  '| --- | ---: | ---: | ---: | --- | --- |']
        for key, cell in decision['cells'].items():
            lo, hi = cell['interval95']
            lines.append(f'| {key} | {cell["control"]:.6f} | {cell["candidate"]:.6f} | {cell["delta"]:.6f} | '
                         f'[{lo:.6f}, {hi:.6f}] | {cell["pass"]} |')
        if 'reason' in decision:
            lines += ['', decision['reason']]
    lines += ['', '## Interpretation and limits', '',
              'Only stationary core coordinates use block alarm rates as false alarms. Mixed increase_first '
              'pairs target-down with noise increase and target-up with noise decrease; decrease_first reverses '
              'that pairing. Each direction remains separate. Exactly quiet and drift are descriptive.', '',
              'Intervals resample whole seeds (10,000 resamples, seed 55000). Rate thresholds are point screens, '
              'not population guarantees. Four overlapping signed scores are correlated, not four independent '
              'pieces of evidence. The standardized mean score is not a calibrated p-value. The CUSUM reference '
              'uses moving estimates and empirical calibration, not known-parameter textbook guarantees.', '',
              'All settings are transferred or fixed before data. This tests specified finite policies, not '
              'globally optimal tuning or optimizer-wide superiority. Passing detection alone establishes no '
              'learning gain. A failure closes this experiment; a positive performance result warrants only '
              'a separately registered agent experiment. No existing result or default is changed.', '',
              'Reproduce every reached row and decision with `python check_v3_persistent.py --evidence '
              'results/v3-persistent --reproduce`. Verify this report with `python report_v3_persistent.py --check`. '
              'Only timings and regenerated scientific-input hashes are excluded from numerical reproduction.', '']
    return '\n'.join(lines)


def publish_report(directory, check=False):
    summary = summarize(directory)
    outputs = {'summary.json': json.dumps(summary, indent=2, sort_keys=True)+'\n', 'report.md': markdown(summary)}
    for name, content in outputs.items():
        path = directory/name
        if check:
            if path.read_text() != content:
                raise ValueError('stale report ' + name)
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
