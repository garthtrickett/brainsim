"""Q3 capacity contrasts and the three-way pools verdict."""
import argparse
import json
from pathlib import Path

import numpy as np

from study_q3 import CELLS, DIRECTORY, SEEDS, digest, finite, source_hashes
from study_q3 import PROTOCOL


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


def key(hidden, k, pools, combos, seed):
    return f'{hidden}/{k}/{pools}/{combos}/{seed}'


def summarize(directory):
    manifest = json.loads((directory/'manifest.json').read_text())
    if manifest['protocol'] != PROTOCOL or manifest['sources'] != source_hashes():
        raise ValueError('manifest differs from registration')
    result = {'status': 'awaiting_confirmation', 'closed': False,
              'protocol': manifest['protocol'], 'manifest_digest': digest(manifest),
              'cells': {}, 'counts': {'confirmation': 0}, 'contrasts': {}}
    if (directory/'confirmation.json').exists():
        envelope = json.loads((directory/'confirmation.json').read_text())
        if envelope['protocol'] != PROTOCOL or envelope['sources'] != source_hashes():
            raise ValueError('changed source/protocol')
        rows = envelope['rows']
        expected = {key(h, k, p, c, s) for (h, k, p, c) in CELLS for s in SEEDS}
        if set(rows) != expected or not finite(rows):
            raise ValueError('incomplete/non-finite confirmation')
        if any(r.get('status') != 'ok' for r in rows.values()):
            raise ValueError('unknown row status')
        for row_key, row in rows.items():
            if row.get('manifest_digest') != digest(manifest):
                raise ValueError('row belongs to another manifest')
        result['counts']['confirmation'] = len(rows)

        def scores(hidden, k, pools, combos):
            return [rows[key(hidden, k, pools, combos, s)]['score'] for s in SEEDS]

        for (hidden, k, pools, combos) in CELLS:
            vals = scores(hidden, k, pools, combos)
            result['cells'][f'{hidden}/{k}/{pools}/{combos}'] = {
                'mean': float(np.mean(vals)), 'interval95': interval(vals)}

        # Premise check: combos-4 at v1 scale must be easy; else stop.
        premise = float(np.mean(scores(80, 6, 1, 4)))
        if premise < 0.8:
            result['status'] = 'premise-broken'
            result['closed'] = True
            return result

        # POOL-WIN leg: each H80 P>1 vs P=1 per combos; adoption needs
        # combos-16 lower > 0 plus no regression (lower > -0.03) anywhere.
        regressions = []
        adopters = []
        for pools in (2, 3, 6):
            for combos in (4, 9, 16):
                c = paired_interval(scores(80, 6, pools, combos),
                                    scores(80, 6, 1, combos))
                result['contrasts'][f'80/6/{pools}/{combos}-vs-P1'] = c
                if c['interval95'][0] <= -0.03:
                    regressions.append((pools, combos))
            c16 = result['contrasts'][f'80/6/{pools}/16-vs-P1']
            if c16['interval95'][0] > 0:
                adopters.append((c16['delta'], pools))
        # Scale legs on combos-16 (and 9 for context).
        for combos in (9, 16):
            c = paired_interval(scores(160, 12, 4, combos), scores(80, 6, 1, combos))
            result['contrasts'][f'160/12/4/{combos}-vs-80P1'] = c
            c = paired_interval(scores(160, 12, 1, combos), scores(80, 6, 1, combos))
            result['contrasts'][f'160/12/1/{combos}-vs-80P1'] = c
        result['regressions'] = [list(r) for r in regressions]
        result['adopters'] = [p for _, p in sorted(adopters)]
        winner = max(adopters)[1] if adopters else None
        needs_scale = (winner is None or regressions) and \
            result['contrasts']['160/12/4/16-vs-80P1']['interval95'][0] > 0
        if winner is not None and not regressions:
            result['status'] = f'pool-win-P{winner}'
        elif needs_scale:
            result['status'] = 'needs-scale'
        else:
            result['status'] = 'dead-end'
        result['closed'] = True
    return result


def markdown(summary):
    lines = ['# Q3 capacity: pools and scale on memorized combinations', '',
             f'Disposition: **{summary["status"]}**.', '',
             '| Stage | Rows |', '| --- | ---: |']
    lines += [f'| {k} | {v} |' for k, v in summary['counts'].items()]
    if summary['cells']:
        lines += ['', '## Absolute train accuracy by cell (H/k/pools/combos)', '',
                  '| Cell | Mean | 95% interval |', '| --- | ---: | --- |']
        for cell, row in summary['cells'].items():
            lines.append(f'| {cell} | {row["mean"]:.4f} | [{row["interval95"][0]:.4f}, {row["interval95"][1]:.4f}] |')
    if summary['contrasts']:
        lines += ['', '## Paired contrasts (same-seed, same cell control)', '',
                  '| Contrast | Treatment | Control | Delta | 95% interval |',
                  '| --- | ---: | ---: | ---: | --- |']
        for name, c in summary['contrasts'].items():
            lines.append(f'| {name} | {c["treatment"]:.4f} | {c["control"]:.4f} | {c["delta"]:+.4f} '
                         f'| [{c["interval95"][0]:+.4f}, {c["interval95"][1]:+.4f}] |')
    if summary.get('regressions') is not None:
        lines += ['', f'Adopters: {summary["adopters"]}; regressions: {summary["regressions"]}.', '']
    lines += ['', '## Scope and reproduction', '',
              'Memorization capacity only (train accuracy, held_out=0): no '
              'generalisation claim. Total sparsity held constant across pools '
              'within each H, so differences are competition geometry. Same-seed '
              'pairing within cells; cross-seed generalisation out of scope.', '',
              '`python check_q3.py --evidence results/q3 --reproduce` regenerates '
              'every row at rtol1e-11/atol1e-13. '
              '`python report_q3.py --check` verifies both generated reports.', '']
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
