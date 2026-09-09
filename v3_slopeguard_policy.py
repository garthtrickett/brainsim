"""Frozen guard menus and the 75-cell gate on adapted cells."""
import numpy as np

from v3_burst import random_probability
from v3_retention_policy import contrast, digest, finite, scientific
from v3_slopebench_policy import SPECS, STRICT, metric_values, objective
from v3_slopeguard import ARMS, FAST, GRIDS

PROTOCOL = {'id': 'v3-slopeguard-20260909-v1',
            'registration_commit': '470344a3b9dc1aaf8721a0874840a4a405130847',
            'registration_sha256': 'b82a30e177b415d6d8d192aedef6e7233ce81812946d21b6755b6eca787e0d06'}
SEEDS = {'development': tuple(range(160000, 160008)), 'tuning': tuple(range(161000, 161008)),
         'confirmation': tuple(range(163000, 163032))}
CONTROLS = ('window', 'sgd', 'adwin', 'random_guard', 'oracle_nofallback')
FAMILIES = ('guard', 'window', 'sgd', 'adwin')
KEYS = {'tuning': {f'{a}/{i}/{s}' for a in FAMILIES for i in range(12) for s in SEEDS['tuning']},
        'confirmation': {f'{a}/{s}' for a in ARMS for s in SEEDS['confirmation']}}


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
        chosen = [rows[f'guard/{indices["guard"]}/{s}'] for s in SEEDS['tuning']]
        counts = [r['memory'][n][c]['reset_count'] for r in chosen for n in r['memory'] for c in r['memory'][n]]
        if len(counts) != 9*8 or any(type(c) is not int or c < 0 for c in counts):
            raise ValueError('incomplete guard frequency evidence')
        count, opportunities = sum(counts), 6000*9*8
        result['random_frequency'] = {'starts': count, 'coordinate_time': opportunities,
                                      'probability': random_probability(count, opportunities, 1)}
        selected['oracle_nofallback'] = dict(FAST)
        selected['reference'] = {'J': 0}
        selected['random_guard'] = dict(selected['guard'])
    return result


def interval(values):
    values = np.asarray(values, dtype=float)
    if values.ndim != 1 or not len(values) or not np.isfinite(values).all():
        raise ValueError('finite seed values required')
    indices = np.random.default_rng(165000).integers(0, len(values), (10000, len(values)))
    return np.quantile(values[indices].mean(axis=1), [.025, .975]).tolist()


def performance_decision(rows, candidate='guard'):
    complete(rows, 'confirmation')
    if candidate != 'guard':
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
