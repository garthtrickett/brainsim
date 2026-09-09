"""Guard-regime equations, adapted-gate authority and full reproduction."""
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
from report_v3_slopeguard import absolute_summary, publish_report, summarize
from study_v3_slopeguard import (SOURCES, confirm, make_manifest, measure_row, read_stage,
    registration_check, require_committed, simulation, source_hashes, tune,
    verified_manifest, write)
from v3_adwin import run as adwin_run
from v3_forgetting import run as forget_run
from v3_retention import dual_run
from v3_slope import compose as slope_compose
from v3_slopebench import FIXTURES, fixture, ramp_metrics
from v3_slopebench_policy import SPECS, STRICT
from v3_slopeguard import ARMS, FAMILIES, FAST, GRIDS, compose, random_uniforms, run
from v3_slopeguard_policy import (KEYS, PROTOCOL, SEEDS, complete, contrast,
    digest, metric_values, objective, performance_decision, scientific, select)
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
    assert FAST == {'keep': 4, 'window': 32}
    assert [c['J'] for c in GRIDS['guard']] == [0, 48, 64, 96, 128, 192, 256, 384, 512, 1024, 2048, 6000]
    assert len(SPECS) == 15 and [len(KEYS[s]) for s in ('tuning', 'confirmation')] == [384, 224]
    assert all(len(GRIDS[a]) == 12 and len({json.dumps(c, sort_keys=True) for c in GRIDS[a]}) == 12 for a in FAMILIES)
    assert STRICT == {'quiet', 'noisy', 'mixed/increase_first/stable_mse', 'mixed/decrease_first/stable_mse',
                      'ramp_steep', 'ramp_shallow', 'ramp_noisy'}
    parts = list(SEEDS.values())
    assert all(min(s) >= 160000 and max(s) < 166000 for s in parts)
    assert all(not set(a)&set(b) for i, a in enumerate(parts) for b in parts[i+1:])
    for file in SOURCES:
        if not file.endswith('.py'): continue
        for node in ast.walk(ast.parse(Path(file).read_text())):
            names = [node.module] if isinstance(node, ast.ImportFrom) else [a.name for a in node.names] if isinstance(node, ast.Import) else []
            for name in names:
                if name and Path(name+'.py').exists(): assert name+'.py' in SOURCES, name
    values = np.random.default_rng(160001).normal(size=600)
    actual, expected = adwin_run(values[:, None], .1, 1), slow_adwin(values, .1, 1)
    for i, (a, b) in enumerate(zip(actual, expected)):
        a = a if i == 2 else a[:, 0]
        if i in (0, 2): np.testing.assert_allclose(a, b, rtol=1e-11, atol=1e-13)
        else: np.testing.assert_array_equal(a, b)
    # Guard regime: J=0 is slope-study behavior; guard overrides trend near boundaries.
    y = np.random.default_rng(160000).normal(size=(500, 2))
    entered = np.zeros_like(y); entered[100, 0] = 1.
    starts = np.zeros_like(y); starts[[100, 300], 0] = 1.
    for a, b in zip(compose(y, starts, entered, 0)[0],
                     slope_compose(y, starts, entered, {'method': 'ols', 'W': 128})[0]):
        np.testing.assert_array_equal(a, b)
        np.testing.assert_array_equal(a, b)
    guarded = compose(y, starts, entered, 96)
    assert (guarded[7][101:196, 0] == 3).all() and (guarded[7][197:300, 0] == 2).all()
    assert (guarded[7][301:332, 0] == 1).all() and (guarded[7][333:, 0] == 0).all()
    assert guarded[7][100, 0] != 2 and guarded[7][300, 0] == 2
    assert (guarded[7][:, 1] == 0).all()
    wide = compose(y, starts, entered, 6000)
    assert (wide[7][101:, 0] != 2).all()
    # Frozen parity: delegations and estimator reuse.
    triggers = np.zeros_like(y); triggers[200] = 1.
    for a, b in zip(run(y, 'oracle_nofallback', dict(FAST), schedule=triggers),
                     forget_run(y, 'oracle_matched', dict(FAST), triggers=triggers)):
        np.testing.assert_array_equal(a, b)
    for a, b in zip(run(y, 'window', {'window': 16}), forget_run(y, 'window', {'window': 16})):
        np.testing.assert_array_equal(a, b)
    for a, b in zip(run(y, 'sgd', {'lr': .128})[:3], plain_run(y, 'sgd', {'lr': .128})):
        np.testing.assert_array_equal(a, b)
    # Parity, causal prefixes, independent coordinates, privilege isolation.
    uniforms = random_uniforms(160000, 0, len(y), 2)
    for arm in ARMS:
        config = GRIDS[arm][3] if arm in FAMILIES else {'J': 0} if arm == 'reference' else (
            dict(FAST) if arm == 'oracle_nofallback' else dict(GRIDS['guard'][3]))
        if arm in ('window', 'sgd', 'adwin'):
            kwargs = {}
        elif arm == 'random_guard':
            kwargs = {'uniforms': uniforms, 'probability': .01}
        else:
            kwargs = {'schedule': triggers, 'enter': np.zeros_like(triggers)} if arm in ('guard', 'reference') else {'schedule': triggers}
        original = run(y, arm, config, **kwargs)
        later = y.copy(); later[300:] += 5.
        changed = run(later, arm, config, **kwargs)
        np.testing.assert_array_equal(np.asarray(original[0])[:301], np.asarray(changed[0])[:301])
        prefix_kwargs = {k: v[:300] if isinstance(v, np.ndarray) else v for k, v in kwargs.items()}
        for a, b in zip(run(y[:300], arm, config, **prefix_kwargs), original):
            np.testing.assert_array_equal(np.asarray(a), np.asarray(b)[:300])
        other = y.copy(); other[:, 0] += 5.
        changed = run(other, arm, config, **kwargs)
        indices = (0, 1, 3, 4, 5, 6, 7, 8) if len(original) == 9 else (0, 1, 3, 4)
        for i in indices: np.testing.assert_array_equal(np.asarray(original[i])[:, 1], np.asarray(changed[i])[:, 1])
        if arm in ('window', 'sgd', 'adwin'):
            rejects(lambda a=arm, c=config: run(y, a, c, schedule=triggers))
    np.testing.assert_array_equal(uniforms[:200], random_uniforms(160000, 0, 200, 2))
    np.testing.assert_array_equal(uniforms[:, :1], random_uniforms(160000, 0, len(y), 1))
    assert not np.array_equal(uniforms, random_uniforms(160000, 1, len(y), 2))
    assert not np.array_equal(uniforms[:, 0], uniforms[:, 1])
    rejects(lambda: run(y, 'guard', {'J': -1}, schedule=triggers, enter=np.zeros_like(triggers)))
    rejects(lambda: run(y, 'guard', {'J': 32.5}, schedule=triggers, enter=np.zeros_like(triggers)))
    rejects(lambda: run(y, 'reference', {'J': 64}, schedule=triggers, enter=np.zeros_like(triggers)))
    rejects(lambda: run(np.full_like(y, np.nan), 'window', {'window': 16}))
    rejects(lambda: run(y, 'guard', {'J': 64}))
    for name in FIXTURES:
        from v3_slopebench import fixture as bench_fixture
        data = bench_fixture(160001, name)
        with patch('study_v3_slopeguard.enriched_schedule', side_effect=AssertionError('evaluator access')):
            for arm in ('window', 'sgd', 'adwin'):
                simulation(160001, name, arm, GRIDS[arm][3])
    print('PASS slopeguard kernels: guard regimes, J=0 identity, frozen parity, causality, privilege isolation', flush=True)


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
        if arm in ('guard', 'random_guard'):
            for f in r['memory'].values():
                for c in f.values():
                    if arm == 'random_guard':
                        for reset in c['resets']:
                            reset['kind'] = 'random'
                    c.update(kind='dual', adwin_width_mean=2000., adwin_width_min=1000,
                             adwin_width_max=3000, adwin_width_final=2000, adwin_total_discarded=4000,
                             regime_fast_share=.01, regime_guard_share=.05, regime_slope_share=.4, slope_mean=-.001)
    tuning = {}
    for a in FAMILIES:
        for i, config in enumerate(GRIDS[a]):
            for seed in SEEDS['tuning']:
                r = copy.deepcopy(row); r.update(config=config, privileged_timing=a not in ('window', 'sgd', 'adwin')); adjust(r, a)
                tuning[f'{a}/{i}/{seed}'] = r
    manifest = make_manifest(tuning)
    confirmation = {}
    for a in ARMS:
        for seed in SEEDS['confirmation']:
            r = copy.deepcopy(row); adjust(r, a)
            r.update(config=manifest['screen']['selected'][a], privileged_timing=a not in ('window', 'sgd', 'adwin'), manifest_digest=digest(manifest))
            if a == 'guard':
                for f in r['fixtures'].values():
                    for c in f['coordinates'].values():
                        for k in ('excess_mse', 'post_mse', 'stable_mse', 'ramp_mse'):
                            if c[k] is not None: c[k] = .5
                        c['windows'] = {k: .5 for k in c['windows']}
            confirmation[f'{a}/{seed}'] = r
    return tuning, manifest, confirmation


def policy_checks():
    tuning, manifest, rows = synthetic()
    assert objective(tuning['guard/0/161000']) == 1.
    assert all(i == 0 for i in manifest['screen']['indices'].values())
    assert manifest['screen']['selected']['oracle_nofallback'] == dict(FAST)
    assert manifest['screen']['selected']['reference'] == {'J': 0}
    assert manifest['screen']['selected']['random_guard'] == manifest['screen']['selected']['guard']
    assert manifest['screen']['random_frequency']['starts'] == 144 and manifest['screen']['random_frequency']['coordinate_time'] == 432000
    assert performance_decision(rows)['status'] == 'learning_positive' and len(performance_decision(rows)['cells']) == 75
    assert sum(1 for c in performance_decision(rows)['cells'].values() if c['mode'] == 'strict') == 7
    bad = copy.deepcopy(rows)
    for seed in SEEDS['confirmation']:
        for coord in bad[f'guard/{seed}']['fixtures']['steep']['coordinates'].values():
            coord['excess_mse'] = 0.
        for coord in bad[f'oracle_nofallback/{seed}']['fixtures']['steep']['coordinates'].values():
            coord['excess_mse'] = 0.
    repaired = performance_decision(bad)
    assert repaired['cells']['oracle_nofallback/ramp_steep']['mode'] == 'preserve'
    assert repaired['cells']['oracle_nofallback/ramp_steep']['pass']
    bad = copy.deepcopy(tuning); bad['guard/0/161000']['status'] = 'nonfinite'
    assert select(bad)['indices']['guard'] == 1
    for k in bad:
        if k.startswith('guard/'): bad[k]['status'] = 'nonfinite'
    assert select(bad)['status'] == 'tuning_inconclusive'
    rejects(lambda: complete({k: r for k, r in tuning.items() if k != 'guard/0/161000'}, 'tuning'))
    for control in ('window', 'sgd', 'adwin', 'random_guard', 'oracle_nofallback'):
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
    for key in ('adwin/163000', 'random_guard/163000', 'oracle_nofallback/163000', 'guard/163000'):
        rejects(lambda k=key: performance_decision({a: r for a, r in rows.items() if a != k}))
    bad = copy.deepcopy(rows)
    for seed in SEEDS['confirmation']: bad[f'guard/{seed}']['status'] = 'nonfinite'
    assert performance_decision(bad)['status'] == 'learning_negative'
    print('PASS slopeguard policy: frozen menus, 75 vetoes, repaired rule on ramps', flush=True)


def lifecycle_checks():
    tuning, manifest, rows = synthetic()
    with tempfile.TemporaryDirectory() as tmp:
        directory = Path(tmp)
        def envelope(stage, data): write(directory/(stage+'.json'), {'protocol': PROTOCOL, 'sources': source_hashes(), 'rows': data})
        envelope('tuning', tuning); write(directory/'manifest.json', manifest)
        assert summarize(directory)['status'] == 'awaiting_confirmation'
        with patch('study_v3_slopeguard.require_committed', side_effect=ValueError('uncommitted')): rejects(lambda: confirm(directory))
        with patch('study_v3_slopeguard.require_committed'):
            assert verified_manifest(directory) == manifest
            changed = copy.deepcopy(manifest); changed['screen']['indices']['guard'] = 5; write(directory/'manifest.json', changed)
            rejects(lambda: verified_manifest(directory)); write(directory/'manifest.json', manifest)
        envelope('confirmation', rows); publish_report(directory); publish_report(directory, True)
        rejects(lambda: tune(directory))
        broken = copy.deepcopy(rows); broken['random_guard/163000']['manifest_digest'] = 'wrong'
        envelope('confirmation', broken); rejects(lambda: read_stage(directory, 'confirmation'))
        envelope('confirmation', rows)
        raw = json.loads((directory/'confirmation.json').read_text()); raw['sources']['v3_adwin.py'] = 'wrong'
        write(directory/'confirmation.json', raw); rejects(lambda: read_stage(directory, 'confirmation'))
        broken = copy.deepcopy(rows); broken['guard/163000']['privileged_timing'] = False
        envelope('confirmation', broken); rejects(lambda: read_stage(directory, 'confirmation'))
        broken = copy.deepcopy(rows); broken['guard/163000']['memory']['steep']['steep']['resets'][0]['kind'] = 'random'
        rejects(lambda: absolute_summary(broken))
        broken = copy.deepcopy(rows); broken['guard/163000']['memory']['steep']['steep']['regime_guard_share'] = 2.
        rejects(lambda: absolute_summary(broken))
        envelope('confirmation', rows)
        for k in tuning:
            if k.startswith('guard/'): tuning[k]['status'] = 'nonfinite'
        envelope('tuning', tuning); manifest = make_manifest(tuning); write(directory/'manifest.json', manifest)
        rejects(lambda: summarize(directory))
        with patch('study_v3_slopeguard.require_committed'): rejects(lambda: confirm(directory))
        (directory/'confirmation.json').unlink()
        assert summarize(directory)['status'] == 'tuning_inconclusive'
        publish_report(directory); publish_report(directory, True)
    with tempfile.TemporaryDirectory(dir='.') as tmp:
        p = Path(tmp)/'uncommitted.json'; p.write_text('{}'); rejects(lambda: require_committed(p))
    for arm in ARMS:
        config = GRIDS[arm][0] if arm in FAMILIES else {'J': 0} if arm == 'reference' else (
            dict(FAST) if arm == 'oracle_nofallback' else dict(GRIDS['guard'][0]))
        row = measure_row(160002, arm, config, .001 if arm == 'random_guard' else None)
        assert row['status'] == 'ok' and len(row['fixtures']) == 5
        assert row['privileged_timing'] == (arm not in ('window', 'sgd', 'adwin'))
    print('PASS slopeguard lifecycle: ramp provenance, source/manifest/stage gates, complete reports, all-arm development fixtures', flush=True)


def archive_checks(directory, reproduce):
    stored = publish_report(directory, True)
    for path, expected in source_hashes().items():
        assert hashlib.sha256((directory/'source-snapshots'/(expected+'.txt')).read_bytes()).hexdigest() == expected, path
    manifest = json.loads((directory/'manifest.json').read_text()); tuning = read_stage(directory, 'tuning')
    assert manifest == make_manifest(tuning)
    print('PASS slopeguard archive tuning', len(tuning), flush=True)
    if not reproduce:
        if stored['counts']['confirmation']: read_stage(directory, 'confirmation')
        return
    fresh = {}
    for arm in FAMILIES:
        for i, config in enumerate(GRIDS[arm]):
            for seed in SEEDS['tuning']:
                key = f'{arm}/{i}/{seed}'; fresh[key] = measure_row(seed, arm, config)
                compare(fresh[key], scientific(tuning[key]), key)
        print('PASS slopeguard reproduction tuning', arm, '96 rows', flush=True)
    fresh_manifest = make_manifest(fresh); compare(fresh_manifest, manifest, ignore=('tuning_digest',))
    if stored['counts']['confirmation']:
        archived = read_stage(directory, 'confirmation'); recreated = {}
        for arm in ARMS:
            for seed in SEEDS['confirmation']:
                key = f'{arm}/{seed}'
                recreated[key] = measure_row(seed, arm, fresh_manifest['screen']['selected'][arm],
                    fresh_manifest['screen']['random_frequency']['probability'] if arm == 'random_guard' else None, fresh_manifest)
                compare(recreated[key], scientific(archived[key]), key, ignore=('manifest_digest',))
            print('PASS slopeguard reproduction confirmation', arm, '32 rows', flush=True)
        compare(performance_decision(recreated), stored['decisions']['guard'])
        compare(absolute_summary(recreated), stored['absolute'])
    print('PASS full slopeguard reproduction; only reached partitions sampled', flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--evidence', type=Path)
    parser.add_argument('--reproduce', action='store_true')
    args = parser.parse_args()
    kernel_checks(); policy_checks(); lifecycle_checks()
    if args.evidence: archive_checks(args.evidence, args.reproduce)
