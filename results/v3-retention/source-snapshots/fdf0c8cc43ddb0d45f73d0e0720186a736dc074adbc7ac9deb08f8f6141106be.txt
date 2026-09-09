"""Dual-state equations, three-mode authority and full reproduction."""
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
from report_v3_retention import absolute_summary, publish_report, summarize
from study_v3_retention import (SOURCES, confirm, make_manifest, measure_row, oracle_triggers,
    read_stage, registration_check, require_committed, simulation, source_hashes, tune,
    verified_manifest, write)
from v3_adwin import combine, run as adwin_run
from v3_burst import pulse_schedule
from v3_forgetting import run as forget_run
from v3_retention import (ARMS, FAMILIES, FAST, GRIDS, dual_run, random_probability,
                          random_uniforms, request_schedule, run, window_kernel)
from v3_retention_policy import (KEYS, PROTOCOL, SEEDS, SPECS, STRICT, complete, contrast,
    digest, metric_values, objective, performance_decision, scientific, select)
from v3_persistent import FIXTURES, fixture
from v3_slice1_learning import run as plain_run


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
        assert all(sum(len(b) == size for b in buckets) <= 5 for size in {len(b) for b in buckets})
        assert all(len(b) & (len(b)-1) == 0 for b in buckets)
    return (np.array(predictions), np.array(flags), np.abs(np.array(means)-predictions),
            np.array(widths), np.array(removed))


def kernel_checks():
    registration_check()
    assert len(SPECS) == 15 and [len(KEYS[s]) for s in ('tuning', 'confirmation')] == [384, 192]
    assert all(len(GRIDS[a]) == 12 and len({json.dumps(c, sort_keys=True) for c in GRIDS[a]}) == 12 for a in FAMILIES)
    assert [c['H'] for c in GRIDS['retain']] == [h for _ in (.001, .01, .1) for h in (32, 512, 2048, 6000)]
    assert sorted({c['delta'] for c in GRIDS['retain']}) == [.001, .01, .1]
    assert STRICT == {'quiet', 'noisy', 'noise_jump', 'exactly_quiet', 'noise_jump/noise_increase',
                      'noise_jump/noise_decrease', 'mixed/increase_first/stable_mse', 'mixed/decrease_first/stable_mse'}
    parts = list(SEEDS.values())
    assert all(min(s) >= 100000 and max(s) < 106000 for s in parts)
    assert all(not set(a)&set(b) for i, a in enumerate(parts) for b in parts[i+1:])
    for file in SOURCES:
        if not file.endswith('.py'): continue
        for node in ast.walk(ast.parse(Path(file).read_text())):
            names = [node.module] if isinstance(node, ast.ImportFrom) else [a.name for a in node.names] if isinstance(node, ast.Import) else []
            for name in names:
                if name and Path(name+'.py').exists(): assert name+'.py' in SOURCES, name
    # Slice-based reference maintains the ACTUAL retained samples after each request.
    y = np.random.default_rng(100000).normal(size=(500, 2))
    flags = np.zeros_like(y); flags[[3, 4, 8, 90, 149, 150, 200, 202, 490], 0] = 1.; flags[[170, 350], 1] = 1.
    for keep, cap in ((1, 1), (1, 32), (4, 128), (16, 32), (16, 6000)):
        actual = window_kernel(y, flags, keep, cap)
        expected, means = np.zeros_like(y), np.zeros_like(y)
        widths, discarded = np.zeros_like(y, dtype=int), np.zeros_like(y, dtype=int)
        for j in range(2):
            retained, value = [], 0.
            for t in range(len(y)):
                expected[t, j] = value
                before = len(retained)
                retained = (retained+[y[t, j]])[-cap:]
                if flags[t, j]: retained = retained[-keep:]
                value = float(np.mean(retained)); means[t, j] = value
                widths[t, j] = len(retained); discarded[t, j] = before+1-len(retained)
        np.testing.assert_allclose(actual[0], expected, rtol=1e-11, atol=1e-13)
        np.testing.assert_array_equal(actual[1], flags)
        np.testing.assert_allclose(actual[2], np.linalg.norm(means-expected, axis=1), rtol=1e-11, atol=1e-13)
        np.testing.assert_array_equal(actual[3], widths); np.testing.assert_array_equal(actual[4], discarded)
        assert np.all(widths[-1]+actual[4].sum(axis=0) == len(y))
    # From-t0 request scheduler: passthrough unsuppressed, 16-update suppression otherwise.
    binary = np.zeros((300, 2)); binary[[10, 15, 200], 0] = 1.; binary[50, 1] = 1.
    np.testing.assert_array_equal(request_schedule(binary, 0), binary)
    suppressed = request_schedule(binary, 16)
    assert np.flatnonzero(suppressed[:, 0]).tolist() == [10, 200]
    assert np.flatnonzero(suppressed[:, 1]).tolist() == [50]
    resume = np.zeros((300, 1)); resume[[10, 27], 0] = 1.
    assert np.flatnonzero(request_schedule(resume, 16)[:, 0]).tolist() == [10, 27]
    late = np.zeros((300, 2)); late[[200, 250], 0] = 1.
    np.testing.assert_array_equal(request_schedule(late, 16), pulse_schedule(late, 1, False)[1])
    early = np.zeros((300, 2)); early[[10, 200], 0] = 1.
    assert not np.array_equal(request_schedule(early, 16), pulse_schedule(early, 1, False)[1])
    assert np.flatnonzero(request_schedule(early, 16)[:, 0]).tolist() == [10, 200]
    np.testing.assert_allclose(random_probability(1, 17, 1), 1., rtol=1e-14)
    assert abs(random_probability(10, 1000, 1)-.01/.84) < 1e-14
    rejects(lambda: random_probability(2, 17, 1))
    # Independent arithmetic checks for centered-moment merges.
    x = np.array([1., 3., 8.]); z = np.array([-2., 6.])
    n, total, m2 = combine(len(x), x.sum(), ((x-x.mean())**2).sum(), len(z), z.sum(), ((z-z.mean())**2).sum())
    merged = np.r_[x, z]
    assert n == len(merged) and total == merged.sum()
    np.testing.assert_allclose(m2, ((merged-merged.mean())**2).sum(), rtol=1e-13)
    streams = [np.r_[np.zeros(180), np.ones(180), np.zeros(180)],
               np.random.default_rng(100001).normal(size=600),
               np.r_[np.ones(180), np.linspace(1., -1., 180), np.full(180, -1.)]]
    shrinking = False
    for values in streams:
        for delta, clock in ((.1, 1), (.001, 8), (.01, 32)):
            actual = adwin_run(values[:, None], delta, clock)
            expected = slow_adwin(values, delta, clock)
            for i, (a, b) in enumerate(zip(actual, expected)):
                a = a if i == 2 else a[:, 0]
                if i in (0, 2): np.testing.assert_allclose(a, b, rtol=1e-11, atol=1e-13)
                else: np.testing.assert_array_equal(a, b)
            shrinking = shrinking or actual[1].any()
            np.testing.assert_array_equal(actual[3][:, 0], np.arange(1, len(values)+1)-np.cumsum(actual[4][:, 0]))
            np.testing.assert_array_equal(actual[1][:, 0], actual[4][:, 0] > 0)
    assert shrinking
    # Dual-state composition: regime boundary, slow/fast endpoints, frozen parity.
    stepped = np.zeros((400, 1)); stepped[200:] = 5.
    alone = np.zeros((400, 1)); alone[200, 0] = 1.
    result = dual_run(stepped, request_schedule(alone, 0), .1, 32)
    assert result[7][:200].sum() == 0 and result[7][200:233].sum() == 32 and result[7][233:].sum() == 0
    np.testing.assert_array_equal(result[0][:200, 0], adwin_run(stepped[:200], .1, 1)[0][:, 0])
    np.testing.assert_array_equal(result[0][201:233, 0], window_kernel(stepped, alone, 4, 32)[0][201:233, 0])
    np.testing.assert_array_equal(result[5], adwin_run(stepped, .1, 1)[3])
    np.testing.assert_array_equal(result[6], adwin_run(stepped, .1, 1)[4])
    quiet = dual_run(stepped, np.zeros_like(stepped), .1, 6000)
    np.testing.assert_array_equal(quiet[0][:, 0], adwin_run(stepped, .1, 1)[0][:, 0])
    assert not quiet[7].any()
    keeps = dual_run(stepped, alone, .1, 6000)[0][201, 0]
    assert keeps == np.mean([0.]*3+[5.])
    always = dual_run(stepped, alone, .1, 6000)
    np.testing.assert_allclose(always[2][201:232], np.abs(always[0][202:233, 0]-always[0][201:232, 0]),
                               rtol=1e-9, atol=1e-11)
    triggers = np.zeros_like(y); triggers[200] = 1.
    for a, b in zip(run(y, 'oracle_nofallback', dict(FAST), triggers=triggers),
                     forget_run(y, 'oracle_matched', dict(FAST), triggers=triggers)):
        np.testing.assert_array_equal(a, b)
    # Parity, causal prefixes, independent coordinates, privilege isolation.
    uniforms = random_uniforms(100000, 0, len(y), 2)
    for arm in ARMS:
        config = GRIDS[arm][3] if arm in FAMILIES else dict(FAST) if arm == 'oracle_nofallback' else dict(GRIDS['retain'][3])
        kwargs = {'triggers': triggers} if arm in ('retain', 'oracle_nofallback') else (
            {'uniforms': uniforms, 'probability': .01} if arm == 'random_fallback' else {})
        original = run(y, arm, config, **kwargs)
        later = y.copy(); later[300:] += 5.
        changed = run(later, arm, config, **kwargs)
        np.testing.assert_array_equal(original[0][:301], changed[0][:301])
        prefix_kwargs = {k: v[:300] if isinstance(v, np.ndarray) else v for k, v in kwargs.items()}
        for a, b in zip(run(y[:300], arm, config, **prefix_kwargs), original): np.testing.assert_array_equal(np.asarray(a), np.asarray(b)[:300])
        other = y.copy(); other[:, 0] += 5.
        changed = run(other, arm, config, **kwargs)
        indices = (0, 1, 3, 4, 5, 6, 7) if len(original) == 8 else (0, 1, 3, 4)
        for i in indices: np.testing.assert_array_equal(np.asarray(original[i])[:, 1], np.asarray(changed[i])[:, 1])
        if arm not in ('retain', 'oracle_nofallback'):
            rejects(lambda a=arm, c=config: run(y, a, c, triggers=triggers))
    np.testing.assert_array_equal(uniforms[:200], random_uniforms(100000, 0, 200, 2))
    np.testing.assert_array_equal(uniforms[:, :1], random_uniforms(100000, 0, len(y), 1))
    assert not np.array_equal(uniforms, random_uniforms(100000, 1, len(y), 2))
    assert not np.array_equal(uniforms[:, 0], uniforms[:, 1])
    rejects(lambda: run(y, 'retain', {'delta': .1, 'H': 0}, triggers=triggers))
    rejects(lambda: run(y, 'retain', {'delta': 2., 'H': 32}, triggers=triggers))
    rejects(lambda: run(y, 'oracle_nofallback', {'keep': 4, 'window': 64}, triggers=triggers))
    rejects(lambda: run(np.full_like(y, np.nan), 'window', {'window': 16}))
    rejects(lambda: run(y, 'retain', {'delta': .1, 'H': 32}))
    rejects(lambda: run(y, 'random_fallback', GRIDS['retain'][0], uniforms=uniforms, probability=2.))
    for name in FIXTURES:
        data = fixture(100001, name)
        marked = oracle_triggers(data)
        assert {tuple(v) for v in np.argwhere(marked)} == {(t, j) for j, ev in enumerate(data.events) for t, k in ev if k.startswith('target_')}
        with patch('study_v3_retention.oracle_triggers', side_effect=AssertionError('privileged access')):
            for arm in ('window', 'sgd', 'adwin', 'random_fallback'):
                simulation(100001, name, arm, GRIDS[arm][3] if arm in FAMILIES else dict(GRIDS['retain'][3]),
                           .01 if arm == 'random_fallback' else None)
    print('PASS retention kernels: dual-state composition, H boundaries, frozen parity, causality, privilege isolation and frequency', flush=True)


def synthetic():
    coords = {'core': ('quiet', 'noisy', 'switch_quiet', 'switch_noisy'), 'mixed': ('increase_first', 'decrease_first'),
              'noise_jump': ('noise_jump',), 'drift': ('drift',), 'exactly_quiet': ('exactly_quiet',)}
    row = {'status': 'ok', 'config': {}, 'privileged_timing': False, 'fixtures': {}, 'memory': {}}
    for name, coordinates in coords.items():
        row['fixtures'][name] = {'coordinates': {}, 'update_norm_mean': .1, 'update_norm_sum': 600.}
        row['memory'][name] = {}
        for c in coordinates:
            kinds = ('target_down', 'target_up') if name == 'mixed' or c.startswith('switch_') else ('noise_increase', 'noise_decrease') if name == 'noise_jump' else ()
            row['fixtures'][name]['coordinates'][c] = {'excess_mse': 1., 'post_mse': 1. if kinds and kinds[0].startswith('target_') else None,
                'stable_mse': 1., 'adaptation_latency': 10. if kinds and kinds[0].startswith('target_') else None,
                'windows': {'noise_increase': 1., 'noise_decrease': 1., 'drift': 1.}}
            events = [{'index': 2000+2000*i, 'kind': k, 'hit': k.startswith('target_'), 'latency': 0 if k.startswith('target_') else 100} for i, k in enumerate(kinds)]
            record = {'kind': 'window', 'reset_count': 2,
                'resets': [{'index': t, 'width_before': 32, 'width_after': 1, 'discarded': 32} for t in (2000, 4000)],
                'width_mean': 25., 'width_min': 1, 'width_max': 32, 'width_final': 32, 'total_discarded': 5968, 'events': copy.deepcopy(events)}
            row['memory'][name][c] = record
    def adjust(r, arm):
        if arm == 'sgd':
            for f in r['memory'].values():
                for c in f.values():
                    c.update(kind='exponential', resets=[], reset_count=0)
                    c.update({k: None for k in ('width_mean', 'width_min', 'width_max', 'width_final', 'total_discarded')})
        if arm in ('retain', 'random_fallback'):
            for f in r['memory'].values():
                for c in f.values():
                    c.update(kind='dual', adwin_width_mean=2000., adwin_width_min=1000,
                             adwin_width_max=3000, adwin_width_final=2000, adwin_total_discarded=4000,
                             regime_fast_share=.5)
    tuning = {}
    for a in FAMILIES:
        for i, config in enumerate(GRIDS[a]):
            for seed in SEEDS['tuning']:
                r = copy.deepcopy(row); r.update(config=config, privileged_timing=a == 'retain'); adjust(r, a)
                tuning[f'{a}/{i}/{seed}'] = r
    manifest = make_manifest(tuning)
    confirmation = {}
    for a in ARMS:
        for seed in SEEDS['confirmation']:
            r = copy.deepcopy(row); adjust(r, a)
            r.update(config=manifest['screen']['selected'][a], privileged_timing=a in ('retain', 'oracle_nofallback'), manifest_digest=digest(manifest))
            if a == 'retain':
                for f in r['fixtures'].values():
                    for c in f['coordinates'].values():
                        for k in ('excess_mse', 'post_mse', 'stable_mse'):
                            if c[k] is not None: c[k] = .5
                        c['windows'] = {k: .5 for k in c['windows']}
            confirmation[f'{a}/{seed}'] = r
    return tuning, manifest, confirmation


def policy_checks():
    tuning, manifest, rows = synthetic()
    assert objective(tuning['retain/0/101000']) == 1.
    assert all(i == 0 for i in manifest['screen']['indices'].values())
    screen = manifest['screen']
    assert screen['selected']['random_fallback'] == screen['selected']['retain']
    assert screen['selected']['oracle_nofallback'] == dict(FAST)
    assert screen['random_frequency']['starts'] == 144 and screen['random_frequency']['coordinate_time'] == 432000
    bad = copy.deepcopy(tuning); bad['retain/0/101000']['status'] = 'nonfinite'
    assert select(bad)['indices']['retain'] == 1
    for k in bad:
        if k.startswith('retain/'): bad[k]['status'] = 'nonfinite'
    assert select(bad)['status'] == 'tuning_inconclusive'
    rejects(lambda: complete({k: r for k, r in tuning.items() if k != 'retain/0/101000'}, 'tuning'))
    bad = copy.deepcopy(tuning); bad['retain/0/101000']['fixtures']['core']['coordinates']['quiet']['excess_mse'] = float('nan')
    rejects(lambda: select(bad))
    assert performance_decision(rows)['status'] == 'learning_positive' and len(performance_decision(rows)['cells']) == 75
    assert sum(1 for k, c in performance_decision(rows)['cells'].items() if c['mode'] == 'strict') == 8
    for control in ('window', 'sgd', 'adwin', 'random_fallback', 'oracle_nofallback'):
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
    assert contrast([1.]*32, [1.]*32, 'preserve')['pass'] and not contrast([1.]*32, [1.]*32, 'strict')['pass']
    assert contrast([1.]*32, [.5]*32, 'strict')['pass']
    rejects(lambda: contrast([1., 2.], [1.], 'improve'))
    rejects(lambda: contrast([1.]*32, [1.]*32, 'benefit'))
    for key in ('adwin/103000', 'random_fallback/103000', 'oracle_nofallback/103000', 'retain/103000'):
        rejects(lambda k=key: performance_decision({a: r for a, r in rows.items() if a != k}))
    bad = copy.deepcopy(rows)
    for seed in SEEDS['confirmation']: bad[f'retain/{seed}']['status'] = 'nonfinite'
    assert performance_decision(bad)['status'] == 'learning_negative'
    print('PASS retention policy: equal menus/objective, finite selection, all75 vetoes with strict ablation cells', flush=True)


def lifecycle_checks():
    tuning, manifest, rows = synthetic()
    with tempfile.TemporaryDirectory() as tmp:
        directory = Path(tmp)
        def envelope(stage, data): write(directory/(stage+'.json'), {'protocol': PROTOCOL, 'sources': source_hashes(), 'rows': data})
        envelope('tuning', tuning); write(directory/'manifest.json', manifest)
        assert summarize(directory)['status'] == 'awaiting_confirmation'
        with patch('study_v3_retention.require_committed', side_effect=ValueError('uncommitted')): rejects(lambda: confirm(directory))
        with patch('study_v3_retention.require_committed'):
            assert verified_manifest(directory) == manifest
            changed = copy.deepcopy(manifest); changed['screen']['indices']['retain'] = 5; write(directory/'manifest.json', changed)
            rejects(lambda: verified_manifest(directory)); write(directory/'manifest.json', manifest)
        envelope('confirmation', rows); publish_report(directory); publish_report(directory, True)
        rejects(lambda: tune(directory))
        broken = copy.deepcopy(rows); broken['random_fallback/103000']['manifest_digest'] = 'wrong'
        envelope('confirmation', broken); rejects(lambda: read_stage(directory, 'confirmation'))
        envelope('confirmation', rows)
        raw = json.loads((directory/'confirmation.json').read_text()); raw['sources']['v3_adwin.py'] = 'wrong'
        write(directory/'confirmation.json', raw); rejects(lambda: read_stage(directory, 'confirmation'))
        broken = copy.deepcopy(rows); broken['oracle_nofallback/103000']['privileged_timing'] = False
        envelope('confirmation', broken); rejects(lambda: read_stage(directory, 'confirmation'))
        broken = copy.deepcopy(rows); broken['retain/103000']['memory']['core']['quiet']['resets'][0]['discarded'] = 0
        rejects(lambda: absolute_summary(broken))
        broken = copy.deepcopy(rows); broken['retain/103000']['memory']['core']['quiet']['regime_fast_share'] = 2.
        rejects(lambda: absolute_summary(broken))
        envelope('confirmation', rows)
        for k in tuning:
            if k.startswith('retain/'): tuning[k]['status'] = 'nonfinite'
        envelope('tuning', tuning); manifest = make_manifest(tuning); write(directory/'manifest.json', manifest)
        rejects(lambda: summarize(directory))
        with patch('study_v3_retention.require_committed'): rejects(lambda: confirm(directory))
        (directory/'confirmation.json').unlink()
        assert summarize(directory)['status'] == 'tuning_inconclusive'
        publish_report(directory); publish_report(directory, True)
    with tempfile.TemporaryDirectory(dir='.') as tmp:
        p = Path(tmp)/'uncommitted.json'; p.write_text('{}'); rejects(lambda: require_committed(p))
    for arm in ARMS:
        config = GRIDS[arm][0] if arm in FAMILIES else dict(FAST) if arm == 'oracle_nofallback' else dict(GRIDS['retain'][0])
        row = measure_row(100002, arm, config, .001 if arm == 'random_fallback' else None)
        assert row['status'] == 'ok' and len(row['fixtures']) == 5
        assert row['privileged_timing'] == (arm in ('retain', 'oracle_nofallback'))
    print('PASS retention lifecycle: dual memory accounting, source/manifest/stage gates, complete reports, all-arm development fixtures', flush=True)


def archive_checks(directory, reproduce):
    stored = publish_report(directory, True)
    for path, expected in source_hashes().items():
        assert hashlib.sha256((directory/'source-snapshots'/(expected+'.txt')).read_bytes()).hexdigest() == expected, path
    manifest = json.loads((directory/'manifest.json').read_text()); tuning = read_stage(directory, 'tuning')
    assert manifest == make_manifest(tuning)
    print('PASS retention archive tuning', len(tuning), flush=True)
    if not reproduce:
        if stored['counts']['confirmation']: read_stage(directory, 'confirmation')
        return
    fresh = {}
    for arm in FAMILIES:
        for i, config in enumerate(GRIDS[arm]):
            for seed in SEEDS['tuning']:
                key = f'{arm}/{i}/{seed}'; fresh[key] = measure_row(seed, arm, config)
                compare(fresh[key], scientific(tuning[key]), key)
        print('PASS retention reproduction tuning', arm, '96 rows', flush=True)
    fresh_manifest = make_manifest(fresh); compare(fresh_manifest, manifest, ignore=('tuning_digest',))
    if stored['counts']['confirmation']:
        archived = read_stage(directory, 'confirmation'); recreated = {}
        for arm in ARMS:
            for seed in SEEDS['confirmation']:
                key = f'{arm}/{seed}'
                recreated[key] = measure_row(seed, arm, fresh_manifest['screen']['selected'][arm],
                    fresh_manifest['screen']['random_frequency']['probability'] if arm == 'random_fallback' else None, fresh_manifest)
                compare(recreated[key], scientific(archived[key]), key, ignore=('manifest_digest',))
            print('PASS retention reproduction confirmation', arm, '32 rows', flush=True)
        compare(performance_decision(recreated), stored['decisions']['retain'])
        compare(absolute_summary(recreated), stored['absolute'])
    print('PASS full retention reproduction; only reached partitions sampled', flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--evidence', type=Path)
    parser.add_argument('--reproduce', action='store_true')
    args = parser.parse_args()
    kernel_checks(); policy_checks(); lifecycle_checks()
    if args.evidence: archive_checks(args.evidence, args.reproduce)
