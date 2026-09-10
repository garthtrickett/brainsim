"""V5 calibration and paired-contrast results."""
import argparse
import json
from pathlib import Path

import numpy as np

from study_v5 import (ARMS, CONFIRMATION_SEEDS, DIRECTORY, ENDO, LEVELS, PROTOCOL,
                      source_hashes)
from v3_slice1_decisions import digest, finite


def interval(values):
    values = np.asarray(values, dtype=float)
    if values.ndim != 1 or not len(values) or not np.isfinite(values).all():
        raise ValueError('finite seed values required')
    indices = np.random.default_rng(205000).integers(0, len(values), (10000, len(values)))
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
    calibration = json.loads((directory/'calibration.json').read_text())
    manifest = json.loads((directory/'manifest.json').read_text())
    if calibration['manifest'] != manifest or manifest['protocol'] != PROTOCOL:
        raise ValueError('manifest differs from calibration')
    if manifest['sources'] != source_hashes():
        raise ValueError('changed source/protocol')
    result = {'status': manifest['status'], 'closed': manifest['status'] != 'eligible',
              'protocol': manifest['protocol'], 'manifest_digest': digest(manifest),
              'calibration': calibration['rows'], 'usable': manifest['usable'],
              'contrasts': {}, 'counts': {'confirmation': 0}}
    if (directory/'confirmation.json').exists():
        if manifest['status'] != 'eligible':
            raise ValueError('forbidden confirmation stage')
        envelope = json.loads((directory/'confirmation.json').read_text())
        if envelope['protocol'] != PROTOCOL or envelope['sources'] != source_hashes():
            raise ValueError('changed source/protocol')
        rows = envelope['rows']
        expected = {f'{s}/{a}/{seed}' for s in manifest['usable'] for a in ARMS for seed in CONFIRMATION_SEEDS}
        if set(rows) != expected or not finite(rows):
            raise ValueError('incomplete/non-finite confirmation')
        if any(r.get('status') != 'ok' for r in rows.values()):
            raise ValueError('unknown row status')
        for key, row in rows.items():
            if row.get('manifest_digest') != digest(manifest):
                raise ValueError('row belongs to another manifest')
        result['counts']['confirmation'] = len(rows)
        verdicts = []
        for sigma in manifest['usable']:
            tails = {a: [rows[f'{sigma}/{a}/{s}']['tail'] for s in CONFIRMATION_SEEDS] for a in ARMS}
            level = {'contrasts': {}}
            for endo, oracle in ENDO.items():
                gain = paired_interval(tails[endo], tails['baseline'])
                headroom = paired_interval(tails[oracle], tails[endo])
                level['contrasts'][endo] = {'gain': gain, 'headroom': headroom,
                                            'pass': bool(gain['pass'] and headroom['pass'])}
            level['status'] = 'learning_positive' if any(
                v['pass'] for v in level['contrasts'].values()) else 'learning_negative'
            verdicts.append(level['status'] == 'learning_positive')
            result['contrasts'][str(sigma)] = level
        result['status'] = 'learning_positive' if any(verdicts) else 'learning_negative'
        result['closed'] = True
    return result


def number(value):
    return '—' if value is None else f'{value:.6f}'


def markdown(summary):
    lines = ['# V5 embodied volatility', '', f'Disposition: **{summary["status"]}**.', '',
             '| Stage | Rows |', '| --- | ---: |']
    lines += [f'| calibration | {len(summary["calibration"])} levels |',
              f'| usable | {summary["usable"]} |',
              f'| confirmation | {summary["counts"]["confirmation"]} |']
    lines += ['', '## Calibration (floor / ceiling / baseline, tail reward rate)', '',
              '| Noise σ | Floor | Ceiling | Baseline | Position | Usable |',
              '| --- | ---: | ---: | ---: | ---: | ---: |']
    for sigma, row in summary['calibration'].items():
        lines.append(f'| {sigma} | {number(float(sum(row["floor"])/len(row["floor"])))} | '
                     f'{number(float(sum(row["ceiling"])/len(row["ceiling"])))} | '
                     f'{number(float(sum(row["baseline"])/len(row["baseline"])))} | '
                     f'{row["position"]:.2f} | {row["usable"]} |')
    for sigma, level in summary['contrasts'].items():
        lines += ['', f'## Noise σ={sigma}: {level["status"]}', '',
                  'Gain = endo minus baseline (paired); headroom = oracle minus endo (paired). '
                  'A pass needs both intervals strictly above zero.', '',
                  '| Endo arm | Gain Δ | 95% interval | Headroom Δ | 95% interval | Pass |',
                  '| --- | ---: | --- | ---: | --- | --- |']
        for endo, cell in level['contrasts'].items():
            gain, headroom = cell['gain'], cell['headroom']
            lines.append(f'| {endo} | {gain["delta"]:.4f} | [{gain["interval95"][0]:.4f}, {gain["interval95"][1]:.4f}] | '
                         f'{headroom["delta"]:.4f} | [{headroom["interval95"][0]:.4f}, {headroom["interval95"][1]:.4f}] | {cell["pass"]} |')
    lines += ['', '## Scope and reproduction', '',
              'Paired seed design; intervals resample whole seeds10000 times with seed205000. '
              'Eight seeds cannot establish population guarantees or embodiment in general. '
              'Oracle twins are privileged bounds, never deployable arms. '
              'Every reached row and source is archived; prior studies remain intact.', '',
              '`python check_v5.py --evidence results/v5 --reproduce` regenerates every '
              'reached row and scientific manifest/summary at rtol1e-11/atol1e-13. '
              '`python report_v5.py --check` verifies both generated reports.', '']
    return '\n'.join(lines)


def publish_report(directory, check=False):
    summary = summarize(directory)
    for name, content in {'summary.json': json.dumps(summary, indent=2, sort_keys=True)+'\n', 'report.md': markdown(summary)}.items():
        if check:
            if (directory/name).read_text() != content: raise ValueError('stale report '+name)
        else: (directory/name).write_text(content)
    print('RESULT', summary['status'], summary['usable'], flush=True)
    return summary


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--directory', type=Path, default=DIRECTORY)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    publish_report(args.directory, args.check)
