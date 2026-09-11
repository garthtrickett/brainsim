"""L-sweep screen contrasts and collateral verdicts."""
import argparse
import json
from pathlib import Path

import numpy as np

from study_Lsweep import (COLLATERAL_TASKS, CONTROL, DIRECTORY, SCREEN_TASK,
    SEEDS, TASKS, WINDOWS, digest, finite, source_hashes)
from study_Lsweep import PROTOCOL


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


def check_rows(rows, expected, manifest_digest):
    if set(rows) != expected or not finite(rows):
        raise ValueError('incomplete/non-finite evidence')
    if any(r.get('status') != 'ok' for r in rows.values()):
        raise ValueError('unknown row status')
    for key, row in rows.items():
        if row.get('manifest_digest') != manifest_digest:
            raise ValueError('row belongs to another manifest')


def summarize(directory):
    manifest = json.loads((directory/'manifest.json').read_text())
    if manifest['protocol'] != PROTOCOL or manifest['sources'] != source_hashes():
        raise ValueError('manifest differs from registration')
    result = {'status': 'awaiting_screen', 'closed': False,
              'protocol': manifest['protocol'], 'manifest_digest': digest(manifest),
              'screen': {}, 'counts': {'screen': 0, 'collateral': 0},
              'candidate': None, 'collateral': {}}
    if (directory/'screen.json').exists():
        envelope = json.loads((directory/'screen.json').read_text())
        if envelope['protocol'] != PROTOCOL or envelope['sources'] != source_hashes():
            raise ValueError('changed source/protocol')
        rows = envelope['rows']
        check_rows(rows, {f'{SCREEN_TASK}/{w}/{s}' for w in WINDOWS for s in SEEDS},
                   digest(manifest))
        result['counts']['screen'] = len(rows)
        control = [rows[f'{SCREEN_TASK}/{CONTROL}/{s}']['score'] for s in SEEDS]
        cands = []
        for window in WINDOWS:
            if window == CONTROL: continue
            scores = [rows[f'{SCREEN_TASK}/{window}/{s}']['score'] for s in SEEDS]
            contrast = paired_interval(scores, control)
            cell = {**contrast, 'pass': bool(contrast['interval95'][0] > 0)}
            result['screen'][str(window)] = cell
            if cell['pass']: cands.append((contrast['delta'], window))
        result['candidate'] = max(cands)[1] if cands else None
        result['absolute'] = {str(w): {
            'mean': float(np.mean([rows[f'{SCREEN_TASK}/{w}/{s}']['score'] for s in SEEDS])),
            'interval95': interval([rows[f'{SCREEN_TASK}/{w}/{s}']['score'] for s in SEEDS])}
            for w in WINDOWS}
        if result['candidate'] is None:
            result['status'] = 'confirmed-20'
            result['closed'] = True
        elif (directory/'collateral.json').exists():
            envelope = json.loads((directory/'collateral.json').read_text())
            if envelope['protocol'] != PROTOCOL or envelope['sources'] != source_hashes():
                raise ValueError('changed source/protocol')
            crows = envelope['rows']
            winner = result['candidate']
            check_rows(crows, {f'{t}/{winner}/{s}' for t in COLLATERAL_TASKS for s in SEEDS},
                       digest(manifest))
            result['counts']['collateral'] = len(crows)
            frozen_table = json.loads(Path('reference.json').read_text())['suite']
            vetoes = []
            for task in COLLATERAL_TASKS:
                frozen = [float(v) for v in frozen_table[task]['brainsim']]
                scores = [crows[f'{task}/{winner}/{s}']['score'] for s in SEEDS]
                contrast = paired_interval(scores, frozen)
                cell = {**contrast, 'band': 0.03,
                        'pass': bool(abs(contrast['delta']) <= 0.03)}
                vetoes.append(cell['pass'])
                result['collateral'][task] = cell
            if all(vetoes):
                result['status'] = f'adopt-{winner}'
            else:
                result['status'] = f'vetoed-{winner}'
            result['closed'] = True
        else:
            result['status'] = 'awaiting_collateral'
    return result


def markdown(summary):
    lines = ['# Replay window sweep: lock-10 screen and collateral check', '',
             f'Disposition: **{summary["status"]}**.', '',
             '| Stage | Rows |', '| --- | ---: |']
    lines += [f'| {k} | {v} |' for k, v in summary['counts'].items()]
    if summary.get('absolute'):
        lines += ['', '## Screen (lock-10 total reward by window)', '',
                  '| Window | Mean | 95% interval |', '| ---: | ---: | --- |']
        for window, row in summary['absolute'].items():
            lines.append(f'| {window} | {row["mean"]:.4f} | [{row["interval95"][0]:.4f}, {row["interval95"][1]:.4f}] |')
    if summary['screen']:
        lines += ['', '## Screen contrasts vs L=20 (paired, adopt needs lower > 0)', '',
                  '| Window | Treatment | Control | Delta | 95% interval | Pass |',
                  '| ---: | ---: | ---: | ---: | --- | --- |']
        for window, cell in summary['screen'].items():
            lines.append(f'| {window} | {cell["treatment"]:.4f} | {cell["control"]:.4f} | {cell["delta"]:+.4f} '
                         f'| [{cell["interval95"][0]:+.4f}, {cell["interval95"][1]:+.4f}] | {cell["pass"]} |')
    if summary['collateral']:
        lines += ['', '## Collateral check (winner vs frozen, band ±0.03)', '',
                  '| Task | Delta | 95% interval | Pass |', '| --- | ---: | --- | --- |']
        for task, cell in summary['collateral'].items():
            lines.append(f'| {task} | {cell["delta"]:+.6f} | [{cell["interval95"][0]:+.6f}, {cell["interval95"][1]:+.6f}] | {cell["pass"]} |')
    lines += ['', '## Scope and reproduction', '',
              'Same-seed (0–7) paired design on the reference instrument; lock-10 '
              'is total reward (high variance, reported whole). Re-running a '
              'screened window on the same seeds is bit-identical, hence lock is '
              'excluded from stage 2 by design. Eight seeds cannot establish '
              'population guarantees.', '',
              '`python check_Lsweep.py --evidence results/L-sweep --reproduce` '
              'regenerates every row at rtol1e-11/atol1e-13. '
              '`python report_Lsweep.py --check` verifies both generated reports.', '']
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
