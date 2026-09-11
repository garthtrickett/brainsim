"""Q2 screen contrasts, champion selection, and guard verdicts."""
import argparse
import json
from pathlib import Path

import numpy as np

from study_q2 import (CONTROL, DIRECTORY, GUARD_TASKS, SEEDS, SCREEN_TASK,
    TASKS, digest, finite, source_hashes)
from study_q2 import PROTOCOL
from q2_rule import RULES, TAUS


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


def decide(screen_cells):
    """Pre-registered decision procedure over {(rule, tau): cell}."""
    champions = {}
    for rule in RULES:
        taus = sorted(TAUS)
        best = max(taus, key=lambda t: screen_cells[f'{rule}/{t}']['treatment'])
        champions[rule] = best
    clearers = [(screen_cells[f'{r}/{t}']['delta'], r, t) for r, t in champions.items()
                if (r, t) != CONTROL and screen_cells[f'{r}/{t}']['interval95'][0] > 0]
    if not clearers:
        return None
    return max(clearers)[1:]


def summarize(directory):
    manifest = json.loads((directory/'manifest.json').read_text())
    if manifest['protocol'] != PROTOCOL or manifest['sources'] != source_hashes():
        raise ValueError('manifest differs from registration')
    result = {'status': 'awaiting_screen', 'closed': False,
              'protocol': manifest['protocol'], 'manifest_digest': digest(manifest),
              'screen': {}, 'counts': {'screen': 0, 'guard': 0},
              'candidate': None, 'guard': {}}
    if (directory/'screen.json').exists():
        envelope = json.loads((directory/'screen.json').read_text())
        if envelope['protocol'] != PROTOCOL or envelope['sources'] != source_hashes():
            raise ValueError('changed source/protocol')
        rows = envelope['rows']
        check_rows(rows, {f'{SCREEN_TASK}/{r}/{t}/{s}' for r in RULES
                          for t in sorted(TAUS) for s in SEEDS}, digest(manifest))
        result['counts']['screen'] = len(rows)
        control = [rows[f'{SCREEN_TASK}/{CONTROL[0]}/{CONTROL[1]}/{s}']['score'] for s in SEEDS]
        cells = {}
        for rule in RULES:
            for tau in sorted(TAUS):
                scores = [rows[f'{SCREEN_TASK}/{rule}/{tau}/{s}']['score'] for s in SEEDS]
                cells[f'{rule}/{tau}'] = paired_interval(scores, control)
        result['screen'] = cells
        result['absolute'] = {}
        for rule in RULES:
            for tau in sorted(TAUS):
                vals = [rows[f'{SCREEN_TASK}/{rule}/{tau}/{s}']['score'] for s in SEEDS]
                result['absolute'][f'{rule}/{tau}'] = {'mean': float(np.mean(vals)),
                                                       'interval95': interval(vals)}
        cand = decide(cells)
        result['candidate'] = list(cand) if cand else None
        if cand is None:
            result['status'] = 'carry-full-200'
            result['closed'] = True
        elif (directory/'guard.json').exists():
            envelope = json.loads((directory/'guard.json').read_text())
            if envelope['protocol'] != PROTOCOL or envelope['sources'] != source_hashes():
                raise ValueError('changed source/protocol')
            grows = envelope['rows']
            rule, tau = cand
            check_rows(grows, {f'{t}/{rule}/{tau}/{s}' for t in GUARD_TASKS for s in SEEDS},
                       digest(manifest))
            result['counts']['guard'] = len(grows)
            frozen_table = json.loads(Path('reference.json').read_text())['suite']
            vetoes = []
            for task in GUARD_TASKS:
                frozen = [float(v) for v in frozen_table[task]['brainsim']]
                scores = [grows[f'{task}/{rule}/{tau}/{s}']['score'] for s in SEEDS]
                contrast = paired_interval(scores, frozen)
                cell = {**contrast, 'band': 0.03,
                        'pass': bool(abs(contrast['delta']) <= 0.03)}
                vetoes.append(cell['pass'])
                result['guard'][task] = cell
            if all(vetoes):
                result['status'] = f'adopt-{rule}-{tau}'
            else:
                result['status'] = f'vetoed-{rule}-{tau}'
            result['closed'] = True
        else:
            result['status'] = 'awaiting_guard'
    return result


def markdown(summary):
    lines = ['# Q2 consumption × tau: screen, selection, guard', '',
             f'Disposition: **{summary["status"]}**.', '',
             '| Stage | Rows |', '| --- | ---: |']
    lines += [f'| {k} | {v} |' for k, v in summary['counts'].items()]
    if summary.get('absolute'):
        lines += ['', '## Screen (lock-10 total reward)', '',
                  '| Rule / tau | Mean | 95% interval | Paired delta vs full@200 | 95% interval |',
                  '| --- | ---: | --- | ---: | --- |']
        for key, row in summary['absolute'].items():
            cell = summary['screen'][key]
            lines.append(f'| {key} | {row["mean"]:.2f} | [{row["interval95"][0]:.2f}, {row["interval95"][1]:.2f}] '
                         f'| {cell["delta"]:+.2f} | [{cell["interval95"][0]:+.2f}, {cell["interval95"][1]:+.2f}] |')
    if summary['candidate']:
        lines.append('')
        lines.append(f'Candidate: **{summary["candidate"][0]}@{summary["candidate"][1]}**.')
    if summary['guard']:
        lines += ['', '## Dense guard (candidate vs frozen, band ±0.03)', '',
                  '| Task | Delta | 95% interval | Pass |', '| --- | ---: | --- | --- |']
        for task, cell in summary['guard'].items():
            lines.append(f'| {task} | {cell["delta"]:+.6f} | [{cell["interval95"][0]:+.6f}, {cell["interval95"][1]:+.6f}] | {cell["pass"]} |')
    lines += ['', '## Scope and reproduction', '',
              'Same-seed (0–7) paired design on the reference instrument; lock-10 '
              'is total reward (high variance, reported whole). Three champion '
              'comparisons share one control — multiplicity disclosed, adoption '
              'bar is paired lower > 0 outright. Eight seeds cannot establish '
              'population guarantees.', '',
              '`python check_q2.py --evidence results/q2 --reproduce` regenerates '
              'every row at rtol1e-11/atol1e-13. '
              '`python report_q2.py --check` verifies both generated reports.', '']
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
