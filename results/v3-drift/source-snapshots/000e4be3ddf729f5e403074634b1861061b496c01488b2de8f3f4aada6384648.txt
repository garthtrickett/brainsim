"""Causal mean-disagreement candidate and declared controls, without task metadata."""
import numpy as np
from numba import njit

from v3_gate import adam_step, variance_step

ARMS = ('sgd', 'adam', 'single', 'historical', 'candidate')
GATED = ('single', 'historical', 'candidate')
IDS = {name: i for i, name in enumerate(ARMS + ('constant',))}
RATES = (.001, .004, .016, .064, .256, 1.)
GRIDS = {
    'sgd': [{'lr': float(lr)} for lr in np.geomspace(.0001, 1., 24)],
    'adam': [{'lr': lr, 'beta2': beta} for lr in RATES for beta in (.9, .99, .999, .9999)],
    **{arm: [{'lr': lr, 'gain': gain} for lr in RATES for gain in (0., 1., 8., 64.)]
       for arm in GATED},
}


@njit(cache=True)
def signal(mf, ms, sf, ss, arm):
    if arm == 2:
        return sf / (sf + 1.)
    if arm == 3:
        return max(0., sf - ss) / (sf + ss + 1e-8)
    difference = (mf - ms) ** 2
    return difference / (difference + sf + ss + 1e-8)


@njit(cache=True)
def _run(y, arm, lr, beta2, gain, constants, observer):
    n, width = y.shape
    predictions, gates = np.zeros_like(y), np.zeros_like(y)
    norms = np.zeros(n)
    w, m, v = np.zeros(width), np.zeros(width), np.zeros(width)
    mf, ms, sf, ss = np.zeros(width), np.zeros(width), np.zeros(width), np.zeros(width)
    for t in range(n):
        squared_update = 0.
        for j in range(width):
            predictions[t, j] = w[j]
            g = w[j] - y[t, j]
            q = 0.
            if 2 <= arm <= 4:
                if t == 0:
                    mf[j] = ms[j] = g
                else:
                    mf[j], sf[j] = variance_step(mf[j], sf[j], g, .1)
                    if arm >= 3:
                        ms[j], ss[j] = variance_step(ms[j], ss[j], g, .01)
                q = signal(mf[j], ms[j], sf[j], ss[j], arm)
            elif arm == 5:
                q = constants[j]
            gates[t, j] = q
            if observer:
                continue
            if arm == 0:
                update = lr * g
            else:
                m[j], v[j], direction = adam_step(m[j], v[j], g, t + 1, beta2)
                update = lr * (1. + gain * q) * direction
            w[j] -= update
            squared_update += update * update
        norms[t] = np.sqrt(squared_update)
    return predictions, gates, norms


def run(y, arm, config, constants=None, observer=False):
    """Observations only: no targets, condition names, noise strata or event indices."""
    y = np.asarray(y, dtype=np.float64)
    if y.ndim != 2 or not len(y) or not np.isfinite(y).all():
        raise ValueError('finite nonempty observation matrix required')
    if constants is None:
        constants = np.zeros(y.shape[1])
    constants = np.asarray(constants, dtype=np.float64)
    if constants.shape != (y.shape[1],) or not np.isfinite(constants).all():
        raise ValueError('one finite constant per coordinate required')
    return _run(y, IDS[arm], float(config['lr']), float(config.get('beta2', .999)),
                float(config.get('gain', 0.)), constants, bool(observer))


def warmup():
    for arm in IDS:
        for observer in (False, True):
            run(np.ones((2, 4)), arm, {'lr': .01, 'gain': 1.}, observer=observer)
