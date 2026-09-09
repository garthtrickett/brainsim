"""Broader-benchmark ramps; steep, shallow and noisy drift the candidate never saw."""
import numpy as np

from v3_persistent import fixture as persistent_fixture
from v3_slice1_streams import BURN, Fixture, STEPS, rng

FIXTURES = ('core', 'mixed', 'steep', 'shallow', 'noisy')
ORDINAL = {'core': 0, 'mixed': 1, 'steep': 2, 'shallow': 3, 'noisy': 4}


def ramp_fixture(seed, name, start, end, high, low, sigma, domain):
    target = np.ones((STEPS, 1))
    target[start:end, 0] = np.linspace(high, low, end-start, endpoint=False)
    target[end:] = low
    noise = rng(seed, domain).normal(size=(STEPS, 1))
    events = ((start, 'drift_start'), (end, 'drift_end'))
    return Fixture(name, target+sigma*noise, target, (name,), (events,))


def fixture(seed, name='core'):
    if name in ('core', 'mixed'):
        return persistent_fixture(seed, name)
    schedule = rng(seed, 0)
    first = int(schedule.integers(1800, 2201))
    if name == 'steep':
        return ramp_fixture(seed, name, first, first+500, 1., -1., .05, 31)
    if name == 'shallow':
        end = min(first+4000, STEPS-1)
        return ramp_fixture(seed, name, first, end, .5, -.5, .05, 32)
    if name == 'noisy':
        second = int(schedule.integers(3800, 4201))
        return ramp_fixture(seed, name, first, second, 1., -1., .5, 33)
    raise ValueError('unknown fixture')


def ramp_metrics(data, predictions, norms):
    result = {}
    for i, name in enumerate(data.coordinates):
        error = predictions[:, i]-data.target[:, i]
        excess = error**2
        start, end = data.events[i][0][0], data.events[i][1][0]
        stable = np.arange(STEPS) >= BURN
        result[name] = {
            'excess_mse': float(excess[BURN:].mean()),
            'prediction_mse': float(((predictions[:, i]-data.y[:, i])**2)[BURN:].mean()),
            'post_mse': None,
            'stable_mse': float(excess[stable].mean()),
            'adaptation_latency': None,
            'adaptation_success': None,
            'gate_initial': 0.,
            'gate_settled': 0.,
            'multiplier_gate_sum': 0.,
            'windows': {},
            'ramp_mse': float(excess[start:end].mean()),
        }
    return {'coordinates': result, 'update_norm_mean': float(np.mean(norms)),
            'update_norm_sum': float(np.sum(norms))}


def random_uniforms(seed, fixture_ordinal, steps, width):
    return np.column_stack([np.random.default_rng(np.random.SeedSequence(
        [seed, 156000+fixture_ordinal, j])).random(steps) for j in range(width)])
