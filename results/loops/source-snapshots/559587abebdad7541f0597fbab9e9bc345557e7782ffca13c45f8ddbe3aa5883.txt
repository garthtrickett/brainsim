"""Loops-probe contrasts against the frozen reference table."""
import argparse
import json
from pathlib import Path

import numpy as np

from study_loops import ARMS, DIRECTORY, LOOPTASKS, SEEDS, digest, finite, source_hashes
from study_loops import PROTOCOL


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


def band(task, frozen):
    frozen = np.asarray(frozen, dtype=float)
    if task == 'lock-10':
        return 0.10*abs(float(frozen.mean()))
    if task in ('volatile-4', 'nway-8'):
        return 0.03
    raise ValueError(f'no pre-registered band for {task}')


def summarize(directory):
    manifest = json.loads((directory/'manifest.json').read_text())
    if manifest['protocol'] != PROTOCOL or manifest['sources'] != source_hashes():
        raise ValueError('manifest differs from registration')
    result = {'status': 'awaiting_confirmation', 'closed': False,
              'protocol': manifest['protocol'], 'manifest_digest': digest(manifest),
              'cells': {}, 'counts': {'confirmation': 0}, 'absolute': {},
              'candidate': None}
    if (directory/'confirmation.json').exists():
        envelope = json.loads((directory/'confirmation.json').read_text())
        if envelope['protocol'] != PROTOCOL or envelope['sources'] != source_hashes():
            raise ValueError('changed source/protocol')
        rows = envelope['rows']
        expected = {f'{t}/{a}/{s}' for t in LOOPTASKS for a in ARMS for s in SEEDS}
        if set(rows) != expected or not finite(rows):
            raise ValueError('incomplete/non-finite confirmation')
        if any(r.get('status') != 'ok' for r in rows.values()):
            raise ValueError('unknown row status')
        for key, row in rows.items():
            if row.get('manifest_digest') != digest(manifest):
                raise ValueError('row belongs to another manifest')
        result['counts']['confirmation'] = len(rows)
        frozen_table = json.loads(Path('reference.json').read_text())['suite']
        clearers = []
        for task in LOOPTASKS:
            frozen = [float(v) for v in frozen_table[task]['brainsim']]
            for arm in ARMS:
                scores = [rows[f'{task}/{arm}/{s}']['score'] for s in SEEDS]
                contrast = paired_interval(scores, frozen)
                if task == 'nway-8':
                    limit = band(task, frozen)
                    cell = {**contrast, 'band': limit,
                            'pass': bool(abs(contrast['delta']) <= limit)}
                else:
                    cell = {**contrast, 'pass': bool(contrast['interval95'][0] > 0)}
                    if cell['pass']:
                        clearers.append((contrast['delta'], arm, task))
                result['cells'][f'{task}/{arm}'] = cell
            result['absolute'][task] = {
                arm: {'mean': float(np.mean([rows[f'{task}/{arm}/{s}']['score'] for s in SEEDS])),
                      'interval95': interval([rows[f'{task}/{arm}/{s}']['score'] for s in SEEDS])}
                for arm in ARMS}
        # Guard applies to the candidate arm: a clearer that breaks the
        # dense task vetoes itself, not the other arm.
        result['candidate'] = list(max(clearers)) if clearers else None
        guard_ok = True
        if result['candidate'] is not None:
            guard_ok = bool(result['cells'][f'nway-8/{result["candidate"][1]}']['pass'])
        if result['candidate'] is not None and guard_ok:
            result['status'] = f'adopt-loops-{result["candidate"][1]}'
        else:
            result['status'] = 'carry-global'
        result['closed'] = True
    return result


def markdown(summary):
    lines = ['# Parallel loops: per-action modulation vs the global loop', '',
             f'Disposition: **{summary["status"]}**.', '',
             '| Stage | Rows |', '| --- | ---: |']
    lines += [f'| {k} | {v} |' for k, v in summary['counts'].items()]
    for key, cell in summary['cells'].items():
        lines += ['', f'## {key}: {"pass" if cell["pass"] else "fail"}', '',
                  '| Arm mean | Frozen mean | Delta | 95% interval |',
                  '| ---: | ---: | ---: | --- |',
                  f'| {cell["treatment"]:.6f} | {cell["control"]:.6f} | {cell["delta"]:+.6f} '
                  f'| [{cell["interval95"][0]:+.6f}, {cell["interval95"][1]:+.6f}] |']
    if summary['absolute']:
        lines += ['', '## Absolute scores by arm', '',
                  '| Task / arm | Mean | 95% interval |', '| --- | ---: | --- |']
        for task, arms in summary['absolute'].items():
            for arm, row in arms.items():
                lines.append(f'| {task}/{arm} | {row["mean"]:.6f} | [{row["interval95"][0]:.6f}, {row["interval95"][1]:.6f}] |')
    if summary['candidate']:
        lines += ['', f'Candidate (highest paired delta among clearers): '
                     f'**{summary["candidate"][1]} on {summary["candidate"][2]}**.', '']
    lines += ['', '## Scope and reproduction', '',
              'Same-seed paired design against the frozen reference instrument; '
              'the shipped global arm is the frozen column itself '
              '(check_reference.py green is the proof), not a re-measurement. '
              'Lock-10 total reward is high-variance, reported whole. Eight '
              'seeds cannot establish population guarantees.', '',
              '`python check_loops.py --evidence results/loops --reproduce` '
              'regenerates every row at rtol1e-11/atol1e-13. '
              '`python report_loops.py --check` verifies both generated reports.', '']
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
