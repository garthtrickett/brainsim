"""Graded SGD under frozen lies; ordinary when quiet, boosted on alarms."""
import numpy as np
from numba import njit

from v3_forgetting import run as forget_run

FAMILIES = ('graded', 'window', 'sgd', 'adwin')
ARMS = FAMILIES + ('adwin_gated',)
GRIDS = {'graded': [{'gain': g, 'window': w} for g in (1., 2., 4., 8.) for w in (8, 32, 128)],
         'window': [{'window': w} for w in (1, 2, 4, 8, 16, 32, 64, 128, 256, 512, 1024, 6000)],
         'sgd': [{'lr': lr} for lr in (.0001, .0004, .001, .004, .008, .016,
                                       .035743040182210514, .064, .128, .256, .512, 1.)],
         'adwin': [{'delta': d, 'clock': c} for d in (.0001, .001, .01, .1) for c in (1, 8, 32)]}
BASE_LR = .128


@njit(cache=True)
def graded_kernel(y, alarms, gain, width):
    predictions = np.zeros_like(y)
    norms = np.zeros(len(y))
    counts = np.zeros(y.shape, dtype=np.int64)
    for j in range(y.shape[1]):
        weight, recent = 0., 0.
        for t in range(len(y)):
            predictions[t, j] = weight
            recent += alarms[t, j]
            if t >= width:
                recent -= alarms[t-width, j]
            counts[t, j] = recent
            rate = BASE_LR*(1.+gain*recent)
            previous = weight
            weight -= rate*(weight-y[t, j])
            norms[t] += (weight-previous)*(weight-previous)
    return predictions, np.sqrt(norms), counts


def run(y, arm, config, *, alarms=None):
    y = np.asarray(y, dtype=np.float64)
    if y.ndim != 2 or not y.shape[0] or not y.shape[1] or not np.isfinite(y).all():
        raise ValueError('finite nonempty observations required')
    if arm not in ARMS:
        raise ValueError('unknown policy')
    if alarms is not None and arm in ('window', 'sgd', 'adwin'):
        raise ValueError('alarm schedule forbidden for y-only controls')
    if arm in ('window', 'sgd', 'adwin'):
        return forget_run(y, arm, config)
    try:
        gain, width = float(config['gain']), config['window']
    except (KeyError, TypeError):
        raise ValueError('gain/window configuration required')
    if not np.isfinite(gain) or gain < 0 or type(width) is not int or width < 1:
        raise ValueError('invalid graded configuration')
    if alarms is None:
        raise ValueError('alarm schedule required')
    alarms = np.asarray(alarms)
    if alarms.shape != y.shape or not np.isfinite(alarms).all() or np.any((alarms != 0) & (alarms != 1)):
        raise ValueError('binary alarm schedule required')
    predictions, norms, counts = graded_kernel(y, alarms, gain, width)
    return predictions, alarms, norms, counts
