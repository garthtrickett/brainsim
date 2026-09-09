"""Trend equations, repaired veto authority and full reproduction."""
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
from report_v3_slope import absolute_summary, publish_report, summarize
from study_v3_slope import (SOURCES, confirm, entry_flags, make_manifest, measure_row,
    read_stage, registration_check, require_committed, simulation, source_hashes, tune,
    verified_manifest, write)
from v3_adwin import run as adwin_run
from v3_forgetting import run as forget_run
from v3_retention import dual_run
from v3_slope import (ARMS, DELTA, FAMILIES, FAST, GRIDS, HORIZON, compose, holt_column,
                      ols_column, ols_fit, random_uniforms, run)
from v3_slope_policy import (KEYS, PROTOCOL, SEEDS, SPECS, complete, contrast,
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
    return (np.array(predictions), np.array(flags), np.abs(np.array(means)-predictions),
            np.array(widths), np.array(removed))


def kernel_checks():
    registration_check()
    assert DELTA == .1 and HORIZON == 32 and FAST == {'keep': 4, 'window': 32}
    assert len(GRIDS['slope']) == 12 and len({json.dumps(c, sort_keys=True) for c in GRIDS['slope']}) == 12
    assert [c['method'] for c in GRIDS['slope']] == ['ols']*6+['holt']*6
    assert [c['W'] for c in GRIDS['slope'][:6]] == [8, 16, 32, 64, 128, 256]
    assert len(SPECS) == 15 and [len(KEYS[s]) for s in ('tuning', 'confirmation')] == [384, 192]
    assert all(len(GRIDS[a]) == 12 and len({json.dumps(c, sort_keys=True) for c in GRIDS[a]}) == 12 for a in FAMILIES)
    parts = list(SEEDS.values())
    assert all(min(s) >= 130000 and max(s) < 136000 for s in parts)
    assert all(not set(a)&set(b) for i, a in enumerate(parts) for b in parts[i+1:])
    for file in SOURCES:
        if not file.endswith('.py'): continue
        for node in ast.walk(ast.parse(Path(file).read_text())):
            names = [node.module] if isinstance(node, ast.ImportFrom) else [a.name for a in node.names] if isinstance(node, ast.Import) else []
            for name in names:
                if name and Path(name+'.py').exists(): assert name+'.py' in SOURCES, name
    values = np.random.default_rng(130001).normal(size=600)
    actual, expected = adwin_run(values[:, None], .1, 1), slow_adwin(values, .1, 1)
    for i, (a, b) in enumerate(zip(actual, expected)):
        a = a if i == 2 else a[:, 0]
        if i in (0, 2): np.testing.assert_allclose(a, b, rtol=1e-11, atol=1e-13)
        else: np.testing.assert_array_equal(a, b)
    # Estimator parity against independent numpy fits and hand recursions.
    y = np.random.default_rng(130000).normal(size=(500, 2))
    for width in (8, 32, 256):
        pred, updated, slopes = ols_column(y[:, 0], width)
        for t in (0, 1, 7, 100, 499):
            start = max(0, t-width)
            window = y[start:t, 0]
            if len(window) == 0:
                assert pred[t] == 0.
            elif len(window) == 1:
                assert pred[t] == window[0] and slopes[t] == 0.
            else:
                slope, intercept = np.polyfit(np.arange(len(window)), window, 1)
                np.testing.assert_allclose([pred[t], slopes[t]], [intercept+slope*len(window), slope], rtol=1e-9)
    ramp = np.linspace(1., -1., 500)
    pred, _, slopes = ols_column(ramp, 32)
    np.testing.assert_allclose(pred[33:], ramp[33:], rtol=1e-9, atol=1e-11)
    np.testing.assert_allclose(slopes[33:], -2./499, rtol=1e-9)
    flat = np.full(500, 3.)
    pred, updated, slopes = ols_column(flat, 16)
    np.testing.assert_allclose(pred[1:], 3., rtol=1e-12)
    assert (slopes == 0.).all()
    level, trend, expected = 2., 0., [0.]*500
    trace = [1., 2., 1., 0., -1.]
    for t, value in enumerate(trace):
        if t == 0:
            level = value
        else:
            expected[t] = level+trend
            previous = level
            level = .5*value+.5*(level+trend)
            trend = .5*(level-previous)+.5*trend
    pred, updated, slopes = holt_column(np.array(trace), .5, .5)
    np.testing.assert_allclose(pred[:5], expected[:5], rtol=1e-12)
    assert pred[0] == 0. and updated[0] == trace[0]
    rejects(lambda: run(y, 'slope', {'method': 'ols', 'W': 1}, schedule=np.zeros_like(y), enter=np.zeros_like(y)))
    rejects(lambda: run(y, 'slope', {'method': 'holt', 'alpha': 0., 'beta': .1}, schedule=np.zeros_like(y), enter=np.zeros_like(y)))
    rejects(lambda: run(y, 'slope', {'method': 'holt', 'alpha': .5, 'beta': 1.}, schedule=np.zeros_like(y), enter=np.zeros_like(y)))
    rejects(lambda: run(y, 'slope', {'method': 'quadratic', 'W': 8}, schedule=np.zeros_like(y), enter=np.zeros_like(y)))
    # Regime entry/exit on hand-built boundary sequences, pre-request convention.
    stepped = np.zeros((400, 1)); stepped[200:] = 5.
    starts = np.zeros_like(stepped); starts[100, 0] = 1.
    ends = np.zeros_like(stepped); ends[300, 0] = 1.
    both = np.zeros_like(stepped); both[[100, 300], 0] = 1.
    result = compose(stepped, both, starts, {'method': 'ols', 'W': 8})
    assert result[7][:100, 0].max() <= 1 and (result[7][101:300, 0] == 2).all() and (result[7][301:, 0] != 2).all()
    assert result[7][100, 0] != 2 and result[7][300, 0] == 2
    tied = compose(stepped, both, both, {'method': 'ols', 'W': 8})
    assert tied[7][100, 0] != 2 and (tied[7][101:, 0] == 2).all()
    # Frozen parity: outside the slope regime this is the retention dual-state.
    triggers = np.zeros_like(y); triggers[200] = 1.
    for a, b in zip(compose(y, triggers, np.zeros_like(triggers), {'method': 'holt', 'alpha': .5, 'beta': .2})[:7],
                     dual_run(y, triggers, .1, 32)[:7]):
        np.testing.assert_array_equal(np.asarray(a), np.asarray(b))
    for a, b in zip(run(y, 'oracle_nofallback', dict(FAST), schedule=triggers),
                     forget_run(y, 'oracle_matched', dict(FAST), triggers=triggers)):
        np.testing.assert_array_equal(a, b)
    for a, b in zip(run(y, 'window', {'window': 16}), forget_run(y, 'window', {'window': 16})):
        np.testing.assert_array_equal(a, b)
    for a, b in zip(run(y, 'sgd', {'lr': .128})[:3], plain_run(y, 'sgd', {'lr': .128})):
        np.testing.assert_array_equal(a, b)
    # Parity, causal prefixes, independent coordinates, privilege isolation.
    uniforms = random_uniforms(130000, 0, len(y), 2)
    for arm in ARMS:
        config = GRIDS[arm][3] if arm in FAMILIES else dict(FAST) if arm == 'oracle_nofallback' else dict(GRIDS['slope'][3])
        if arm in ('window', 'sgd', 'adwin'):
            kwargs = {}
        elif arm == 'random_slope':
            kwargs = {'uniforms': uniforms, 'probability': .01}
        elif arm == 'slope':
            kwargs = {'schedule': triggers, 'enter': np.zeros_like(triggers)}
        else:
            kwargs = {'schedule': triggers}
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
    np.testing.assert_array_equal(uniforms[:200], random_uniforms(130000, 0, 200, 2))
    np.testing.assert_array_equal(uniforms[:, :1], random_uniforms(130000, 0, len(y), 1))
    assert not np.array_equal(uniforms, random_uniforms(130000, 1, len(y), 2))
    assert not np.array_equal(uniforms[:, 0], uniforms[:, 1])
    rejects(lambda: run(np.full_like(y, np.nan), 'window', {'window': 16}))
    rejects(lambda: run(y, 'slope', GRIDS['slope'][0]))
    for name in FIXTURES:
        data = fixture(130001, name)
        with patch('study_v3_slope.enriched_schedule', side_effect=AssertionError('evaluator access')):
            for arm in ('window', 'sgd', 'adwin'):
                simulation(130001, name, arm, GRIDS[arm][3])
    print('PASS slope kernels: OLS/Holt parity, regime entry/exit, frozen parity, causality, privilege isolation', flush=True)


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
                             regime_fast_share=.01, regime_slope_share=.5, slope_mean=-.001)
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
            if a == 'slope':
                for f in r['fixtures'].values():
                    for c in f['coordinates'].values():
                        for k in ('excess_mse', 'post_mse', 'stable_mse'):
                            if c[k] is not None: c[k] = .5
                        c['windows'] = {k: .5 for k in c['windows']}
            confirmation[f'{a}/{seed}'] = r
    return tuning, manifest, confirmation


def policy_checks():
    tuning, manifest, rows = synthetic()
    assert objective(tuning['slope/0/131000']) == 1.
    assert all(i == 0 for i in manifest['screen']['indices'].values())
    assert manifest['screen']['selected']['oracle_nofallback'] == dict(FAST)
    assert manifest['screen']['selected']['random_slope'] == manifest['screen']['selected']['slope']
    assert manifest['screen']['random_frequency']['starts'] == 144 and manifest['screen']['random_frequency']['coordinate_time'] == 432000
    assert performance_decision(rows)['status'] == 'learning_positive' and len(performance_decision(rows)['cells']) == 75
    assert sum(1 for c in performance_decision(rows)['cells'].values() if c['mode'] == 'strict') == 8
    assert performance_decision(rows)['cells']['oracle_nofallback/noisy']['mode'] == 'strict'
    bad = copy.deepcopy(rows)
    for seed in SEEDS['confirmation']:
        for coord in bad[f'slope/{seed}']['fixtures']['exactly_quiet']['coordinates'].values():
            coord['excess_mse'] = 0.
        for coord in bad[f'oracle_nofallback/{seed}']['fixtures']['exactly_quiet']['coordinates'].values():
            coord['excess_mse'] = 0.
    repaired = performance_decision(bad)
    assert repaired['cells']['oracle_nofallback/exactly_quiet']['mode'] == 'preserve'
    assert repaired['cells']['oracle_nofallback/exactly_quiet']['pass']
    assert repaired['status'] == 'learning_positive'
    bad = copy.deepcopy(tuning); bad['slope/0/131000']['status'] = 'nonfinite'
    assert select(bad)['indices']['slope'] == 1
    for k in bad:
        if k.startswith('slope/'): bad[k]['status'] = 'nonfinite'
    assert select(bad)['status'] == 'tuning_inconclusive'
    rejects(lambda: complete({k: r for k, r in tuning.items() if k != 'slope/0/131000'}, 'tuning'))
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
    for key in ('adwin/133000', 'random_slope/133000', 'oracle_nofallback/133000', 'slope/133000'):
        rejects(lambda k=key: performance_decision({a: r for a, r in rows.items() if a != k}))
    bad = copy.deepcopy(rows)
    for seed in SEEDS['confirmation']: bad[f'slope/{seed}']['status'] = 'nonfinite'
    assert performance_decision(bad)['status'] == 'learning_negative'
    print('PASS slope policy: frozen menus, 75 vetoes, repaired both-perfect rule, strict ablation cells', flush=True)


def lifecycle_checks():
    tuning, manifest, rows = synthetic()
    with tempfile.TemporaryDirectory() as tmp:
        directory = Path(tmp)
        def envelope(stage, data): write(directory/(stage+'.json'), {'protocol': PROTOCOL, 'sources': source_hashes(), 'rows': data})
        envelope('tuning', tuning); write(directory/'manifest.json', manifest)
        assert summarize(directory)['status'] == 'awaiting_confirmation'
        with patch('study_v3_slope.require_committed', side_effect=ValueError('uncommitted')): rejects(lambda: confirm(directory))
        with patch('study_v3_slope.require_committed'):
            assert verified_manifest(directory) == manifest
            changed = copy.deepcopy(manifest); changed['screen']['indices']['slope'] = 5; write(directory/'manifest.json', changed)
            rejects(lambda: verified_manifest(directory)); write(directory/'manifest.json', manifest)
        envelope('confirmation', rows); publish_report(directory); publish_report(directory, True)
        rejects(lambda: tune(directory))
        broken = copy.deepcopy(rows); broken['random_slope/133000']['manifest_digest'] = 'wrong'
        envelope('confirmation', broken); rejects(lambda: read_stage(directory, 'confirmation'))
        envelope('confirmation', rows)
        raw = json.loads((directory/'confirmation.json').read_text()); raw['sources']['v3_adwin.py'] = 'wrong'
        write(directory/'confirmation.json', raw); rejects(lambda: read_stage(directory, 'confirmation'))
        broken = copy.deepcopy(rows); broken['slope/133000']['privileged_timing'] = False
        envelope('confirmation', broken); rejects(lambda: read_stage(directory, 'confirmation'))
        broken = copy.deepcopy(rows); broken['slope/133000']['memory']['core']['quiet']['resets'][0]['kind'] = 'random'
        rejects(lambda: absolute_summary(broken))
        broken = copy.deepcopy(rows); broken['slope/133000']['memory']['core']['quiet']['regime_slope_share'] = 2.
        rejects(lambda: absolute_summary(broken))
        envelope('confirmation', rows)
        for k in tuning:
            if k.startswith('slope/'): tuning[k]['status'] = 'nonfinite'
        envelope('tuning', tuning); manifest = make_manifest(tuning); write(directory/'manifest.json', manifest)
        rejects(lambda: summarize(directory))
        with patch('study_v3_slope.require_committed'): rejects(lambda: confirm(directory))
        (directory/'confirmation.json').unlink()
        assert summarize(directory)['status'] == 'tuning_inconclusive'
        publish_report(directory); publish_report(directory, True)
    with tempfile.TemporaryDirectory(dir='.') as tmp:
        p = Path(tmp)/'uncommitted.json'; p.write_text('{}'); rejects(lambda: require_committed(p))
    for arm in ARMS:
        config = GRIDS[arm][0] if arm in FAMILIES else dict(FAST) if arm == 'oracle_nofallback' else dict(GRIDS['slope'][0])
        row = measure_row(130002, arm, config, .001 if arm == 'random_slope' else None)
        assert row['status'] == 'ok' and len(row['fixtures']) == 5
        assert row['privileged_timing'] == (arm not in ('window', 'sgd', 'adwin'))
        if arm not in FAMILIES:
            for records in row['memory'].values():
                for record in records.values():
                    for reset in record['resets']:
                        if arm == 'random_slope':
                            assert reset['kind'] == 'random'
                        else:
                            assert reset['kind'] in ('target', 'drift')
    print('PASS slope lifecycle: boundary provenance, source/manifest/stage gates, complete reports, all-arm development fixtures', flush=True)


def archive_checks(directory, reproduce):
    stored = publish_report(directory, True)
    for path, expected in source_hashes().items():
        assert hashlib.sha256((directory/'source-snapshots'/(expected+'.txt')).read_bytes()).hexdigest() == expected, path
    manifest = json.loads((directory/'manifest.json').read_text()); tuning = read_stage(directory, 'tuning')
    assert manifest == make_manifest(tuning)
    print('PASS slope archive tuning', len(tuning), flush=True)
    if not reproduce:
        if stored['counts']['confirmation']: read_stage(directory, 'confirmation')
        return
    fresh = {}
    for arm in FAMILIES:
        for i, config in enumerate(GRIDS[arm]):
            for seed in SEEDS['tuning']:
                key = f'{arm}/{i}/{seed}'; fresh[key] = measure_row(seed, arm, config)
                compare(fresh[key], scientific(tuning[key]), key)
        print('PASS slope reproduction tuning', arm, '96 rows', flush=True)
    fresh_manifest = make_manifest(fresh); compare(fresh_manifest, manifest, ignore=('tuning_digest',))
    if stored['counts']['confirmation']:
        archived = read_stage(directory, 'confirmation'); recreated = {}
        for arm in ARMS:
            for seed in SEEDS['confirmation']:
                key = f'{arm}/{seed}'
                recreated[key] = measure_row(seed, arm, fresh_manifest['screen']['selected'][arm],
                    fresh_manifest['screen']['random_frequency']['probability'] if arm == 'random_slope' else None, fresh_manifest)
                compare(recreated[key], scientific(archived[key]), key, ignore=('manifest_digest',))
            print('PASS slope reproduction confirmation', arm, '32 rows', flush=True)
        compare(performance_decision(recreated), stored['decisions']['slope'])
        compare(absolute_summary(recreated), stored['absolute'])
    print('PASS full slope reproduction; only reached partitions sampled', flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--evidence', type=Path)
    parser.add_argument('--reproduce', action='store_true')
    args = parser.parse_args()
    kernel_checks(); policy_checks(); lifecycle_checks()
    if args.evidence: archive_checks(args.evidence, args.reproduce)
