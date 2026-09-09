"""Evaluator-owned fixtures and metrics for the registered slice1 experiment."""
from dataclasses import dataclass

import numpy as np

STEPS, BURN, BLOCK = 6000, 1000, 100
COORDINATES = ('quiet', 'noisy', 'switch_quiet', 'switch_noisy')
FIXTURES = ('core', 'noise_jump', 'drift', 'exactly_quiet')
SEEDS = {'development': tuple(range(30000, 30008)),
         'calibration': tuple(range(31000, 31016)),
         'tuning': tuple(range(32000, 32016)),
         'diagnostics': tuple(range(33000, 33032)),
         'performance': tuple(range(34000, 34032))}


@dataclass(frozen=True)
class Fixture:
    name: str
    y: np.ndarray
    target: np.ndarray
    coordinates: tuple
    events: tuple  # Per-coordinate tuples of (index, kind); evaluator only.


def rng(seed, domain):
    return np.random.default_rng(np.random.SeedSequence([seed, domain]))


def fixture(seed, name='core'):
    schedule = rng(seed, 0)
    first = int(schedule.integers(1800, 2201))
    second = int(schedule.integers(3800, 4201))
    changes = ((first, 'target_down'), (second, 'target_up'))
    if name == 'core':
        target = np.ones((STEPS, 4))
        target[first:second, 2:] = -1.
        noise = np.column_stack([rng(seed, i + 1).normal(size=STEPS) for i in range(4)])
        y = target + noise * np.array([.05, 1., .05, 1.])
        return Fixture(name, y, target, COORDINATES, ((), (), changes, changes))
    if name not in FIXTURES:
        raise ValueError(name)
    target = np.ones((STEPS, 1))
    sigma = np.full((STEPS, 1), .05)
    if name == 'noise_jump':
        sigma[first:second] = 1.
        events = ((first, 'noise_increase'), (second, 'noise_decrease'))
        domain = 11
    elif name == 'drift':
        target[first:second, 0] = np.linspace(1., -1., second - first, endpoint=False)
        target[second:] = -1.
        events = ((first, 'drift_start'), (second, 'drift_end'))
        domain = 12
    else:
        sigma[:] = 0.
        events, domain = (), 13
    y = target + sigma * rng(seed, domain).normal(size=(STEPS, 1))
    return Fixture(name, y, target, (name,), (events,))


def maxima(values):
    values = np.asarray(values)
    if values.ndim != 1 or len(values) % BLOCK:
        raise ValueError('whole one-dimensional blocks required')
    return values.reshape(-1, BLOCK).max(axis=1)


def recovery(error, start):
    good = np.abs(error[start:start + 1000]) < .2
    hits = np.flatnonzero(np.convolve(good.astype(int), np.ones(10, dtype=int), 'valid') == 10)
    return int(hits[0]) if len(hits) else 1000, bool(len(hits))


def learning_metrics(data, predictions, gates, norms):
    result = {}
    for i, name in enumerate(data.coordinates):
        error = predictions[:, i] - data.target[:, i]
        excess = error ** 2
        post = np.zeros(STEPS, dtype=bool)
        recoveries, windows = [], {}
        for start, kind in data.events[i]:
            if kind.startswith('target_'):
                post[start:start + 200] = True
                recoveries.append(recovery(error, start))
            elif kind.startswith('noise_'):
                windows[kind] = float(excess[start:start + 200].mean())
        if name == 'drift':
            windows['drift'] = float(excess[data.events[i][0][0]:data.events[i][1][0]].mean())
        stable = (np.arange(STEPS) >= BURN) & ~post
        result[name] = {
            'excess_mse': float(excess[BURN:].mean()),
            'prediction_mse': float(((predictions[:, i] - data.y[:, i]) ** 2)[BURN:].mean()),
            'post_mse': float(excess[post].mean()) if post.any() else None,
            'stable_mse': float(excess[stable].mean()),
            'adaptation_latency': float(np.mean([r[0] for r in recoveries])) if recoveries else None,
            'adaptation_success': float(np.mean([r[1] for r in recoveries])) if recoveries else None,
            'gate_initial': float(gates[:BURN, i].mean()),
            'gate_settled': float(gates[BURN:, i].mean()),
            'multiplier_gate_sum': float(gates[:, i].sum()), 'windows': windows,
        }
    return {'coordinates': result, 'update_norm_mean': float(np.mean(norms)),
            'update_norm_sum': float(np.sum(norms))}


def diagnostic_metrics(data, gates, threshold):
    if not np.isfinite(threshold) or not np.isfinite(gates).all():
        raise ValueError('non-finite diagnostic input')
    result = {}
    for i, name in enumerate(data.coordinates):
        values = gates[:, i]
        alarms = values > threshold
        events = []
        for start, kind in data.events[i]:
            hits = np.flatnonzero(alarms[start:start + BLOCK])
            events.append({'index': start, 'kind': kind, 'hit': bool(len(hits)),
                           'latency': int(hits[0]) if len(hits) else BLOCK})
        result[name] = {'gate_initial': float(values[:BURN].mean()),
                        'gate_mean': float(values[BURN:].mean()),
                        'point_count': int(alarms[BURN:].sum()), 'point_total': STEPS - BURN,
                        'block_count': int((maxima(values[BURN:]) > threshold).sum()),
                        'block_total': (STEPS - BURN) // BLOCK, 'events': events}
    return result
