"""Frozen drift menus and the 75-cell gate with the repaired both-perfect veto."""
import numpy as np

from v3_drift import ARMS, FAMILIES, FAST, FROZEN, GRIDS
from v3_retention_policy import (SPECS, STRICT, contrast, digest, finite, metric_values,
                                 objective, scientific)

PROTOCOL = {'id': 'v3-drift-20260909-v1',
            'registration_commit': 'd25ccfe9eabf9af566aac2b21e5ec9f9d381b7a3',
            'registration_sha256': '62a8eb8470e934430cfbcc9ee21fc3cad3c10853774ea795c4f38bcddcc713bb'}
SEEDS = {'development': tuple(range(120000, 120008)), 'tuning': tuple(range(121000, 121008)),
         'confirmation': tuple(range(123000, 123032))}
KEYS = {'tuning': {f'{a}/{i}/{s}' for a in FAMILIES for i in range(12) for s in SEEDS['tuning']},
        'confirmation': {f'{a}/{s}' for a in ARMS for s in SEEDS['confirmation']}}
CONTROLS = ('window', 'sgd', 'adwin', 'random_drift', 'oracle_nofallback')


def complete(rows, stage):
    if set(rows) != KEYS[stage] or not finite(rows):
        raise ValueError('incomplete/non-finite '+stage)
    if any(r.get('status') not in ('ok', 'nonfinite') for r in rows.values()):
        raise ValueError('unknown row status')


def select(rows):
    complete(rows, 'tuning')
    selected, indices, scores, reasons = {}, {}, {}, []
    for arm in FAMILIES:
        scores[arm] = []
        for i in range(12):
            trials = [rows[f'{arm}/{i}/{s}'] for s in SEEDS['tuning']]
            scores[arm].append(float(np.mean([objective(r) for r in trials]))
                               if all(r['status'] == 'ok' for r in trials) else None)
        valid = [i for i, score in enumerate(scores[arm]) if score is not None]
        if not valid:
            reasons.append(arm+': no finite complete configuration')
            continue
        index = min(valid, key=lambda i: scores[arm][i])
        selected[arm], indices[arm] = dict(GRIDS[arm][index]), index
    result = {'status': 'tuning_inconclusive' if reasons else 'eligible', 'reasons': reasons,
              'selected': selected, 'indices': indices, 'objectives': scores}
    if not reasons:
        selected['oracle_nofallback'] = dict(FAST)
        selected['retain_drift'] = dict(FROZEN)
        selected['random_drift'] = dict(FROZEN)
    return result


def interval(values):
    values = np.asarray(values, dtype=float)
    if values.ndim != 1 or not len(values) or not np.isfinite(values).all():
        raise ValueError('finite seed values required')
    indices = np.random.default_rng(125000).integers(0, len(values), (10000, len(values)))
    return np.quantile(values[indices].mean(axis=1), [.025, .975]).tolist()


def performance_decision(rows, candidate='retain_drift'):
    complete(rows, 'confirmation')
    if candidate != 'retain_drift':
        raise ValueError('invalid candidate')
    if any(rows[f'{a}/{s}']['status'] != 'ok' for a in (candidate,)+CONTROLS for s in SEEDS['confirmation']):
        return {'status': 'learning_negative', 'reason': 'non-finite required trajectory', 'cells': {}}
    metrics = {a: [metric_values(rows[f'{a}/{s}']) for s in SEEDS['confirmation']] for a in (candidate,)+CONTROLS}
    cells = {}
    for control in CONTROLS:
        cells[f'{control}/primary'] = contrast([m['primary'] for m in metrics[control]],
            [m['primary'] for m in metrics[candidate]], 'preserve' if control == 'oracle_nofallback' else 'improve')
        for label, _ in SPECS[1:]:
            control_mean = float(np.mean([m[label] for m in metrics[control]]))
            if control == 'oracle_nofallback' and label in STRICT and control_mean > 0:
                mode = 'strict'
            else:
                mode = 'preserve'
            cells[f'{control}/{label}'] = contrast([m[label] for m in metrics[control]],
                [m[label] for m in metrics[candidate]], mode)
    status = 'learning_positive' if all(c['pass'] for c in cells.values()) else 'learning_negative'
    return {'status': status, 'cells': cells}
