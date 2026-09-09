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



def decision_checks():
    import copy
    import json
    from pathlib import Path
    import tempfile
    from unittest.mock import patch
    from v3_slice1_decisions import (KEYS, PROTOCOL, contrast, detector_cell, detector_decision,
                                     digest, expected_stages, performance_decision, tuning_screen)
    from v3_slice1_learning import ARMS, GATED
    from study_v3_slice1 import diagnostics, require_detection, verified_manifest

    def raises(fn):
        try:
            fn()
        except (ValueError, KeyError, FileNotFoundError):
            return
        raise AssertionError('expected prerequisite/data rejection')

    # Synthetic scores exercise the decision code without sampling study streams.
    rows = {key: {'status': 'ok', 'metrics': {'coordinates': {
        c: {'excess_mse': float(1 + abs(int(key.split('/')[1]) - 5))}
        for c in ('quiet', 'noisy', 'switch_quiet', 'switch_noisy')}}} for key in KEYS['tuning']}
    assert tuning_screen(rows)['status'] == 'eligible'

    def prefer(arm, index):
        altered = copy.deepcopy(rows)
        for s in SEEDS['tuning']:
            for c in altered[f'{arm}/{index}/{s}']['metrics']['coordinates'].values():
                c['excess_mse'] = .1
        return altered

    assert tuning_screen(prefer('candidate', 4))['status'] == 'tuning_negative'
    assert tuning_screen(prefer('candidate', 7))['status'] == 'tuning_inconclusive'
    # Exercise complete early-stop reporting using constructed rows, no study observations.
    from study_v3_slice1 import make_manifest, source_hashes, validate_registration, write
    from report_v3_slice1 import publish_report
    validate_registration()
    with tempfile.TemporaryDirectory() as temporary:
        directory = Path(temporary)
        constructed = prefer('candidate', 7)
        write(directory/'tuning.json', {'protocol': PROTOCOL, 'sources': source_hashes(), 'rows': constructed})
        write(directory/'manifest.json', make_manifest(constructed))
        (directory/'source-snapshots').mkdir()
        summary = publish_report(directory)
        assert summary['status'] == 'tuning_inconclusive' and summary['closed_scientifically']
        assert summary['counts']['tuning'] == 1920 and summary['counts']['performance'] == 0
        publish_report(directory, check=True)
        write(directory/'performance.json', {})
        raises(lambda: publish_report(directory))
    assert tuning_screen(prefer('single', 7))['status'] == 'tuning_inconclusive'
    assert tuning_screen(prefer('historical', 7))['status'] == 'eligible'
    assert tuning_screen(prefer('sgd', 0))['status'] == 'tuning_inconclusive'
    altered = copy.deepcopy(rows)
    for key in altered:
        if key.startswith('adam/'):
            altered[key] = {'status': 'nonfinite', 'reason': 'constructed divergence'}
    assert tuning_screen(altered)['status'] == 'tuning_inconclusive'
    altered = copy.deepcopy(rows); altered.pop(next(iter(altered)))
    raises(lambda: tuning_screen(altered))
    altered = copy.deepcopy(rows)
    next(iter(altered.values()))['metrics']['coordinates']['quiet']['excess_mse'] = float('nan')
    raises(lambda: tuning_screen(altered))
    assert detector_cell([4] * 32, [5] * 32, True)['pass']
    assert not detector_cell([3] * 32, [5] * 32, True)['pass']
    assert detector_cell([5] * 32, [100] * 32)['pass']
    assert not detector_cell([6] * 32, [100] * 32)['pass']
    raises(lambda: detector_cell([float('nan')], [1]))
    assert contrast([10.] * 32, [9.] * 32, True)['pass']
    assert not contrast([10.] * 32, [9.01] * 32, True)['pass']
    assert contrast([1.25] * 32, [1.375] * 32, False)['pass']
    assert not contrast([1.25] * 32, [1.376] * 32, False)['pass']

    def metric(kinds=(), hit=False):
        return {'block_count': 0, 'block_total': 50, 'events': [
            {'index': 2000 + 2000 * i, 'kind': k, 'hit': hit, 'latency': 0 if hit else 100}
            for i, k in enumerate(kinds)]}

    modes = {mode: {'core': {'quiet': metric(), 'noisy': metric(),
                            'switch_quiet': metric(('target_down', 'target_up'), True),
                            'switch_noisy': metric(('target_down', 'target_up'), True)},
                    'noise_jump': {'noise_jump': metric(('noise_increase', 'noise_decrease'))}}
             for mode in ('fixed', 'closed')}
    diagnostic = {key: {'status': 'ok', 'modes': copy.deepcopy(modes)} for key in KEYS['diagnostics']}
    assert detector_decision(diagnostic)['status'] == 'detector_pass'
    assert len(detector_decision(diagnostic)['cells']) == 16
    for seed in SEEDS['diagnostics']:
        diagnostic[f'candidate/{seed}']['modes']['closed']['noise_jump']['noise_jump']['events'][0]['hit'] = True
    assert detector_decision(diagnostic)['status'] == 'detector_negative'
    manifest = {'synthetic': True}
    with tempfile.TemporaryDirectory() as temporary:
        directory = Path(temporary)
        (directory/'manifest.json').write_text('{}')
        raises(lambda: diagnostics(directory))
        assert not (directory/'diagnostics.json').exists()
        decision = {'manifest_digest': digest(manifest), 'evidence_digest': digest(diagnostic),
                    **detector_decision(diagnostic)}
        (directory/'diagnostic-decision.json').write_text(json.dumps(decision))
        with patch('study_v3_slice1.load', return_value=diagnostic):
            raises(lambda: require_detection(directory, manifest))
        assert not (directory/'performance.json').exists()
    altered = copy.deepcopy(diagnostic)
    altered['candidate/33000']['modes']['closed']['core']['quiet']['block_total'] = 49
    raises(lambda: detector_decision(altered))

    performance = {}
    for key in KEYS['performance']:
        value = .5 if key.startswith('candidate/') else 1.
        coordinates = {'core': ('quiet', 'noisy', 'switch_quiet', 'switch_noisy'),
                       'noise_jump': ('noise_jump',), 'drift': ('drift',), 'exactly_quiet': ('exactly_quiet',)}
        performance[key] = {'status': 'ok', 'fixtures': {name: {'coordinates': {
            c: {'post_mse': value, 'excess_mse': value,
                'windows': {'noise_increase': value, 'noise_decrease': value, 'drift': value}}
            for c in names}} for name, names in coordinates.items()}}
    assert performance_decision(performance)['status'] == 'positive'
    for key in performance:
        if key.startswith('candidate/'):
            performance[key]['fixtures']['core']['coordinates']['switch_noisy']['post_mse'] = 4.
    assert performance_decision(performance)['status'] == 'learning_negative'
    for status in ('tuning_negative', 'tuning_inconclusive', 'detector_negative', 'positive', 'learning_negative'):
        assert expected_stages(status)[0] == 'tuning'
    raises(lambda: expected_stages('missing'))
    print('PASS slice1 decisions: boundary/tie/zero-gain screens, full cells, independent gates and forbidden stages', flush=True)


def archive_checks(directory):
    import hashlib
    import json
    from pathlib import Path
    from report_v3_slice1 import publish_report
    from study_v3_slice1 import SOURCES, require_committed
    summary = publish_report(directory, check=True)
    require_committed(directory/'manifest.json')
    for stage in summary['reached']:
        evidence = json.loads((directory/(stage + '.json')).read_text())
        for source, digest in evidence['sources'].items():
            snapshot = directory/'source-snapshots'/(digest + '.txt')
            assert hashlib.sha256(snapshot.read_bytes()).hexdigest() == digest, source
            assert hashlib.sha256(Path(source).read_bytes()).hexdigest() == digest, source
        assert set(evidence['sources']) == set(SOURCES)
        print('PASS slice1 archive', stage, len(evidence['rows']), 'rows', flush=True)
    return summary


def reproduce(directory, summary):
    import json
    from pathlib import Path
    import tempfile
    from check_v3_gate import compare
    from study_v3_slice1 import (calibration_row, diagnostic_row, make_manifest,
                                 performance_row, source_hashes, tuning_row)
    from v3_slice1_decisions import PROTOCOL, detector_decision, scientific, tuning_screen
    from v3_slice1_learning import GRIDS, warmup
    from report_v3_slice1 import publish_report
    warmup()
    expected_manifest = json.loads((directory/'manifest.json').read_text())
    actual_rows = {}
    with tempfile.TemporaryDirectory(prefix='brainsim-slice1-reproduction-') as temporary:
        out = Path(temporary)
        for stage in summary['reached']:
            expected = json.loads((directory/(stage + '.json')).read_text())
            rows = {}
            for key, wanted in expected['rows'].items():
                pieces = key.split('/')
                arm, seed = pieces[0], int(pieces[-1])
                if stage == 'tuning':
                    row = tuning_row(seed, arm, GRIDS[arm][int(pieces[1])])
                elif stage == 'calibration':
                    row = calibration_row(seed, arm, expected_manifest['screen']['selected'][arm])
                elif stage == 'diagnostics':
                    row = diagnostic_row(seed, arm, expected_manifest)
                else:
                    row = performance_row(seed, arm, expected_manifest)
                compare(scientific(wanted), scientific(row), stage + '/' + key)
                rows[key] = row
            actual_rows[stage] = rows
            (out/(stage + '.json')).write_text(json.dumps({'protocol': PROTOCOL, 'sources': source_hashes(), 'rows': rows}))
            print('PASS slice1 reproduction', stage, len(rows), 'scientific rows', flush=True)
        actual_manifest = make_manifest(actual_rows['tuning'], actual_rows.get('calibration'))
        # Recomputed scientific input digests may differ within numerical tolerance.
        for key in expected_manifest.keys() - {'tuning_digest', 'calibration_digest'}:
            compare(expected_manifest[key], actual_manifest[key], 'manifest/' + key)
        (out/'manifest.json').write_text(json.dumps(actual_manifest))
        from v3_slice1_decisions import digest
        for stage in ('diagnostics', 'performance'):
            if stage in actual_rows:
                for row in actual_rows[stage].values():
                    row['manifest_digest'] = digest(actual_manifest)
                path = out/(stage + '.json')
                envelope = json.loads(path.read_text())
                envelope['rows'] = actual_rows[stage]
                path.write_text(json.dumps(envelope))
        if 'diagnostics' in actual_rows:
            from v3_slice1_decisions import digest
            (out/'diagnostic-decision.json').write_text(json.dumps({
                'manifest_digest': digest(actual_manifest), 'evidence_digest': digest(actual_rows['diagnostics']),
                **detector_decision(actual_rows['diagnostics'])}))
        (out/'source-snapshots').mkdir()
        actual_summary = publish_report(out)
        for stage, decision in summary['decisions'].items():
            wanted = {k: v for k, v in decision.items() if k not in ('manifest_digest', 'evidence_digest')}
            actual = {k: v for k, v in actual_summary['decisions'][stage].items()
                      if k not in ('manifest_digest', 'evidence_digest')}
            compare(wanted, actual, 'decision/' + stage)
        for key in ('status', 'screen', 'counts', 'reached', 'not_run', 'closed_scientifically'):
            compare(summary[key], actual_summary[key], 'summary/' + key)
    print('PASS full reached-stage reproduction; unapproved stages were not sampled', flush=True)


def main():
    import argparse
    from pathlib import Path
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--evidence', type=Path)
    parser.add_argument('--reproduce', action='store_true')
    args = parser.parse_args()
    instrument_checks()
    learning_checks()
    decision_checks()
    if args.reproduce and args.evidence is None:
        parser.error('--reproduce requires --evidence')
    if args.evidence:
        summary = archive_checks(args.evidence)
        if args.reproduce:
            reproduce(args.evidence, summary)


if __name__ == '__main__':
    main()
