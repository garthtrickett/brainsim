"""Recompute the reached-stage decision; incomplete evidence never becomes closure."""
import argparse
import hashlib
import json
from pathlib import Path

from study_v3_slice1 import DIRECTORY, load, make_manifest, write
from v3_slice1_decisions import KEYS, detector_decision, digest, performance_decision


def summarize(directory):
    tuning = load(directory, 'tuning')
    manifest = json.loads((directory/'manifest.json').read_text())
    calibration = load(directory, 'calibration') if manifest['screen']['status'] == 'eligible' else None
    if manifest != make_manifest(tuning, calibration):
        raise ValueError('manifest does not match evidence')
    reached = ['tuning']
    status = manifest['screen']['status']
    decisions = {}
    if status == 'eligible':
        reached.append('calibration')
        status = 'awaiting_diagnostics'
        if (directory/'diagnostics.json').exists():
            diagnostic = load(directory, 'diagnostics')
            reached.append('diagnostics')
            expected = {'manifest_digest': digest(manifest), 'evidence_digest': digest(diagnostic),
                        **detector_decision(diagnostic)}
            if json.loads((directory/'diagnostic-decision.json').read_text()) != expected:
                raise ValueError('diagnostic decision mismatch')
            decisions['diagnostics'] = expected
            status = expected['status']
            if status == 'detector_pass':
                status = 'awaiting_performance'
                if (directory/'performance.json').exists():
                    performance = load(directory, 'performance')
                    reached.append('performance')
                    decisions['performance'] = performance_decision(performance)
                    status = decisions['performance']['status']
    for stage in KEYS:
        if (directory/(stage + '.json')).exists() != (stage in reached):
            raise ValueError('forbidden/missing stage: ' + stage)
    if 'diagnostics' not in reached and (directory/'diagnostic-decision.json').exists():
        raise ValueError('unexpected diagnostic decision')
    return {'status': status, 'closed_scientifically': not status.startswith('awaiting_'),
            'protocol': manifest['protocol'], 'manifest_digest': digest(manifest),
            'screen': manifest['screen'], 'decisions': decisions,
            'counts': {s: len(KEYS[s]) if s in reached else 0 for s in KEYS},
            'reached': reached, 'not_run': {s: 'pending prerequisite' if status.startswith('awaiting_')
                                          else 'prerequisite failed' for s in KEYS if s not in reached}}


def markdown(summary):
    screen = summary['screen']
    lines = ['# Slice1 registered result', '', f"Status: **{summary['status']}**.", '',
             'This is the mean-disagreement successor, not a revision of the original '
             'centered-variance result. The registered scientific gates determine the disposition.', '',
             '## Tuning choices', '', '| Arm | Configuration | Tuning excess MSE |',
             '| --- | --- | ---: |']
    for arm, config in screen['selected'].items():
        score = min(v for v in screen['objectives'][arm] if v is not None)
        lines.append(f'| {arm} | `{json.dumps(config)}` | {score:.8f} |')
    if screen['reasons']:
        lines += ['', '## Screening reasons', ''] + ['- ' + r for r in screen['reasons']]
    lines += ['', '## Reached evidence', '', '| Stage | Rows | Disposition |', '| --- | ---: | --- |']
    for stage, count in summary['counts'].items():
        state = 'complete' if stage in summary['reached'] else 'not run: ' + summary['not_run'][stage]
        lines.append(f'| {stage} | {count} | {state} |')
    for stage, decision in summary['decisions'].items():
        lines += ['', f'## {stage} decision', '', f"**{decision['status']}**", '']
        if 'reason' in decision:
            lines.append(decision['reason'])
        if stage == 'diagnostics':
            lines += ['| Cell | Count / total | Rate | 95% interval | Pass |',
                      '| --- | --- | ---: | --- | --- |']
            for key, cell in decision['cells'].items():
                lo, hi = cell['interval95']
                lines.append(f"| {key} | {cell['count']}/{cell['total']} | {cell['rate']:.5f} | "
                             f"[{lo:.5f}, {hi:.5f}] | {cell['pass']} |")
        else:
            lines += ['| Comparison | Control | Candidate | Difference | 95% interval | Pass |',
                      '| --- | ---: | ---: | ---: | --- | --- |']
            for key, cell in decision['cells'].items():
                lo, hi = cell['interval95']
                lines.append(f"| {key} | {cell['control']:.6f} | {cell['candidate']:.6f} | "
                             f"{cell['delta']:.6f} | [{lo:.6f}, {hi:.6f}] | {cell['pass']} |")
    lines += ['', '## Interpretation', '']
    if summary['status'] == 'tuning_inconclusive':
        lines.append('The bounded search did not establish adequate tuning. No independent '
                     'detector or performance confirmation was run. These selected tuning scores '
                     'are not held-out evidence of superiority or a refutation of the candidate. '
                     'The registered rule requires closure without grid extension or integration.')
    elif summary['status'] == 'tuning_negative':
        lines.append('The selected candidate has zero modulation gain. This is a tuning-only '
                     'rejection, not an independently confirmed null. Stop before integration.')
    elif summary['status'] == 'detector_negative':
        lines.append('The candidate failed the registered detector screen. Performance confirmation '
                     'was not opened; do not claim a tested learning advantage or integrate the gate.')
    elif summary['status'] == 'learning_negative':
        lines.append('The detector prerequisite passed, but registered learning/retention comparisons '
                     'failed. Do not integrate the gate.')
    elif summary['status'] == 'positive':
        lines.append('All gates passed on these synthetic fixtures. This only licenses a separately '
                     'registered noisy-volatile agent study; it does not enable a brainsim default.')
    else:
        lines.append('This is an interim checkpoint. Required confirmation remains; the slice is not closed.')
    lines += ['', '## Limits and reproducibility', '',
              'Five tuned arms receive 24 configurations × 16 seeds × 6,000 four-coordinate '
              'observations: 1,920 trajectories and 46,080,000 coordinate updates. The constant '
              'ablation, if reached, is derived from calibration without an extra tuning search. '
              'Gate timescales are fixed. Point detector screens and percentile intervals do not '
              'establish universal guarantees. These are separable quadratics, not agent tasks.', '',
              'State used by the mathematical updates differs across arms, but the simple reference '
              'kernel allocates seven width-sized state arrays for every arm plus recorded output '
              'arrays. No optimized memory-cost advantage is claimed. High-resolution elapsed '
              'seconds are archived for learning runs and excluded from scientific reproduction.', '',
              'Run `python check_v3_slice1.py --evidence results/v3-slice1 --reproduce` and '
              '`python report_v3_slice1.py --check`. Validation requires every reached scientific '
              'row, recomputed selections/decisions, unchanged source hashes, and absence of '
              'forbidden later-stage evidence. The older V1/V3 gates remain independent.', '']
    return '\n'.join(lines)


def publish_report(directory, check=False):
    summary = summarize(directory)
    source = Path(__file__).read_bytes()
    fingerprint = hashlib.sha256(source).hexdigest()
    files = {'summary.json': json.dumps(summary, indent=2, sort_keys=True) + '\n',
             'report.md': markdown(summary),
             'report-source.json': json.dumps({'report_v3_slice1.py': fingerprint}, indent=2) + '\n'}
    snapshot = directory/'source-snapshots'/(fingerprint + '.txt')
    for name, content in files.items():
        path = directory/name
        if check:
            if path.read_text() != content:
                raise ValueError('stale report: ' + name)
        else:
            path.write_text(content)
    if check:
        if snapshot.read_bytes() != source:
            raise ValueError('report source snapshot mismatch')
    else:
        snapshot.write_bytes(source)
    print('RESULT', summary['status'], json.dumps(summary['counts']), flush=True)
    return summary


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--directory', type=Path, default=DIRECTORY)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    publish_report(args.directory, args.check)


if __name__ == '__main__':
    main()
