"""Lie generator, graded authority and full reproduction."""
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
from report_v4_robust import absolute_summary, publish_report, summarize
from study_v4_robust import (DIRECTORY, LIE, SOURCES, build_lies, confirm, lie_rng, make_manifest,
    measure_row, read_stage, registration_check, require_committed, simulation,
    source_hashes, tune, verified_manifest, write)
from v3_adwin import run as adwin_run
from v3_forgetting import run as forget_run
from v3_persistent import FIXTURES, fixture
from v3_slice1_learning import run as plain_run
from v4_robust import ARMS, BASE_LR, FAMILIES, GRIDS, graded_kernel, run
from v4_robust_policy import (KEYS, PROTOCOL, SEEDS, SPECS, complete, contrast,
    digest, metric_values, objective, performance_decision, scientific, select)


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
    assert BASE_LR == .128
    assert LIE == {'delay_lo': 0, 'delay_hi': 8, 'miss': .1, 'false': .001}
    assert len(SPECS) == 15 and [len(KEYS[s]) for s in ('tuning', 'confirmation')] == [384, 160]
    assert all(len(GRIDS[a]) == 12 and len({json.dumps(c, sort_keys=True) for c in GRIDS[a]}) == 12 for a in FAMILIES)
    assert [c['gain'] for c in GRIDS['graded']] == [g for g in (1., 2., 4., 8.) for _ in (8, 32, 128)]
    parts = list(SEEDS.values())
    assert all(min(s) >= 180000 and max(s) < 186000 for s in parts)
    assert all(not set(a)&set(b) for i, a in enumerate(parts) for b in parts[i+1:])
    for file in SOURCES:
        if not file.endswith('.py'): continue
        for node in ast.walk(ast.parse(Path(file).read_text())):
            names = [node.module] if isinstance(node, ast.ImportFrom) else [a.name for a in node.names] if isinstance(node, ast.Import) else []
            for name in names:
                if name and Path(name+'.py').exists(): assert name+'.py' in SOURCES, name
    values = np.random.default_rng(180001).normal(size=600)
    actual, expected = adwin_run(values[:, None], .1, 1), slow_adwin(values, .1, 1)
    for i, (a, b) in enumerate(zip(actual, expected)):
        a = a if i == 2 else a[:, 0]
        if i in (0, 2): np.testing.assert_allclose(a, b, rtol=1e-11, atol=1e-13)
        else: np.testing.assert_array_equal(a, b)
    # Graded kernel against hand-worked traces.
    trace_y = np.array([1., 1., 1., 1., 5., 5., 5., 5.])[:, None]
    trace_alarms = np.zeros_like(trace_y); trace_alarms[4, 0] = 1.
    pred, norms, counts = graded_kernel(trace_y, trace_alarms, 2., 4)
    assert pred[0, 0] == 0. and counts[0, 0] == 0
    np.testing.assert_array_equal(counts[:, 0], [0, 0, 0, 0, 1, 1, 1, 1])
    weight = 0.
    for t in range(8):
        assert pred[t, 0] == weight
        recent = 1. if 4 <= t < 8 else 0.
        weight -= .128*(1.+2.*recent)*(weight-trace_y[t, 0])
    np.testing.assert_allclose(norms[:7], np.abs(np.diff(pred[:, 0])), rtol=1e-12)
    # Frozen lies: profile bounds, determinism, domain separation, prefix.
    for name in FIXTURES:
        data = fixture(180001, name)
        order = FIXTURES.index(name)
        alarms, kinds = build_lies(data, 180001, order)
        assert alarms.shape == data.y.shape and set(np.unique(alarms)) <= {0., 1.}
        assert set(kinds.values()) <= {'delayed', 'false'}
        for (t, j), kind in kinds.items():
            assert alarms[t, j] == 1.
            if kind == 'delayed':
                assert any(s <= t <= s+8 for s, k in data.events[j]
                           if k.startswith('target_') or k in ('drift_start', 'drift_end'))
        assert np.array_equal(alarms, build_lies(data, 180001, order)[0])
        assert not np.array_equal(alarms, build_lies(data, 180002, order)[0])
        assert not np.array_equal(alarms, build_lies(data, 180001, (order+1) % 5)[0])
    falses = []
    for seed in range(180001, 180009):
        alarms, _ = build_lies(fixture(seed, 'core'), seed, 0)
        falses.append(alarms.sum()/(6000*4))
    assert .0002 < sum(falses)/len(falses) < .003
    # Parity, causal prefixes, independent coordinates, privilege isolation.
    from types import SimpleNamespace
    y = np.random.default_rng(180000).normal(size=(500, 2))
    proxy = SimpleNamespace(y=y, events=[[(200, 'target_down')], [(100, 'drift_start'), (400, 'drift_end')]])
    for arm in ARMS:
        config = GRIDS[arm][3] if arm in FAMILIES else {'gain': 2., 'window': 32}
        if arm in ('window', 'sgd', 'adwin'):
            kwargs = {}
        elif arm == 'adwin_gated':
            kwargs = {'alarms': adwin_run(y, .1, 1)[1]}
        else:
            alarms, _ = build_lies(proxy, 180000, 0)
            kwargs = {'alarms': alarms}
        original = run(y, arm, config, **kwargs)
        later = y.copy(); later[300:] += 5.
        changed = run(later, arm, config, **kwargs)
        np.testing.assert_array_equal(np.asarray(original[0])[:301], np.asarray(changed[0])[:301])
        prefix_kwargs = {k: v[:300] if isinstance(v, np.ndarray) else v for k, v in kwargs.items()}
        for a, b in zip(run(y[:300], arm, config, **prefix_kwargs), original):
            np.testing.assert_array_equal(np.asarray(a), np.asarray(b)[:300])
        other = y.copy(); other[:, 0] += 5.
        changed = run(other, arm, config, **kwargs)
        indices = (0, 1, 3) if arm in ('graded', 'adwin_gated') else (0, 1, 3, 4)
        for i in indices: np.testing.assert_array_equal(np.asarray(original[i])[:, 1], np.asarray(changed[i])[:, 1])
        if arm in ('window', 'sgd', 'adwin'):
            rejects(lambda a=arm, c=config: run(y, a, c, alarms=np.ones_like(y)))
    rejects(lambda: run(y, 'graded', {'gain': -1., 'window': 8}, alarms=np.zeros_like(y)))
    rejects(lambda: run(y, 'graded', {'gain': 1., 'window': 0}, alarms=np.zeros_like(y)))
    rejects(lambda: run(y, 'graded', {'gain': 1., 'window': 8}))
    rejects(lambda: run(np.full_like(y, np.nan), 'window', {'window': 16}))
    for name in FIXTURES:
        with patch('study_v4_robust.build_lies', side_effect=AssertionError('evaluator access')):
            for arm in ('window', 'sgd', 'adwin'):
                simulation(180001, name, arm, GRIDS[arm][3])
    print('PASS robust kernels: graded equations, frozen lies, causality, privilege isolation', flush=True)


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
            row['memory'][name][c] = {'kind': 'window', 'reset_count': 0, 'resets': [],
                'width_mean': 25., 'width_min': 1, 'width_max': 32, 'width_final': 32, 'total_discarded': 5968,
                'events': copy.deepcopy(events)}
    def adjust(r, arm):
        if arm == 'sgd':
            for f in r['memory'].values():
                for c in f.values():
                    c.update(kind='exponential', resets=[], reset_count=0)
                    c.update({k: None for k in ('width_mean', 'width_min', 'width_max', 'width_final', 'total_discarded')})
        if arm in ('graded', 'adwin_gated'):
            for f in r['memory'].values():
                for c in f.values():
                    resets = [{'index': t, 'kind': k} for t, k in ((2000, 'delayed'), (4000, 'false'))]
                    c.update(kind='graded', resets=resets, reset_count=2, alarm_total=2, gain_levels=[0, 1])
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
            if a in ('graded', 'adwin_gated'):
                for f in r['fixtures'].values():
                    for c in f['coordinates'].values():
                        for k in ('excess_mse', 'post_mse', 'stable_mse'):
                            if c[k] is not None: c[k] = .5
                        c['windows'] = {k: .5 for k in c['windows']}
            confirmation[f'{a}/{seed}'] = r
    return tuning, manifest, confirmation


def policy_checks():
    tuning, manifest, rows = synthetic()
    assert objective(tuning['graded/0/181000']) == 1.
    assert all(i == 0 for i in manifest['screen']['indices'].values())
    assert manifest['screen']['selected']['adwin_gated'] == manifest['screen']['selected']['graded']
    assert performance_decision(rows, 'graded')['status'] == 'learning_positive'
    assert len(performance_decision(rows, 'graded')['cells']) == 45
    assert performance_decision(rows, 'adwin_gated')['status'] == 'learning_positive'
    bad = copy.deepcopy(tuning); bad['graded/0/181000']['status'] = 'nonfinite'
    assert select(bad)['indices']['graded'] == 1
    for k in bad:
        if k.startswith('graded/'): bad[k]['status'] = 'nonfinite'
    assert select(bad)['status'] == 'tuning_inconclusive'
    rejects(lambda: complete({k: r for k, r in tuning.items() if k != 'graded/0/181000'}, 'tuning'))
    for control in ('window', 'sgd', 'adwin'):
        for label, fields in SPECS:
            bad = copy.deepcopy(rows)
            for seed in SEEDS['confirmation']:
                for n, c, f, w in fields:
                    dest = bad[f'{control}/{seed}']['fixtures'][n]['coordinates'][c]
                    if w: dest[f][w] = .01
                    else: dest[f] = .01
            for subject in ('graded', 'adwin_gated'):
                result = performance_decision(bad, subject)
                assert result['status'] == 'learning_negative' and not result['cells'][f'{control}/{label}']['pass']
    assert contrast([1.]*32, [.89]*32, 'improve')['pass'] and not contrast([1.]*32, [.91]*32, 'improve')['pass']
    assert not contrast([1.]*32, [1.101]*32, 'preserve')['pass']
    rejects(lambda: contrast([1., 2.], [1.], 'improve'))
    rejects(lambda: performance_decision(rows, 'window'))
    for key in ('adwin/183000', 'graded/183000', 'adwin_gated/183000'):
        rejects(lambda k=key: performance_decision({a: r for a, r in rows.items() if a != k}, 'graded'))
    bad = copy.deepcopy(rows)
    for seed in SEEDS['confirmation']: bad[f'graded/{seed}']['status'] = 'nonfinite'
    assert performance_decision(bad, 'graded')['status'] == 'learning_negative'
    print('PASS robust policy: frozen menus, 45-cell gate, diagnostic instrument', flush=True)


def lifecycle_checks():
    tuning, manifest, rows = synthetic()
    with tempfile.TemporaryDirectory() as tmp:
        directory = Path(tmp)
        def envelope(stage, data): write(directory/(stage+'.json'), {'protocol': PROTOCOL, 'sources': source_hashes(), 'rows': data})
        envelope('tuning', tuning); write(directory/'manifest.json', manifest)
        assert summarize(directory)['status'] == 'awaiting_confirmation'
        with patch('study_v4_robust.require_committed', side_effect=ValueError('uncommitted')): rejects(lambda: confirm(directory))
        with patch('study_v4_robust.require_committed'):
            assert verified_manifest(directory) == manifest
            changed = copy.deepcopy(manifest); changed['screen']['indices']['graded'] = 5; write(directory/'manifest.json', changed)
            rejects(lambda: verified_manifest(directory)); write(directory/'manifest.json', manifest)
        envelope('confirmation', rows); publish_report(directory); publish_report(directory, True)
        rejects(lambda: tune(directory))
        broken = copy.deepcopy(rows); broken['graded/183000']['manifest_digest'] = 'wrong'
        envelope('confirmation', broken); rejects(lambda: read_stage(directory, 'confirmation'))
        envelope('confirmation', rows)
        raw = json.loads((directory/'confirmation.json').read_text()); raw['sources']['v3_adwin.py'] = 'wrong'
        write(directory/'confirmation.json', raw); rejects(lambda: read_stage(directory, 'confirmation'))
        broken = copy.deepcopy(rows); broken['graded/183000']['privileged_timing'] = False
        envelope('confirmation', broken); rejects(lambda: read_stage(directory, 'confirmation'))
        broken = copy.deepcopy(rows); broken['graded/183000']['memory']['core']['quiet']['resets'][0]['kind'] = 'noisy'
        rejects(lambda: absolute_summary(broken))
        broken = copy.deepcopy(rows); broken['graded/183000']['memory']['core']['quiet']['alarm_total'] = -1
        rejects(lambda: absolute_summary(broken))
        envelope('confirmation', rows)
        for k in tuning:
            if k.startswith('graded/'): tuning[k]['status'] = 'nonfinite'
        envelope('tuning', tuning); manifest = make_manifest(tuning); write(directory/'manifest.json', manifest)
        rejects(lambda: summarize(directory))
        with patch('study_v4_robust.require_committed'): rejects(lambda: confirm(directory))
        (directory/'confirmation.json').unlink()
        assert summarize(directory)['status'] == 'tuning_inconclusive'
        publish_report(directory); publish_report(directory, True)
    with tempfile.TemporaryDirectory(dir='.') as tmp:
        p = Path(tmp)/'uncommitted.json'; p.write_text('{}'); rejects(lambda: require_committed(p))
    alarm = {'delta': .1, 'clock': 1}
    for arm in ARMS:
        config = GRIDS[arm][0] if arm in FAMILIES else dict(GRIDS['graded'][0])
        row = measure_row(180002, arm, config, alarm if arm == 'adwin_gated' else None)
        assert row['status'] == 'ok' and len(row['fixtures']) == 5
        assert row['privileged_timing'] == (arm not in ('window', 'sgd', 'adwin'))
    print('PASS robust lifecycle: lie provenance, source/manifest/stage gates, complete reports, all-arm development fixtures', flush=True)


def archive_checks(directory, reproduce):
    stored = publish_report(directory, True)
    for path, expected in source_hashes().items():
        assert hashlib.sha256((directory/'source-snapshots'/(expected+'.txt')).read_bytes()).hexdigest() == expected, path
    manifest = json.loads((directory/'manifest.json').read_text()); tuning = read_stage(directory, 'tuning')
    assert manifest == make_manifest(tuning)
    print('PASS robust archive tuning', len(tuning), flush=True)
    if not reproduce:
        if stored['counts']['confirmation']: read_stage(directory, 'confirmation')
        return
    fresh = {}
    for arm in FAMILIES:
        for i, config in enumerate(GRIDS[arm]):
            for seed in SEEDS['tuning']:
                key = f'{arm}/{i}/{seed}'; fresh[key] = measure_row(seed, arm, config)
                compare(fresh[key], scientific(tuning[key]), key)
        print('PASS robust reproduction tuning', arm, '96 rows', flush=True)
    fresh_manifest = make_manifest(fresh); compare(fresh_manifest, manifest, ignore=('tuning_digest',))
    if stored['counts']['confirmation']:
        archived = read_stage(directory, 'confirmation'); recreated = {}
        for arm in ARMS:
            for seed in SEEDS['confirmation']:
                key = f'{arm}/{seed}'
                recreated[key] = measure_row(seed, arm, fresh_manifest['screen']['selected'][arm],
                                             fresh_manifest['screen']['selected']['adwin'] if arm == 'adwin_gated' else None,
                                             fresh_manifest)
                compare(recreated[key], scientific(archived[key]), key, ignore=('manifest_digest',))
            print('PASS robust reproduction confirmation', arm, '32 rows', flush=True)
        for arm in ('graded', 'adwin_gated'):
            compare(performance_decision(recreated, arm), stored['decisions'][arm])
        compare(absolute_summary(recreated), stored['absolute'])
    print('PASS full robust reproduction; only reached partitions sampled', flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--evidence', type=Path)
    parser.add_argument('--reproduce', action='store_true')
    args = parser.parse_args()
    kernel_checks(); policy_checks(); lifecycle_checks()
    if args.evidence: archive_checks(args.evidence, args.reproduce)
