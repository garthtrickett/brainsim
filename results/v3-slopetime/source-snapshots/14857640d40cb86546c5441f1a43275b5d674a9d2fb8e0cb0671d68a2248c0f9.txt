"""Observations-only persistent detectors; evaluator-owned mixed-change fixture."""
import numpy as np
from numba import njit

from v3_gate import adam_step, variance_step
from v3_slice1_learning import run as old_run, signal
from v3_slice1_streams import Fixture, STEPS, fixture as old_fixture, rng

DETECTORS = ('current', 'persistence', 'candidate', 'cusum')
FIXTURES = ('core', 'noise_jump', 'drift', 'exactly_quiet', 'mixed')
CONFIGS = {**{a: {'lr': .004, 'gain': 64., 'beta2': .999} for a in DETECTORS},
           'sgd': {'lr': .035743040182210514}, 'adam': {'lr': .032, 'beta2': .9999},
           'single': {'lr': .016, 'gain': 1.}, 'constant': {'lr': .004, 'gain': 64., 'beta2': .999}}


def fixture(seed, name='core'):
    if name != 'mixed':
        return old_fixture(seed, name)
    schedule = rng(seed, 0)
    first, second = int(schedule.integers(1800, 2201)), int(schedule.integers(3800, 4201))
    target = np.ones((STEPS, 2))
    target[first:second] = -1.
    sigma = np.tile(np.array([.05, 1.]), (STEPS, 1))
    sigma[first:second] = [1., .05]
    noise = np.column_stack([rng(seed, d).normal(size=STEPS) for d in (21, 22)])
    events = ((first, 'target_down'), (second, 'target_up'))
    return Fixture(name, target + sigma*noise, target,
                   ('increase_first', 'decrease_first'), (events, events))


@njit(cache=True)
def directional_min(values):
    positive, negative = True, True
    smallest = np.inf
    for value in values:
        if not np.isfinite(value):
            return np.nan
        positive = positive and value > 0.
        negative = negative and value < 0.
        smallest = min(smallest, abs(value))
    return smallest if positive or negative else 0.


@njit(cache=True)
def window_stats(history, t, j):
    recent, reference = 0., 0.
    for k in range(16):
        recent += history[(t-k) % 144, j]
    for k in range(16, 144):
        reference += history[(t-k) % 144, j]
    recent /= 16.
    reference /= 128.
    vr, vb = 0., 0.
    for k in range(16):
        vr += (history[(t-k) % 144, j] - recent)**2
    for k in range(16, 144):
        vb += (history[(t-k) % 144, j] - reference)**2
    return recent, reference, vr/15., vb/127.


@njit(cache=True)
def cusum_step(positive, negative, innovation):
    return max(0., positive + innovation - .5), max(0., negative - innovation - .5)


@njit(cache=True)
def kernel(y, arm, lr, gain, beta2, observer):
    n, width = y.shape
    predictions, gates, norms = np.zeros_like(y), np.zeros_like(y), np.zeros(n)
    w, m, v = np.zeros(width), np.zeros(width), np.zeros(width)
    mf, ms, sf, ss = np.zeros(width), np.zeros(width), np.zeros(width), np.zeros(width)
    history, scores = np.zeros((144, width)), np.zeros((4, width))
    cp, cn = np.zeros(width), np.zeros(width)
    for t in range(n):
        squared = 0.
        for j in range(width):
            predictions[t, j] = w[j]
            gradient = w[j] - y[t, j]
            history[t % 144, j] = gradient
            q = 0.
            if arm < 2:
                if t == 0:
                    mf[j] = ms[j] = gradient
                else:
                    mf[j], sf[j] = variance_step(mf[j], sf[j], gradient, .1)
                    ms[j], ss[j] = variance_step(ms[j], ss[j], gradient, .01)
                q = signal(mf[j], ms[j], sf[j], ss[j], 4)
                if not (np.isfinite(mf[j]) and np.isfinite(ms[j]) and np.isfinite(sf[j]) and np.isfinite(ss[j])):
                    q = np.nan
                if arm == 1:
                    scores[t % 4, j] = np.sign(mf[j]-ms[j])*np.sqrt(q)
                    q = directional_min(scores[:, j])**2 if t >= 3 else 0.
            elif t >= 143:
                recent, reference, vr, vb = window_stats(history, t, j)
                if not (np.isfinite(recent) and np.isfinite(reference) and np.isfinite(vr) and np.isfinite(vb)):
                    q = np.nan
                elif arm == 2:
                    scores[t % 4, j] = (recent-reference)/np.sqrt(vr/16. + vb/128. + 1e-8)
                    a = directional_min(scores[:, j])
                    q = a*a/(a*a+16.)
                else:
                    innovation = (gradient-reference)/np.sqrt(max(vr, vb)+1e-8)
                    cp[j], cn[j] = cusum_step(cp[j], cn[j], innovation)
                    c = max(cp[j], cn[j])
                    q = c/(c+16.)
            gates[t, j] = q
            if not observer:
                m[j], v[j], direction = adam_step(m[j], v[j], gradient, t+1, beta2)
                update = lr*(1.+gain*q)*direction
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
    return kernel(y, DETECTORS.index(arm), float(config['lr']), float(config['gain']),
                  float(config.get('beta2', .999)), bool(observer))


def warmup():
    for arm in DETECTORS:
        run(np.ones((150, 1)), arm)
