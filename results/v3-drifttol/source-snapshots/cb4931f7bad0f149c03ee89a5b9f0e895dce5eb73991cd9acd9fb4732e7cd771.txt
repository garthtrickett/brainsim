"""Frozen slope on perturbed drift boundaries; abrupt times stay exact."""
import numpy as np

from v3_forgetting import run as forget_run
from v3_slope import FAST, run as slope_run

ESTIMATOR = {'method': 'ols', 'W': 128}

FAMILIES = ('window', 'sgd', 'adwin')
ARMS = FAMILIES + ('reference', 'jitter_32', 'jitter_256', 'jitter_1024', 'drop_50', 'oracle_nofallback')
GRIDS = {'window': [{'window': w} for w in (1, 2, 4, 8, 16, 32, 64, 128, 256, 512, 1024, 6000)],
         'sgd': [{'lr': lr} for lr in (.0001, .0004, .001, .004, .008, .016,
                                       .035743040182210514, .064, .128, .256, .512, 1.)],
         'adwin': [{'delta': d, 'clock': c} for d in (.0001, .001, .01, .1) for c in (1, 8, 32)]}


def run(y, arm, config, *, schedule=None, enter=None):
    y = np.asarray(y, dtype=np.float64)
    if y.ndim != 2 or not y.shape[0] or not y.shape[1] or not np.isfinite(y).all():
        raise ValueError('finite nonempty observations required')
    if arm not in ARMS:
        raise ValueError('unknown policy')
    if schedule is not None and arm in FAMILIES:
        raise ValueError('evaluator schedule forbidden for y-only controls')
    if arm in FAMILIES:
        return forget_run(y, arm, config)
    if arm == 'oracle_nofallback':
        if dict(config) != dict(FAST):
            raise ValueError('fixed fast base required')
    elif dict(config) != dict(ESTIMATOR):
        raise ValueError('frozen slope configuration required')
    if schedule is None:
        raise ValueError('evaluator schedule required')
    schedule = np.asarray(schedule)
    if schedule.shape != y.shape or not np.isfinite(schedule).all() or np.any((schedule != 0) & (schedule != 1)):
        raise ValueError('binary evaluator schedule required')
    if arm == 'oracle_nofallback':
        return forget_run(y, 'oracle_matched', dict(FAST), triggers=schedule)
    if enter is None:
        raise ValueError('evaluator entries required')
    enter = np.asarray(enter)
    if enter.shape != y.shape or not np.isfinite(enter).all() or np.any((enter != 0) & (enter != 1)):
        raise ValueError('binary evaluator entries required')
    if np.any(enter > schedule):
        raise ValueError('entries must be requests')
    return slope_run(y, 'slope', dict(ESTIMATOR), schedule=schedule, enter=enter)
