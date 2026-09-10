"""Distance-adaptive OLS windows; short at kinks, long mid-ramp."""
import numpy as np

from v3_adwin import column
from v3_forgetting import run as forget_run, window_kernel
from v3_retention import request_schedule
from v3_slope import ols_fit

FAST = {'keep': 4, 'window': 32}
ESTIMATOR = {'method': 'ols', 'W': 128}
FAMILIES = ('win', 'window', 'sgd', 'adwin')
ARMS = FAMILIES + ('reference', 'random_win', 'oracle_nofallback')
GRIDS = {'win': [{'W_near': n, 'W_far': f, 'S': s} for n in (4, 8) for f in (64, 128, 256) for s in (16, 32)],
         'window': [{'window': w} for w in (1, 2, 4, 8, 16, 32, 64, 128, 256, 512, 1024, 6000)],
         'sgd': [{'lr': lr} for lr in (.0001, .0004, .001, .004, .008, .016,
                                       .035743040182210514, .064, .128, .256, .512, 1.)],
         'adwin': [{'delta': d, 'clock': c} for d in (.0001, .001, .01, .1) for c in (1, 8, 32)]}


def random_uniforms(seed, fixture_ordinal, steps, width):
    return np.column_stack([np.random.default_rng(np.random.SeedSequence(
        [seed, 196000+fixture_ordinal, j])).random(steps) for j in range(width)])


def adaptive_predictions(values, widths):
    """OLS forecast per step at its own window; strictly causal."""
    length = len(values)
    prediction, slopes = np.zeros(length), np.zeros(length)
    for t in range(length):
        width = int(widths[t])
        start = t-width if t-width > 0 else 0
        count = t-start
        if count == 0:
            continue
        if count == 1:
            prediction[t] = values[t-1]
            continue
        slope, intercept = ols_fit(values, start, count)
        prediction[t] = intercept+slope*count
        slopes[t] = slope
    return prediction, slopes


def adaptive_updated(values, widths):
    """Post-ingest OLS forecast per step at its own window; strictly causal."""
    length = len(values)
    index = np.arange(length)
    start = np.maximum(index+1-widths, 0)
    count = index+1-start
    padded = np.concatenate(([0.], np.cumsum(values)))
    timed = np.concatenate(([0.], np.cumsum(index*values)))
    sum_y = padded[index+1]-padded[start]
    sum_xy = timed[index+1]-timed[start]-start*sum_y
    sum_x = count*(count-1)/2.
    sum_xx = (count-1)*count*(2*count-1)/6.
    denominator = np.where(count > 1, count*sum_xx-sum_x*sum_x, 1.)
    slope = np.where(count > 1, (count*sum_xy-sum_x*sum_y)/denominator, 0.)
    intercept = np.where(count > 1, (sum_y-slope*sum_x)/count, sum_y)
    return intercept+slope*count, slope


def compose(y, resets, enter, schedule):
    fast_pred, _, _, fast_widths, fast_removed = window_kernel(
        y, resets, FAST['keep'], FAST['window'])
    slow_pred, slow_updated = np.zeros_like(y), np.zeros_like(y)
    slow_widths = np.zeros(y.shape, dtype=np.int64)
    slow_removed = np.zeros(y.shape, dtype=np.int64)
    for j in range(y.shape[1]):
        slow_pred[:, j], slow_updated[:, j], _, slow_widths[:, j], slow_removed[:, j] = column(
            y[:, j], .1, 1)
    est_pred, est_slope, win_trace = np.zeros_like(y), np.zeros_like(y), np.zeros_like(y)
    est_updated = np.zeros_like(y)
    for j in range(y.shape[1]):
        est_pred[:, j], est_slope[:, j] = adaptive_predictions(y[:, j], schedule[:, j])
        est_updated[:, j], _ = adaptive_updated(y[:, j], schedule[:, j])
        win_trace[:, j] = schedule[:, j]
    fast_updated = np.empty_like(y)
    for j in range(y.shape[1]):
        cumulative = np.concatenate(([0.], np.cumsum(y[:, j])))
        begin = np.arange(len(y))-fast_widths[:, j]+1
        fast_updated[:, j] = (cumulative[1:]-cumulative[begin])/fast_widths[:, j]
    steps = np.arange(len(y))[:, None]
    first = np.where(resets > 0, steps, -1)
    last = np.empty_like(first)
    last[0] = -1
    last[1:] = np.maximum.accumulate(first[:-1], axis=0)
    within = np.where(last >= 0, steps-last, np.inf) <= 32
    entered = np.where(enter > 0, steps, -1)
    exited = np.where((resets > 0) & (enter == 0), steps, -1)
    previous_entered = np.empty_like(entered)
    previous_entered[0] = -1
    previous_entered[1:] = np.maximum.accumulate(entered[:-1], axis=0)
    previous_exited = np.empty_like(exited)
    previous_exited[0] = -1
    previous_exited[1:] = np.maximum.accumulate(exited[:-1], axis=0)
    in_slope = previous_entered > previous_exited
    predictions = np.where(in_slope, est_pred, np.where(within, fast_pred, slow_pred))
    updated = np.where(in_slope, est_updated, np.where(within, fast_updated, slow_updated))
    norms = np.sqrt(np.sum((updated-predictions)**2, axis=1))
    regime = np.where(in_slope, 2, np.where(within, 1, 0)).astype(np.int64)
    trace = np.where(in_slope, est_slope, 0.)
    return predictions, resets, norms, fast_widths, fast_removed, slow_widths, slow_removed, regime, trace, win_trace


def width_schedule(y, resets, near, far, distance):
    steps = np.arange(len(y))[:, None]
    first = np.where(resets > 0, steps, -1)
    last = np.empty_like(first)
    last[0] = -1
    last[1:] = np.maximum.accumulate(first[:-1], axis=0)
    elapsed = np.where(last >= 0, steps-last, np.inf)
    return np.where(elapsed <= distance, near, far)


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
    if arm == 'reference':
        if dict(config) != dict(ESTIMATOR):
            raise ValueError('frozen slope configuration required')
        widths = None
    else:
        try:
            near, far, distance = int(config['W_near']), int(config['W_far']), int(config['S'])
        except (KeyError, TypeError):
            raise ValueError('window-schedule configuration required')
        if min(near, far) < 2 or distance < 0 or type(config.get('W_near')) is not int or type(config.get('W_far')) is not int or type(config.get('S')) is not int:
            raise ValueError('invalid window schedule')
        widths = None
    if arm == 'random_win':
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
    if arm == 'reference':
        widths = np.full_like(y, ESTIMATOR['W'], dtype=np.int64)
    else:
        widths = width_schedule(y, resets, near, far, distance)
    return compose(y, resets, enter, widths)[:9] + (widths,)
