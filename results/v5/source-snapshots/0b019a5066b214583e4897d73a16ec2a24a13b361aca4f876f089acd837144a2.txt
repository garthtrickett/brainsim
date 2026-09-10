"""Three causal signal/learner arrangements around the frozen persistent detector."""
import numpy as np
from numba import njit

from v3_gate import adam_step
from v3_persistent import FIXTURES, fixture, run as persistent_run
from v3_slice1_learning import run as old_run

DETECTORS = ('coupled', 'watch_adam', 'separate')
CONFIGS = {'coupled': {'lr': .004, 'gain': 64., 'beta2': .999},
           'watch_adam': {'lr': .004, 'gain': 0., 'beta2': .999},
           'separate': {'lr': .004, 'gain': 64., 'beta2': .999},
           'adam': {'lr': .032, 'beta2': .9999}, 'sgd': {'lr': .035743040182210514},
           'single': {'lr': .016, 'gain': 1., 'beta2': .999},
           'constant': {'lr': .004, 'gain': 64., 'beta2': .999}}


@njit(cache=True)
def controlled_adam(y, gates, lr, gain, beta2):
    predictions, norms = np.zeros_like(y), np.zeros(len(y))
    w, m, v = np.zeros(y.shape[1]), np.zeros(y.shape[1]), np.zeros(y.shape[1])
    for t in range(len(y)):
        squared = 0.
        for j in range(y.shape[1]):
            predictions[t, j] = w[j]
            gradient = w[j]-y[t, j]
            m[j], v[j], direction = adam_step(m[j], v[j], gradient, t+1, beta2)
            update = lr*(1.+gain*gates[t, j])*direction
            w[j] -= update
            squared += update*update
        norms[t] = np.sqrt(squared)
    return predictions, gates, norms


def run(y, arm, observer=False, constants=None, config=None):
    if arm not in CONFIGS:
        raise ValueError('unknown policy')
    y = np.asarray(y, dtype=np.float64)
    if y.ndim != 2 or not y.shape[0] or not y.shape[1] or not np.isfinite(y).all():
        raise ValueError('finite nonempty observation matrix required')
    config = CONFIGS[arm] if config is None else config
    if arm not in DETECTORS:
        return old_run(y, arm, config, constants, observer)
    if observer:
        return persistent_run(y, 'candidate', observer=True)
    if arm == 'coupled':
        return persistent_run(y, 'candidate', config=config)
    if arm == 'watch_adam':
        predictions, _, norms = old_run(y, 'adam', config)
        gradients = predictions-y
        # The fixed observer's gradient on observation -g is exactly g.
        if not np.isfinite(gradients).all():
            return predictions, np.full_like(y, np.nan), norms
        gates = persistent_run(-gradients, 'candidate', observer=True)[1]
        return predictions, gates, norms
    gates = persistent_run(y, 'candidate', observer=True)[1]
    return controlled_adam(y, gates, float(config['lr']), float(config['gain']), float(config['beta2']))


def warmup():
    for arm in DETECTORS:
        run(np.ones((150, 1)), arm)
