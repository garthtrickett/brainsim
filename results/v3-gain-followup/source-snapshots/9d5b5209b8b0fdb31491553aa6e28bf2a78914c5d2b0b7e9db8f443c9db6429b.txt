"""Independent follow-up report: preserve search flags alongside detector findings."""
import argparse
import hashlib
import json
from pathlib import Path

import numpy as np

from study_v3_gain import (DIRECTORY, diagnostic_result, make_manifest, read_stage,
                           stage_exists)
from v3_gain_policy import GATED, KEYS, SEEDS, digest, performance_decision


def summarize(directory):
    tuning = read_stage(directory, 'tuning')
    manifest = json.loads((directory/'manifest.json').read_text())
    calibration = read_stage(directory, 'calibration') if manifest['screen']['detector_allowed'] else None
    if manifest != make_manifest(tuning, calibration):
        raise ValueError('manifest differs from source evidence')
    reached, decisions, descriptive = ['tuning'], {}, {}
    status = manifest['screen']['status']
    if calibration is not None:
        reached.append('calibration')
        status = 'calibration_inconclusive'
        if manifest['calibration_status'] == 'ok':
            status = 'awaiting_diagnostics'
            if stage_exists(directory, 'diagnostics'):
                reached.append('diagnostics')
                decision = diagnostic_result(directory, manifest)
                if json.loads((directory/'diagnostic-decision.json').read_text()) != decision:
                    raise ValueError('stale diagnostic decision')
                decisions['diagnostics'] = decision
                status = decision['status']
                raw = read_stage(directory, 'diagnostics')
                for arm in GATED:
                    for mode in ('fixed', 'closed'):
                        first = next((raw[f'{arm}/{s}'] for s in SEEDS['diagnostics']
                                      if raw[f'{arm}/{s}']['status'] == 'ok'), None)
                        if first is None:
                            descriptive[f'{arm}/{mode}'] = {'n': 0}
                            continue
                        for name, coords in first['modes'][mode].items():
                            for coord in coords:
                                rows = [raw[f'{arm}/{s}']['modes'][mode][name][coord]
                                        for s in SEEDS['diagnostics'] if raw[f'{arm}/{s}']['status'] == 'ok']
                                descriptive[f'{arm}/{mode}/{name}/{coord}'] = {
                                    'n': len(rows), 'gate_mean': float(np.mean([r['gate_mean'] for r in rows])),
                                    'gate_initial': float(np.mean([r['gate_initial'] for r in rows])),
                                    'point_alarm_rate': float(np.mean([r['point_count']/r['point_total'] for r in rows])),
                                    'block_alarm_rate': float(np.mean([r['block_count']/r['block_total'] for r in rows]))}
                if status == 'detector_pass':
                    status = 'search_inconclusive' if manifest['screen']['status'] != 'eligible' else 'awaiting_performance'
                    if status == 'awaiting_performance' and stage_exists(directory, 'performance'):
                        reached.append('performance')
                        decisions['performance'] = performance_decision(read_stage(directory, 'performance'))
                        status = decisions['performance']['status']
    for stage in KEYS:
        if stage_exists(directory, stage) != (stage in reached):
            raise ValueError('forbidden/missing stage: ' + stage)
    if 'diagnostics' not in reached and (directory/'diagnostic-decision.json').exists():
        raise ValueError('unexpected diagnostic decision')
    return {'status': status, 'closed': not status.startswith('awaiting_'),
            'protocol': manifest['protocol'], 'manifest_digest': digest(manifest),
            'search': manifest['screen'], 'calibration_status': manifest['calibration_status'],
            'reached': reached, 'counts': {s: len(KEYS[s]) if s in reached else 0 for s in KEYS},
            'decisions': decisions, 'descriptive_diagnostics': descriptive}


def markdown(summary):
    lines = ['# V3 bounded gain follow-up', '', f"Overall disposition: **{summary['status']}**.", '',
             f"Search disposition: **{summary['search']['status']}**. Search limits and detector findings are separate.", '',
             '## Frozen tuning choices', '',
             '| Arm | Configuration | Added step amplitude (lr × gain) | Tuning excess MSE |',
             '| --- | --- | ---: | ---: |']
    for arm, config in summary['search']['selected'].items():
        score = min(v for v in summary['search']['objectives'][arm] if v is not None)
        boost = summary['search']['added_step_amplitude'].get(arm)
        lines.append(f'| {arm} | `{json.dumps(config)}` | {boost if boost is not None else "—"} | {score:.8f} |')
    if summary['search']['reasons']:
        lines += ['', 'Search flags:', ''] + ['- ' + x for x in summary['search']['reasons']]
    lines += ['', '## Reached stages', '', '| Stage | Rows | Status |', '| --- | ---: | --- |']
    for stage, count in summary['counts'].items():
        state = 'complete' if stage in summary['reached'] else ('pending' if not summary['closed'] else 'not run: prerequisite failed')
        lines.append(f'| {stage} | {count} | {state} |')
    if 'diagnostics' in summary['decisions']:
        decision = summary['decisions']['diagnostics']
        lines += ['', '## Independent detector result', '',
                  '| Required cell | Count / total | Rate | 95% interval | Censored latency | Pass |',
                  '| --- | --- | ---: | --- | ---: | --- |']
        for name, cell in decision['cells'].items():
            lo, hi = cell['interval95']
            latency = f"{cell['latency']:.2f}" if 'latency' in cell else '—'
            lines.append(f"| {name} | {cell['count']}/{cell['total']} | {cell['rate']:.4f} | [{lo:.4f}, {hi:.4f}] | {latency} | {cell['pass']} |")
        if 'reason' in decision:
            lines += ['', decision['reason']]
        lines += ['', '## Descriptive diagnostics: every control and condition', '',
                  '| Arm/mode/fixture/coordinate | Finite seeds | Initial gate | Settled gate | Point alarm rate | Block alarm rate |',
                  '| --- | ---: | ---: | ---: | ---: | ---: |']
        for key, row in summary['descriptive_diagnostics'].items():
            if row['n'] == 0:
                lines.append(f'| {key} | 0 | unavailable | unavailable | unavailable | unavailable |')
                continue
            lines.append(f"| {key} | {row['n']} | {row['gate_initial']:.5f} | {row['gate_mean']:.5f} | "
                         f"{row['point_alarm_rate']:.5f} | {row['block_alarm_rate']:.5f} |")
        lines += ['', 'Only stationary coordinates use block alarms as false alarms. Drift and noise changes '
                  'are not successful target-switch detections. Intervals resample whole seeds, not independent events. '
                  'Finite-seed counts expose any non-finite trajectories; raw event records are retained.']
    if 'performance' in summary['decisions']:
        lines += ['', '## Independent performance contrasts', '',
                  '| Contrast | Control | Candidate | Difference | 95% interval | Pass |',
                  '| --- | ---: | ---: | ---: | --- | --- |']
        for key, cell in summary['decisions']['performance']['cells'].items():
            lo, hi = cell['interval95']
            lines.append(f"| {key} | {cell['control']:.6f} | {cell['candidate']:.6f} | {cell['delta']:.6f} | "
                         f"[{lo:.6f}, {hi:.6f}] | {cell['pass']} |")
    lines += ['', '## Limits and decision', '',
              'Five arms each receive 48 configurations × 16 tuning seeds × 6,000 four-coordinate observations: '
              '3,840 trajectories, 92,160,000 coordinate updates. Tuning scores are selected training evidence, '
              'not independent performance results. The kernel, tasks and metrics are unchanged from slice1.', '',
              'A wider-search boundary flag remains an unresolved search limit. This follow-up independently '
              'tests the detector at a specified finite configuration even with such a flag; it cannot run '
              'performance unless search adequacy AND every detector criterion pass. No existing experiment '
              'was reopened or its outcome changed. No automatic grid extension or agent integration follows.', '',
              'A detector-negative result rejects the claimed detection behavior of this specified signal/policy '
              'on these fixtures, not all v3 ideas. A positive result would justify only a separately registered '
              'agent experiment. The synthetic separable coordinates do not test representation interference. '
              'Detector rate thresholds are point screens, not population-wide guarantees.', '',
              'Reproduce with `python check_v3_gain.py --evidence results/v3-gain-followup --reproduce`; '
              'check this generated report with `python report_v3_gain.py --check`. Every reached scientific '
              'row, selection, calibrated threshold and decision is checked. Only timing and regenerated '
              'input hashes are excluded from numerical comparisons.', '']
    return '\n'.join(lines)


def publish_report(directory, check=False):
    summary = summarize(directory)
    fingerprint = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    files = {'summary.json': json.dumps(summary, indent=2, sort_keys=True) + '\n', 'report.md': markdown(summary),
             'report-source.json': json.dumps({'report_v3_gain.py': fingerprint}, indent=2) + '\n'}
    for name, content in files.items():
        path = directory/name
        if check:
            if path.read_text() != content:
                raise ValueError('stale report: ' + name)
        else:
            path.write_text(content)
    snapshot = directory/'source-snapshots'/(fingerprint + '.txt')
    if check:
        if snapshot.read_bytes() != Path(__file__).read_bytes():
            raise ValueError('report snapshot mismatch')
    else:
        snapshot.write_bytes(Path(__file__).read_bytes())
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
