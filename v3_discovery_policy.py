"""Frozen discovery menus, ground-truth discovery gate and learning decisions."""
import numpy as np

from v3_discovery import ARMS, FAMILIES, GRIDS
from v3_slice1_decisions import digest, finite, scientific

PROTOCOL = {'id': 'v3-discovery-20260909-v1',
            'registration_commit': '30d0ac3bb38504baf210d1bf83762faf3fd836bd',
            'registration_sha256': '48006f99b4e29475b265a883b73eff680da7bddcaa3adbedb34e15fda44d07cb'}
SEEDS = {'development': tuple(range(90000, 90008)), 'tuning': tuple(range(91000, 91008)),
         'confirmation': tuple(range(93000, 93032))}
KEYS = {'tuning': {f'{a}/{i}/{s}' for a in FAMILIES for i in range(12) for s in SEEDS['tuning']},
        'confirmation': {f'{a}/{s}' for a in ARMS for s in SEEDS['confirmation']}}
CONTROLS = ('window', 'sgd', 'adwin', 'random', 'shuffled', 'nocontext_matched')
SWITCH_COORDS = (('core', 'switch_quiet'), ('core', 'switch_noisy'),
                 ('mixed', 'increase_first'), ('mixed', 'decrease_first'))
SPECS = [('primary', [('core', c, 'post_mse', None) for c in ('switch_quiet', 'switch_noisy')] +
                      [('mixed', c, 'post_mse', None) for c in ('increase_first', 'decrease_first')])]
SPECS += [(c, [('core', c, 'post_mse' if c.startswith('switch_') else 'excess_mse', None)])
          for c in ('quiet', 'noisy', 'switch_quiet', 'switch_noisy')]
SPECS += [(c, [(c, c, 'excess_mse', None)]) for c in ('noise_jump', 'drift', 'exactly_quiet')]
SPECS += [(f'{n}/{w}', [(n, n, 'windows', w)]) for n, w in
          (('noise_jump', 'noise_increase'), ('noise_jump', 'noise_decrease'), ('drift', 'drift'))]
SPECS += [(f'mixed/{c}/{f}', [('mixed', c, f, None)]) for c in ('increase_first', 'decrease_first')
          for f in ('post_mse', 'stable_mse')]


def complete(rows, stage):
    if set(rows) != KEYS[stage] or not finite(rows):
        raise ValueError('incomplete/non-finite ' + stage)
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
    return .5 * (values['primary'] + np.mean([values[k] for k, _ in SPECS[1:]]))


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
            reasons.append(arm + ': no finite complete configuration')
            continue
        index = min(valid, key=lambda i: scores[arm][i])
        selected[arm], indices[arm] = dict(GRIDS[arm][index]), index
    result = {'status': 'tuning_inconclusive' if reasons else 'eligible', 'reasons': reasons,
              'selected': selected, 'indices': indices, 'objectives': scores}
    if not reasons:
        selected['oracle_matched'] = dict(selected['discover'])
        selected['random'] = dict(selected['discover'])
        selected['shuffled'] = dict(selected['discover'])
        selected['nocontext_matched'] = dict(selected['discover'])
    return result


def interval(values):
    values = np.asarray(values, dtype=float)
    if values.ndim != 1 or not len(values) or not np.isfinite(values).all():
        raise ValueError('finite seed values required')
    indices = np.random.default_rng(95000).integers(0, len(values), (10000, len(values)))
    return np.quantile(values[indices].mean(axis=1), [.025, .975]).tolist()


def contrast(control, candidate, improvement):
    control, candidate = np.asarray(control), np.asarray(candidate)
    if control.shape != candidate.shape or control.ndim != 1 or not len(control) or not np.isfinite(control).all() or not np.isfinite(candidate).all():
        raise ValueError('finite paired samples required')
    delta = candidate - control
    bounds, allowed = interval(delta), max(.002, .1 * float(control.mean()))
    passed = (candidate.mean() <= .9 * control.mean() and bounds[1] < 0) if improvement else bounds[1] <= allowed
    return {'control': float(control.mean()), 'candidate': float(candidate.mean()),
            'delta': float(delta.mean()), 'interval95': bounds, 'allowed': allowed, 'pass': bool(passed)}


def seed_auc(row):
    """Mean polarity-invariant AUC* over the four switching coordinates."""
    aucs = []
    for name, coord in SWITCH_COORDS:
        auc = row['discovery'][name][coord]['auc']
        if auc is None or not np.isfinite(auc):
            raise ValueError('missing switching-coordinate AUC')
        aucs.append(max(float(auc), 1.0 - float(auc)))
    return float(np.mean(aucs))


def discovery_decision(rows):
    complete(rows, 'confirmation')
    for a in ('discover', 'shuffled'):
        if any(rows[f'{a}/{s}']['status'] != 'ok' for s in SEEDS['confirmation']):
            return {'status': 'discovery_negative', 'reason': f'non-finite {a} trajectory', 'cells': {}}
    cand = np.array([seed_auc(rows[f'discover/{s}']) for s in SEEDS['confirmation']])
    shuf = np.array([seed_auc(rows[f'shuffled/{s}']) for s in SEEDS['confirmation']])
    if not np.isfinite(cand).all() or not np.isfinite(shuf).all() or np.any((cand < 0) | (cand > 1)) or np.any((shuf < 0) | (shuf > 1)):
        raise ValueError('AUCs out of range')
    delta = cand - shuf
    cells = {
        'candidate_auc': {'mean': float(cand.mean()), 'interval95': interval(cand),
                          'pass': bool(cand.mean() >= 0.65 and interval(cand)[0] > 0.55)},
        'shuffled_auc': {'mean': float(shuf.mean()), 'interval95': interval(shuf),
                         'pass': bool(0.40 <= shuf.mean() <= 0.60)},
        'delta': {'mean': float(delta.mean()), 'interval95': interval(delta),
                  'pass': bool(delta.mean() > 0.10 and interval(delta)[0] > 0.05)},
    }
    status = 'discovery_pass' if all(c['pass'] for c in cells.values()) else 'discovery_negative'
    return {'status': status, 'cells': cells}


def performance_decision(rows, candidate='discover'):
    complete(rows, 'confirmation')
    if candidate not in ('discover', 'oracle', 'oracle_matched'):
        raise ValueError('invalid candidate')
    controls = CONTROLS if candidate == 'discover' else ('window', 'sgd', 'adwin')
    prefix = 'learning' if candidate == 'discover' else 'oracle'
    if any(rows[f'{a}/{s}']['status'] != 'ok' for a in (candidate,) + controls for s in SEEDS['confirmation']):
        return {'status': prefix + '_negative', 'reason': 'non-finite required trajectory', 'cells': {}}
    metrics = {a: [metric_values(rows[f'{a}/{s}']) for s in SEEDS['confirmation']] for a in (candidate,) + controls}
    cells = {f'{a}/{k}': contrast([m[k] for m in metrics[a]], [m[k] for m in metrics[candidate]], k == 'primary')
             for a in controls for k, _ in SPECS}
    status = ('learning_positive' if candidate == 'discover' else 'oracle_pass') if all(c['pass'] for c in cells.values()) else prefix + '_negative'
    return {'status': status, 'cells': cells}
