"""Separate-reference equations, causal invariants, diagnostic rules and reproduction."""
import argparse
import copy
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile
from unittest.mock import patch

import numpy as np

from check_v3_gate import compare
from report_v3_reference import explanatory_summary, publish_report
from study_v3_reference import (SOURCES, calibration_row, diagnostic_result, diagnostic_row, diagnostics,
                                explanatory_events, make_manifest, performance, performance_row,
                                read_stage, registration_check, require_committed, require_detection,
                                simulation, source_hashes, write)
from v3_reference import CONFIGS, DETECTORS, FIXTURES, controlled_adam, fixture, run, warmup
from v3_reference_policy import (KEYS, PROTOCOL, SEEDS, contrast, detector_cell, detector_decision,
                                 digest, performance_decision, scientific)
from v3_persistent import run as persistent_run
from v3_slice1_learning import run as old_run
from v3_slice1_streams import rng


def rejects(fn):
    try:
        fn()
    except (ValueError, KeyError, FileNotFoundError, subprocess.CalledProcessError):
        return
    raise AssertionError('expected rejection')


def kernel_checks():
    registration_check()
    assert [len(KEYS[s]) for s in ('calibration', 'diagnostics', 'performance')] == [48, 96, 224]
    parts = list(SEEDS.values())
    assert all(min(s) >= 60000 and max(s) < 65000 for s in parts)
    assert all(not set(a)&set(b) for i, a in enumerate(parts) for b in parts[i+1:])
    # Independent scalar Adam calculation with externally supplied time-varying gates.
    observations = np.array([[2.], [-1.], [3.], [1.]])
    gates = np.array([[0.], [.2], [1.], [.1]])
    predictions, norms = [], []
    w, m, v = 0., 0., 0.
    for t, (y, q) in enumerate(zip(observations[:, 0], gates[:, 0]), 1):
        predictions.append(w)
        gradient = w-y
        m, v = .9*m+.1*gradient, .999*v+.001*gradient*gradient
        update = .004*(1+64*q)*(m/(1-.9**t))/(np.sqrt(v/(1-.999**t))+1e-8)
        w -= update; norms.append(abs(update))
    actual = controlled_adam(observations, gates, .004, 64., .999)
    np.testing.assert_allclose(actual[0][:, 0], predictions, rtol=1e-12, atol=1e-13)
    np.testing.assert_array_equal(actual[1], gates)
    np.testing.assert_allclose(actual[2], norms, rtol=1e-12, atol=1e-13)
    y = rng(60000, 31).normal(size=(400, 3)); y[220:] += 2.
    for actual, expected in zip(run(y, 'coupled'), persistent_run(y, 'candidate')):
        np.testing.assert_array_equal(actual, expected)
    watch = run(y, 'watch_adam')
    plain = old_run(y, 'adam', CONFIGS['watch_adam'])
    np.testing.assert_array_equal(watch[0], plain[0]); np.testing.assert_array_equal(watch[2], plain[2])
    expected_q = persistent_run(-(plain[0]-y), 'candidate', True)[1]
    np.testing.assert_array_equal(watch[1], expected_q)
    separate = run(y, 'separate')
    assert separate[1][146:].max() > 0.
    passive = persistent_run(y, 'candidate', True)
    np.testing.assert_array_equal(separate[1], passive[1])
    for config in ({'lr': .001, 'gain': 0., 'beta2': .99}, {'lr': .1, 'gain': 128., 'beta2': .9999}):
        np.testing.assert_array_equal(separate[1], run(y, 'separate', config=config)[1])
    for arm in DETECTORS:
        for a, b in zip(run(y, arm, True), passive): np.testing.assert_array_equal(a, b)
        prediction, q, norms = run(y, arm)
        assert all(np.isfinite(x).all() for x in (prediction, q, norms))
        later = y.copy(); later[300:] *= -5.
        p2, q2, _ = run(later, arm)
        np.testing.assert_array_equal(prediction[:301], p2[:301])
        np.testing.assert_array_equal(q[:300], q2[:300])
        other = y.copy(); other[:, 0] += 10.
        np.testing.assert_array_equal(prediction[:, 1:], run(other, arm)[0][:, 1:])
        np.testing.assert_array_equal(q[:, 1:], run(other, arm)[1][:, 1:])
        np.testing.assert_array_equal(prediction[:, 1], run(y[:, 1:2], arm)[0][:, 0])
        np.testing.assert_array_equal(q[:, 1], run(y[:, 1:2], arm)[1][:, 0])
        zero = {**CONFIGS[arm], 'gain': 0.}
        np.testing.assert_array_equal(run(y, arm, config=zero)[0], old_run(y, 'adam', zero)[0])
    rejects(lambda: run(np.array([[np.nan]]), 'separate'))
    rejects(lambda: run(np.ones((2, 1)), 'unknown'))
    # Evaluator-only event windows and complete recovery run at the 100-step boundary.
    data = fixture(60001)
    first = data.events[2][0][0]
    prediction = data.target.copy()
    prediction[first:first+90, 2] += 1.
    gates = np.zeros_like(data.y); gates[first+4, 2] = .7
    event = explanatory_events(data, prediction, gates)['switch_quiet'][0]
    assert event['recovery_latency'] == 90 and event['recovered_within_100']
    assert event['mse_after20'] == 1. and event['mse_after100'] == .9 and event['mse_after200'] == .45
    assert event['mse_before100'] == 0. and event['q_max100'] == .7 and event['error_at_event'] == 1.
    prediction[first+90, 2] += 1.
    event = explanatory_events(data, prediction, gates)['switch_quiet'][0]
    assert event['recovery_latency'] == 91 and not event['recovered_within_100']
    prediction[first:first+1000, 2] = data.target[first:first+1000, 2]+1.
    event = explanatory_events(data, prediction, gates)['switch_quiet'][0]
    assert event['recovery_latency'] == 1000 and not event['recovery_success']
    print('PASS reference kernels: exact coupled/Adam parity, independent update equations, signal independence, causality and recovery windows', flush=True)


def synthetic():
    coordinates = {'core': ('quiet', 'noisy', 'switch_quiet', 'switch_noisy'),
                   'mixed': ('increase_first', 'decrease_first'), 'noise_jump': ('noise_jump',),
                   'drift': ('drift',), 'exactly_quiet': ('exactly_quiet',)}
    calibration = {key: {'status': 'ok', 'modes': {m: {'maxima': {c: [.5]*50 for c in ('quiet', 'noisy')},
                    'gate_means': [.1, .2, .3, .4]} for m in ('fixed', 'closed')}} for key in KEYS['calibration']}

    def metric(kinds=(), hit=False):
        return {'block_count': 0, 'block_total': 50, 'point_count': 0, 'point_total': 5000,
                'gate_initial': 0., 'gate_mean': .1, 'events': [
                    {'index': 2000+2000*i, 'kind': k, 'hit': hit, 'latency': 0 if hit else 100}
                    for i, k in enumerate(kinds)]}

    modes = {m: {'core': {'quiet': metric(), 'noisy': metric(),
                          'switch_quiet': metric(('target_down', 'target_up'), True),
                          'switch_noisy': metric(('target_down', 'target_up'), True)},
                  'noise_jump': {'noise_jump': metric(('noise_increase', 'noise_decrease'))},
                  'mixed': {c: metric(('target_down', 'target_up'), True) for c in coordinates['mixed']},
                  'drift': {'drift': metric()}, 'exactly_quiet': {'exactly_quiet': metric()}}
             for m in ('fixed', 'closed')}

    def learning(value):
        return {name: {'update_norm_mean': .1, 'update_norm_sum': 600., 'coordinates': {
            c: {'excess_mse': value, 'post_mse': value if (name == 'mixed' or c.startswith('switch_')) else None,
                'stable_mse': value, 'adaptation_latency': 20., 'gate_settled': .1,
                'windows': {'noise_increase': value, 'noise_decrease': value, 'drift': value}}
            for c in coords}} for name, coords in coordinates.items()}

    events = {m: {name: {c: [
        {'index': 2000+2000*i, 'kind': k, 'q_max100': .8, 'error_at_event': 2., 'mse_before100': .01,
         'mse_after20': .2, 'mse_after100': .1, 'mse_after200': .05, 'recovery_latency': 20,
         'recovery_success': True, 'recovered_within_100': True} for i, k in enumerate(('target_down', 'target_up'))]
         if name == 'mixed' or c.startswith('switch_') else [] for c in coords}
         for name, coords in coordinates.items()} for m in ('fixed', 'closed')}
    diagnostic = {key: {'status': 'ok', 'modes': copy.deepcopy(modes), 'common_modes': copy.deepcopy(modes),
                        'learning': {m: learning(1.) for m in ('fixed', 'closed')},
                        'explanatory_events': copy.deepcopy(events)} for key in KEYS['diagnostics']}
    performance = {key: {'status': 'ok', 'fixtures': learning(.5 if key.startswith('separate/') else 1.)}
                   for key in KEYS['performance']}
    return calibration, diagnostic, performance


def store_stage(directory, stage, rows):
    write(directory/(stage+'.json'), {'protocol': PROTOCOL, 'sources': source_hashes(), 'rows': rows})


def explanatory_checks(rows):
    data = copy.deepcopy(rows)
    alarm = data['coupled/63000']['modes']['closed']['core']['switch_noisy']['events'][0]
    alarm.update(hit=False, latency=100)
    summary = explanatory_summary(data)
    key = 'coupled/closed/core/switch_noisy/target_down'
    assert summary[key]['missed_count'] == 1 and summary[key]['missed_and_recovered_count'] == 1
    assert summary[key]['recovered_fraction_among_missed'] == 1.
    assert summary['separate/closed/core/switch_noisy/target_down']['recovered_fraction_among_missed'] is None
    event = data['coupled/63000']['explanatory_events']['closed']['core']['switch_noisy'][0]
    event.update(recovery_latency=1000, recovery_success=False, recovered_within_100=False)
    assert explanatory_summary(data)[key]['recovered_fraction_among_missed'] == 0.
    event['recovered_within_100'] = True
    rejects(lambda: explanatory_summary(data))
    event['recovered_within_100'] = False; event['index'] += 1
    rejects(lambda: explanatory_summary(data))
    print('PASS explanatory summaries: matched events, recovery/miss intersections and zero-denominator handling', flush=True)


def policy_checks():
    calibration, rows, perf = synthetic()
    manifest = make_manifest(calibration)
    assert manifest['status'] == 'eligible' and manifest['thresholds']['separate']['closed'] == .5
    compare([.1, .2, .3, .4], manifest['constants'], 'constants')
    assert detector_cell([4]*32, [5]*32, True)['pass']
    assert not detector_cell([3]*32, [5]*32, True)['pass']
    assert detector_cell([5]*32, [100]*32)['pass']
    assert not detector_cell([6]*32, [100]*32)['pass']
    assert contrast([10.]*32, [9.]*32, True)['pass']
    assert not contrast([10.]*32, [9.01]*32, True)['pass']
    assert contrast([1.25]*32, [1.375]*32, False)['pass']
    assert not contrast([1.25]*32, [1.376]*32, False)['pass']
    decision = detector_decision(rows)
    assert decision['status'] == 'detector_pass' and len(decision['cells']) == 24
    for cell in decision['cells']:
        mode, coord, kind = cell.split('/')
        bad = copy.deepcopy(rows)
        name = 'core' if coord in ('quiet', 'noisy', 'switch_quiet', 'switch_noisy') else (
            'noise_jump' if coord == 'noise_jump' else 'mixed')
        for seed in SEEDS['diagnostics']:
            metric = bad[f'separate/{seed}']['modes'][mode][name][coord]
            if kind == 'blocks': metric['block_count'] = 3
            else:
                event = next(e for e in metric['events'] if e['kind'] == kind)
                hit = kind.startswith('noise_'); event.update(hit=hit, latency=0 if hit else 100)
        assert detector_decision(bad)['status'] == 'detector_negative', cell
        # Common-threshold passing cannot override a native failure.
        assert detector_decision(bad, common=True)['status'] == 'detector_pass'
    for change in ('denominator', 'missing', 'nan', 'invalid_hit', 'latency'):
        bad = copy.deepcopy(rows)
        metric = bad['separate/63000']['modes']['closed']['mixed']['increase_first']
        if change == 'denominator': bad['separate/63000']['modes']['fixed']['core']['quiet']['block_total'] = 49
        elif change == 'missing': metric['events'].pop()
        elif change == 'nan': metric['gate_mean'] = float('nan')
        elif change == 'invalid_hit': metric['events'][0]['hit'] = 2
        else: metric['events'][0]['latency'] = 100
        rejects(lambda: detector_decision(bad))
    bad = copy.deepcopy(calibration); bad[next(iter(bad))] = {'status': 'nonfinite'}
    assert make_manifest(bad)['status'] == 'calibration_inconclusive'
    rejects(lambda: make_manifest({}))
    bad = copy.deepcopy(calibration); next(iter(bad.values()))['modes']['fixed']['maxima']['quiet'].pop()
    rejects(lambda: make_manifest(bad))
    result = performance_decision(perf)
    assert result['status'] == 'positive' and len(result['cells']) == 90
    bad = copy.deepcopy(perf)
    for seed in SEEDS['performance']:
        bad[f'separate/{seed}']['fixtures']['mixed']['coordinates']['decrease_first']['stable_mse'] = 2.
    assert performance_decision(bad)['status'] == 'learning_negative'
    for arm in CONFIGS:
        rejects(lambda arm=arm: performance_decision({k: v for k, v in perf.items() if not k.startswith(arm+'/')}))
    with tempfile.TemporaryDirectory(dir='.', prefix='.reference-uncommitted-') as tmp:
        p = Path(tmp); write(p/'manifest.json', manifest)
        rejects(lambda: diagnostics(p)); assert not (p/'diagnostics.json').exists()
    # Full report lifecycle, using constructed records without observing any study seed.
    failed = copy.deepcopy(rows)
    for seed in SEEDS['diagnostics']:
        for mode in ('fixed', 'closed'):
            failed[f'separate/{seed}']['modes'][mode]['noise_jump']['noise_jump']['events'][0].update(hit=True, latency=0)
    for diag, scores, expected in ((None, None, 'awaiting_diagnostics'),
                                   (failed, None, 'detector_negative'), (rows, None, 'awaiting_performance'),
                                   (rows, perf, 'positive')):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp); store_stage(path, 'calibration', calibration); write(path/'manifest.json', manifest)
            for stage, values in (('diagnostics', diag), ('performance', scores)):
                if values is not None:
                    values = copy.deepcopy(values)
                    for row in values.values(): row['manifest_digest'] = digest(manifest)
                    store_stage(path, stage, values)
            if diag is not None: write(path/'diagnostic-decision.json', diagnostic_result(path, manifest))
            assert publish_report(path)['status'] == expected
            publish_report(path, check=True)
            if expected == 'detector_negative':
                rejects(lambda: require_detection(path, manifest))
                with patch('study_v3_reference.verified_manifest', return_value=manifest): rejects(lambda: performance(path))
                assert not (path/'performance.json').exists()
                write(path/'performance.json', {}); rejects(lambda: publish_report(path))
            if diag is not None:
                changed = copy.deepcopy(manifest); changed['configs']['separate']['lr'] = .1
                write(path/'manifest.json', changed); rejects(lambda: read_stage(path, 'diagnostics'))
    for arm in CONFIGS:
        row = performance_row(60002, arm, manifest)
        assert row['status'] == 'ok' and set(row['fixtures']) == set(FIXTURES)
    for name in FIXTURES:
        data, (_, gates, _) = simulation(60002, name, 'constant', constants=manifest['constants'])
        expected = manifest['constants'] if name == 'core' else [np.mean(manifest['constants'])]*len(data.coordinates)
        np.testing.assert_array_equal(gates, np.tile(expected, (len(data.y), 1)))
    with tempfile.TemporaryDirectory() as tmp:
        p = Path(tmp); store_stage(p, 'calibration', calibration)
        envelope = json.loads((p/'calibration.json').read_text()); envelope['sources']['v3_reference.py'] = 'changed'
        write(p/'calibration.json', envelope); rejects(lambda: read_stage(p, 'calibration'))
    explanatory_checks(rows)
    print('PASS reference policy: all 24 native vetoes, common-threshold non-authority, 90 performance contrasts, source/manifest/stage enforcement', flush=True)


def archive_checks(directory):
    summary = publish_report(directory, check=True)
    require_committed(directory/'manifest.json')
    for stage in summary['reached']:
        envelope = json.loads((directory/(stage+'.json')).read_text())
        assert set(envelope['sources']) == set(SOURCES)
        for source, fingerprint in envelope['sources'].items():
            blob = (directory/'source-snapshots'/(fingerprint+'.txt')).read_bytes()
            assert hashlib.sha256(blob).hexdigest() == fingerprint and Path(source).read_bytes() == blob, source
        print('PASS reference archive', stage, summary['counts'][stage], 'rows', flush=True)
    return summary


def reproduce(directory, summary):
    warmup()
    manifest = json.loads((directory/'manifest.json').read_text())
    actual_rows = {}
    with tempfile.TemporaryDirectory(prefix='brainsim-reference-reproduce-') as tmp:
        out = Path(tmp)
        for stage in summary['reached']:
            actual_rows[stage] = {}
            for key, wanted in read_stage(directory, stage).items():
                arm, seed = key.split('/'); seed = int(seed)
                if stage == 'calibration': row = calibration_row(seed, arm)
                elif stage == 'diagnostics': row = diagnostic_row(seed, arm, manifest)
                else: row = performance_row(seed, arm, manifest)
                compare(scientific(wanted), scientific(row), stage+'/'+key)
                actual_rows[stage][key] = row
            store_stage(out, stage, actual_rows[stage])
            print('PASS reference reproduction', stage, len(actual_rows[stage]), 'rows', flush=True)
        actual_manifest = make_manifest(actual_rows['calibration'])
        assert set(actual_manifest) == set(manifest)
        for key in manifest.keys() - {'calibration_digest'}:
            compare(manifest[key], actual_manifest[key], 'manifest/'+key)
        write(out/'manifest.json', actual_manifest)
        for stage in ('diagnostics', 'performance'):
            if stage in actual_rows:
                for row in actual_rows[stage].values(): row['manifest_digest'] = digest(actual_manifest)
                store_stage(out, stage, actual_rows[stage])
        if 'diagnostics' in actual_rows: write(out/'diagnostic-decision.json', diagnostic_result(out, actual_manifest))
        actual = publish_report(out)
        for key in summary.keys() - {'manifest_digest'}: compare(summary[key], actual[key], 'summary/'+key)
    print('PASS full reference reproduction; unreached partitions are not sampled', flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--evidence', type=Path)
    parser.add_argument('--reproduce', action='store_true')
    args = parser.parse_args()
    if args.reproduce and args.evidence is None: parser.error('--reproduce requires --evidence')
    kernel_checks(); policy_checks()
    if args.evidence:
        summary = archive_checks(args.evidence)
        if args.reproduce: reproduce(args.evidence, summary)


if __name__ == '__main__':
    main()
