"""Scientific invariants for slice1; later phases extend this same check."""
import numpy as np

from v3_slice1_streams import (BURN, SEEDS, diagnostic_metrics, fixture,
                               learning_metrics, maxima, recovery, rng)


def instrument_checks():
    partitions = list(SEEDS.values())
    assert all(not set(a) & set(b) for i, a in enumerate(partitions) for b in partitions[i + 1:])
    # Prior study's complete registered seed ranges do not overlap this study.
    prior = set(range(8)) | set(range(1000, 1008)) | set(range(2000, 2032))
    assert not prior & set().union(*map(set, partitions))
    data = fixture(30000)
    first, second = [e[0] for e in data.events[2]]
    assert 1800 <= first <= 2200 and 3800 <= second <= 4200
    assert data.y.shape == (6000, 4)
    np.testing.assert_array_equal(data.y, fixture(30000).y)
    np.testing.assert_array_equal(data.target[first:second, 2:], -np.ones((second - first, 2)))
    np.testing.assert_array_equal(data.target[:, :2], np.ones((6000, 2)))
    for i, sigma in enumerate((.05, 1., .05, 1.)):
        np.testing.assert_allclose((data.y[:, i] - data.target[:, i]) / sigma,
                                    rng(30000, i + 1).normal(size=6000), atol=1e-13)
    noise = fixture(30000, 'noise_jump')
    np.testing.assert_array_equal(noise.target, np.ones((6000, 1)))
    assert noise.events[0] == ((first, 'noise_increase'), (second, 'noise_decrease'))
    drift = fixture(30000, 'drift')
    assert drift.target[first, 0] == 1. and drift.target[second, 0] == -1.
    np.testing.assert_array_equal(fixture(30000, 'exactly_quiet').y, np.ones((6000, 1)))
    # Squaring a sign-reflected observation destroys the distinction exactly.
    samples = 1. + np.array([-2., -.5, 0., .5, 2.])
    np.testing.assert_array_equal(samples ** 2, (-samples) ** 2)
    predictions = data.target.copy()
    predictions[[first, second], 2:] *= -1.
    scored = learning_metrics(data, predictions, np.zeros_like(data.y), np.zeros(6000))
    for name in ('switch_quiet', 'switch_noisy'):
        row = scored['coordinates'][name]
        assert row['post_mse'] == .02 and row['stable_mse'] == 0.
        assert row['adaptation_latency'] == 1. and row['adaptation_success'] == 1.
    error = np.ones(6000)
    assert recovery(error, first) == (1000, False)
    error[first + 7:first + 17] = .1
    assert recovery(error, first) == (7, True)
    gates = np.zeros_like(data.y)
    gates[first + 3, 2] = .5
    metrics = diagnostic_metrics(data, gates, .4)['switch_quiet']
    assert metrics['events'][0]['latency'] == 3 and metrics['events'][1]['latency'] == 100
    assert metrics['block_count'] == 1 and metrics['block_total'] == 50
    assert diagnostic_metrics(data, gates, .5)['switch_quiet']['point_count'] == 0
    np.testing.assert_array_equal(maxima(np.arange(200)), [99, 199])
    # Noise-direction scoring does not pool the two windows.
    prediction = noise.target.copy()
    prediction[first:first + 200] += 2.
    scored = learning_metrics(noise, prediction, np.zeros_like(prediction), np.zeros(6000))
    assert scored['coordinates']['noise_jump']['windows'] == {'noise_increase': 4., 'noise_decrease': 0.}
    print('PASS slice1 instruments: RNG isolation, event labels, causal scoring, censoring and noise directions', flush=True)



def learning_checks():
    from v3_gate import adam_step, variance_step
    from v3_slice1_learning import ARMS, GRIDS, IDS, run, signal
    assert all(len(grid) == 24 for grid in GRIDS.values())
    # Explicit two-step Adam reference independent of the runner.
    m, v, direction = adam_step(0., 0., 2., 1, .999)
    np.testing.assert_allclose((m, v, direction), (.2, .004, 2. / (2. + 1e-8)))
    m, v, direction = adam_step(m, v, -1., 2, .999)
    np.testing.assert_allclose((m, v, direction),
                              (.08, .004996, (.08 / .19) / (np.sqrt(.004996 / .001999) + 1e-8)))
    xs = np.array([3., -2., 5., 1.])
    for rate in (.1, .01):
        mean, variance, weights = xs[0], 0., np.array([1.])
        for i, x in enumerate(xs[1:], 1):
            mean, variance = variance_step(mean, variance, x, rate)
            weights = np.append(weights * (1. - rate), rate)
            expected = weights @ xs[:i + 1]
            np.testing.assert_allclose(mean, expected)
            np.testing.assert_allclose(variance, weights @ (xs[:i + 1] - expected) ** 2)
    assert signal(1., 1., 2., 3., 4) == 0.
    assert 0. <= signal(2., 1., 0., 0., 4) <= 1.
    y = rng(30001, 1).normal(size=(250, 4))
    config = {'lr': .016, 'gain': 4.}
    plain = run(y, 'adam', config)[0]
    for arm in ('single', 'historical', 'candidate'):
        np.testing.assert_array_equal(plain, run(y, arm, {'lr': .016, 'gain': 0.})[0])
    for arm in IDS:
        pred, gates, norms = run(y, arm, config)
        assert np.isfinite(pred).all() and np.isfinite(gates).all() and np.isfinite(norms).all()
        later = y.copy(); later[90:] += 100.
        other, other_gates, _ = run(later, arm, config)
        np.testing.assert_array_equal(pred[:91], other[:91])
        np.testing.assert_array_equal(gates[:90], other_gates[:90])
        changed = y.copy(); changed[:, 0] += 100.
        other, other_gates, _ = run(changed, arm, config)
        np.testing.assert_array_equal(pred[:, 1:], other[:, 1:])
        np.testing.assert_array_equal(gates[:, 1:], other_gates[:, 1:])
        # A standalone coordinate and the same coordinate in a joint run agree.
        isolated = run(y[:, 2:3], arm, config)[0]
        np.testing.assert_array_equal(pred[:, 2], isolated[:, 0])
        np.testing.assert_array_equal(pred, run(y, arm, config)[0])
    q = run(y, 'candidate', config, observer=True)[1]
    np.testing.assert_array_equal(q, run(-y, 'candidate', config, observer=True)[1])
    np.testing.assert_allclose(q, run(y + 7., 'candidate', config, observer=True)[1], atol=1e-13)
    assert np.all((q >= 0.) & (q <= 1.))
    for arm in ARMS:
        assert all(np.isfinite(x).all() for x in run(np.ones((200, 1)), arm, config))
    scalar = np.array([[2.], [10.], [99.]])
    np.testing.assert_array_equal(run(scalar, 'sgd', {'lr': .5})[0][:, 0], [0., 1., 5.5])
    print('PASS slice1 updates: equations, invariances, pre-update causality, no coordinate/arm state leakage', flush=True)


if __name__ == '__main__':
    instrument_checks()
    learning_checks()
