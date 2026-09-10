"""V6 paired contrasts with headroom checks."""
import argparse
import json
from pathlib import Path

import numpy as np

from study_v6 import (AGENT_SEEDS, ARMS, DIRECTORY, ENDO, PROTOCOL,
                      source_hashes)
from v3_slice1_decisions import digest, finite


def interval(values):
    values = np.asarray(values, dtype=float)
    if values.ndim != 1 or not len(values) or not np.isfinite(values).all():
        raise ValueError('finite seed values required')
    indices = np.random.default_rng(215000).integers(0, len(values), (10000, len(values)))
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
            'delta': float(delta.mean()), 'interval95': bounds, 'pass': bool(bounds[0] > 0)}


def summarize(directory):
    manifest = json.loads((directory/'manifest.json').read_text())
    if manifest['protocol'] != PROTOCOL or manifest['sources'] != source_hashes():
        raise ValueError('manifest differs from registration')
    result = {'status': manifest.get('status', 'eligible'), 'closed': False,
              'protocol': manifest['protocol'], 'manifest_digest': digest(manifest),
              'usable': manifest.get('usable', []), 'contrasts': {},
              'counts': {'confirmation': 0}, 'positions': manifest.get('positions', {})}
    if (directory/'confirmation.json').exists():
        envelope = json.loads((directory/'confirmation.json').read_text())
        if envelope['protocol'] != PROTOCOL or envelope['sources'] != source_hashes():
            raise ValueError('changed source/protocol')
        rows = envelope['rows']
        expected = {f'{t}/{a}/{s}' for t in result['usable'] for a in ARMS for s in AGENT_SEEDS}
        if set(rows) != expected or not finite(rows):
            raise ValueError('incomplete/non-finite confirmation')
        if any(r.get('status') != 'ok' for r in rows.values()):
            raise ValueError('unknown row status')
        for key, row in rows.items():
            if row.get('manifest_digest') != digest(manifest):
                raise ValueError('row belongs to another manifest')
        result['counts']['confirmation'] = len(rows)
        verdicts = []
        result['positions'] = {}
        for task in result['usable']:
            tails = {a: [rows[f'{task}/{a}/{s}']['score'] for s in AGENT_SEEDS] for a in ARMS}
            floor, ceiling = manifest['frozen_bounds'][task]
            position = (float(sum(tails['baseline'])/len(tails['baseline']))-floor)/(ceiling-floor)
            result['positions'][task] = position
            if not .1 <= position <= .9:
                result['contrasts'][task] = {'status': 'no_verdict', 'contrasts': {}}
                continue
            level = {'contrasts': {}}
            for endo, oracle in ENDO.items():
                gain = paired_interval(tails[endo], tails['baseline'])
                headroom = paired_interval(tails[oracle], tails[endo])
                level['contrasts'][endo] = {'gain': gain, 'headroom': headroom,
                                            'pass': bool(gain['pass'] and headroom['pass'])}
            level['status'] = 'learning_positive' if any(
                v['pass'] for v in level['contrasts'].values()) else 'learning_negative'
            verdicts.append(level['status'] == 'learning_positive')
            result['contrasts'][task] = level
        result['status'] = 'learning_positive' if any(verdicts) else 'learning_negative'
        result['closed'] = True
    return result


def number(value):
    return '—' if value is None else f'{value:.6f}'


def markdown(summary):
    lines = ['# V6 margin-directed exploration', '', f'Disposition: **{summary["status"]}**.', '',
             '| Task | Usable | Confirmation rows |', '| --- | --- | ---: |']
    for task in ('volatile', 'noisy', 'lock'):
        usable = task in summary['usable']
        lines.append(f'| {task} | {usable} | {summary["counts"]["confirmation"] if usable else 0} |')
    if summary.get('positions'):
        manifest_bounds = {'volatile': (0.251, 1.0), 'noisy': (0.2495, 1.0), 'lock': (12.5, 1333.0)}
        lines += ['', '## Task usability (remeasured baseline vs frozen bounds)', '',
                  '| Task | Floor | Ceiling | Baseline | Position | Verdict |',
                  '| --- | ---: | ---: | ---: | ---: | ---: |']
        for task, position in summary['positions'].items():
            floor, ceiling = manifest_bounds[task]
            verdict = summary['contrasts'][task]['status']
            lines.append(f'| {task} | {floor} | {ceiling} | {number(position*(ceiling-floor)+floor)} | {position:.2f} | {verdict} |')
    for task, level in summary['contrasts'].items():
        if level['status'] == 'no_verdict':
            lines += ['', f'## Task {task}: no verdict (baseline outside 10–90% band)', '']
            continue
        lines += ['', f'## Task {task}: {level["status"]}', '',
                  'Gain = explorer minus baseline (paired); headroom = oracle minus explorer (paired). '
                  'A pass needs both intervals strictly above zero.', '',
                  '| Explorer | Gain Δ | 95% interval | Headroom Δ | 95% interval | Pass |',
                  '| --- | ---: | --- | ---: | --- | --- |']
        for endo, cell in level['contrasts'].items():
            gain, headroom = cell['gain'], cell['headroom']
            lines.append(f'| {endo} | {gain["delta"]:.4f} | [{gain["interval95"][0]:.4f}, {gain["interval95"][1]:.4f}] | '
                         f'{headroom["delta"]:.4f} | [{headroom["interval95"][0]:.4f}, {headroom["interval95"][1]:.4f}] | {cell["pass"]} |')
    lines += ['', '## Scope and reproduction', '',
              'Paired seed design; intervals resample whole seeds10000 times with seed215000. '
              'Eight seeds and three tasks cannot establish population guarantees, exploration '
              'in general, or superiority over deep learning. The oracle is a privileged bound, '
              'never a deployable arm. Every reached row and source is archived; prior studies '
              'remain intact.', '',
              '`python check_v6.py --evidence results/v6 --reproduce` regenerates every '
              'reached row and scientific manifest/summary at rtol1e-11/atol1e-13. '
              '`python report_v6.py --check` verifies both generated reports.', '']
    return '\n'.join(lines)


def publish_report(directory, check=False):
    summary = summarize(directory)
    for name, content in {'summary.json': json.dumps(summary, indent=2, sort_keys=True)+'\n', 'report.md': markdown(summary)}.items():
        if check:
            if (directory/name).read_text() != content: raise ValueError('stale report '+name)
        else: (directory/name).write_text(content)
    print('RESULT', summary['status'], summary.get('usable'), flush=True)
    return summary


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--directory', type=Path, default=DIRECTORY)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    publish_report(args.directory, args.check)
