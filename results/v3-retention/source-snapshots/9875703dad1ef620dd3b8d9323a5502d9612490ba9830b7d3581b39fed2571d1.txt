"""Standalone supervised V3 instrument; no brainsim imports or task metadata in updates."""
import numpy as np
from numba import njit

STEPS = 6000
BURN = 1000
SWITCHES = (2000, 4000)
WINDOW = 100
LEARNING = ('quiet', 'noisy', 'switch_quiet', 'switch_noisy')
DIAGNOSTIC = LEARNING + ('drift', 'noise_jump')
CALIBRATION_SEEDS = tuple(range(8))
TUNING_SEEDS = tuple(range(1000, 1008))
CONFIRMATION_SEEDS = tuple(range(2000, 2032))
RATES = (.004, .016, .064, .256)
GRIDS = {
    'sgd': [{'lr': x} for x in
            (.001, .002, .004, .008, .016, .032, .064, .128, .256, .512, .768, 1.)],
    'adam': [{'lr': x, 'beta2': b} for x in RATES for b in (.9, .99, .999)],
    'single': [{'lr': x, 'gain': k} for x in RATES for k in (1., 4., 16.)],
    'dual': [{'lr': x, 'gain': k} for x in RATES for k in (1., 4., 16.)],
}
ARM_IDS = {'sgd': 0, 'adam': 1, 'single': 2, 'dual': 3}


def stream(seed, condition):
    """Only the evaluator retains theta. All learners get the same paired noise."""
    if condition not in DIAGNOSTIC:
        raise ValueError(condition)
    theta = np.ones(STEPS)
    sigma = np.full(STEPS, 1. if 'noisy' in condition else .05)
    if condition.startswith('switch_'):
        theta[2000:4000] = -1.
    elif condition == 'drift':
        theta[2000:4000] = np.linspace(1., -1., 2000, endpoint=False)
        theta[4000:] = -1.
    elif condition == 'noise_jump':
        sigma[2000:4000] = 1.
    y = theta + sigma * np.random.default_rng(seed).standard_normal(STEPS)
    return y, theta


@njit(cache=True)
def variance_step(mean, variance, x, rate):
    delta = x - mean
    return mean + rate * delta, (1. - rate) * (variance + rate * delta * delta)


@njit(cache=True)
def adam_step(m, v, g, t, beta2):
    m = .9 * m + .1 * g
    v = beta2 * v + (1. - beta2) * g * g
    direction = (m / (1. - .9 ** t)) / (np.sqrt(v / (1. - beta2 ** t)) + 1e-8)
    return m, v, direction


@njit(cache=True)
def gate_value(fast, slow, dual):
    if dual:
        return max(0., fast - slow) / (fast + slow + 1e-8)
    return fast / (fast + 1.)


@njit(cache=True)
def simulate(y, arm, lr, beta2=.999, gain=0.):
    """Causal pre-update predictions. No target or switch metadata accepted."""
    predictions = np.empty(len(y))
    gates = np.zeros(len(y))
    w = m = v = mf = ms = sf = ss = 0.
    for i in range(len(y)):
        predictions[i] = w
        g = w - y[i]
        if arm >= 2:
            if i == 0:
                mf = ms = g
            else:
                mf, sf = variance_step(mf, sf, g, .1)
                if arm == 3:
                    ms, ss = variance_step(ms, ss, g, .01)
            gates[i] = gate_value(sf, ss, arm == 3)
        if arm == 0:
            w -= lr * g
        else:
            m, v, direction = adam_step(m, v, g, i + 1, beta2)
            w -= lr * (1. + gain * gates[i]) * direction
    return predictions, gates


@njit(cache=True)
def fixed_gates(y):
    values = np.zeros((2, len(y)))
    mf = ms = -y[0]
    sf = ss = 0.
    for i in range(1, len(y)):
        mf, sf = variance_step(mf, sf, -y[i], .1)
        ms, ss = variance_step(ms, ss, -y[i], .01)
        values[0, i] = gate_value(sf, ss, False)
        values[1, i] = gate_value(sf, ss, True)
    return values


def block_maxima(values):
    values = np.asarray(values)
    if len(values) % WINDOW:
        raise ValueError('whole blocks required')
    return values.reshape(-1, WINDOW).max(axis=1)


def adaptation(errors, switches=SWITCHES):
    latencies = []
    successes = []
    for start in switches:
        good = np.abs(errors[start:start + 1000]) < .2
        consecutive = np.convolve(good.astype(int), np.ones(10, dtype=int), mode='valid')
        hits = np.flatnonzero(consecutive == 10)
        latencies.append(int(hits[0]) if len(hits) else 1000)
        successes.append(bool(len(hits)))
    return float(np.mean(latencies)), float(np.mean(successes))


def learning_metrics(y, theta, predictions, gates, switching):
    error = predictions - theta
    excess = error ** 2
    post = np.zeros(len(y), dtype=bool)
    if switching:
        for start in SWITCHES:
            post[start:start + 200] = True
    stable = np.arange(len(y)) >= BURN
    stable &= ~post
    latency, success = adaptation(error) if switching else (None, None)
    return {
        'excess_mse': float(excess[BURN:].mean()),
        'prediction_mse': float(((predictions - y) ** 2)[BURN:].mean()),
        'post_mse': float(excess[post].mean()) if switching else None,
        'stable_mse': float(excess[stable].mean()),
        'adaptation_latency': latency, 'adaptation_success': success,
        'gate_initial': float(gates[:BURN].mean()),
        'gate_settled': float(gates[BURN:].mean()),
    }


def diagnostic_metrics(values, threshold, events=()):
    alarm = values > threshold
    latency = []
    for start in events:
        hits = np.flatnonzero(alarm[start:start + WINDOW])
        latency.append(int(hits[0]) if len(hits) else WINDOW)
    return {
        'gate_mean': float(values[BURN:].mean()),
        'point_alarm_rate': float(alarm[BURN:].mean()),
        'block_alarm_rate': float((block_maxima(values[BURN:]) > threshold).mean()),
        'event_hit_rate': float(np.mean(np.array(latency) < WINDOW)) if events else None,
        'event_latency': float(np.mean(latency)) if events else None,
    }


def paired(control, treatment):
    """Positive differences mean more error/latency, not favorable wins."""
    control, treatment = np.asarray(control), np.asarray(treatment)
    delta = treatment - control
    indices = np.random.default_rng(20260909).integers(0, len(delta), (10000, len(delta)))
    interval = np.quantile(delta[indices].mean(axis=1), [.025, .975])
    return {'control': float(control.mean()), 'treatment': float(treatment.mean()),
            'delta': float(delta.mean()), 'interval95': interval.tolist(),
            'lower_error_seeds': int((delta < 0).sum()), 'n': len(delta)}
