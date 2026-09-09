"""Independent equations, policy boundaries, archive integrity and complete reproduction."""
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
from report_v3_persistent import publish_report
from study_v3_persistent import (SOURCES, calibration_row, diagnostic_result, diagnostic_row,
                                 diagnostics, make_manifest, performance, performance_row,
                                 read_stage, registration_check, require_committed, require_detection,
                                 source_hashes, write)
from v3_persistent import (CONFIGS, DETECTORS, FIXTURES, cusum_step, directional_min,
                           fixture, run, warmup, window_stats)
from v3_persistent_policy import (KEYS, PROTOCOL, SEEDS, contrast, detector_cell, detector_decision,
                                  digest, performance_decision, scientific)
from v3_slice1_learning import run as old_run
from v3_slice1_streams import rng


def rejects(fn):
    try:
        fn()
    except (ValueError, KeyError, FileNotFoundError, subprocess.CalledProcessError):
        return
    raise AssertionError('expected prerequisite/data rejection')


def kernel_checks():
    registration_check()
    assert all(min(seeds) >= 50000 and max(seeds) < 55000 for seeds in SEEDS.values())
    parts = list(SEEDS.values())
    assert all(not set(a) & set(b) for i, a in enumerate(parts) for b in parts[i+1:])
    assert [len(KEYS[s]) for s in ('calibration', 'diagnostics', 'performance')] == [64, 128, 256]
    for values, expected in (([1., 3., 2., 4.], 1.), ([-2., -3., -1., -4.], 1.),
                             ([1., 2., -1., 3.], 0.), ([0., 2., 3., 4.], 0.)):
        assert directional_min(np.array(values)) == expected
    # Independent centered-window reference, including ring wrap and unequal variances.
    y = rng(50000, 31).normal(size=(260, 3))
    y[128:] = 3.*y[128:] + 2.
    buffer = np.zeros((144, 3))
    for t in range(len(y)):
        buffer[t % 144] = y[t]
        if t >= 143:
            for j in range(3):
                recent, reference = y[t-15:t+1, j], y[t-143:t-15, j]
                np.testing.assert_allclose(window_stats(buffer, t, j),
                    [recent.mean(), reference.mean(), recent.var(ddof=1), reference.var(ddof=1)],
                    rtol=1e-13, atol=1e-13)
    # CUSUM recurrence checked against explicit hand-worked positive/negative/reset steps.
    assert cusum_step(0., 0., 2.) == (1.5, 0.)
    assert cusum_step(1.5, 0., -1.) == (0., .5)
    assert cusum_step(0., .5, 0.) == (0., 0.)
    expected = {a: np.zeros_like(y) for a in ('candidate', 'cusum')}
    for j in range(3):
        z, cp, cn = [], 0., 0.
        for t in range(len(y)):
            score = 0.
            if t >= 143:
                # Fixed observer gradients are -y, independently sliced, no ring/helper calls.
                r, b = -y[t-15:t+1, j], -y[t-143:t-15, j]
                score = (r.mean()-b.mean())/np.sqrt(r.var(ddof=1)/16+b.var(ddof=1)/128+1e-8)
                u = (-y[t, j]-b.mean())/np.sqrt(max(r.var(ddof=1), b.var(ddof=1))+1e-8)
                cp, cn = max(0., cp+u-.5), max(0., cn-u-.5)
                expected['cusum'][t, j] = max(cp, cn)/(max(cp, cn)+16)
            z.append(score)
            last = np.array(z[-4:])
            a = min(abs(last)) if len(last) == 4 and (np.all(last > 0) or np.all(last < 0)) else 0.
            expected['candidate'][t, j] = a*a/(a*a+16)
    for arm, wanted in expected.items():
        np.testing.assert_allclose(run(y, arm, observer=True)[1], wanted, rtol=1e-12, atol=1e-13)
    for observer in (False, True):
        for actual, wanted in zip(run(y, 'current', observer), old_run(y, 'candidate', CONFIGS['current'], observer=observer)):
            np.testing.assert_array_equal(actual, wanted)
    # Independent original EMA recurrence and persistence rule.
    for j in range(3):
        mf = ms = -y[0, j]
        vf = vs = 0.
        scores = []
        expected_q = []
        for t, gradient in enumerate(-y[:, j]):
            if t:
                df, ds = gradient-mf, gradient-ms
                mf, ms = mf+.1*df, ms+.01*ds
                vf, vs = .9*(vf+.1*df*df), .99*(vs+.01*ds*ds)
            delta = mf-ms
            q = delta*delta/(delta*delta+vf+vs+1e-8)
            scores.append(np.sign(delta)*np.sqrt(q))
            recent = np.array(scores[-4:])
            expected_q.append(min(abs(recent))**2 if len(recent) == 4 and
                              (np.all(recent > 0) or np.all(recent < 0)) else 0.)
        np.testing.assert_allclose(run(y, 'persistence', observer=True)[1][:, j], expected_q, rtol=1e-12, atol=1e-13)
    for arm in DETECTORS:
        prediction, gate, norm = run(y, arm)
        assert all(np.isfinite(x).all() for x in (prediction, gate, norm))
        assert np.all((gate >= 0) & (gate <= 1))
        later = y.copy(); later[190:] += 10.
        p2, q2, _ = run(later, arm)
        np.testing.assert_array_equal(prediction[:191], p2[:191])
        np.testing.assert_array_equal(gate[:190], q2[:190])
        other = y.copy(); other[:, 0] *= 5.
        np.testing.assert_array_equal(prediction[:, 1:], run(other, arm)[0][:, 1:])
        np.testing.assert_array_equal(prediction[:, 1], run(y[:, 1:2], arm)[0][:, 0])
        np.testing.assert_allclose(run(y, arm, True)[1], run(-y, arm, True)[1], atol=1e-13)
        np.testing.assert_allclose(run(y, arm, True)[1], run(y+5., arm, True)[1], rtol=1e-11, atol=1e-13)
        zero_gain = {**CONFIGS[arm], 'gain': 0.}
        np.testing.assert_array_equal(run(y, arm, config=zero_gain)[0], old_run(y, 'adam', zero_gain)[0])
    assert not run(y, 'candidate', True)[1][:146].any()
    assert not run(y, 'cusum', True)[1][:143].any()
    rejects(lambda: run(np.ones((2, 1)), 'unknown'))
    rejects(lambda: run(np.array([[np.nan]]), 'candidate'))
    assert np.isnan(directional_min(np.array([1., np.inf, 2., 3.])))
    extreme = np.full((160, 1), 1e308); extreme[::2] *= -1.
    with np.errstate(over='ignore', invalid='ignore'):
        for arm in DETECTORS:
            assert not np.isfinite(run(extreme, arm, True)[1]).all()
    mixed = fixture(50001, 'mixed')
    first, second = [index for index, _ in mixed.events[0]]
    assert mixed.events[0] == mixed.events[1] == fixture(50001).events[2]
    np.testing.assert_array_equal(mixed.target[:first], np.ones((first, 2)))
    np.testing.assert_array_equal(mixed.target[first:second], -np.ones((second-first, 2)))
    np.testing.assert_array_equal(mixed.target[second:], np.ones((6000-second, 2)))
    for j, domain in enumerate((21, 22)):
        sigma = np.full(6000, .05 if j == 0 else 1.)
        sigma[first:second] = 1. if j == 0 else .05
        np.testing.assert_allclose((mixed.y[:, j]-mixed.target[:, j])/sigma, rng(50001, domain).normal(size=6000), atol=1e-13)
    print('PASS persistent kernels: independent equations, parity, causal windows, persistence, mixed fixtures, isolation', flush=True)


def synthetic():
    calibration = {key: {'status': 'ok', 'modes': {mode: {
        'maxima': {c: [.5]*50 for c in ('quiet', 'noisy')}, 'gate_means': [.1, .2, .3, .4]}
        for mode in ('fixed', 'closed')}} for key in KEYS['calibration']}

    def metric(kinds=(), hit=False):
        return {'block_count': 0, 'block_total': 50, 'point_count': 0, 'point_total': 5000,
                'gate_initial': 0., 'gate_mean': .1, 'events': [
                    {'index': 2000+2000*i, 'kind': k, 'hit': hit, 'latency': 0 if hit else 100}
                    for i, k in enumerate(kinds)]}

    modes = {mode: {'core': {'quiet': metric(), 'noisy': metric(),
                            'switch_quiet': metric(('target_down', 'target_up'), True),
                            'switch_noisy': metric(('target_down', 'target_up'), True)},
                    'noise_jump': {'noise_jump': metric(('noise_increase', 'noise_decrease'))},
                    'mixed': {c: metric(('target_down', 'target_up'), True) for c in ('increase_first', 'decrease_first')},
                    'drift': {'drift': metric()}, 'exactly_quiet': {'exactly_quiet': metric()}}
             for mode in ('fixed', 'closed')}
    diagnostics = {key: {'status': 'ok', 'modes': copy.deepcopy(modes)} for key in KEYS['diagnostics']}
    performance = {}
    coordinates = {'core': ('quiet', 'noisy', 'switch_quiet', 'switch_noisy'),
                   'mixed': ('increase_first', 'decrease_first'), 'noise_jump': ('noise_jump',),
                   'drift': ('drift',), 'exactly_quiet': ('exactly_quiet',)}
    for key in KEYS['performance']:
        value = .5 if key.startswith('candidate/') else 1.
        performance[key] = {'status': 'ok', 'fixtures': {name: {'coordinates': {
            c: {'excess_mse': value, 'stable_mse': value, 'post_mse': value,
                'windows': {'noise_increase': value, 'noise_decrease': value, 'drift': value}}
            for c in coords}} for name, coords in coordinates.items()}}
    return calibration, diagnostics, performance


def store_stage(directory, stage, rows):
    write(directory/(stage+'.json'), {'protocol': PROTOCOL, 'sources': source_hashes(), 'rows': rows})


def policy_checks():
    calibration, rows, perf = synthetic()
    manifest = make_manifest(calibration)
    assert manifest['status'] == 'eligible' and manifest['thresholds']['candidate']['closed'] == .5
    compare([.1, .2, .3, .4], manifest['constants'], 'constants')
    bad = copy.deepcopy(calibration)
    next(iter(bad.values()))['modes']['fixed']['maxima']['quiet'].pop()
    rejects(lambda: make_manifest(bad))
    bad = copy.deepcopy(calibration); bad[next(iter(bad))] = {'status': 'nonfinite'}
    assert make_manifest(bad)['status'] == 'calibration_inconclusive'
    rejects(lambda: make_manifest({}))
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
    # Every required cell must veto independently, including all mixed directions.
    for cell in decision['cells']:
        mode, coord, kind = cell.split('/')
        bad = copy.deepcopy(rows)
        name = 'core' if coord in ('quiet', 'noisy', 'switch_quiet', 'switch_noisy') else (
            'noise_jump' if coord == 'noise_jump' else 'mixed')
        for seed in SEEDS['diagnostics']:
            data = bad[f'candidate/{seed}']['modes'][mode][name][coord]
            if kind == 'blocks':
                data['block_count'] = 3
            else:
                event = next(e for e in data['events'] if e['kind'] == kind)
                hit = kind.startswith('noise_')
                event.update(hit=hit, latency=0 if hit else 100)
        assert detector_decision(bad)['status'] == 'detector_negative', cell
    failed = bad
    for change in ('denominator', 'missing', 'nan', 'invalid_hit', 'latency'):
        bad = copy.deepcopy(rows)
        data = bad['candidate/53000']['modes']['closed']['mixed']['increase_first']
        if change == 'denominator':
            bad['candidate/53000']['modes']['fixed']['core']['quiet']['block_total'] = 49
        elif change == 'missing':
            data['events'].pop()
        elif change == 'nan':
            data['gate_mean'] = float('nan')
        elif change == 'invalid_hit':
            data['events'][0]['hit'] = 2
        else:
            data['events'][0]['latency'] = 100
        rejects(lambda: detector_decision(bad))
    result = performance_decision(perf)
    assert result['status'] == 'positive' and len(result['cells']) == 105
    bad = copy.deepcopy(perf)
    for seed in SEEDS['performance']:
        bad[f'candidate/{seed}']['fixtures']['mixed']['coordinates']['decrease_first']['stable_mse'] = 2.
    assert performance_decision(bad)['status'] == 'learning_negative'
    for arm in CONFIGS:
        rejects(lambda arm=arm: performance_decision({k: v for k, v in perf.items() if not k.startswith(arm+'/')}))
    with tempfile.TemporaryDirectory(dir='.', prefix='.persistent-uncommitted-') as tmp:
        path = Path(tmp)
        write(path/'manifest.json', manifest)
        rejects(lambda: diagnostics(path))
        assert not (path/'diagnostics.json').exists()
    for diag, scores, expected in ((None, None, 'awaiting_diagnostics'),
                                   (failed, None, 'detector_negative'), (rows, None, 'awaiting_performance'),
                                   (rows, perf, 'positive')):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp)
            store_stage(path, 'calibration', calibration)
            write(path/'manifest.json', manifest)
            for stage, values in (('diagnostics', diag), ('performance', scores)):
                if values is not None:
                    values = copy.deepcopy(values)
                    for row in values.values(): row['manifest_digest'] = digest(manifest)
                    store_stage(path, stage, values)
            if diag is not None:
                write(path/'diagnostic-decision.json', diagnostic_result(path, manifest))
            summary = publish_report(path)
            assert summary['status'] == expected
            publish_report(path, check=True)
            if expected == 'detector_negative':
                rejects(lambda: require_detection(path, manifest))
                with patch('study_v3_persistent.verified_manifest', return_value=manifest):
                    rejects(lambda: performance(path))
                assert not (path/'performance.json').exists()
                write(path/'performance.json', {})
                rejects(lambda: publish_report(path))
            if diag is not None:
                changed = copy.deepcopy(manifest); changed['configs']['candidate']['lr'] = .1
                write(path/'manifest.json', changed)
                rejects(lambda: read_stage(path, 'diagnostics'))
    print('PASS persistent policy: every 24-cell veto, 105 contrasts, exact cohorts, invalid data and stage/manifest enforcement', flush=True)


def archive_checks(directory):
    summary = publish_report(directory, check=True)
    require_committed(directory/'manifest.json')
    for stage in summary['reached']:
        envelope = json.loads((directory/(stage+'.json')).read_text())
        assert set(envelope['sources']) == set(SOURCES)
        for source, fingerprint in envelope['sources'].items():
            blob = (directory/'source-snapshots'/(fingerprint+'.txt')).read_bytes()
            assert hashlib.sha256(blob).hexdigest() == fingerprint and Path(source).read_bytes() == blob, source
        print('PASS persistent archive', stage, summary['counts'][stage], 'rows', flush=True)
    return summary


def reproduce(directory, summary):
    warmup()
    manifest = json.loads((directory/'manifest.json').read_text())
    actual_rows = {}
    with tempfile.TemporaryDirectory(prefix='brainsim-persistent-reproduce-') as tmp:
        out = Path(tmp)
        for stage in summary['reached']:
            actual_rows[stage] = {}
            for key, wanted in read_stage(directory, stage).items():
                arm, seed = key.split('/'); seed = int(seed)
                if stage == 'calibration':
                    row = calibration_row(seed, arm)
                elif stage == 'diagnostics':
                    row = diagnostic_row(seed, arm, manifest)
                else:
                    row = performance_row(seed, arm, manifest)
                compare(scientific(wanted), scientific(row), stage+'/'+key)
                actual_rows[stage][key] = row
            store_stage(out, stage, actual_rows[stage])
            print('PASS persistent reproduction', stage, len(actual_rows[stage]), 'rows', flush=True)
        actual_manifest = make_manifest(actual_rows['calibration'])
        assert set(actual_manifest) == set(manifest)
        for key in manifest.keys() - {'calibration_digest'}:
            compare(manifest[key], actual_manifest[key], 'manifest/'+key)
        write(out/'manifest.json', actual_manifest)
        for stage in ('diagnostics', 'performance'):
            if stage in actual_rows:
                for row in actual_rows[stage].values(): row['manifest_digest'] = digest(actual_manifest)
                store_stage(out, stage, actual_rows[stage])
        if 'diagnostics' in actual_rows:
            write(out/'diagnostic-decision.json', diagnostic_result(out, actual_manifest))
        actual = publish_report(out)
        for key in summary.keys() - {'manifest_digest'}:
            compare(summary[key], actual[key], 'summary/'+key)
    print('PASS complete reached-stage reproduction; unreached observation seeds remain unused', flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--evidence', type=Path)
    parser.add_argument('--reproduce', action='store_true')
    args = parser.parse_args()
    if args.reproduce and args.evidence is None:
        parser.error('--reproduce requires --evidence')
    kernel_checks()
    policy_checks()
    if args.evidence:
        summary = archive_checks(args.evidence)
        if args.reproduce:
            reproduce(args.evidence, summary)


if __name__ == '__main__':
    main()
