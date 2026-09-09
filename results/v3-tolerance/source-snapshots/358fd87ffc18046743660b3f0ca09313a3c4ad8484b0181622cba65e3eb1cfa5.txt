"""Schedule construction, tolerance authority and full reproduction."""
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
from report_v3_tolerance import absolute_summary, publish_report, summarize
from study_v3_tolerance import (LEVELS, PARAMS, SOURCES, build_schedule, confirm, make_manifest,
    measure_row, read_stage, registration_check, require_committed, simulation,
    source_hashes, tune, verified_manifest, write)
from v3_adwin import run as adwin_run
from v3_forgetting import run as forget_run
from v3_retention import dual_run
from v3_retention_policy import SPECS
from v3_slice1_decisions import digest, finite, scientific
from v3_tolerance import ARMS, FAMILIES, FROZEN, GRIDS, run
from v3_tolerance_policy import (KEYS, PROTOCOL, SEEDS, complete, contrast, metric_values,
    objective, performance_decision, select, tolerance_point)
from v3_persistent import FIXTURES, fixture
from v3_slice1_learning import run as plain_run

SCHEDULED = [a for a in ARMS if a not in FAMILIES]


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
    assert FROZEN == {'delta': .1, 'H': 32}
    assert len(SPECS) == 15 and [len(KEYS[s]) for s in ('tuning', 'confirmation')] == [288, 448]
    assert all(len(GRIDS[a]) == 12 and len({json.dumps(c, sort_keys=True) for c in GRIDS[a]}) == 12 for a in FAMILIES)
    assert len(ARMS) == 14 and len(SCHEDULED) == 11
    parts = list(SEEDS.values())
    assert all(min(s) >= 110000 and max(s) < 116000 for s in parts)
    assert all(not set(a)&set(b) for i, a in enumerate(parts) for b in parts[i+1:])
    assert set(LEVELS) == {'jitter_2', 'jitter_8', 'jitter_16', 'jitter_32', 'jitter_128',
                             'drop_10', 'drop_50', 'add_0005', 'add_0020'}
    assert sorted(PARAMS[a] for a in LEVELS if a.startswith('jitter_')) == [2, 8, 16, 32, 128]
    for file in SOURCES:
        if not file.endswith('.py'): continue
        for node in ast.walk(ast.parse(Path(file).read_text())):
            names = [node.module] if isinstance(node, ast.ImportFrom) else [a.name for a in node.names] if isinstance(node, ast.Import) else []
            for name in names:
                if name and Path(name+'.py').exists(): assert name+'.py' in SOURCES, name
    values = np.random.default_rng(110001).normal(size=600)
    actual, expected = adwin_run(values[:, None], .1, 1), slow_adwin(values, .1, 1)
    for i, (a, b) in enumerate(zip(actual, expected)):
        a = a if i == 2 else a[:, 0]
        if i in (0, 2): np.testing.assert_allclose(a, b, rtol=1e-11, atol=1e-13)
        else: np.testing.assert_array_equal(a, b)
    # Schedule construction: bounds, clipping, merging, determinism, domains.
    y = np.random.default_rng(110000).normal(size=(500, 2))
    for name in FIXTURES:
        data = fixture(110001, name)
        order, width = FIXTURES.index(name), len(data.coordinates)
        assert np.array_equal(build_schedule(data, 'reference', 110001, order), true_marks(data))
        targets = any(k.startswith('target_') for ev in data.events for _, k in ev)
        for arm, bound in (('jitter_2', 2), ('jitter_8', 8), ('jitter_16', 16), ('jitter_32', 32), ('jitter_128', 128)):
            first = build_schedule(data, arm, 110001, order)
            assert first.shape == data.y.shape and set(np.unique(first)) <= {0., 1.}
            for j, events in enumerate(data.events):
                for start, kind in events:
                    if kind.startswith('target_'):
                        window = first[max(0, start-bound):start+bound+1, j]
                        assert window.sum() >= 1.
            assert np.array_equal(first, build_schedule(data, arm, 110001, order))
            if targets:
                assert not np.array_equal(first, build_schedule(data, arm, 110002, order))
            else:
                assert not first.any()
        for arm, rate in (('drop_10', .1), ('drop_50', .5)):
            kept = build_schedule(data, arm, 110001, order)
            assert (kept <= true_marks(data)).all()
    from types import SimpleNamespace
    many = SimpleNamespace(y=np.zeros((6000, 1)), events=[[(t, 'target_down') for t in range(100, 5900, 25)]])
    ntrue = sum(1 for ev in many.events for _, k in ev if k.startswith('target_'))
    for arm, rate in (('drop_10', .1), ('drop_50', .5)):
        first, second = build_schedule(many, arm, 110001, 0), build_schedule(many, arm, 110002, 0)
        assert not np.array_equal(first, second)
        assert abs(first.sum()/ntrue-(1.-rate)) < .1 and abs(second.sum()/ntrue-(1.-rate)) < .1
        for arm, rate in (('add_0005', .0005), ('add_0020', .002)):
            added = build_schedule(data, arm, 110001, order)
            assert abs(added.mean()-rate) < .002
            assert not np.array_equal(added, build_schedule(data, arm, 110001, (order+1) % 5))
        assert np.array_equal(build_schedule(data, 'adwin_schedule', 110001, order, {'delta': .1, 'clock': 1}),
                              adwin_run(data.y, .1, 1)[1])
        rejects(lambda: build_schedule(data, 'adwin_schedule', 110001, order))
    edge = fixture(110001, 'core')
    early = np.zeros_like(edge.y); early[3, 2] = 1.
    assert set(np.unique(build_schedule(edge, 'jitter_128', 110001, 0))) <= {0., 1.}
    # Frozen parity: scheduled arms are the retention dual-state at FROZEN.
    triggers = np.zeros_like(y); triggers[200] = 1.
    marks = np.zeros_like(y); marks[[100, 400], 0] = 1.; marks[250, 1] = 1.
    for a, b in zip(run(y, 'reference', dict(FROZEN), schedule=triggers), dual_run(y, triggers, .1, 32)):
        np.testing.assert_array_equal(np.asarray(a), np.asarray(b))
    for a, b in zip(run(y, 'reference', dict(FROZEN), schedule=triggers), dual_run(y, triggers, .1, 32)):
        np.testing.assert_array_equal(np.asarray(a), np.asarray(b))
    for a, b in zip(run(y, 'window', {'window': 16}), forget_run(y, 'window', {'window': 16})):
        np.testing.assert_array_equal(a, b)
    for a, b in zip(run(y, 'sgd', {'lr': .128})[:3], plain_run(y, 'sgd', {'lr': .128})):
        np.testing.assert_array_equal(a, b)
    # Parity, causal prefixes, independent coordinates, privilege isolation.
    for arm in ARMS:
        config = GRIDS[arm][3] if arm in FAMILIES else dict(FROZEN)
        if arm in FAMILIES:
            kwargs = {}
        elif arm == 'adwin_schedule':
            kwargs = {'schedule': adwin_run(y, .1, 1)[1]}
        else:
            kwargs = {'schedule': marks}
        original = run(y, arm, config, **kwargs)
        later = y.copy(); later[300:] += 5.
        changed = run(later, arm, config, **kwargs)
        np.testing.assert_array_equal(np.asarray(original[0])[:301], np.asarray(changed[0])[:301])
        prefix_kwargs = {k: v[:300] if isinstance(v, np.ndarray) else v for k, v in kwargs.items()}
        for a, b in zip(run(y[:300], arm, config, **prefix_kwargs), original):
            np.testing.assert_array_equal(np.asarray(a), np.asarray(b)[:300])
        other = y.copy(); other[:, 0] += 5.
        changed = run(other, arm, config, **kwargs)
        indices = (0, 1, 3, 4, 5, 6, 7) if len(original) == 8 else (0, 1, 3, 4)
        for i in indices: np.testing.assert_array_equal(np.asarray(original[i])[:, 1], np.asarray(changed[i])[:, 1])
        if arm in FAMILIES:
            rejects(lambda a=arm, c=config: run(y, a, c, schedule=triggers))
    rejects(lambda: run(y, 'reference', {'delta': .1, 'H': 64}, schedule=triggers))
    rejects(lambda: run(np.full_like(y, np.nan), 'window', {'window': 16}))
    rejects(lambda: run(y, 'reference', dict(FROZEN)))
    rejects(lambda: run(y, 'reference', dict(FROZEN), schedule=np.full_like(y, 2.)))
    for name in FIXTURES:
        data = fixture(110001, name)
        with patch('study_v3_tolerance.build_schedule', side_effect=AssertionError('evaluator access')):
            for arm in FAMILIES:
                simulation(110001, name, arm, GRIDS[arm][3])
    print('PASS tolerance kernels: schedule construction, frozen parity, causality, privilege isolation', flush=True)


def true_marks(data):
    marks = np.zeros_like(data.y)
    for j, events in enumerate(data.events):
        for start, kind in events:
            if kind.startswith('target_'):
                marks[start, j] = 1.
    return marks


def synthetic():
    coords = {'core': ('quiet', 'noisy', 'switch_quiet', 'switch_noisy'), 'mixed': ('increase_first', 'decrease_first'),
              'noise_jump': ('noise_jump',), 'drift': ('drift',), 'exactly_quiet': ('exactly_quiet',)}
    provenance = {'reference': 'true', 'adwin_schedule': 'observed'}
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
            row['memory'][name][c] = {'kind': 'window', 'reset_count': 2,
                'resets': [{'index': t, 'width_before': 32, 'width_after': 1, 'discarded': 32} for t in (2000, 4000)],
                'width_mean': 25., 'width_min': 1, 'width_max': 32, 'width_final': 32, 'total_discarded': 5968,
                'events': copy.deepcopy(events), 'provenance': 'none'}
    def adjust(r, arm):
        prov = provenance.get(arm, arm if arm not in FAMILIES else 'none')
        if arm == 'sgd':
            for f in r['memory'].values():
                for c in f.values():
                    c.update(kind='exponential', resets=[], reset_count=0, provenance=prov)
                    c.update({k: None for k in ('width_mean', 'width_min', 'width_max', 'width_final', 'total_discarded')})
        elif arm not in FAMILIES:
            for f in r['memory'].values():
                for c in f.values():
                    c.update(kind='dual', provenance=prov, adwin_width_mean=2000., adwin_width_min=1000,
                             adwin_width_max=3000, adwin_width_final=2000, adwin_total_discarded=4000,
                             regime_fast_share=.5)
        else:
            for f in r['memory'].values():
                for c in f.values():
                    c.update(provenance=prov)
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
            if a in SCHEDULED:
                for f in r['fixtures'].values():
                    for c in f['coordinates'].values():
                        for k in ('excess_mse', 'post_mse', 'stable_mse'):
                            if c[k] is not None: c[k] = .5
                        c['windows'] = {k: .5 for k in c['windows']}
            confirmation[f'{a}/{seed}'] = r
    return tuning, manifest, confirmation


def policy_checks():
    tuning, manifest, rows = synthetic()
    assert objective(tuning['window/0/111000']) == 1.
    assert all(i == 0 for i in manifest['screen']['indices'].values())
    assert all(manifest['screen']['selected'][a] == dict(FROZEN) for a in SCHEDULED)
    bad = copy.deepcopy(tuning); bad['window/0/111000']['status'] = 'nonfinite'
    assert select(bad)['indices']['window'] == 1
    for k in bad:
        if k.startswith('window/'): bad[k]['status'] = 'nonfinite'
    assert select(bad)['status'] == 'tuning_inconclusive'
    rejects(lambda: complete({k: r for k, r in tuning.items() if k != 'window/0/111000'}, 'tuning'))
    assert tolerance_point(rows)['tolerance'] == 128
    assert performance_decision(rows, 'adwin_schedule')['status'] == 'learning_positive'
    assert len(performance_decision(rows, 'adwin_schedule')['cells']) == 45
    bad = copy.deepcopy(rows)
    for seed in SEEDS['confirmation']:
        for arm in ('jitter_16', 'jitter_32', 'jitter_128'):
            bad[f'{arm}/{seed}']['fixtures']['core']['coordinates']['switch_noisy']['post_mse'] = 99.
    assert tolerance_point(bad)['tolerance'] == 8
    for control in ('window', 'sgd', 'adwin'):
        for label, fields in SPECS:
            bad = copy.deepcopy(rows)
            for seed in SEEDS['confirmation']:
                for n, c, f, w in fields:
                    dest = bad[f'{control}/{seed}']['fixtures'][n]['coordinates'][c]
                    if w: dest[f][w] = .01
                    else: dest[f] = .01
            result = performance_decision(bad, 'adwin_schedule')
            assert result['status'] == 'learning_negative' and not result['cells'][f'{control}/{label}']['pass']
    assert contrast([1.]*32, [.89]*32, 'improve')['pass'] and not contrast([1.]*32, [.91]*32, 'improve')['pass']
    assert not contrast([1.]*32, [1.101]*32, 'preserve')['pass']
    rejects(lambda: contrast([1., 2.], [1.], 'improve'))
    rejects(lambda: performance_decision(rows, 'window'))
    for key in ('adwin/113000', 'adwin_schedule/113000', 'jitter_16/113000', 'reference/113000'):
        rejects(lambda k=key: performance_decision({a: r for a, r in rows.items() if a != k}, 'adwin_schedule'))
    bad = copy.deepcopy(rows)
    for seed in SEEDS['confirmation']: bad[f'adwin_schedule/{seed}']['status'] = 'nonfinite'
    assert performance_decision(bad, 'adwin_schedule')['status'] == 'learning_negative'
    print('PASS tolerance policy: frozen menus, 45-cell instrument, tolerance point, advancement gate', flush=True)


def lifecycle_checks():
    tuning, manifest, rows = synthetic()
    with tempfile.TemporaryDirectory() as tmp:
        directory = Path(tmp)
        def envelope(stage, data): write(directory/(stage+'.json'), {'protocol': PROTOCOL, 'sources': source_hashes(), 'rows': data})
        envelope('tuning', tuning); write(directory/'manifest.json', manifest)
        assert summarize(directory)['status'] == 'awaiting_confirmation'
        with patch('study_v3_tolerance.require_committed', side_effect=ValueError('uncommitted')): rejects(lambda: confirm(directory))
        with patch('study_v3_tolerance.require_committed'):
            assert verified_manifest(directory) == manifest
            changed = copy.deepcopy(manifest); changed['screen']['indices']['window'] = 5; write(directory/'manifest.json', changed)
            rejects(lambda: verified_manifest(directory)); write(directory/'manifest.json', manifest)
        envelope('confirmation', rows); publish_report(directory); publish_report(directory, True)
        rejects(lambda: tune(directory))
        broken = copy.deepcopy(rows); broken['jitter_16/113000']['manifest_digest'] = 'wrong'
        envelope('confirmation', broken); rejects(lambda: read_stage(directory, 'confirmation'))
        envelope('confirmation', rows)
        raw = json.loads((directory/'confirmation.json').read_text()); raw['sources']['v3_adwin.py'] = 'wrong'
        write(directory/'confirmation.json', raw); rejects(lambda: read_stage(directory, 'confirmation'))
        broken = copy.deepcopy(rows); broken['adwin_schedule/113000']['privileged_timing'] = False
        envelope('confirmation', broken); rejects(lambda: read_stage(directory, 'confirmation'))
        broken = copy.deepcopy(rows); broken['reference/113000']['memory']['core']['quiet']['provenance'] = 'jitter_2'
        rejects(lambda: absolute_summary(broken))
        envelope('confirmation', rows)
        for k in tuning:
            if k.startswith('window/'): tuning[k]['status'] = 'nonfinite'
        envelope('tuning', tuning); manifest = make_manifest(tuning); write(directory/'manifest.json', manifest)
        rejects(lambda: summarize(directory))
        with patch('study_v3_tolerance.require_committed'): rejects(lambda: confirm(directory))
        (directory/'confirmation.json').unlink()
        assert summarize(directory)['status'] == 'tuning_inconclusive'
        publish_report(directory); publish_report(directory, True)
    with tempfile.TemporaryDirectory(dir='.') as tmp:
        p = Path(tmp)/'uncommitted.json'; p.write_text('{}'); rejects(lambda: require_committed(p))
    alarm = {'delta': .1, 'clock': 1}
    for arm in ARMS:
        config = GRIDS[arm][0] if arm in FAMILIES else dict(FROZEN)
        row = measure_row(110002, arm, config, alarm if arm == 'adwin_schedule' else None)
        assert row['status'] == 'ok' and len(row['fixtures']) == 5
        assert row['privileged_timing'] == (arm not in FAMILIES)
        expected_prov = ('none' if arm in FAMILIES else 'observed' if arm == 'adwin_schedule'
                         else 'true' if arm == 'reference' else arm)
        for records in row['memory'].values():
            for record in records.values():
                assert record['provenance'] == expected_prov
    print('PASS tolerance lifecycle: provenance accounting, source/manifest/stage gates, complete reports, all-arm development fixtures', flush=True)


def archive_checks(directory, reproduce):
    stored = publish_report(directory, True)
    for path, expected in source_hashes().items():
        assert hashlib.sha256((directory/'source-snapshots'/(expected+'.txt')).read_bytes()).hexdigest() == expected, path
    manifest = json.loads((directory/'manifest.json').read_text()); tuning = read_stage(directory, 'tuning')
    assert manifest == make_manifest(tuning)
    print('PASS tolerance archive tuning', len(tuning), flush=True)
    if not reproduce:
        if stored['counts']['confirmation']: read_stage(directory, 'confirmation')
        return
    fresh = {}
    for arm in FAMILIES:
        for i, config in enumerate(GRIDS[arm]):
            for seed in SEEDS['tuning']:
                key = f'{arm}/{i}/{seed}'; fresh[key] = measure_row(seed, arm, config)
                compare(fresh[key], scientific(tuning[key]), key)
        print('PASS tolerance reproduction tuning', arm, '96 rows', flush=True)
    fresh_manifest = make_manifest(fresh); compare(fresh_manifest, manifest, ignore=('tuning_digest',))
    if stored['counts']['confirmation']:
        archived = read_stage(directory, 'confirmation'); recreated = {}
        alarm = fresh_manifest['screen']['selected']['adwin']
        for arm in ARMS:
            for seed in SEEDS['confirmation']:
                key = f'{arm}/{seed}'
                recreated[key] = measure_row(seed, arm, fresh_manifest['screen']['selected'][arm],
                                             alarm if arm == 'adwin_schedule' else None, fresh_manifest)
                compare(recreated[key], scientific(archived[key]), key, ignore=('manifest_digest',))
            print('PASS tolerance reproduction confirmation', arm, '32 rows', flush=True)
        for arm in SCHEDULED:
            compare(performance_decision(recreated, arm), stored['decisions'][arm])
        compare(tolerance_point(recreated), stored['tolerance'])
        compare(absolute_summary(recreated), stored['absolute'])
    print('PASS full tolerance reproduction; only reached partitions sampled', flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--evidence', type=Path)
    parser.add_argument('--reproduce', action='store_true')
    args = parser.parse_args()
    kernel_checks(); policy_checks(); lifecycle_checks()
    if args.evidence: archive_checks(args.evidence, args.reproduce)
