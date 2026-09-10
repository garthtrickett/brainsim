"""Frozen slope-benchmark menus and the 75-cell gate on adapted cells."""
import numpy as np

from v3_retention_policy import contrast, digest, finite, scientific
from v3_slope import FAST
from v3_slopebench import FIXTURES

ESTIMATOR = {'method': 'ols', 'W': 128}
FAMILIES = ('window', 'sgd', 'adwin')
ARMS = FAMILIES + ('slope', 'oracle_nofallback', 'random_slope')
GRIDS = {'window': [{'window': w} for w in (1, 2, 4, 8, 16, 32, 64, 128, 256, 512, 1024, 6000)],
         'sgd': [{'lr': lr} for lr in (.0001, .0004, .001, .004, .008, .016,
                                       .035743040182210514, .064, .128, .256, .512, 1.)],
         'adwin': [{'delta': d, 'clock': c} for d in (.0001, .001, .01, .1) for c in (1, 8, 32)]}
PROTOCOL = {'id': 'v3-slopebench-20260909-v1',
            'registration_commit': '04ccd3d42664cd241d3f78a2183dcefb022a1c3d',
            'registration_sha256': 'c209ca01fe5388538c129ad99f1f198ee6bc8d4092bb2b77110b11eafd2033e0'}
SEEDS = {'development': tuple(range(150000, 150008)), 'tuning': tuple(range(151000, 151008)),
         'confirmation': tuple(range(153000, 153032))}
KEYS = {'tuning': {f'{a}/{i}/{s}' for a in FAMILIES for i in range(12) for s in SEEDS['tuning']},
        'confirmation': {f'{a}/{s}' for a in ARMS for s in SEEDS['confirmation']}}
CONTROLS = ('window', 'sgd', 'adwin', 'random_slope', 'oracle_nofallback')
SPECS = [('primary', [('core', c, 'post_mse', None) for c in ('switch_quiet', 'switch_noisy')] +
                      [('mixed', c, 'post_mse', None) for c in ('increase_first', 'decrease_first')])]
SPECS += [(c, [('core', c, 'post_mse' if c.startswith('switch_') else 'excess_mse', None)])
          for c in ('quiet', 'noisy', 'switch_quiet', 'switch_noisy')]
SPECS += [(f'mixed/{c}/{f}', [('mixed', c, f, None)]) for c in ('increase_first', 'decrease_first')
          for f in ('post_mse', 'stable_mse')]
SPECS += [(f'ramp_{n}', [(n, n, 'excess_mse', None)]) for n in ('steep', 'shallow', 'noisy')]
SPECS += [(f'ramp_{n}/ramp', [(n, n, 'ramp_mse', None)]) for n in ('steep', 'shallow', 'noisy')]
STRICT = {'quiet', 'noisy', 'mixed/increase_first/stable_mse', 'mixed/decrease_first/stable_mse',
          'ramp_steep', 'ramp_shallow', 'ramp_noisy'}


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
        selected['oracle_nofallback'] = dict(FAST)
        selected['slope'] = dict(ESTIMATOR)
        selected['random_slope'] = dict(ESTIMATOR)
    return result


def interval(values):
    values = np.asarray(values, dtype=float)
    if values.ndim != 1 or not len(values) or not np.isfinite(values).all():
        raise ValueError('finite seed values required')
    indices = np.random.default_rng(155000).integers(0, len(values), (10000, len(values)))
    return np.quantile(values[indices].mean(axis=1), [.025, .975]).tolist()


def performance_decision(rows, candidate='slope'):
    complete(rows, 'confirmation')
    if candidate != 'slope':
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
