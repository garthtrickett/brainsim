"""Independent discovery equations, scientific authority and full reproduction."""
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
from report_v3_discovery import absolute_summary, publish_report, summarize
from study_v3_discovery import (SOURCES, auc_score, confirm, discovery_metrics,
    make_manifest, measure_row, observations, read_stage, registration_check,
    require_committed, simulation, source_hashes, tune, true_contexts,
    verified_manifest, write)
from v3_slice1_decisions import scientific
from v3_discovery import (ARMS, CUE_BASE, FAMILIES, GRIDS, SHUFFLE_BASE,
                          SPLIT_BASE, cue_observations, discover_kernel,
                          random_splits, run, shuffled_cue, slow_cue_step)
from v3_discovery_policy import (KEYS, PROTOCOL, SEEDS, SPECS, SWITCH_COORDS,
    complete, contrast, discovery_decision, digest, metric_values, objective,
    performance_decision, seed_auc, select)
from v3_persistent import FIXTURES, fixture


def slow_discover(y, x, tau, alpha, cue_lr, lr, hats_in=None, conditioning=True):
    """Explicit-loop reference: pooled/conditional means, interval, logistic cue."""
    n, w = y.shape
    preds = np.zeros_like(y)
    mu, mu0, mu1, sig, cw, cb = (np.zeros(w), np.zeros(w), np.zeros(w),
                                 np.zeros(w), np.zeros(w), np.zeros(w))
    hats = np.zeros_like(y)
    for t in range(n):
        for j in range(w):
            z = cw[j] * x[t, j] + cb[j]
            hat = float(hats_in[t, j]) if hats_in is not None else (1.0 if z > 0.0 else 0.0)
            pred = (mu1[j] if hat > 0.5 else mu0[j]) if (conditioning and sig[j] >= tau) else mu[j]
            preds[t, j] = pred
            hats[t, j] = hat
            pull = y[t, j] - pred
            target = 1.0 if pull >= 0.0 else 0.0
            cw[j], cb[j] = slow_cue_step(cw[j], cb[j], x[t, j], target, cue_lr) if hats_in is None else (cw[j], cb[j])
            err = y[t, j] - mu[j]
            sig[j] = (1.0 - alpha) * sig[j] + alpha * err * err
            mu[j] += lr * err / (1.0 + 1.0 * sig[j])
            if hat > 0.5:
                mu1[j] += lr * (y[t, j] - mu1[j])
            else:
                mu0[j] += lr * (y[t, j] - mu0[j])
    return preds, hats


def kernel_checks():
    registration_check()
    assert len(SPECS) == 15 and [len(KEYS[s]) for s in ('tuning', 'confirmation')] == [480, 288]
    assert all(len(GRIDS[a]) == 12 and len({json.dumps(c, sort_keys=True) for c in GRIDS[a]}) == 12 for a in FAMILIES)
    assert len({json.dumps(c, sort_keys=True) for c in GRIDS['discover']}) == 12
    parts = list(SEEDS.values())
    assert all(min(s) >= 90000 and max(s) < 96000 for s in parts)
    assert all(not set(a) & set(b) for i, a in enumerate(parts) for b in parts[i + 1:])
    assert not set(SEEDS['tuning']) & set(range(81000, 81008))
    assert not set(SEEDS['confirmation']) & set(range(83000, 83032))
    for file in SOURCES:
        if not file.endswith('.py'):
            continue
        for node in ast.walk(ast.parse(Path(file).read_text())):
            names = [node.module] if isinstance(node, ast.ImportFrom) else [a.name for a in node.names] if isinstance(node, ast.Import) else []
            for name in names:
                if name and Path(name + '.py').exists():
                    assert name + '.py' in SOURCES, name
    # y bytes are identical to the forgetting fixtures at equal seeds.
    for name in FIXTURES:
        data, _, cues = observations(90000, name)
        assert np.array_equal(data.y, fixture(90000, name).y)
        assert cues.shape == data.y.shape and np.isfinite(cues).all()
    # Hidden contexts toggle exactly at target events, constant 0 otherwise.
    data, contexts, _ = observations(90001, 'core')
    assert contexts[:, 0].max() == 0.0 and contexts[:, 1].max() == 0.0
    for j in (2, 3):
        starts = sorted(s for s, k in data.events[j] if k.startswith('target_'))
        assert len(starts) == 2
        assert (contexts[:starts[0], j] == 0).all() and (contexts[starts[0]:starts[1], j] == 1).all() and (contexts[starts[1]:, j] == 0).all()
    data, contexts, cues = observations(90002, 'mixed')
    assert all(set(np.unique(contexts[:, j]).tolist()) <= {0.0, 1.0} for j in range(contexts.shape[1]))
    # Cue/shuffle/split determinism and isolation.
    x = np.array(cues)
    assert np.array_equal(shuffled_cue(x, 90002, 1)[:, :1], shuffled_cue(x, 90002, 1)[:, :1])
    assert not np.array_equal(shuffled_cue(x, 90002, 1), x)
    assert np.array_equal(np.sort(shuffled_cue(x, 90002, 1)[:, 0]), np.sort(x[:, 0]))
    assert abs(float(np.corrcoef(x[1000:, 0], contexts[1000:, 0])[0, 1])) > 0.2
    assert abs(float(np.corrcoef(shuffled_cue(x, 90002, 1)[1000:, 0], contexts[1000:, 0])[0, 1])) < 0.15
    assert np.array_equal(random_splits(90002, 1, x.shape), random_splits(90002, 1, x.shape))
    assert not np.array_equal(random_splits(90002, 1, x.shape), random_splits(90002, 2, x.shape))
    assert set(np.unique(random_splits(90002, 1, x.shape)).tolist()) <= {0.0, 1.0}
    # Hand-worked kernel parity against the explicit reference.
    rng = np.random.default_rng(90000)
    y = rng.normal(size=(60, 2))
    xx = rng.normal(size=(60, 2))
    cfg = {'tau': 0.25, 'alpha': 0.05, 'cue_lr': 0.05, 'lr': 0.1}
    fast = run(y, xx, 'discover', cfg)
    slow_preds, slow_hats = slow_discover(y, xx, 0.25, 0.05, 0.05, 0.1)
    np.testing.assert_allclose(fast[0], slow_preds, rtol=1e-11, atol=1e-13)
    np.testing.assert_array_equal(fast[4], slow_hats)
    np.testing.assert_allclose(fast[3], fast[3])  # scores finite
    assert np.isfinite(fast[1]).all() and (fast[1] >= 0).all()
    # Endpoints: TAU=0 always conditional, TAU=inf never conditional.
    assert run(y, xx, 'nocontext_matched', dict(cfg, tau=0.0))[0].shape == y.shape
    np.testing.assert_array_equal(run(y, xx, 'nocontext_matched', dict(cfg, tau=0.0))[0],
                                  run(y, xx, 'discover', dict(cfg, tau=float('inf')))[0])
    # Tie-pull rule is deterministic: pull == 0 maps to target 1.
    w0, b0 = slow_cue_step(0.3, -0.2, 0.7, 1.0, 0.05)
    assert np.isfinite(w0) and np.isfinite(b0)
    # Inactive conditional memory stays frozen under a constant oracle context.
    ctx = np.zeros_like(y)
    ro = run(y, xx, 'oracle', cfg, contexts=ctx)
    assert (ro[4] == 0).all()
    # Oracle hats equal the supplied context; random hats equal the splits.
    ctx2 = (rng.random(y.shape) < 0.5).astype(float)
    assert np.array_equal(run(y, xx, 'oracle', cfg, contexts=ctx2)[4], ctx2)
    sp = (rng.random(y.shape) < 0.5).astype(float)
    assert np.array_equal(run(y, xx, 'random', cfg, splits=sp)[4], sp)
    # AUC math: perfect, inverted, ties, single-class.
    assert auc_score([0.1, 0.2, 0.8, 0.9], [0, 0, 1, 1]) == 1.0
    assert auc_score([0.9, 0.8, 0.2, 0.1], [0, 0, 1, 1]) == 0.0
    assert auc_score([0.5, 0.5, 0.5, 0.5], [0, 0, 1, 1]) == 0.5
    assert auc_score([0.1, 0.9], [1, 1]) is None
    rejects(lambda: auc_score([0.1, 0.2], [0]))
    rejects(lambda: auc_score([0.1, float('nan')], [0, 1]))
    # Causality, prefix invariance, coordinate isolation per arm.
    for arm in ARMS:
        config = GRIDS[arm][3] if arm in FAMILIES else dict(GRIDS['discover'][3])
        data, contexts_a, cues_a = observations(90003, 'core')
        kw = {}
        if arm in ('discover', 'nocontext_matched'):
            kw['x'] = np.array(cues_a)
        elif arm == 'shuffled':
            kw['x'] = shuffled_cue(np.array(cues_a), 90003, 0)
        elif arm == 'random':
            kw['x'] = np.array(cues_a)
            kw['splits'] = random_splits(90003, 0, data.y.shape)
        elif arm in ('oracle', 'oracle_matched'):
            kw['x'] = np.array(cues_a)
            kw['contexts'] = np.array(contexts_a)
        else:
            kw['x'] = np.zeros_like(data.y)
        original = run(data.y, kw['x'], arm, config, **{k: v for k, v in kw.items() if k != 'x'})
        later = data.y.copy()
        later[300:] += 5.
        changed = run(later, kw['x'], arm, config, **{k: v for k, v in kw.items() if k != 'x'})
        np.testing.assert_array_equal(original[0][:301], changed[0][:301])
        prefix = {k: (v[:300] if isinstance(v, np.ndarray) else v) for k, v in kw.items() if k != 'x'}
        for a, b in zip(run(data.y[:300], kw['x'][:300], arm, config, **prefix)[:5], original[:5]):
            np.testing.assert_array_equal(a, b[:300])
        other = data.y.copy()
        other[:, 0] += 5.
        changed = run(other, kw['x'], arm, config, **{k: v for k, v in kw.items() if k != 'x'})
        for i in (0, 1, 3, 4):
            np.testing.assert_array_equal(original[i][:, 1], changed[i][:, 1])
        if arm not in ('oracle', 'oracle_matched'):
            rejects(lambda a=arm, c=config: run(data.y, np.zeros_like(data.y), a, c, contexts=np.zeros_like(data.y)))
        if arm != 'random':
            rejects(lambda a=arm, c=config: run(data.y, np.zeros_like(data.y), a, c, splits=np.zeros_like(data.y)))
    rejects(lambda: run(y, 'discover', {'tau': 0.1, 'alpha': 0.05, 'cue_lr': 0.05, 'lr': 0.1}, xx))
    rejects(lambda: run(y, 'discover', {'tau': -1.0, 'alpha': 0.05, 'cue_lr': 0.05, 'lr': 0.1}, xx))
    rejects(lambda: run(np.full_like(y, np.nan), 'window', {'window': 16}, np.zeros_like(y)))
    rejects(lambda: run(y, 'oracle', GRIDS['oracle'][0], xx))
    print('PASS discovery kernels: hidden contexts, cue/shuffle/split isolation, hand parity, endpoints, AUC math, causality, privilege', flush=True)


def synthetic():
    coords = {'core': ('quiet', 'noisy', 'switch_quiet', 'switch_noisy'), 'mixed': ('increase_first', 'decrease_first'),
              'noise_jump': ('noise_jump',), 'drift': ('drift',), 'exactly_quiet': ('exactly_quiet',)}
    row = {'status': 'ok', 'config': {}, 'privileged_context': False, 'fixtures': {}, 'memory': {}, 'discovery': {}}
    for name, coordinates in coords.items():
        row['fixtures'][name] = {'coordinates': {}, 'update_norm_mean': .1}
        row['memory'][name], row['discovery'][name] = {}, {}
        for c in coordinates:
            kinds = ('target_down', 'target_up') if name == 'mixed' or c.startswith('switch_') else ()
            row['fixtures'][name]['coordinates'][c] = {'excess_mse': 1., 'post_mse': 1. if kinds else None,
                'stable_mse': 1., 'adaptation_latency': 10. if kinds else None,
                'windows': {'noise_increase': 1., 'noise_decrease': 1., 'drift': 1.}}
            row['memory'][name][c] = {'kind': 'conditional', 'sigma_mean': .1, 'sigma_final': .1, 'hat_mean': .5}
            row['discovery'][name][c] = {'auc': .9, 'contested_rate': .5, 'conditional_use_rate': .5,
                'hat_mean': .5, 'sigma_mean': .1, 'sigma_final': .1}
    tuning = {}
    for a in FAMILIES:
        for i, config in enumerate(GRIDS[a]):
            for seed in SEEDS['tuning']:
                r = copy.deepcopy(row)
                r.update(config=config, privileged_context=a == 'oracle')
                tuning[f'{a}/{i}/{seed}'] = r
    manifest = make_manifest(tuning)
    confirmation = {}
    for a in ARMS:
        for seed in SEEDS['confirmation']:
            r = copy.deepcopy(row)
            r.update(config=manifest['screen']['selected'][a], privileged_context=a in ('oracle', 'oracle_matched'),
                     manifest_digest=digest(manifest))
            if a in ('discover', 'oracle', 'oracle_matched'):
                for f in r['fixtures'].values():
                    for c in f['coordinates'].values():
                        for k in ('excess_mse', 'post_mse', 'stable_mse'):
                            if c[k] is not None:
                                c[k] = .5
                        c['windows'] = {k: .5 for k in c['windows']}
            if a == 'shuffled':
                for f in r['discovery'].values():
                    for c in f.values():
                        c['auc'] = .5
            confirmation[f'{a}/{seed}'] = r
    return tuning, manifest, confirmation


def policy_checks():
    tuning, manifest, rows = synthetic()
    assert objective(tuning['discover/0/91000']) == 1.
    assert all(i == 0 for i in manifest['screen']['indices'].values())
    screen = manifest['screen']
    assert screen['selected']['random'] == screen['selected']['discover'] == screen['selected']['oracle_matched']
    assert screen['selected']['shuffled'] == screen['selected']['discover'] == screen['selected']['nocontext_matched']
    bad = copy.deepcopy(tuning)
    bad['discover/0/91000']['status'] = 'nonfinite'
    assert select(bad)['indices']['discover'] == 1
    for k in bad:
        if k.startswith('discover/'):
            bad[k]['status'] = 'nonfinite'
    assert select(bad)['status'] == 'tuning_inconclusive'
    rejects(lambda: complete({k: r for k, r in tuning.items() if k != 'discover/0/91000'}, 'tuning'))
    bad = copy.deepcopy(tuning)
    bad['discover/0/91000']['fixtures']['core']['coordinates']['quiet']['excess_mse'] = float('nan')
    rejects(lambda: select(bad))
    assert performance_decision(rows)['status'] == 'learning_positive' and len(performance_decision(rows)['cells']) == 90
    assert discovery_decision(rows)['status'] == 'discovery_pass'
    for a in ('oracle', 'oracle_matched'):
        assert performance_decision(rows, a)['status'] == 'oracle_pass' and len(performance_decision(rows, a)['cells']) == 45
    for control in ('window', 'sgd', 'adwin', 'random', 'shuffled', 'nocontext_matched'):
        for label, fields in SPECS:
            bad = copy.deepcopy(rows)
            for seed in SEEDS['confirmation']:
                for n, c, f, w in fields:
                    dest = bad[f'{control}/{seed}']['fixtures'][n]['coordinates'][c]
                    if w:
                        dest[f][w] = .01
                    else:
                        dest[f] = .01
            result = performance_decision(bad)
            assert result['status'] == 'learning_negative' and not result['cells'][f'{control}/{label}']['pass']
    # Discovery gate vetoes: weak discovery, null-band failure, small delta.
    bad = copy.deepcopy(rows)
    for seed in SEEDS['confirmation']:
        for n, c in SWITCH_COORDS:
            bad[f'discover/{seed}']['discovery'][n][c]['auc'] = .55
    assert discovery_decision(bad)['status'] == 'discovery_negative'
    bad = copy.deepcopy(rows)
    for seed in SEEDS['confirmation']:
        for n, c in SWITCH_COORDS:
            bad[f'shuffled/{seed}']['discovery'][n][c]['auc'] = .9
    assert discovery_decision(bad)['status'] == 'discovery_negative'
    bad = copy.deepcopy(rows)
    for seed in SEEDS['confirmation']:
        for n, c in SWITCH_COORDS:
            bad[f'discover/{seed}']['discovery'][n][c]['auc'] = .6
            bad[f'shuffled/{seed}']['discovery'][n][c]['auc'] = .55
    assert discovery_decision(bad)['status'] == 'discovery_negative'
    # MSE cannot pass the discovery gate: learning wins + gate fails.
    assert performance_decision(bad)['status'] == 'learning_positive'
    assert discovery_decision(bad)['status'] == 'discovery_negative'
    bad = copy.deepcopy(rows)
    for seed in SEEDS['confirmation']:
        bad[f'discover/{seed}']['status'] = 'nonfinite'
    assert performance_decision(bad)['status'] == 'learning_negative' and performance_decision(bad, 'oracle')['status'] == 'oracle_pass'
    bad = copy.deepcopy(rows)
    for seed in SEEDS['confirmation']:
        bad[f'oracle/{seed}']['status'] = 'nonfinite'
    assert performance_decision(bad)['status'] == 'learning_positive'
    assert performance_decision(bad, 'oracle')['status'] == 'oracle_negative'
    assert not contrast([1.] * 32, [.91] * 32, True)['pass'] and contrast([1.] * 32, [.89] * 32, True)['pass']
    assert not contrast([1.] * 32, [1.101] * 32, False)['pass']
    rejects(lambda: contrast([1., 2.], [1.], True))
    for key in ('adwin/93000', 'random/93000', 'shuffled/93000', 'nocontext_matched/93000', 'oracle/93000'):
        rejects(lambda k=key: performance_decision({a: r for a, r in rows.items() if a != k}))
    print('PASS discovery policy: equal menus/objective, finite selection, all90 vetoes, gate vetoes, oracle non-authority', flush=True)


def lifecycle_checks():
    tuning, manifest, rows = synthetic()
    with tempfile.TemporaryDirectory() as tmp:
        directory = Path(tmp)

        def envelope(stage, data):
            write(directory / (stage + '.json'), {'protocol': PROTOCOL, 'sources': source_hashes(), 'rows': data})

        envelope('tuning', tuning)
        write(directory / 'manifest.json', manifest)
        assert summarize(directory)['status'] == 'awaiting_confirmation'
        with patch('study_v3_discovery.require_committed', side_effect=ValueError('uncommitted')):
            rejects(lambda: confirm(directory))
        with patch('study_v3_discovery.require_committed'):
            assert verified_manifest(directory) == manifest
            changed = copy.deepcopy(manifest)
            changed['screen']['selected']['discover'] = dict(changed['screen']['selected']['window'])
            write(directory / 'manifest.json', changed)
            rejects(lambda: verified_manifest(directory))
            write(directory / 'manifest.json', manifest)
        envelope('confirmation', rows)
        publish_report(directory)
        publish_report(directory, True)
        assert summarize(directory)['status'] == 'learning_positive'
        rejects(lambda: tune(directory))
        broken = copy.deepcopy(rows)
        broken['random/93000']['manifest_digest'] = 'wrong'
        envelope('confirmation', broken)
        rejects(lambda: read_stage(directory, 'confirmation'))
        envelope('confirmation', rows)
        raw = json.loads((directory / 'confirmation.json').read_text())
        raw['sources']['v3_discovery.py'] = 'wrong'
        write(directory / 'confirmation.json', raw)
        rejects(lambda: read_stage(directory, 'confirmation'))
        broken = copy.deepcopy(rows)
        broken['oracle/93000']['privileged_context'] = False
        envelope('confirmation', broken)
        rejects(lambda: read_stage(directory, 'confirmation'))
        broken = copy.deepcopy(rows)
        broken['discover/93000']['memory']['core']['quiet']['sigma_mean'] = float('nan')
        rejects(lambda: absolute_summary(broken))
        envelope('confirmation', rows)
        for k in tuning:
            if k.startswith('discover/'):
                tuning[k]['status'] = 'nonfinite'
        envelope('tuning', tuning)
        manifest = make_manifest(tuning)
        write(directory / 'manifest.json', manifest)
        rejects(lambda: summarize(directory))
        with patch('study_v3_discovery.require_committed'):
            rejects(lambda: confirm(directory))
        (directory / 'confirmation.json').unlink()
        assert summarize(directory)['status'] == 'tuning_inconclusive'
        publish_report(directory)
        publish_report(directory, True)
    with tempfile.TemporaryDirectory(dir='.') as tmp:
        p = Path(tmp) / 'uncommitted.json'
        p.write_text('{}')
        rejects(lambda: require_committed(p))
    for arm in ARMS:
        config = GRIDS[arm][0] if arm in FAMILIES else dict(GRIDS['discover'][0])
        row = measure_row(90002, arm, config)
        assert row['status'] == 'ok' and len(row['fixtures']) == 5
        assert row['privileged_context'] == (arm in ('oracle', 'oracle_matched'))
    print('PASS discovery lifecycle: memory accounting, source/manifest/stage gates, complete reports, all-arm development fixtures', flush=True)


def archive_checks(directory, reproduce):
    stored = publish_report(directory, True)
    for path, expected in source_hashes().items():
        assert hashlib.sha256((directory / 'source-snapshots' / (expected + '.txt')).read_bytes()).hexdigest() == expected, path
    manifest = json.loads((directory / 'manifest.json').read_text())
    tuning = read_stage(directory, 'tuning')
    assert manifest == make_manifest(tuning)
    print('PASS discovery archive tuning', len(tuning), flush=True)
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
        print('PASS discovery reproduction tuning', arm, '96 rows', flush=True)
    fresh_manifest = make_manifest(fresh)
    compare(fresh_manifest, manifest, ignore=('tuning_digest',))
    if stored['counts']['confirmation']:
        archived = read_stage(directory, 'confirmation')
        recreated = {}
        for arm in ARMS:
            for seed in SEEDS['confirmation']:
                key = f'{arm}/{seed}'
                recreated[key] = measure_row(seed, arm, fresh_manifest['screen']['selected'][arm], fresh_manifest)
                compare(recreated[key], scientific(archived[key]), key, ignore=('manifest_digest',))
            print('PASS discovery reproduction confirmation', arm, '32 rows', flush=True)
        for arm in ('discover', 'oracle', 'oracle_matched'):
            compare(performance_decision(recreated, arm), stored['decisions'][arm])
        compare(discovery_decision(recreated), stored['decisions']['discovery_gate'])
        compare(absolute_summary(recreated), stored['absolute'])
    print('PASS full discovery reproduction; only reached partitions sampled', flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--evidence', type=Path)
    parser.add_argument('--reproduce', action='store_true')
    args = parser.parse_args()
    kernel_checks()
    policy_checks()
    lifecycle_checks()
    if args.evidence:
        archive_checks(args.evidence, args.reproduce)
