"""Kink-guarded trend regime; fast mean owns boundaries, trend owns mid-ramp."""
import numpy as np

from v3_adwin import column
from v3_forgetting import run as forget_run, window_kernel
from v3_retention import request_schedule
from v3_slope import ols_column

FAST = {'keep': 4, 'window': 32}
ESTIMATOR = {'method': 'ols', 'W': 128}
FAMILIES = ('guard', 'window', 'sgd', 'adwin')
ARMS = FAMILIES + ('reference', 'random_guard', 'oracle_nofallback')
GRIDS = {'guard': [{'J': j} for j in (0, 48, 64, 96, 128, 192, 256, 384, 512, 1024, 2048, 6000)],
         'window': [{'window': w} for w in (1, 2, 4, 8, 16, 32, 64, 128, 256, 512, 1024, 6000)],
         'sgd': [{'lr': lr} for lr in (.0001, .0004, .001, .004, .008, .016,
                                       .035743040182210514, .064, .128, .256, .512, 1.)],
         'adwin': [{'delta': d, 'clock': c} for d in (.0001, .001, .01, .1) for c in (1, 8, 32)]}


def random_uniforms(seed, fixture_ordinal, steps, width):
    return np.column_stack([np.random.default_rng(np.random.SeedSequence(
        [seed, 166000+fixture_ordinal, j])).random(steps) for j in range(width)])


def compose(y, resets, enter, guard):
    fast_pred, _, _, fast_widths, fast_removed = window_kernel(
        y, resets, FAST['keep'], FAST['window'])
    slow_pred, slow_updated = np.zeros_like(y), np.zeros_like(y)
    slow_widths = np.zeros(y.shape, dtype=np.int64)
    slow_removed = np.zeros(y.shape, dtype=np.int64)
    for j in range(y.shape[1]):
        slow_pred[:, j], slow_updated[:, j], _, slow_widths[:, j], slow_removed[:, j] = column(
            y[:, j], .1, 1)
    est_pred, est_updated, est_slope = np.zeros_like(y), np.zeros_like(y), np.zeros_like(y)
    for j in range(y.shape[1]):
        est_pred[:, j], est_updated[:, j], est_slope[:, j] = ols_column(y[:, j], ESTIMATOR['W'])
    steps = np.arange(len(y))[:, None]
    first = np.where(resets > 0, steps, -1)
    last = np.empty_like(first)
    last[0] = -1
    last[1:] = np.maximum.accumulate(first[:-1], axis=0)
    distance = np.where(last >= 0, steps-last, np.inf)
    entered = np.where(enter > 0, steps, -1)
    exited = np.where((resets > 0) & (enter == 0), steps, -1)
    previous_entered = np.empty_like(entered)
    previous_entered[0] = -1
    previous_entered[1:] = np.maximum.accumulate(entered[:-1], axis=0)
    previous_exited = np.empty_like(exited)
    previous_exited[0] = -1
    previous_exited[1:] = np.maximum.accumulate(exited[:-1], axis=0)
    in_segment = previous_entered > previous_exited
    guarded = in_segment & (distance <= guard) if guard else np.zeros_like(in_segment)
    in_slope = in_segment & ~guarded
    fast = ~in_segment & (distance <= 32)
    fast_updated = np.empty_like(y)
    for j in range(y.shape[1]):
        cumulative = np.concatenate(([0.], np.cumsum(y[:, j])))
        begin = np.arange(len(y))-fast_widths[:, j]+1
        fast_updated[:, j] = (cumulative[1:]-cumulative[begin])/fast_widths[:, j]
    predictions = np.where(in_slope, est_pred, fast_pred)
    updated = np.where(in_slope, est_updated, fast_updated)
    slow_only = ~(in_slope | guarded | fast)
    predictions = np.where(slow_only, slow_pred, predictions)
    updated = np.where(slow_only, slow_updated, updated)
    norms = np.sqrt(np.sum((updated-predictions)**2, axis=1))
    regime = np.where(in_slope, 2, np.where(guarded, 3, np.where(fast, 1, 0))).astype(np.int64)
    trace = np.where(in_slope, est_slope, 0.)
    return predictions, resets, norms, fast_widths, fast_removed, slow_widths, slow_removed, regime, trace


def run(y, arm, config, *, schedule=None, enter=None, uniforms=None, probability=None):
    y = np.asarray(y, dtype=np.float64)
    if y.ndim != 2 or not y.shape[0] or not y.shape[1] or not np.isfinite(y).all():
        raise ValueError('finite nonempty observations required')
    if arm not in ARMS:
        raise ValueError('unknown policy')
    if (schedule is not None or enter is not None or uniforms is not None) and arm in ('window', 'sgd', 'adwin'):
        raise ValueError('evaluator schedule forbidden for y-only controls')
    if arm in ('window', 'sgd', 'adwin'):
        return forget_run(y, arm, config)
    if arm == 'oracle_nofallback':
        if dict(config) != dict(FAST):
            raise ValueError('fixed fast base required')
        if schedule is None:
            raise ValueError('evaluator schedule required')
        schedule = np.asarray(schedule)
        if schedule.shape != y.shape or not np.isfinite(schedule).all() or np.any((schedule != 0) & (schedule != 1)):
            raise ValueError('binary evaluator schedule required')
        return forget_run(y, 'oracle_matched', dict(FAST), triggers=schedule)
    if arm in ('guard', 'random_guard', 'reference'):
        if arm == 'reference':
            guard = 0
            if dict(config) != {'J': 0}:
                raise ValueError('reference is the no-guard policy')
        else:
            try:
                guard = config['J']
            except (KeyError, TypeError):
                raise ValueError('guard configuration required')
            if type(guard) is not int or guard < 0:
                raise ValueError('invalid guard horizon')
    if arm == 'random_guard':
        uniforms = np.asarray(uniforms)
        if uniforms.shape != y.shape or not np.isfinite(uniforms).all() or np.any((uniforms < 0) | (uniforms >= 1)):
            raise ValueError('valid independent uniforms required')
        if probability is None or not np.isfinite(probability) or not 0 <= probability <= 1:
            raise ValueError('valid frozen probability required')
        resets = request_schedule((uniforms < probability).astype(float), 16)
        enter = np.zeros_like(resets)
    else:
        if schedule is None or enter is None:
            raise ValueError('evaluator schedule required')
        schedule = np.asarray(schedule)
        enter = np.asarray(enter)
        for array in (schedule, enter):
            if array.shape != y.shape or not np.isfinite(array).all() or np.any((array != 0) & (array != 1)):
                raise ValueError('binary evaluator schedule required')
        if np.any(enter > schedule):
            raise ValueError('entries must be requests')
        resets = schedule
    return compose(y, resets, enter, guard if arm != 'reference' else 0)
