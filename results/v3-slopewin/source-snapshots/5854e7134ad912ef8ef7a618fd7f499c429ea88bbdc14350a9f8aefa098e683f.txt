"""Trend estimators for drift regimes; OLS windows and Holt recursions, causal only."""
import numpy as np
from numba import njit

from v3_adwin import column
from v3_forgetting import run as forget_run, window_kernel
from v3_retention import request_schedule


@njit(cache=True)
def ols_fit(values, start, count):
    """Slope and intercept on local x=0..count-1; requires count>=2."""
    sum_x = count*(count-1)/2.
    sum_xx = (count-1)*count*(2*count-1)/6.
    sum_y, sum_xy = 0., 0.
    for i in range(count):
        value = values[start+i]
        sum_y += value
        sum_xy += i*value
    denominator = count*sum_xx-sum_x*sum_x
    slope = (count*sum_xy-sum_x*sum_y)/denominator
    return slope, (sum_y-slope*sum_x)/count


@njit(cache=True)
def ols_column(values, width):
    length = len(values)
    prediction, updated, slopes = np.zeros(length), np.zeros(length), np.zeros(length)
    for t in range(length):
        start = t-width if t-width > 0 else 0
        count = t-start
        if count == 0:
            updated[t] = values[t]
            continue
        if count == 1:
            prediction[t], updated[t] = values[t-1], values[t]
            continue
        slope, intercept = ols_fit(values, start, count)
        prediction[t] = intercept+slope*count
        slopes[t] = slope
        start2 = t+1-width if t+1-width > 0 else 0
        count2 = t+1-start2
        slope2, intercept2 = ols_fit(values, start2, count2)
        updated[t] = intercept2+slope2*count2
    return prediction, updated, slopes


@njit(cache=True)
def holt_column(values, alpha, beta):
    length = len(values)
    prediction, updated, slopes = np.zeros(length), np.zeros(length), np.zeros(length)
    level, trend = values[0], 0.
    updated[0] = level
    for t in range(1, length):
        prediction[t] = level+trend
        slopes[t] = trend
        previous = level
        level = alpha*values[t]+(1.-alpha)*(level+trend)
        trend = beta*(level-previous)+(1.-beta)*trend
        updated[t] = level+trend
    return prediction, updated, slopes


FAST = {'keep': 4, 'window': 32}
DELTA, HORIZON = .1, 32
FAMILIES = ('slope', 'window', 'sgd', 'adwin')
ARMS = FAMILIES + ('oracle_nofallback', 'random_slope')
YONLY = ('window', 'sgd', 'adwin')
GRIDS = {'slope': [{'method': 'ols', 'W': w} for w in (8, 16, 32, 64, 128, 256)] +
                  [{'method': 'holt', 'alpha': a, 'beta': b} for a, b in
                   ((.3, .1), (.5, .2), (.8, .3), (.2, .05), (.5, .05), (.8, .1))],
         'window': [{'window': w} for w in (1, 2, 4, 8, 16, 32, 64, 128, 256, 512, 1024, 6000)],
         'sgd': [{'lr': lr} for lr in (.0001, .0004, .001, .004, .008, .016,
                                       .035743040182210514, .064, .128, .256, .512, 1.)],
         'adwin': [{'delta': d, 'clock': c} for d in (.0001, .001, .01, .1) for c in (1, 8, 32)]}


def random_uniforms(seed, fixture_ordinal, steps, width):
    return np.column_stack([np.random.default_rng(np.random.SeedSequence(
        [seed, 136000+fixture_ordinal, j])).random(steps) for j in range(width)])


def compose(y, resets, enter, config):
    """Fast/ADWIN/slope composition; requests apply after scoring.

    Entries are entry-requests, exits are non-entry requests; disjoint by
    fixture construction, so no index is ever both. Entries-only input stays
    in slope (no exits exist); exits cut the regime from the next step.
    """
    fast_pred, _, _, fast_widths, fast_removed = window_kernel(
        y, resets, FAST['keep'], FAST['window'])
    slow_pred, slow_updated = np.zeros_like(y), np.zeros_like(y)
    slow_widths = np.zeros(y.shape, dtype=np.int64)
    slow_removed = np.zeros(y.shape, dtype=np.int64)
    for j in range(y.shape[1]):
        slow_pred[:, j], slow_updated[:, j], _, slow_widths[:, j], slow_removed[:, j] = column(
            y[:, j], DELTA, 1)
    if config['method'] == 'ols':
        width = config['W']
        run_column = lambda v: ols_column(v, width)
    else:
        alpha, beta = config['alpha'], config['beta']
        run_column = lambda v: holt_column(v, alpha, beta)
    est_pred, est_updated, est_slope = np.zeros_like(y), np.zeros_like(y), np.zeros_like(y)
    for j in range(y.shape[1]):
        est_pred[:, j], est_updated[:, j], est_slope[:, j] = run_column(y[:, j])
    steps = np.arange(len(y))[:, None]
    first = np.where(resets > 0, steps, -1)
    last = np.empty_like(first)
    last[0] = -1
    last[1:] = np.maximum.accumulate(first[:-1], axis=0)
    within = np.where(last >= 0, steps-last, np.inf) <= HORIZON
    entered = np.where(enter > 0, steps, -1)
    exited = np.where((resets > 0) & (enter == 0), steps, -1)
    previous_entered = np.empty_like(entered)
    previous_entered[0] = -1
    previous_entered[1:] = np.maximum.accumulate(entered[:-1], axis=0)
    previous_exited = np.empty_like(exited)
    previous_exited[0] = -1
    previous_exited[1:] = np.maximum.accumulate(exited[:-1], axis=0)
    in_slope = previous_entered > previous_exited
    fast_updated = np.empty_like(y)
    for j in range(y.shape[1]):
        cumulative = np.concatenate(([0.], np.cumsum(y[:, j])))
        begin = np.arange(len(y))-fast_widths[:, j]+1
        fast_updated[:, j] = (cumulative[1:]-cumulative[begin])/fast_widths[:, j]
    predictions = np.where(in_slope, est_pred, np.where(within, fast_pred, slow_pred))
    updated = np.where(in_slope, est_updated, np.where(within, fast_updated, slow_updated))
    norms = np.sqrt(np.sum((updated-predictions)**2, axis=1))
    regime = np.where(in_slope, 2, np.where(within, 1, 0)).astype(np.int64)
    trace = np.where(in_slope, est_slope, 0.)
    return predictions, resets, norms, fast_widths, fast_removed, slow_widths, slow_removed, regime, trace


def run(y, arm, config, *, schedule=None, enter=None, uniforms=None, probability=None):
    y = np.asarray(y, dtype=np.float64)
    if y.ndim != 2 or not y.shape[0] or not y.shape[1] or not np.isfinite(y).all():
        raise ValueError('finite nonempty observations required')
    if arm not in ARMS:
        raise ValueError('unknown policy')
    if (schedule is not None or enter is not None or uniforms is not None) and arm in YONLY:
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
    try:
        method = config['method']
    except (KeyError, TypeError):
        raise ValueError('estimator configuration required')
    if method == 'ols':
        width = config.get('W')
        if type(width) is not int or width < 2:
            raise ValueError('invalid estimator window')
    elif method == 'holt':
        try:
            alpha, beta = float(config['alpha']), float(config['beta'])
        except (KeyError, TypeError):
            raise ValueError('invalid estimator rates')
        if not all(np.isfinite(v) and 0. < v < 1. for v in (alpha, beta)):
            raise ValueError('invalid estimator rates')
    else:
        raise ValueError('unknown estimator')
    if arm == 'random_slope':
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
    return compose(y, resets, enter, dict(config))
