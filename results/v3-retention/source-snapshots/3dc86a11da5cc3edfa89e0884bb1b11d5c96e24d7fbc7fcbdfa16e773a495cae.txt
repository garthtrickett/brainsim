"""Frozen retention menus, three-mode comparisons and the strict ablation veto."""
import numpy as np

from v3_retention import ARMS, FAMILIES, FAST, GRIDS, random_probability
from v3_slice1_decisions import digest, finite, scientific

PROTOCOL = {'id': 'v3-retention-20260909-v1',
            'registration_commit': '5c07122fb9a047730121791d737f2ac6c3cda027',
            'registration_sha256': '8efd8adfeda13a3fc1079b94f69b26b4e9091ad1c1729a3a8cd4c129dd056309'}
SEEDS = {'development': tuple(range(100000, 100008)), 'tuning': tuple(range(101000, 101008)),
         'confirmation': tuple(range(103000, 103032))}
KEYS = {'tuning': {f'{a}/{i}/{s}' for a in FAMILIES for i in range(12) for s in SEEDS['tuning']},
        'confirmation': {f'{a}/{s}' for a in ARMS for s in SEEDS['confirmation']}}
CONTROLS = ('window', 'sgd', 'adwin', 'random_fallback', 'oracle_nofallback')
SPECS = [('primary', [('core', c, 'post_mse', None) for c in ('switch_quiet', 'switch_noisy')] +
                      [('mixed', c, 'post_mse', None) for c in ('increase_first', 'decrease_first')])]
SPECS += [(c, [('core', c, 'post_mse' if c.startswith('switch_') else 'excess_mse', None)])
          for c in ('quiet', 'noisy', 'switch_quiet', 'switch_noisy')]
SPECS += [(c, [(c, c, 'excess_mse', None)]) for c in ('noise_jump', 'drift', 'exactly_quiet')]
SPECS += [(f'{n}/{w}', [(n, n, 'windows', w)]) for n, w in
          (('noise_jump', 'noise_increase'), ('noise_jump', 'noise_decrease'), ('drift', 'drift'))]
SPECS += [(f'mixed/{c}/{f}', [('mixed', c, f, None)]) for c in ('increase_first', 'decrease_first')
          for f in ('post_mse', 'stable_mse')]
STRICT = {'quiet', 'noisy', 'noise_jump', 'exactly_quiet', 'noise_jump/noise_increase',
          'noise_jump/noise_decrease', 'mixed/increase_first/stable_mse', 'mixed/decrease_first/stable_mse'}


def complete(rows, stage):
    if set(rows) != KEYS[stage] or not finite(rows):
        raise ValueError('incomplete/non-finite '+stage)
    if any(r.get('status') not in ('ok', 'nonfinite') for r in rows.values()):
        raise ValueError('unknown row status')


def metric_values(row):
    result = {}
    for label, fields in SPECS:
        values = [row['fixtures'][n]['coordinates'][c][f][w] if w else
                  row['fixtures'][n]['coordinates'][c][f] for n, c, f, w in fields]
        if any(type(v) not in (int, float) or not np.isfinite(v) or v < 0 for v in values):
            raise ValueError('invalid learning metric')
        result[label] = float(np.mean(values))
    return result


def objective(row):
    values = metric_values(row)
    return .5*(values['primary']+np.mean([values[k] for k, _ in SPECS[1:]]))


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
        chosen = [rows[f'retain/{indices["retain"]}/{s}'] for s in SEEDS['tuning']]
        counts = [r['memory'][n][c]['reset_count'] for r in chosen for n in r['memory'] for c in r['memory'][n]]
        if len(counts) != 9*8 or any(type(c) is not int or c < 0 for c in counts):
            raise ValueError('incomplete retain frequency evidence')
        count, opportunities = sum(counts), 6000*9*8
        result['random_frequency'] = {'starts': count, 'coordinate_time': opportunities,
                                      'probability': random_probability(count, opportunities, 1)}
        selected['oracle_nofallback'] = dict(FAST)
        selected['random_fallback'] = dict(selected['retain'])
    return result


def interval(values):
    values = np.asarray(values, dtype=float)
    if values.ndim != 1 or not len(values) or not np.isfinite(values).all():
        raise ValueError('finite seed values required')
    indices = np.random.default_rng(105000).integers(0, len(values), (10000, len(values)))
    return np.quantile(values[indices].mean(axis=1), [.025, .975]).tolist()


def contrast(control, candidate, mode):
    control, candidate = np.asarray(control), np.asarray(candidate)
    if control.shape != candidate.shape or control.ndim != 1 or not len(control) or not np.isfinite(control).all() or not np.isfinite(candidate).all():
        raise ValueError('finite paired samples required')
    if mode not in ('improve', 'preserve', 'strict'):
        raise ValueError('unknown comparison mode')
    delta = candidate-control
    bounds, allowed = interval(delta), max(.002, .1*float(control.mean()))
    if mode == 'improve':
        passed = candidate.mean() <= .9*control.mean() and bounds[1] < 0
    elif mode == 'preserve':
        passed = bounds[1] <= allowed
    else:
        passed = bounds[1] < 0
    return {'control': float(control.mean()), 'candidate': float(candidate.mean()),
            'delta': float(delta.mean()), 'interval95': bounds, 'allowed': allowed,
            'mode': mode, 'pass': bool(passed)}


def performance_decision(rows, candidate='retain'):
    complete(rows, 'confirmation')
    if candidate != 'retain':
        raise ValueError('invalid candidate')
    if any(rows[f'{a}/{s}']['status'] != 'ok' for a in (candidate,)+CONTROLS for s in SEEDS['confirmation']):
        return {'status': 'learning_negative', 'reason': 'non-finite required trajectory', 'cells': {}}
    metrics = {a: [metric_values(rows[f'{a}/{s}']) for s in SEEDS['confirmation']] for a in (candidate,)+CONTROLS}
    cells = {}
    for control in CONTROLS:
        cells[f'{control}/primary'] = contrast([m['primary'] for m in metrics[control]],
            [m['primary'] for m in metrics[candidate]], 'preserve' if control == 'oracle_nofallback' else 'improve')
        for label, _ in SPECS[1:]:
            mode = 'strict' if control == 'oracle_nofallback' and label in STRICT else 'preserve'
            cells[f'{control}/{label}'] = contrast([m[label] for m in metrics[control]],
                [m[label] for m in metrics[candidate]], mode)
    status = 'learning_positive' if all(c['pass'] for c in cells.values()) else 'learning_negative'
    return {'status': status, 'cells': cells}
