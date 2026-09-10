"""Independent controller equations, stage authority and complete evidence reproduction."""
import argparse
import copy
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile
from unittest.mock import patch

import numpy as np

from report_v3_burst import absolute_summary, publish_report, summarize
from study_v3_burst import (SOURCES, activity_metrics, confirm, make_manifest, measure_row,
    oracle_triggers, read_stage, registration_check, require_committed, simulation,
    source_hashes, tune, verified_manifest, write)
from v3_burst import (ARMS, FAMILIES, GRIDS, QUIET, START, THRESHOLD, pulse_schedule,
                      random_probability, random_uniforms, reference_gates, run)
from v3_burst_policy import (KEYS, PROTOCOL, SEEDS, SPECS, complete, contrast, detector_decision,
                            digest, metric_values, objective, performance_decision, scientific, select)
from v3_persistent import FIXTURES, fixture
from v3_reference import run as previous_run
from v3_slice1_learning import run as plain_run


def rejects(fn):
    try:
        fn()
    except (ValueError, KeyError, FileNotFoundError, subprocess.CalledProcessError, TypeError):
        return
    raise AssertionError('expected rejection')


def compare(actual, expected, path='root', ignore=()):
    if isinstance(expected, dict):
        assert isinstance(actual, dict) and set(actual) == set(expected), path
        for key in expected:
            if key not in ignore:
                compare(actual[key], expected[key], path+'/'+key, ignore)
    elif isinstance(expected, list):
        assert isinstance(actual, list) and len(actual) == len(expected), path
        for i, (a, b) in enumerate(zip(actual, expected)):
            compare(a, b, path+'/'+str(i), ignore)
    elif type(expected) is float:
        assert type(actual) in (int, float), path
        np.testing.assert_allclose(actual, expected, rtol=1e-11, atol=1e-13, err_msg=path)
    else:
        assert type(actual) is type(expected) and actual == expected, (path, actual, expected)


def kernel_checks():
    registration_check()
    assert THRESHOLD == json.loads(Path('results/v3-reference/manifest.json').read_text())['thresholds']['separate']['fixed']
    assert len(SPECS) == 15 and [len(KEYS[k]) for k in ('tuning', 'confirmation')] == [480, 224]
    assert all(len(GRIDS[a]) == 12 for a in FAMILIES)
    assert all(len({json.dumps(c, sort_keys=True) for c in GRIDS[a]}) == 12 for a in FAMILIES)
    partitions = list(SEEDS.values())
    assert all(min(s) >= 70000 and max(s) < 75000 for s in partitions)
    assert all(not set(a)&set(b) for i, a in enumerate(partitions) for b in partitions[i+1:])
    q = np.ones((400, 2))
    active, starts = pulse_schedule(q, 16, True)
    assert np.flatnonzero(starts[:, 0]).tolist() == [146]
    assert np.flatnonzero(active[:, 0]).tolist() == list(range(146, 162))
    q[162:178, 0] = THRESHOLD
    active, starts = pulse_schedule(q, 16, True)
    assert np.flatnonzero(starts[:, 0]).tolist() == [146, 178]
    assert np.flatnonzero(starts[:, 1]).tolist() == [146]
    q[177, 0] = 1.
    assert np.flatnonzero(pulse_schedule(q, 16, True)[1][:, 0]).tolist() == [146]
    # Quiet observations DURING a pulse cannot pre-arm the next one.
    q = np.ones((300, 1)); q[147:163] = 0.
    assert np.flatnonzero(pulse_schedule(q, 16, True)[1][:, 0]).tolist() == [146]
    assert pulse_schedule(np.full((300, 1), THRESHOLD), 16, True)[0].sum() == 0
    ext = np.ones((300, 1))
    active, starts = pulse_schedule(ext, 16, False)
    assert np.flatnonzero(starts[:, 0]).tolist() == [146, 178, 210, 242, 274]
    active, starts = pulse_schedule(ext, 64, False)
    assert np.flatnonzero(starts[:, 0]).tolist() == [146, 226]
    assert active[299, 0] == 0 and active.sum() == 128
    assert pulse_schedule(np.ones((147, 1)), 1, False)[0].sum() == 1
    # Independent scalar recurrence: current observation changes update, never its prediction.
    y = np.random.default_rng(70000).normal(size=(420, 2))
    q = np.zeros_like(y); q[150:160, 0] = .8; q[250:310, 1] = .9
    config = {'lr': .016, 'factor': 8., 'duration': 16, 'beta2': .999}
    actual = run(y, 'burst', config, gates=q)
    for j, window in ((0, range(150, 166)), (1, range(250, 266))):
        w, m, v = 0., 0., 0.
        expected = []
        for t in range(len(y)):
            expected.append(w)
            g = w-y[t, j]
            m, v = .9*m+.1*g, .999*v+.001*g*g
            direction = (m/(1-.9**(t+1)))/(np.sqrt(v/(1-.999**(t+1)))+1e-8)
            w -= .016*(8. if t in window else 1.)*direction
        np.testing.assert_allclose(actual[0][:, j], expected, rtol=1e-12, atol=1e-13)
    expected_norms = np.sqrt(np.sum(np.diff(actual[0], axis=0)**2, axis=1))
    np.testing.assert_allclose(actual[2][:-1], expected_norms, rtol=1e-12, atol=1e-13)
    plain = plain_run(y, 'adam', config)
    for special in ({'gates': np.zeros_like(y)}, {'gates': q}):
        c = config if not special['gates'].any() else {**config, 'factor': 1.}
        for index in (0, 2):
            np.testing.assert_array_equal(run(y, 'burst', c, **special)[index], plain[index])
    for index in (0, 2):
        np.testing.assert_array_equal(run(y, 'continuous', {'lr': .016, 'gain': 0., 'beta2': .999})[index], plain[index])
    for a, b in zip(run(y, 'continuous', {'lr': .004, 'gain': 64., 'beta2': .999})[:3], previous_run(y, 'separate')):
        np.testing.assert_array_equal(a, b)
    triggers = np.zeros_like(y); triggers[200] = 1.
    uniforms = random_uniforms(70000, 0, 420, 2)
    for arm in ARMS:
        c = GRIDS[arm][3] if arm in FAMILIES else GRIDS['burst'][3]
        kwargs = {'triggers': triggers} if arm in ('oracle', 'oracle_matched') else (
            {'uniforms': uniforms, 'probability': .02} if arm == 'random' else {})
        original = run(y, arm, c, **kwargs)
        other = y.copy(); other[300:] += 10.
        changed = run(other, arm, c, **kwargs)
        np.testing.assert_array_equal(original[0][:301], changed[0][:301])
        for index in (1, 2, 3):
            np.testing.assert_array_equal(original[index][:300], changed[index][:300])
        prefix_kwargs = {k: v[:300] if isinstance(v, np.ndarray) else v for k, v in kwargs.items()}
        for a, b in zip(run(y[:300], arm, c, **prefix_kwargs), original):
            np.testing.assert_array_equal(a, b[:300])
        other = y.copy(); other[:, 0] += 10.
        changed = run(other, arm, c, **kwargs)
        for index in (0, 1, 3):
            np.testing.assert_array_equal(original[index][:, 1], changed[index][:, 1])
    for arm in ('burst', 'continuous', 'adam', 'sgd', 'random'):
        c = GRIDS[arm][0] if arm != 'random' else GRIDS['burst'][0]
        rejects(lambda a=arm, c=c: run(y, a, c, triggers=triggers))
    np.testing.assert_array_equal(uniforms[:200], random_uniforms(70000, 0, 200, 2))
    np.testing.assert_array_equal(uniforms[:, :1], random_uniforms(70000, 0, 420, 1))
    assert not np.array_equal(uniforms, random_uniforms(70000, 1, 420, 2))
    assert not np.array_equal(uniforms[:, 0], uniforms[:, 1])
    assert random_probability(0, 1000, 16) == 0.
    assert random_probability(1, 32, 16) == 1.
    assert abs(random_probability(10, 1000, 16)-(.01/.69)) < 1e-14
    rejects(lambda: random_probability(2, 32, 16))
    rejects(lambda: random_probability(-1, 32, 16))
    rejects(lambda: run(y, 'random', config, uniforms=uniforms, probability=1.1))
    rejects(lambda: run(y, 'burst', config, gates=np.full_like(y, np.nan)))
    rejects(lambda: run(y, 'burst', {**config, 'duration': 1.5}))
    rejects(lambda: run(np.full_like(y, np.nan), 'burst', config))
    rejects(lambda: run(y, 'oracle', config))
    for name in FIXTURES:
        data = fixture(70001, name)
        marked = oracle_triggers(data)
        expected = {(t, j) for j, events in enumerate(data.events) for t, kind in events if kind.startswith('target_')}
        assert {tuple(v) for v in np.argwhere(marked)} == expected
        with patch('study_v3_burst.oracle_triggers', side_effect=AssertionError('privileged access')):
            simulation(70001, name, 'burst', config)
    print('PASS burst kernels: duration, quiet rearm, caps, independent Adam, inherited parity, causality, oracle isolation and random schedules', flush=True)


def synthetic():
    coordinates = {'core': ('quiet', 'noisy', 'switch_quiet', 'switch_noisy'),
        'mixed': ('increase_first', 'decrease_first'), 'noise_jump': ('noise_jump',),
        'drift': ('drift',), 'exactly_quiet': ('exactly_quiet',)}
    row = {'status': 'ok', 'config': {}, 'privileged_timing': False, 'fixtures': {}, 'activity': {}, 'detector': {}}
    for name, coords in coordinates.items():
        row['fixtures'][name] = {'coordinates': {}, 'update_norm_mean': .1, 'update_norm_sum': 600.}
        row['activity'][name], row['detector'][name] = {}, {}
        for coord in coords:
            kinds = ('target_down', 'target_up') if name == 'mixed' or coord.startswith('switch_') else (
                ('noise_increase', 'noise_decrease') if name == 'noise_jump' else ())
            row['fixtures'][name]['coordinates'][coord] = {
                'excess_mse': 1., 'post_mse': 1. if kinds and kinds[0].startswith('target_') else None,
                'stable_mse': 1., 'adaptation_latency': 10. if kinds and kinds[0].startswith('target_') else None,
                'windows': {'noise_increase': 1., 'noise_decrease': 1., 'drift': 1.}}
            events = [{'index': 2000+2000*i, 'kind': k, 'hit': k.startswith('target_'),
                       'latency': 0 if k.startswith('target_') else 100} for i, k in enumerate(kinds)]
            row['activity'][name][coord] = {'starts': [2000, 4000], 'start_count': 2,
                'active_updates': 32, 'duty_cycle': 32/5854, 'events': copy.deepcopy(events)}
            row['detector'][name][coord] = {'block_count': 0, 'block_total': 50, 'events': events}
    tuning = {}
    for a in FAMILIES:
        for i, config in enumerate(GRIDS[a]):
            for s in SEEDS['tuning']:
                r = copy.deepcopy(row); r['config'] = config; r['privileged_timing'] = a == 'oracle'
                tuning[f'{a}/{i}/{s}'] = r
    manifest = make_manifest(tuning)
    confirmation = {}
    for a in ARMS:
        for s in SEEDS['confirmation']:
            r = copy.deepcopy(row)
            r.update(config=manifest['screen']['selected'][a], manifest_digest=digest(manifest),
                     privileged_timing=a in ('oracle', 'oracle_matched'))
            if a in ('burst', 'oracle', 'oracle_matched'):
                for f in r['fixtures'].values():
                    for c in f['coordinates'].values():
                        for k in ('excess_mse', 'post_mse', 'stable_mse'):
                            if c[k] is not None: c[k] = .5
                        c['windows'] = {k: .5 for k in c['windows']}
            confirmation[f'{a}/{s}'] = r
    return tuning, manifest, confirmation


def policy_checks():
    tuning, manifest, rows = synthetic()
    assert objective(tuning['burst/0/71000']) == 1.
    assert all(i == 0 for i in manifest['screen']['indices'].values())
    assert manifest['screen']['selected']['random'] == manifest['screen']['selected']['burst']
    assert manifest['screen']['selected']['oracle_matched'] == manifest['screen']['selected']['burst']
    assert manifest['screen']['random_frequency']['starts'] == 144
    assert manifest['screen']['random_frequency']['coordinate_time'] == 421488
    bad = copy.deepcopy(tuning); bad['burst/0/71000']['status'] = 'nonfinite'
    assert select(bad)['indices']['burst'] == 1
    for k, r in bad.items():
        if k.startswith('burst/'): r['status'] = 'nonfinite'
    assert select(bad)['status'] == 'tuning_inconclusive'
    rejects(lambda: complete({k: v for k, v in tuning.items() if k != 'burst/0/71000'}, 'tuning'))
    bad = copy.deepcopy(tuning); bad['burst/0/71000']['fixtures']['core']['coordinates']['quiet']['excess_mse'] = float('nan')
    rejects(lambda: select(bad))
    result = performance_decision(rows)
    assert result['status'] == 'learning_positive' and len(result['cells']) == 60
    assert detector_decision(rows)['status'] == 'detector_pass' and len(detector_decision(rows)['cells']) == 12
    for arm in ('oracle', 'oracle_matched'):
        assert performance_decision(rows, arm)['status'] == 'oracle_pass'
        assert len(performance_decision(rows, arm)['cells']) == 30
    # Every individual registered contrast must be capable of vetoing advancement.
    for control in ('adam', 'sgd', 'continuous', 'random'):
        for label, fields in SPECS:
            bad = copy.deepcopy(rows)
            for s in SEEDS['confirmation']:
                for n, c, f, w in fields:
                    dest = bad[f'{control}/{s}']['fixtures'][n]['coordinates'][c]
                    if w: dest[f][w] = .01
                    else: dest[f] = .01
            decision = performance_decision(bad)
            assert decision['status'] == 'learning_negative' and not decision['cells'][f'{control}/{label}']['pass']
    bad = copy.deepcopy(rows)
    for s in SEEDS['confirmation']:
        bad[f'burst/{s}']['status'] = 'nonfinite'
    assert performance_decision(bad)['status'] == 'learning_negative'
    assert performance_decision(bad, 'oracle')['status'] == 'oracle_pass'
    bad = copy.deepcopy(rows)
    for s in SEEDS['confirmation']:
        bad[f'oracle/{s}']['status'] = 'nonfinite'
        bad[f'burst/{s}']['detector']['core']['quiet']['block_count'] = 50
    assert performance_decision(bad)['status'] == 'learning_positive'
    assert detector_decision(bad)['status'] == 'detector_negative'
    assert performance_decision(bad, 'oracle')['status'] == 'oracle_negative'
    rejects(lambda: contrast([1., 2.], [1.], True))
    assert not contrast([1.]*32, [.91]*32, True)['pass']
    assert contrast([1.]*32, [.89]*32, True)['pass']
    assert not contrast([1.]*32, [1.101]*32, False)['pass']
    for k in ('random/73000', 'oracle/73000'):
        rejects(lambda k=k: performance_decision({a: r for a, r in rows.items() if a != k}))
    print('PASS burst policy: equal menus/objective, deterministic finite selection, 60 vetoes, oracle and detector non-authority', flush=True)


def lifecycle_checks():
    tuning, manifest, rows = synthetic()
    with tempfile.TemporaryDirectory() as tmp:
        directory = Path(tmp)
        def envelope(stage, data):
            write(directory/(stage+'.json'), {'protocol': PROTOCOL, 'sources': source_hashes(), 'rows': data})
        envelope('tuning', tuning); write(directory/'manifest.json', manifest)
        assert summarize(directory)['status'] == 'awaiting_confirmation'
        with patch('study_v3_burst.require_committed', side_effect=ValueError('uncommitted')):
            rejects(lambda: confirm(directory))
        with patch('study_v3_burst.require_committed'):
            assert verified_manifest(directory) == manifest
            changed = copy.deepcopy(manifest); changed['threshold'] = .1
            write(directory/'manifest.json', changed)
            rejects(lambda: verified_manifest(directory))
            write(directory/'manifest.json', manifest)
        envelope('confirmation', rows)
        publish_report(directory); publish_report(directory, True)
        assert summarize(directory)['status'] == 'learning_positive'
        rejects(lambda: tune(directory))
        broken = copy.deepcopy(rows); broken['random/73000']['manifest_digest'] = 'wrong'
        envelope('confirmation', broken); rejects(lambda: read_stage(directory, 'confirmation'))
        envelope('confirmation', rows)
        raw = json.loads((directory/'confirmation.json').read_text()); raw['sources']['v3_burst.py'] = 'wrong'
        write(directory/'confirmation.json', raw); rejects(lambda: read_stage(directory, 'confirmation'))
        envelope('confirmation', rows)
        broken = copy.deepcopy(rows); broken['oracle/73000']['privileged_timing'] = False
        envelope('confirmation', broken); rejects(lambda: read_stage(directory, 'confirmation'))
        envelope('confirmation', rows)
        for key in tuning:
            if key.startswith('burst/'):
                tuning[key]['status'] = 'nonfinite'
        envelope('tuning', tuning); manifest = make_manifest(tuning); write(directory/'manifest.json', manifest)
        rejects(lambda: summarize(directory))
        with patch('study_v3_burst.require_committed'):
            rejects(lambda: confirm(directory))
        (directory/'confirmation.json').unlink()
        assert summarize(directory)['status'] == 'tuning_inconclusive'
        publish_report(directory); publish_report(directory, True)
    with tempfile.TemporaryDirectory(dir='.') as tmp:
        path = Path(tmp)/'uncommitted.json'; path.write_text('{}')
        rejects(lambda: require_committed(path))
    # Actual development-only full fixtures for every arm, independently of study cohorts.
    for arm in ARMS:
        c = GRIDS[arm][0] if arm in FAMILIES else GRIDS['burst'][0]
        r = measure_row(70002, arm, c, .001 if arm == 'random' else None)
        assert r['status'] == 'ok' and len(r['fixtures']) == 5
        assert r['privileged_timing'] == (arm in ('oracle', 'oracle_matched'))
    print('PASS burst lifecycle: immutable manifests/sources, forbidden stages, complete reports and all-arm development fixtures', flush=True)


def archive_checks(directory, reproduce):
    stored = publish_report(directory, True)
    for path, expected in source_hashes().items():
        snapshot = directory/'source-snapshots'/(expected+'.txt')
        assert hashlib.sha256(snapshot.read_bytes()).hexdigest() == expected, path
    manifest = json.loads((directory/'manifest.json').read_text())
    tuning = read_stage(directory, 'tuning')
    assert manifest == make_manifest(tuning)
    print('PASS burst archive tuning', len(tuning), flush=True)
    if not reproduce:
        if stored['counts']['confirmation']:
            read_stage(directory, 'confirmation')
        return
    fresh = {}
    for arm in FAMILIES:
        for i, config in enumerate(GRIDS[arm]):
            for seed in SEEDS['tuning']:
                key = f'{arm}/{i}/{seed}'
                fresh[key] = measure_row(seed, arm, config)
                compare(fresh[key], scientific(tuning[key]), key)
        print('PASS burst reproduction tuning', arm, '96 rows', flush=True)
    fresh_manifest = make_manifest(fresh)
    compare(fresh_manifest, manifest, ignore=('tuning_digest',))
    if stored['counts']['confirmation']:
        archived = read_stage(directory, 'confirmation')
        recreated = {}
        for arm in ARMS:
            for seed in SEEDS['confirmation']:
                key = f'{arm}/{seed}'
                recreated[key] = measure_row(seed, arm, fresh_manifest['screen']['selected'][arm],
                    fresh_manifest['screen']['random_frequency']['probability'] if arm == 'random' else None, fresh_manifest)
                compare(recreated[key], scientific(archived[key]), key, ignore=('manifest_digest',))
            print('PASS burst reproduction confirmation', arm, '32 rows', flush=True)
        for arm in ('burst', 'oracle', 'oracle_matched'):
            compare(performance_decision(recreated, arm), stored['decisions'][arm])
        compare(detector_decision(recreated), stored['decisions']['detector_diagnostic'])
        compare(absolute_summary(recreated), stored['absolute'])
    print('PASS full burst reproduction; only reached partitions sampled', flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--evidence', type=Path)
    parser.add_argument('--reproduce', action='store_true')
    args = parser.parse_args()
    kernel_checks(); policy_checks(); lifecycle_checks()
    if args.evidence:
        archive_checks(args.evidence, args.reproduce)
