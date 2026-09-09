"""Horizon menus and the 45-cell advancement gate for observable-gated slope."""
import numpy as np

from v3_burst import random_probability
from v3_retention_policy import SPECS, contrast, digest, finite, metric_values, objective, scientific
from v3_slopetime import ARMS, ESTIMATOR, FAMILIES, FAST, GRIDS

PROTOCOL = {'id': 'v3-slopetime-20260909-v1',
            'registration_commit': '645c62bf6490fabe0ec565724438928ffc66d6a2',
            'registration_sha256': '6d2eb7366e12f1fadd1f3c979e5398e022ad0744a169bc61839f6c33b4e84d6d'}
SEEDS = {'development': tuple(range(140000, 140008)), 'tuning': tuple(range(141000, 141008)),
         'confirmation': tuple(range(143000, 143032))}
KEYS = {'tuning': {f'{a}/{i}/{s}' for a in FAMILIES for i in range(12) for s in SEEDS['tuning']},
        'confirmation': {f'{a}/{s}' for a in ARMS for s in SEEDS['confirmation']}}
CONTROLS = ('window', 'sgd', 'adwin')
TUNING_ALARM = {'delta': .1, 'clock': 1}
TUNING_ALARM = {'delta': .1, 'clock': 1}


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
        chosen = [rows[f'slope_adwin/{indices["slope_adwin"]}/{s}'] for s in SEEDS['tuning']]
        counts = [r['memory'][n][c]['reset_count'] for r in chosen for n in r['memory'] for c in r['memory'][n]]
        if len(counts) != 9*8 or any(type(c) is not int or c < 0 for c in counts):
            raise ValueError('incomplete slope frequency evidence')
        count, opportunities = sum(counts), 6000*9*8
        result['random_frequency'] = {'starts': count, 'coordinate_time': opportunities,
                                      'probability': random_probability(count, opportunities, 1)}
        selected['reference'] = dict(ESTIMATOR)
        selected['random_slope'] = dict(selected['slope_adwin'])
        selected['oracle_nofallback'] = dict(FAST)
    return result


def interval(values):
    values = np.asarray(values, dtype=float)
    if values.ndim != 1 or not len(values) or not np.isfinite(values).all():
        raise ValueError('finite seed values required')
    indices = np.random.default_rng(145000).integers(0, len(values), (10000, len(values)))
    return np.quantile(values[indices].mean(axis=1), [.025, .975]).tolist()


def performance_decision(rows, subject):
    complete(rows, 'confirmation')
    if subject not in ('slope_adwin', 'reference', 'random_slope', 'oracle_nofallback'):
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
