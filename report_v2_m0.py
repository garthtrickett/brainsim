"""M0-motor paired contrasts with headroom checks."""
import argparse
import json
from pathlib import Path

import numpy as np

from study_v2_m0 import CLASSES, DIRECTORY, SEEDS, digest, finite, source_hashes
from study_v2_m0 import PROTOCOL


def interval(values):
    values = np.asarray(values, dtype=float)
    if values.ndim != 1 or not len(values) or not np.isfinite(values).all():
        raise ValueError('finite seed values required')
    indices = np.random.default_rng(225000).integers(0, len(values), (10000, len(values)))
    return np.quantile(values[indices].mean(axis=1), [.025, .975]).tolist()


def paired_interval(treatment, control):
    treatment, control = np.asarray(treatment), np.asarray(control)
    if treatment.shape != control.shape or treatment.ndim != 1 or not len(control):
        raise ValueError('paired samples required')
    if not np.isfinite(treatment).all() or not np.isfinite(control).all():
        raise ValueError('finite paired samples required')
    delta = treatment-control
    bounds = interval(delta)
    return {'control': float(control.mean()), 'treatment': float(treatment.mean()),
            'delta': float(delta.mean()), 'interval95': bounds}


def summarize(directory):
    manifest = json.loads((directory/'manifest.json').read_text())
    if manifest['protocol'] != PROTOCOL or manifest['sources'] != source_hashes():
        raise ValueError('manifest differs from registration')
    result = {'status': 'awaiting_confirmation', 'closed': False,
              'protocol': manifest['protocol'], 'manifest_digest': digest(manifest),
              'cells': {}, 'counts': {'confirmation': 0}, 'absolute': {}}
    if (directory/'confirmation.json').exists():
        envelope = json.loads((directory/'confirmation.json').read_text())
        if envelope['protocol'] != PROTOCOL or envelope['sources'] != source_hashes():
            raise ValueError('changed source/protocol')
        rows = envelope['rows']
        expected = {f'{c}/{a}/{s}' for c in CLASSES for a in ('pertick', 'aggregate', 'shipped') for s in SEEDS}
        if set(rows) != expected or not finite(rows):
            raise ValueError('incomplete/non-finite confirmation')
        if any(r.get('status') != 'ok' for r in rows.values()):
            raise ValueError('unknown row status')
        for key, row in rows.items():
            if row.get('manifest_digest') != digest(manifest):
                raise ValueError('row belongs to another manifest')
        result['counts']['confirmation'] = len(rows)
        verdicts = []
        for ncls in CLASSES:
            acc = {a: [rows[f'{ncls}/{a}/{s}']['accuracy'] for s in SEEDS] for a in ('pertick', 'aggregate', 'shipped')}
            beats = paired_interval(acc['pertick'], acc['aggregate'])
            matches = paired_interval(acc['pertick'], acc['shipped'])
            cell = {'beats_aggregate': {**beats, 'pass': bool(beats['interval95'][0] > 0)},
                    'matches_shipped': {**matches, 'pass': bool(matches['interval95'][0] <= 0 <= matches['interval95'][1])}}
            cell['pass'] = bool(cell['beats_aggregate']['pass'] and cell['matches_shipped']['pass'])
            verdicts.append(cell['pass'])
            result['cells'][str(ncls)] = cell
            result['absolute'][str(ncls)] = {
                arm: {'mean': float(np.mean(acc[arm])),
                      'interval95': interval(acc[arm]),
                      'winner_rate': float(np.mean([rows[f'{ncls}/{arm}/{s}'].get('winner_rate', 1.0) for s in SEEDS]))}
                for arm in ('pertick', 'aggregate', 'shipped')}
        result['status'] = 'learning_positive' if all(verdicts) else 'learning_negative'
        result['closed'] = True
    return result


def number(value):
    return '—' if value is None else f'{value:.6f}'


def markdown(summary):
    lines = ['# V2 M0-motor: 1-of-N without aggregates', '', f'Disposition: **{summary["status"]}**.', '',
             '| Stage | Rows |', '| --- | ---: |']
    lines += [f'| {k} | {v} |' for k, v in summary['counts'].items()]
    for ncls, cell in summary['cells'].items():
        lines += ['', f'## nway-{ncls}: {"pass" if cell["pass"] else "fail"}', '',
                  '| Contrast | Treatment | Control | Delta | 95% interval | Pass |',
                  '| --- | ---: | ---: | ---: | --- | --- |']
        for key in ('beats_aggregate', 'matches_shipped'):
            c = cell[key]
            lines.append(f'| {key} | {c["treatment"]:.6f} | {c["control"]:.6f} | {c["delta"]:.6f} | [{c["interval95"][0]:.6f}, {c["interval95"][1]:.6f}] | {c["pass"]} |')
    if summary['absolute']:
        lines += ['', '## Absolute per-tick accuracy and winner rates', '',
                  '| Class count / arm | Accuracy | 95% interval | Winner rate |',
                  '| --- | ---: | --- | ---: |']
        for ncls, arms in summary['absolute'].items():
            for arm, row in arms.items():
                lines.append(f'| {ncls}/{arm} | {row["mean"]:.6f} | [{row["interval95"][0]:.6f}, {row["interval95"][1]:.6f}] | {row["winner_rate"]:.4f} |')
    lines += ['', '## Scope and reproduction', '',
              'Per-tick units throughout; silence scores 0. Cross-study comparison with v1 tail '
              'accuracies is forbidden. Six seeds cannot establish population guarantees. '
              'Every reached row and source is archived; prior studies remain intact.', '',
              '`python check_v2_m0.py --evidence results/v2-m0 --reproduce` regenerates every '
              'reached row at rtol1e-11/atol1e-13. '
              '`python report_v2_m0.py --check` verifies both generated reports.', '']
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
