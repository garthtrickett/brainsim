"""Oracle-gated fast-window/ADWIN2 fallback; no detector, schedule granted by evaluator."""
import numpy as np
from numba import njit

from v3_adwin import column, run as adwin_run
from v3_burst import random_probability
from v3_forgetting import run as forget_run, window_kernel

FAMILIES = ('retain', 'window', 'sgd', 'adwin')
ARMS = FAMILIES + ('oracle_nofallback', 'random_fallback')
FAST = {'keep': 4, 'window': 32}
GRIDS = {'retain': [{'delta': d, 'H': h} for d in (.001, .01, .1) for h in (32, 512, 2048, 6000)],
         'window': [{'window': w} for w in (1, 2, 4, 8, 16, 32, 64, 128, 256, 512, 1024, 6000)],
         'sgd': [{'lr': lr} for lr in (.0001, .0004, .001, .004, .008, .016,
                                       .035743040182210514, .064, .128, .256, .512, 1.)],
         'adwin': [{'delta': d, 'clock': c} for d in (.0001, .001, .01, .1) for c in (1, 8, 32)]}


def random_uniforms(seed, fixture_ordinal, steps, width):
    return np.column_stack([np.random.default_rng(np.random.SeedSequence(
        [seed, 106000+fixture_ordinal, j])).random(steps) for j in range(width)])


@njit(cache=True)
def request_schedule(signal, suppress):
    """Starts from t0; after each request suppress the next `suppress` updates.

    Unlike pulse_schedule this honors pre-146 opportunities, per the registered
    from-t0 random schedule. Oracle triggers pass through unsuppressed.
    """
    starts = np.zeros_like(signal)
    for j in range(signal.shape[1]):
        cooldown = 0
        for t in range(len(signal)):
            if cooldown:
                cooldown -= 1
                continue
            if signal[t, j] > 0.:
                starts[t, j] = 1.
                cooldown = suppress
    return starts


def dual_run(y, resets, delta, horizon):
    fast_pred, _, _, fast_widths, fast_removed = window_kernel(
        y, resets, FAST['keep'], FAST['window'])
    slow_pred, slow_updated = np.zeros_like(y), np.zeros_like(y)
    slow_widths = np.zeros(y.shape, dtype=np.int64)
    slow_removed = np.zeros(y.shape, dtype=np.int64)
    for j in range(y.shape[1]):
        slow_pred[:, j], slow_updated[:, j], _, slow_widths[:, j], slow_removed[:, j] = column(
            y[:, j], delta, 1)
    fast_updated = np.empty_like(y)
    for j in range(y.shape[1]):
        cumulative = np.concatenate(([0.], np.cumsum(y[:, j])))
        begin = np.arange(len(y))-fast_widths[:, j]+1
        fast_updated[:, j] = (cumulative[1:]-cumulative[begin])/fast_widths[:, j]
    first = np.arange(len(y))[:, None]
    marks = np.where(resets > 0, first, -1)
    last = np.empty_like(marks)
    last[0] = -1
    last[1:] = np.maximum.accumulate(marks[:-1], axis=0)
    within = np.where(last >= 0, first-last, np.inf) <= horizon
    predictions = np.where(within, fast_pred, slow_pred)
    updated = np.where(within, fast_updated, slow_updated)
    norms = np.sqrt(np.sum((updated-predictions)**2, axis=1))
    return predictions, resets, norms, fast_widths, fast_removed, slow_widths, slow_removed, within


def run(y, arm, config, *, triggers=None, uniforms=None, probability=None):
    y = np.asarray(y, dtype=np.float64)
    if y.ndim != 2 or not y.shape[0] or not y.shape[1] or not np.isfinite(y).all():
        raise ValueError('finite nonempty observations required')
    if arm not in ARMS:
        raise ValueError('unknown policy')
    if triggers is not None and arm not in ('retain', 'oracle_nofallback'):
        raise ValueError('privileged triggers forbidden')
    if arm in ('window', 'sgd', 'adwin'):
        return forget_run(y, arm, config)
    if arm == 'oracle_nofallback':
        if dict(config) != dict(FAST):
            raise ValueError('fixed fast base required')
        if triggers is None:
            raise ValueError('evaluator timing required')
        triggers = np.asarray(triggers)
        if triggers.shape != y.shape or not np.isfinite(triggers).all() or np.any((triggers != 0) & (triggers != 1)):
            raise ValueError('binary evaluator timing required')
        return forget_run(y, 'oracle_matched', dict(FAST), triggers=triggers)
    try:
        delta, horizon = float(config['delta']), config['H']
    except (KeyError, TypeError):
        raise ValueError('delta/H configuration required')
    if not np.isfinite(delta) or not 0. < delta < 1. or type(horizon) is not int or horizon < 1:
        raise ValueError('invalid fallback configuration')
    if arm == 'random_fallback':
        uniforms = np.asarray(uniforms)
        if uniforms.shape != y.shape or not np.isfinite(uniforms).all() or np.any((uniforms < 0) | (uniforms >= 1)):
            raise ValueError('valid independent uniforms required')
        if probability is None or not np.isfinite(probability) or not 0 <= probability <= 1:
            raise ValueError('valid frozen probability required')
        resets = request_schedule((uniforms < probability).astype(float), 16)
    else:
        if triggers is None:
            raise ValueError('evaluator timing required')
        triggers = np.asarray(triggers)
        if triggers.shape != y.shape or not np.isfinite(triggers).all() or np.any((triggers != 0) & (triggers != 1)):
            raise ValueError('binary evaluator timing required')
        resets = request_schedule(triggers, 0)
    return dual_run(y, resets, delta, horizon)
