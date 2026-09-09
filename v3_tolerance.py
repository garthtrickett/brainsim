"""Frozen-candidate schedule variants; only the request schedule varies."""
import numpy as np

from v3_forgetting import run as forget_run
from v3_retention import FAST, dual_run

FAMILIES = ('window', 'sgd', 'adwin')
ARMS = FAMILIES + ('reference', 'jitter_2', 'jitter_8', 'jitter_16', 'jitter_32', 'jitter_128',
                   'drop_10', 'drop_50', 'add_0005', 'add_0020', 'adwin_schedule')
FROZEN = {'delta': .1, 'H': 32}
GRIDS = {'window': [{'window': w} for w in (1, 2, 4, 8, 16, 32, 64, 128, 256, 512, 1024, 6000)],
         'sgd': [{'lr': lr} for lr in (.0001, .0004, .001, .004, .008, .016,
                                       .035743040182210514, .064, .128, .256, .512, 1.)],
         'adwin': [{'delta': d, 'clock': c} for d in (.0001, .001, .01, .1) for c in (1, 8, 32)]}


def run(y, arm, config, *, schedule=None):
    y = np.asarray(y, dtype=np.float64)
    if y.ndim != 2 or not y.shape[0] or not y.shape[1] or not np.isfinite(y).all():
        raise ValueError('finite nonempty observations required')
    if arm not in ARMS:
        raise ValueError('unknown policy')
    if schedule is not None and arm in FAMILIES:
        raise ValueError('evaluator schedule forbidden for y-only controls')
    if arm in FAMILIES:
        return forget_run(y, arm, config)
    if dict(config) != dict(FROZEN):
        raise ValueError('frozen candidate configuration required')
    if schedule is None:
        raise ValueError('evaluator schedule required')
    schedule = np.asarray(schedule)
    if schedule.shape != y.shape or not np.isfinite(schedule).all() or np.any((schedule != 0) & (schedule != 1)):
        raise ValueError('binary evaluator schedule required')
    return dual_run(y, schedule, FROZEN['delta'], FROZEN['H'])
