"""Causal arithmetic-window learners with detector, oracle and random reset schedules."""
import numpy as np
from numba import njit

from v3_adwin import run as adwin_run
from v3_burst import START, THRESHOLD, pulse_schedule, random_probability, reference_gates
from v3_slice1_learning import run as plain_run

FAMILIES = ('forget', 'oracle', 'window', 'sgd', 'adwin')
ARMS = FAMILIES + ('oracle_matched', 'random', 'noreset_matched')
MENUS = [{'keep': k, 'window': w} for k in (1, 4, 16) for w in (32, 128, 512, 6000)]
GRIDS = {'forget': MENUS, 'oracle': [dict(c) for c in MENUS],
         'window': [{'window': w} for w in (1, 2, 4, 8, 16, 32, 64, 128, 256, 512, 1024, 6000)],
         'sgd': [{'lr': lr} for lr in (.0001, .0004, .001, .004, .008, .016,
                                     .035743040182210514, .064, .128, .256, .512, 1.)],
         'adwin': [{'delta': d, 'clock': c} for d in (.0001, .001, .01, .1) for c in (1, 8, 32)]}


def random_uniforms(seed, fixture_ordinal, steps, width):
    return np.column_stack([np.random.default_rng(np.random.SeedSequence(
        [seed, 86000+fixture_ordinal, j])).random(steps) for j in range(width)])


@njit(cache=True)
def window_kernel(y, resets, keep, cap):
    predictions, updates = np.zeros_like(y), np.zeros_like(y)
    widths, removed = np.zeros(y.shape, dtype=np.int64), np.zeros(y.shape, dtype=np.int64)
    for j in range(y.shape[1]):
        begin, total, estimate = 0, 0., 0.
        for t in range(len(y)):
            predictions[t, j] = estimate
            total += y[t, j]
            previous = begin
            new_begin = max(begin, t-cap+1)
            if resets[t, j] > 0:
                new_begin = max(new_begin, t-keep+1)
            for i in range(begin, new_begin): total -= y[i, j]
            begin = new_begin
            widths[t, j] = t-begin+1
            removed[t, j] = begin-previous
            estimate = total/widths[t, j]
            updates[t, j] = estimate-predictions[t, j]
    return predictions, resets, np.sqrt(np.sum(updates*updates, axis=1)), widths, removed


def run(y, arm, config, *, gates=None, triggers=None, uniforms=None, probability=None):
    y = np.asarray(y, dtype=np.float64)
    if y.ndim != 2 or not y.shape[0] or not y.shape[1] or not np.isfinite(y).all():
        raise ValueError('finite nonempty observations required')
    if arm not in ARMS:
        raise ValueError('unknown policy')
    if triggers is not None and arm not in ('oracle', 'oracle_matched'):
        raise ValueError('privileged triggers forbidden')
    zero = np.zeros_like(y)
    if arm == 'sgd':
        if not np.isfinite(config['lr']) or config['lr'] <= 0: raise ValueError('invalid rate')
        return (*plain_run(y, 'sgd', config), np.zeros(y.shape, dtype=np.int64), np.zeros(y.shape, dtype=np.int64))
    if arm == 'adwin':
        return adwin_run(y, config['delta'], config['clock'])
    cap, keep = config['window'], config.get('keep', config['window'])
    if type(cap) is not int or type(keep) is not int or not 1 <= keep <= cap:
        raise ValueError('positive integer keep<=window required')
    if arm in ('window', 'noreset_matched'):
        resets = zero
    elif arm == 'forget':
        gates = reference_gates(y) if gates is None else np.asarray(gates)
        if gates.shape != y.shape or not np.isfinite(gates).all() or np.any((gates < 0) | (gates > 1)):
            raise ValueError('invalid causal gate array')
        resets = pulse_schedule(gates, 1, True)[1]
    else:
        if arm == 'random':
            uniforms = np.asarray(uniforms)
            if uniforms.shape != y.shape or not np.isfinite(uniforms).all() or np.any((uniforms < 0) | (uniforms >= 1)):
                raise ValueError('valid independent uniforms required')
            if probability is None or not np.isfinite(probability) or not 0 <= probability <= 1:
                raise ValueError('valid frozen probability required')
            triggers = (uniforms < probability).astype(float)
        else:
            triggers = np.asarray(triggers)
            if triggers.shape != y.shape or not np.isfinite(triggers).all() or np.any((triggers != 0) & (triggers != 1)):
                raise ValueError('binary evaluator timing required')
        resets = pulse_schedule(triggers, 1, False)[1]
    return window_kernel(y, resets, keep, cap)
