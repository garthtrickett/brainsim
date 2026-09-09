"""Scientific unit checks and archived/reproduced standalone-study validation."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile

import numpy as np

from study_v3_gate import SOURCES, scientific, selection_from
from v3_gate import (ARM_IDS, BURN, CALIBRATION_SEEDS, CONFIRMATION_SEEDS,
                     GRIDS, LEARNING, TUNING_SEEDS, adaptation, adam_step,
                     block_maxima, diagnostic_metrics, fixed_gates, gate_value,
                     learning_metrics, simulate, stream, variance_step)


def unit_checks():
    # Independent two-step Adam calculation, including both bias corrections.
    m, v, direction = adam_step(0., 0., 2., 1, .999)
    np.testing.assert_allclose((m, v, direction), (.2, .004, 2. / (2. + 1e-8)))
    m, v, direction = adam_step(m, v, -1., 2, .999)
    np.testing.assert_allclose((m, v, direction),
                              (.08, .004996, (.08 / .19) / (np.sqrt(.004996 / .001999) + 1e-8)))
    # Centered EMA recurrence agrees with explicit exponentially decaying weights.
    xs = np.array([3., -2., 5., 5., 1.])
    for rate in (.1, .01):
        mean, variance = xs[0], 0.
        weights = np.array([1.])
        for i, x in enumerate(xs[1:], 1):
            mean, variance = variance_step(mean, variance, x, rate)
            weights = np.append(weights * (1. - rate), rate)
            expected_mean = weights @ xs[:i + 1]
            np.testing.assert_allclose(mean, expected_mean)
            np.testing.assert_allclose(variance, weights @ ((xs[:i + 1] - expected_mean) ** 2))
    assert gate_value(1., 2., True) == 0.
    assert 0. < gate_value(2., 1., True) < 1.
    assert np.all(fixed_gates(np.ones(200)) == 0.)
    noise_gates = fixed_gates(np.random.default_rng(9999).normal(size=6000))
    assert noise_gates[1, BURN:].mean() > 0., 'stationary rectification is not zero'

    y = np.random.default_rng(9876).normal(size=200)
    adam, _ = simulate(y, 1, .016, .999, 0.)
    for arm in (2, 3):
        gated, _ = simulate(y, arm, .016, .999, 0.)
        np.testing.assert_array_equal(adam, gated)
    # Prediction precedes observing y; future suffix cannot affect earlier outputs.
    for arm in ARM_IDS.values():
        pred, gates = simulate(y, arm, .016, .999, 4.)
        changed = y.copy()
        changed[90:] += 100.
        other, other_gates = simulate(changed, arm, .016, .999, 4.)
        np.testing.assert_array_equal(pred[:91], other[:91])
        np.testing.assert_array_equal(gates[:90], other_gates[:90])
        assert pred[0] == 0.
    pred, _ = simulate(np.array([2., 10., 99.]), 0, .5, .999, 0.)
    np.testing.assert_array_equal(pred, [0., 1., 5.5])
    # Streams and common random numbers: optimizer never receives these labels.
    for seed in (9998,):
        quiet, theta = stream(seed, 'quiet')
        noisy, _ = stream(seed, 'noisy')
        np.testing.assert_allclose((quiet - theta) / .05, noisy - theta, atol=1e-13)
        switched, target = stream(seed, 'switch_quiet')
        np.testing.assert_allclose(switched - target, quiet - theta, atol=1e-13)
        assert target[1999] == target[4000] == 1. and target[2000] == -1.
    # Include the first, necessarily wrong pre-update switch prediction.
    theta = np.ones(6000)
    theta[2000:4000] = -1.
    prediction = theta.copy()
    prediction[[2000, 4000]] *= -1.
    metrics = learning_metrics(theta, theta, prediction, np.zeros(6000), True)
    assert metrics['post_mse'] == .02 and metrics['stable_mse'] == 0.
    assert metrics['adaptation_latency'] == 1. and metrics['adaptation_success'] == 1.
    errors = np.ones(6000)
    assert adaptation(errors) == (1000., 0.)
    errors[2010:2020] = .1
    assert adaptation(errors) == (505., .5)
    np.testing.assert_array_equal(block_maxima(np.arange(200)), [99, 199])
    values = np.zeros(6000)
    values[2003] = 1.
    measured = diagnostic_metrics(values, .5, (2000, 4000))
    assert measured['event_hit_rate'] == .5 and measured['event_latency'] == 51.5
    assert measured['block_alarm_rate'] == 1 / 50
    assert diagnostic_metrics(values, 1.)['block_alarm_rate'] == 0., 'strict threshold'
    seeds = [set(s) for s in (CALIBRATION_SEEDS, TUNING_SEEDS, CONFIRMATION_SEEDS)]
    assert all(not a & b for i, a in enumerate(seeds) for b in seeds[i + 1:])
    assert all(len(configs) == 12 for configs in GRIDS.values())
    print('PASS v3 update equations, causality, controls, metrics and seed budgets', flush=True)


def compare(expected, actual, path=''):
    if isinstance(expected, dict):
        assert expected.keys() == actual.keys(), path
        for key in expected:
            compare(expected[key], actual[key], path + '/' + key)
    elif isinstance(expected, list):
        assert len(expected) == len(actual), path
        for i, (a, b) in enumerate(zip(expected, actual)):
            compare(a, b, path + '/' + str(i))
    elif isinstance(expected, (int, float)):
        np.testing.assert_allclose(actual, expected, rtol=1e-11, atol=1e-13, err_msg=path)
    else:
        assert actual == expected, (path, expected, actual)


def archives(directory):
    expected_keys = {
        'calibration': {str(s) for s in CALIBRATION_SEEDS},
        'tuning': {f'{a}/{i}/{s}' for a in GRIDS for i in range(12) for s in TUNING_SEEDS},
        'diagnostic': {str(s) for s in CONFIRMATION_SEEDS},
        'confirmation': {f'{a}/{s}' for a in GRIDS for s in CONFIRMATION_SEEDS},
    }
    data = {}
    for stage, keys in expected_keys.items():
        data[stage] = json.loads((directory/(stage + '.json')).read_text())
        assert set(data[stage]['rows']) == keys, stage
        # Numpy allclose rejects non-finite floats against a finite placeholder.
        def finite(value):
            if isinstance(value, dict):
                for child in value.values(): finite(child)
            elif isinstance(value, list):
                for child in value: finite(child)
            elif isinstance(value, float):
                assert np.isfinite(value), stage
        finite(data[stage])
        for source, digest in data[stage]['sources'].items():
            snapshot = directory/'source-snapshots'/(digest + '.txt')
            assert hashlib.sha256(snapshot.read_bytes()).hexdigest() == digest, source
            # Current study sources must reproduce the archived implementation.
            assert hashlib.sha256(Path(source).read_bytes()).hexdigest() == digest, source
        assert set(SOURCES).issubset(data[stage]['sources'])
        print('PASS v3 archive', stage, len(keys), 'rows', flush=True)
    selection = json.loads((directory/'selection.json').read_text())
    assert selection == selection_from(data['calibration'], data['tuning'])
    return data, selection


def reproduce(directory, expected, selection):
    with tempfile.TemporaryDirectory(prefix='brainsim-v3-') as temporary:
        out = Path(temporary)/'evidence'
        log = Path(temporary)/'reproduce.log'
        import sys
        with log.open('w') as handle:
            for stage in ('prepare', 'confirm'):
                result = subprocess.run([sys.executable, 'study_v3_gate.py', stage,
                                         '--out-dir', str(out)], stdout=handle, stderr=subprocess.STDOUT)
                if result.returncode:
                    raise RuntimeError(log.read_text()[-5000:])
        actual, reproduced_selection = archives(out)
        for stage in expected:
            compare(scientific(expected[stage]['rows']), scientific(actual[stage]['rows']), stage)
        # Input-row hashes can differ under tolerated floating-point roundoff.
        for key in ('thresholds', 'selected', 'tuning_objectives', 'protocol'):
            compare(selection[key], reproduced_selection[key], key)
    print('PASS complete v3 reproduction (rtol 1e-11; atol 1e-13; runtime excluded)', flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--evidence', type=Path)
    parser.add_argument('--reproduce', action='store_true')
    args = parser.parse_args()
    unit_checks()
    if args.reproduce and args.evidence is None:
        parser.error('--reproduce requires --evidence')
    if args.evidence:
        data, selection = archives(args.evidence)
        if args.reproduce:
            reproduce(args.evidence, data, selection)


if __name__ == '__main__':
    main()
