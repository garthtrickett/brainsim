"""New-ramp fixtures, adapted gate authority and full reproduction."""
import argparse
import ast
import copy
import hashlib
import json
from pathlib import Path
import tempfile
from unittest.mock import patch

import numpy as np

from check_v3_burst import compare, rejects
from report_v3_slopebench import absolute_summary, publish_report, summarize
from study_v3_slopebench import (SOURCES, confirm, enriched_frequency, make_manifest, measure_row,
    read_stage, registration_check, require_committed, simulation, source_hashes, tune,
    verified_manifest, write)
from v3_adwin import run as adwin_run
from v3_forgetting import run as forget_run
from v3_slope import run as slope_run
from v3_slopebench import FIXTURES, ORDINAL, fixture, ramp_fixture, ramp_metrics, random_uniforms
from v3_slopebench_policy import (ARMS, ESTIMATOR, FAMILIES, GRIDS, KEYS, PROTOCOL, SEEDS, SPECS,
    STRICT, complete, contrast, digest, metric_values, objective, performance_decision, scientific, select)
from v3_persistent import fixture as persistent_fixture
from v3_slice1_learning import run as plain_run
from v3_slice1_streams import BURN, STEPS


def slow_adwin(values, delta, clock):
    """Explicit bucket CONTENTS and direct numpy variance; no compressed statistics."""
    buckets, predictions, means, flags, widths, removed = [], [], [], [], [], []
    estimate = 0.
    for t, value in enumerate(values):
        predictions.append(estimate)
        buckets.append([float(value)])
        size = 1
        while True:
            matching = [i for i, b in enumerate(buckets) if len(b) == size]
            if len(matching) <= 5: break
            a, b = matching[:2]
            assert b == a+1
            buckets[a:b+1] = [buckets[a]+buckets[b]]
            size *= 2
        discarded = 0
        if (t+1) % clock == 0:
            while sum(map(len, buckets)) >= 10:
                full = np.array([x for b in buckets for x in b])
                n, cut, significant = len(full), 0, False
                for b in buckets[:-1]:
                    cut += len(b)
                    if cut < 5 or n-cut < 5: continue
                    inverse = 1/cut+1/(n-cut)
                    logterm = np.log(2*np.log(n)/delta)
                    bound = np.sqrt(2*inverse*np.var(full)*logterm)+2*inverse*logterm/3
                    if abs(np.mean(full[:cut])-np.mean(full[cut:])) > bound:
                        significant = True
                        break
                if not significant: break
                discarded += len(buckets.pop(0))
        retained = np.array([x for b in buckets for x in b])
        estimate = float(retained.mean())
        means.append(estimate); flags.append(float(discarded > 0))
        widths.append(len(retained)); removed.append(discarded)
    return (np.array(predictions), np.array(flags), np.abs(np.array(means)-predictions),
            np.array(widths), np.array(removed))


def kernel_checks():
    registration_check()
    assert ESTIMATOR == {'method': 'ols', 'W': 128}
    assert set(FIXTURES) == {'core', 'mixed', 'steep', 'shallow', 'noisy'}
    assert ORDINAL == {'core': 0, 'mixed': 1, 'steep': 2, 'shallow': 3, 'noisy': 4}
    assert STRICT == {'quiet', 'noisy', 'mixed/increase_first/stable_mse', 'mixed/decrease_first/stable_mse',
                      'ramp_steep', 'ramp_shallow', 'ramp_noisy'}
    assert len(SPECS) == 15 and [len(KEYS[s]) for s in ('tuning', 'confirmation')] == [288, 192]
    assert all(len(GRIDS[a]) == 12 and len({json.dumps(c, sort_keys=True) for c in GRIDS[a]}) == 12 for a in FAMILIES)
    parts = list(SEEDS.values())
    assert all(min(s) >= 150000 and max(s) < 156000 for s in parts)
    assert all(not set(a)&set(b) for i, a in enumerate(parts) for b in parts[i+1:])
    for file in SOURCES:
        if not file.endswith('.py'): continue
        for node in ast.walk(ast.parse(Path(file).read_text())):
            names = [node.module] if isinstance(node, ast.ImportFrom) else [a.name for a in node.names] if isinstance(node, ast.Import) else []
            for name in names:
                if name and Path(name+'.py').exists(): assert name+'.py' in SOURCES, name
    values = np.random.default_rng(150001).normal(size=600)
    actual, expected = adwin_run(values[:, None], .1, 1), slow_adwin(values, .1, 1)
    for i, (a, b) in enumerate(zip(actual, expected)):
        a = a if i == 2 else a[:, 0]
        if i in (0, 2): np.testing.assert_allclose(a, b, rtol=1e-11, atol=1e-13)
        else: np.testing.assert_array_equal(a, b)
    # New-ramp fixtures against hand-computed values, events and noise.
    for name in ('core', 'mixed'):
        assert fixture(150001, name).y.shape == persistent_fixture(150001, name).y.shape
        np.testing.assert_array_equal(fixture(150001, name).y, persistent_fixture(150001, name).y)
    steep = fixture(150001, 'steep')
    start, end = steep.events[0][0][0], steep.events[0][1][0]
    assert steep.events[0][0][1] == 'drift_start' and steep.events[0][1][1] == 'drift_end'
    assert end-start == 500 and steep.coordinates == ('steep',)
    np.testing.assert_allclose(steep.target[start:end, 0], np.linspace(1., -1., 500, endpoint=False), rtol=1e-12)
    assert (steep.target[end:] == -1.).all() and (steep.target[:start] == 1.).all()
    shallow = fixture(150001, 'shallow')
    start, end = shallow.events[0][0][0], shallow.events[0][1][0]
    assert 3799 <= end-start <= 4000 and end < 6000
    np.testing.assert_allclose(shallow.target[start:end, 0], np.linspace(.5, -.5, end-start, endpoint=False), rtol=1e-12)
    assert (shallow.target[end:] == -.5).all()
    noisy = fixture(150001, 'noisy')
    start, end = noisy.events[0][0][0], noisy.events[0][1][0]
    assert 1800 <= end-start <= 2400
    np.testing.assert_allclose(noisy.target[start:end, 0], np.linspace(1., -1., end-start, endpoint=False), rtol=1e-12)
    assert abs((noisy.y[start:end, 0]-noisy.target[start:end, 0]).std()-.5) < .05
    steep_start = steep.events[0][0][0]
    assert abs((steep.y[steep_start-200:steep_start, 0]-steep.target[steep_start-200:steep_start, 0]).std()-.05) < .02
    for name in ('steep', 'shallow', 'noisy'):
        data = fixture(150002, name)
        assert data.y.shape == (6000, 1) and len(data.coordinates) == 1
        metrics = ramp_metrics(data, np.zeros_like(data.y), np.zeros(len(data.y)))
        start, end = data.events[0][0][0], data.events[0][1][0]
        assert metrics['coordinates'][name]['post_mse'] is None
        np.testing.assert_allclose(metrics['coordinates'][name]['ramp_mse'],
                                   float(((data.target[start:end, 0])**2).mean()), rtol=1e-12)
        np.testing.assert_allclose(metrics['coordinates'][name]['excess_mse'],
                                   float(((data.target[BURN:, 0])**2).mean()), rtol=1e-12)
    rejects(lambda: fixture(150001, 'unknown'))
    # Frozen candidate parity: identical calls through either study entry point.
    from study_v3_drift import enriched_schedule as enrich
    from study_v3_slope import entry_flags as entries
    from study_v3_slopebench import simulation as bench_simulation
    data = fixture(150002, 'core')
    _, via_bench = bench_simulation(150002, 'core', 'slope', dict(ESTIMATOR))
    direct = slope_run(data.y, 'slope', dict(ESTIMATOR), schedule=enrich(data), enter=entries(data))
    for a, b in zip(via_bench, direct):
        np.testing.assert_array_equal(np.asarray(a), np.asarray(b))
    # Parity, causal prefixes, independent coordinates, privilege isolation.
    y = np.random.default_rng(150000).normal(size=(500, 2))
    triggers = np.zeros_like(y); triggers[200] = 1.
    uniforms = random_uniforms(150000, 0, len(y), 2)
    for arm in ARMS:
        config = GRIDS[arm][3] if arm in FAMILIES else dict(ESTIMATOR) if arm in ('slope', 'random_slope') else {'keep': 4, 'window': 32}
        if arm in FAMILIES:
            kwargs = {}
        elif arm == 'random_slope':
            kwargs = {'uniforms': uniforms, 'probability': .01}
        else:
            kwargs = {'schedule': triggers, 'enter': np.zeros_like(triggers)} if arm == 'slope' else {'schedule': triggers}
        original = slope_run(y, arm, config, **kwargs)
        later = y.copy(); later[300:] += 5.
        changed = slope_run(later, arm, config, **kwargs)
        np.testing.assert_array_equal(np.asarray(original[0])[:301], np.asarray(changed[0])[:301])
        prefix_kwargs = {k: v[:300] if isinstance(v, np.ndarray) else v for k, v in kwargs.items()}
        for a, b in zip(slope_run(y[:300], arm, config, **prefix_kwargs), original):
            np.testing.assert_array_equal(np.asarray(a), np.asarray(b)[:300])
        other = y.copy(); other[:, 0] += 5.
        changed = slope_run(other, arm, config, **kwargs)
        indices = (0, 1, 3, 4, 5, 6, 7, 8) if len(original) == 9 else (0, 1, 3, 4)
        for i in indices: np.testing.assert_array_equal(np.asarray(original[i])[:, 1], np.asarray(changed[i])[:, 1])
        if arm in FAMILIES:
            rejects(lambda a=arm, c=config: slope_run(y, a, c, schedule=triggers))
    np.testing.assert_array_equal(uniforms[:200], random_uniforms(150000, 0, 200, 2))
    np.testing.assert_array_equal(uniforms[:, :1], random_uniforms(150000, 0, len(y), 1))
    assert not np.array_equal(uniforms, random_uniforms(150000, 1, len(y), 2))
    assert not np.array_equal(uniforms[:, 0], uniforms[:, 1])
    rejects(lambda: slope_run(np.full_like(y, np.nan), 'window', {'window': 16}))
    for name in FIXTURES:
        with patch('study_v3_slopebench.enriched_schedule', side_effect=AssertionError('evaluator access')):
            for arm in FAMILIES:
                simulation(150001, name, arm, GRIDS[arm][3])
    print('PASS slopebench kernels: new ramps, adapted metrics, frozen parity, causality, privilege isolation', flush=True)


def synthetic():
    coords = {'core': ('quiet', 'noisy', 'switch_quiet', 'switch_noisy'), 'mixed': ('increase_first', 'decrease_first'),
              'steep': ('steep',), 'shallow': ('shallow',), 'noisy': ('noisy',)}
    row = {'status': 'ok', 'config': {}, 'privileged_timing': False, 'fixtures': {}, 'memory': {}}
    for name, coordinates in coords.items():
        row['fixtures'][name] = {'coordinates': {}, 'update_norm_mean': .1, 'update_norm_sum': 600.}
        row['memory'][name] = {}
        for c in coordinates:
            kinds = ('target_down', 'target_up') if name == 'mixed' or c.startswith('switch_') else ('noise_increase', 'noise_decrease') if name == 'noise_jump' else ()
            row['fixtures'][name]['coordinates'][c] = {'excess_mse': 1., 'post_mse': 1. if kinds and kinds[0].startswith('target_') else None,
                'stable_mse': 1., 'adaptation_latency': 10. if kinds and kinds[0].startswith('target_') else None,
                'ramp_mse': 1. if name in ('steep', 'shallow', 'noisy') else None,
                'windows': {'noise_increase': 1., 'noise_decrease': 1., 'drift': 1.}}
            events = [{'index': 2000+2000*i, 'kind': k, 'hit': k.startswith('target_'), 'latency': 0 if k.startswith('target_') else 100} for i, k in enumerate(kinds)]
            row['memory'][name][c] = {'kind': 'window', 'reset_count': 2,
                'resets': [{'index': t, 'width_before': 32, 'width_after': 1, 'discarded': 32, 'kind': 'target'} for t in (2000, 4000)],
                'width_mean': 25., 'width_min': 1, 'width_max': 32, 'width_final': 32, 'total_discarded': 5968,
                'events': copy.deepcopy(events)}
    def adjust(r, arm):
        if arm == 'sgd':
            for f in r['memory'].values():
                for c in f.values():
                    c.update(kind='exponential', resets=[], reset_count=0)
                    c.update({k: None for k in ('width_mean', 'width_min', 'width_max', 'width_final', 'total_discarded')})
        if arm in ('slope', 'random_slope'):
            for f in r['memory'].values():
                for c in f.values():
                    if arm == 'random_slope':
                        for reset in c['resets']:
                            reset['kind'] = 'random'
                    c.update(kind='dual', adwin_width_mean=2000., adwin_width_min=1000,
                             adwin_width_max=3000, adwin_width_final=2000, adwin_total_discarded=4000,
                             regime_fast_share=.01, regime_slope_share=.4, slope_mean=-.001)
    tuning = {}
    for a in FAMILIES:
        for i, config in enumerate(GRIDS[a]):
            for seed in SEEDS['tuning']:
                r = copy.deepcopy(row); r.update(config=config, privileged_timing=False); adjust(r, a)
                tuning[f'{a}/{i}/{seed}'] = r
    manifest = make_manifest(tuning)
    confirmation = {}
    for a in ARMS:
        for seed in SEEDS['confirmation']:
            r = copy.deepcopy(row); adjust(r, a)
            r.update(config=manifest['screen']['selected'][a], privileged_timing=a not in FAMILIES, manifest_digest=digest(manifest))
            if a == 'slope':
                for f in r['fixtures'].values():
                    for c in f['coordinates'].values():
                        for k in ('excess_mse', 'post_mse', 'stable_mse', 'ramp_mse'):
                            if c[k] is not None: c[k] = .5
                        c['windows'] = {k: .5 for k in c['windows']}
            confirmation[f'{a}/{seed}'] = r
    return tuning, manifest, confirmation


def policy_checks():
    tuning, manifest, rows = synthetic()
    assert objective(tuning['window/0/151000']) == 1.
    assert all(i == 0 for i in manifest['screen']['indices'].values())
    assert manifest['screen']['selected']['oracle_nofallback'] == {'keep': 4, 'window': 32}
    assert manifest['screen']['selected']['slope'] == manifest['screen']['selected']['random_slope'] == dict(ESTIMATOR)
    assert manifest['screen']['random_frequency']['starts'] == 112
    assert manifest['screen']['random_frequency']['coordinate_time'] == 432000
    assert performance_decision(rows)['status'] == 'learning_positive' and len(performance_decision(rows)['cells']) == 75
    assert sum(1 for c in performance_decision(rows)['cells'].values() if c['mode'] == 'strict') == 7
    bad = copy.deepcopy(rows)
    for seed in SEEDS['confirmation']:
        for coord in bad[f'slope/{seed}']['fixtures']['steep']['coordinates'].values():
            coord['excess_mse'] = 0.
        for coord in bad[f'oracle_nofallback/{seed}']['fixtures']['steep']['coordinates'].values():
            coord['excess_mse'] = 0.
    repaired = performance_decision(bad)
    assert repaired['cells']['oracle_nofallback/ramp_steep']['mode'] == 'preserve'
    assert repaired['cells']['oracle_nofallback/ramp_steep']['pass']
    for control in ('window', 'sgd', 'adwin', 'random_slope', 'oracle_nofallback'):
        for label, fields in SPECS:
            bad = copy.deepcopy(rows)
            for seed in SEEDS['confirmation']:
                for n, c, f, w in fields:
                    dest = bad[f'{control}/{seed}']['fixtures'][n]['coordinates'][c]
                    if w: dest[f][w] = .01
                    else: dest[f] = .01
            result = performance_decision(bad)
            assert result['status'] == 'learning_negative' and not result['cells'][f'{control}/{label}']['pass']
    assert contrast([1.]*32, [.89]*32, 'improve')['pass'] and not contrast([1.]*32, [.91]*32, 'improve')['pass']
    assert not contrast([1.]*32, [1.101]*32, 'preserve')['pass']
    rejects(lambda: contrast([1., 2.], [1.], 'improve'))
    for key in ('adwin/153000', 'random_slope/153000', 'oracle_nofallback/153000', 'slope/153000'):
        rejects(lambda k=key: performance_decision({a: r for a, r in rows.items() if a != k}))
    bad = copy.deepcopy(rows)
    for seed in SEEDS['confirmation']: bad[f'slope/{seed}']['status'] = 'nonfinite'
    assert performance_decision(bad)['status'] == 'learning_negative'
    print('PASS slopebench policy: adapted menus, 75 vetoes, repaired rule on ramps', flush=True)


def lifecycle_checks():
    tuning, manifest, rows = synthetic()
    with tempfile.TemporaryDirectory() as tmp:
        directory = Path(tmp)
        def envelope(stage, data): write(directory/(stage+'.json'), {'protocol': PROTOCOL, 'sources': source_hashes(), 'rows': data})
        envelope('tuning', tuning); write(directory/'manifest.json', manifest)
        assert summarize(directory)['status'] == 'awaiting_confirmation'
        with patch('study_v3_slopebench.require_committed', side_effect=ValueError('uncommitted')): rejects(lambda: confirm(directory))
        with patch('study_v3_slopebench.require_committed'):
            assert verified_manifest(directory) == manifest
            changed = copy.deepcopy(manifest); changed['screen']['indices']['window'] = 5; write(directory/'manifest.json', changed)
            rejects(lambda: verified_manifest(directory)); write(directory/'manifest.json', manifest)
        envelope('confirmation', rows); publish_report(directory); publish_report(directory, True)
        rejects(lambda: tune(directory))
        broken = copy.deepcopy(rows); broken['random_slope/153000']['manifest_digest'] = 'wrong'
        envelope('confirmation', broken); rejects(lambda: read_stage(directory, 'confirmation'))
        envelope('confirmation', rows)
        raw = json.loads((directory/'confirmation.json').read_text()); raw['sources']['v3_adwin.py'] = 'wrong'
        write(directory/'confirmation.json', raw); rejects(lambda: read_stage(directory, 'confirmation'))
        broken = copy.deepcopy(rows); broken['slope/153000']['privileged_timing'] = False
        envelope('confirmation', broken); rejects(lambda: read_stage(directory, 'confirmation'))
        broken = copy.deepcopy(rows); broken['slope/153000']['memory']['steep']['steep']['resets'][0]['kind'] = 'random'
        rejects(lambda: absolute_summary(broken))
        broken = copy.deepcopy(rows); broken['slope/153000']['memory']['steep']['steep']['regime_slope_share'] = 2.
        rejects(lambda: absolute_summary(broken))
        envelope('confirmation', rows)
        for k in tuning:
            if k.startswith('window/'): tuning[k]['status'] = 'nonfinite'
        envelope('tuning', tuning); manifest = make_manifest(tuning); write(directory/'manifest.json', manifest)
        rejects(lambda: summarize(directory))
        with patch('study_v3_slopebench.require_committed'): rejects(lambda: confirm(directory))
        (directory/'confirmation.json').unlink()
        assert summarize(directory)['status'] == 'tuning_inconclusive'
        publish_report(directory); publish_report(directory, True)
    with tempfile.TemporaryDirectory(dir='.') as tmp:
        p = Path(tmp)/'uncommitted.json'; p.write_text('{}'); rejects(lambda: require_committed(p))
    for arm in ARMS:
        config = GRIDS[arm][0] if arm in FAMILIES else dict(ESTIMATOR) if arm in ('slope', 'random_slope') else {'keep': 4, 'window': 32}
        row = measure_row(150002, arm, config, .001 if arm == 'random_slope' else None)
        assert row['status'] == 'ok' and len(row['fixtures']) == 5
        assert row['privileged_timing'] == (arm not in FAMILIES)
    print('PASS slopebench lifecycle: ramp provenance, source/manifest/stage gates, complete reports, all-arm development fixtures', flush=True)


def archive_checks(directory, reproduce):
    stored = publish_report(directory, True)
    for path, expected in source_hashes().items():
        assert hashlib.sha256((directory/'source-snapshots'/(expected+'.txt')).read_bytes()).hexdigest() == expected, path
    manifest = json.loads((directory/'manifest.json').read_text()); tuning = read_stage(directory, 'tuning')
    assert manifest == make_manifest(tuning)
    print('PASS slopebench archive tuning', len(tuning), flush=True)
    if not reproduce:
        if stored['counts']['confirmation']: read_stage(directory, 'confirmation')
        return
    fresh = {}
    for arm in FAMILIES:
        for i, config in enumerate(GRIDS[arm]):
            for seed in SEEDS['tuning']:
                key = f'{arm}/{i}/{seed}'; fresh[key] = measure_row(seed, arm, config)
                compare(fresh[key], scientific(tuning[key]), key)
        print('PASS slopebench reproduction tuning', arm, '96 rows', flush=True)
    fresh_manifest = make_manifest(fresh); compare(fresh_manifest, manifest, ignore=('tuning_digest',))
    if stored['counts']['confirmation']:
        archived = read_stage(directory, 'confirmation'); recreated = {}
        for arm in ARMS:
            for seed in SEEDS['confirmation']:
                key = f'{arm}/{seed}'
                recreated[key] = measure_row(seed, arm, fresh_manifest['screen']['selected'][arm],
                    fresh_manifest['screen']['random_frequency']['probability'] if arm == 'random_slope' else None, fresh_manifest)
                compare(recreated[key], scientific(archived[key]), key, ignore=('manifest_digest',))
            print('PASS slopebench reproduction confirmation', arm, '32 rows', flush=True)
        compare(performance_decision(recreated), stored['decisions']['slope'])
        compare(absolute_summary(recreated), stored['absolute'])
    print('PASS full slopebench reproduction; only reached partitions sampled', flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--evidence', type=Path)
    parser.add_argument('--reproduce', action='store_true')
    args = parser.parse_args()
    kernel_checks(); policy_checks(); lifecycle_checks()
    if args.evidence: archive_checks(args.evidence, args.reproduce)
