"""Frozen drift-tolerance menus, per-level instrument and tolerance point."""
import numpy as np

from v3_drifttol import ARMS, ESTIMATOR, FAMILIES, FAST, GRIDS
from v3_retention_policy import SPECS, contrast, digest, finite, metric_values, objective, scientific

PROTOCOL = {'id': 'v3-drifttol-20260909-v1',
            'registration_commit': '1a3aa910792a3161701aebf21f8b0ed43436d089',
            'registration_sha256': 'd5c1b929e8269d270d20c604ab548a90573a2a104e9954446791f2de986df2ad'}
SEEDS = {'development': tuple(range(170000, 170008)), 'tuning': tuple(range(171000, 171008)),
         'confirmation': tuple(range(173000, 173032))}
KEYS = {'tuning': {f'{a}/{i}/{s}' for a in FAMILIES for i in range(12) for s in SEEDS['tuning']},
        'confirmation': {f'{a}/{s}' for a in ARMS for s in SEEDS['confirmation']}}
CONTROLS = ('window', 'sgd', 'adwin')
LEVELS = ['jitter_32', 'jitter_256', 'jitter_1024']


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
        for arm in ARMS:
            if arm not in FAMILIES:
                selected[arm] = dict(ESTIMATOR) if arm != 'oracle_nofallback' else dict(FAST)
    return result


def interval(values):
    values = np.asarray(values, dtype=float)
    if values.ndim != 1 or not len(values) or not np.isfinite(values).all():
        raise ValueError('finite seed values required')
    indices = np.random.default_rng(175000).integers(0, len(values), (10000, len(values)))
    return np.quantile(values[indices].mean(axis=1), [.025, .975]).tolist()


def performance_decision(rows, subject):
    complete(rows, 'confirmation')
    if subject not in ARMS or subject in FAMILIES:
        raise ValueError('invalid subject')
    if any(rows[f'{a}/{s}']['status'] != 'ok' for a in (subject,)+CONTROLS for s in SEEDS['confirmation']):
        return {'status': 'learning_negative', 'reason': 'non-finite required trajectory', 'cells': {}}
    metrics = {a: [metric_values(rows[f'{a}/{s}']) for s in SEEDS['confirmation']] for a in (subject,)+CONTROLS}
    cells = {}
    for control in CONTROLS:
        cells[f'{control}/primary'] = contrast([m['primary'] for m in metrics[control]],
            [m['primary'] for m in metrics[subject]], 'improve')
        for label, _ in SPECS[1:]:
            cells[f'{control}/{label}'] = contrast([m[label] for m in metrics[control]],
                [m[label] for m in metrics[subject]], 'preserve')
    status = 'learning_positive' if all(c['pass'] for c in cells.values()) else 'learning_negative'
    return {'status': status, 'cells': cells}


def tolerance_point(rows):
    levels = {}
    for arm in LEVELS:
        decision = performance_decision(rows, arm)
        levels[arm] = {'status': decision['status'],
                       'passed': sum(c['pass'] for c in decision['cells'].values()), 'cells': 45}
    passing = [int(a.split('_')[1]) for a in LEVELS if levels[a]['status'] == 'learning_positive']
    return {'levels': levels, 'tolerance': max(passing) if passing else None}
