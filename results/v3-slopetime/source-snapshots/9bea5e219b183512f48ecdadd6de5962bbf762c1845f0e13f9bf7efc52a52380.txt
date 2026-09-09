"""Horizon-gated slope regime on observed alarms; estimator and base frozen."""
import numpy as np

from v3_adwin import column
from v3_forgetting import run as forget_run, window_kernel
from v3_retention import FAST, dual_run, request_schedule
from v3_slope import ols_column

ESTIMATOR = {'method': 'ols', 'W': 128}
FAMILIES = ('slope_adwin', 'window', 'sgd', 'adwin')
ARMS = FAMILIES + ('reference', 'random_slope', 'oracle_nofallback')
GRIDS = {'slope_adwin': [{'Hs': h} for h in (16, 32, 64, 128, 256, 512, 1024, 2048, 3000, 4000, 5000, 6000)],
         'window': [{'window': w} for w in (1, 2, 4, 8, 16, 32, 64, 128, 256, 512, 1024, 6000)],
         'sgd': [{'lr': lr} for lr in (.0001, .0004, .001, .004, .008, .016,
                                       .035743040182210514, .064, .128, .256, .512, 1.)],
         'adwin': [{'delta': d, 'clock': c} for d in (.0001, .001, .01, .1) for c in (1, 8, 32)]}


def random_uniforms(seed, fixture_ordinal, steps, width):
    return np.column_stack([np.random.default_rng(np.random.SeedSequence(
        [seed, 146000+fixture_ordinal, j])).random(steps) for j in range(width)])


def compose(y, alarms, horizon):
    """Fast wins within 32 steps of an alarm; slope fills to the horizon."""
    fast_pred, _, _, fast_widths, fast_removed = window_kernel(
        y, alarms, FAST['keep'], FAST['window'])
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
    marks = np.where(alarms > 0, steps, -1)
    last = np.empty_like(marks)
    last[0] = -1
    last[1:] = np.maximum.accumulate(marks[:-1], axis=0)
    distance = np.where(last >= 0, steps-last, np.inf)
    fast = distance <= 32
    in_slope = (distance <= horizon) & ~fast
    fast_updated = np.empty_like(y)
    for j in range(y.shape[1]):
        cumulative = np.concatenate(([0.], np.cumsum(y[:, j])))
        begin = np.arange(len(y))-fast_widths[:, j]+1
        fast_updated[:, j] = (cumulative[1:]-cumulative[begin])/fast_widths[:, j]
    predictions = np.where(in_slope, est_pred, np.where(fast, fast_pred, slow_pred))
    updated = np.where(in_slope, est_updated, np.where(fast, fast_updated, slow_updated))
    norms = np.sqrt(np.sum((updated-predictions)**2, axis=1))
    regime = np.where(in_slope, 2, np.where(fast, 1, 0)).astype(np.int64)
    trace = np.where(in_slope, est_slope, 0.)
    return predictions, alarms, norms, fast_widths, fast_removed, slow_widths, slow_removed, regime, trace


def run(y, arm, config, *, schedule=None, uniforms=None, probability=None):
    y = np.asarray(y, dtype=np.float64)
    if y.ndim != 2 or not y.shape[0] or not y.shape[1] or not np.isfinite(y).all():
        raise ValueError('finite nonempty observations required')
    if arm not in ARMS:
        raise ValueError('unknown policy')
    if (schedule is not None or uniforms is not None) and arm in ('window', 'sgd', 'adwin'):
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
    if arm in ('slope_adwin', 'random_slope'):
        try:
            horizon = config['Hs']
        except (KeyError, TypeError):
            raise ValueError('horizon configuration required')
        if type(horizon) is not int or horizon < 1:
            raise ValueError('invalid horizon')
    elif dict(config) != dict(ESTIMATOR):
        raise ValueError('frozen estimator configuration required')
    if arm == 'random_slope':
        uniforms = np.asarray(uniforms)
        if uniforms.shape != y.shape or not np.isfinite(uniforms).all() or np.any((uniforms < 0) | (uniforms >= 1)):
            raise ValueError('valid independent uniforms required')
        if probability is None or not np.isfinite(probability) or not 0 <= probability <= 1:
            raise ValueError('valid frozen probability required')
        resets = request_schedule((uniforms < probability).astype(float), 16)
    else:
        if schedule is None:
            raise ValueError('evaluator schedule required')
        schedule = np.asarray(schedule)
        if schedule.shape != y.shape or not np.isfinite(schedule).all() or np.any((schedule != 0) & (schedule != 1)):
            raise ValueError('binary evaluator schedule required')
        resets = schedule
    if arm == 'reference':
        return dual_run(y, resets, .1, 32)
    return compose(y, resets, horizon)
