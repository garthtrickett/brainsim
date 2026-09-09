"""Follow-up policy tests and complete reached-stage numerical reproduction."""
import argparse
import copy
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile

from check_v3_gate import compare
from check_v3_slice1 import instrument_checks, learning_checks
from report_v3_gain import publish_report
from study_v3_gain import (SOURCES, allow_diagnostics, allow_performance, calibration_row,
                           diagnostics, diagnostic_row, filenames, make_manifest,
                           performance_row, read_stage, registration_check, require_committed,
                           source_hashes, tuning_row, write)
from v3_gain_policy import (ARMS, GATED, GRIDS, KEYS, PROTOCOL, SEEDS, contrast, detector_cell,
                            detector_decision, digest, performance_decision, scientific, tuning_screen)
from v3_slice1_learning import warmup
from v3_slice1_streams import COORDINATES


def rejects(fn):
    try:
        fn()
    except (ValueError, KeyError, FileNotFoundError, subprocess.CalledProcessError):
        return
    raise AssertionError('expected rejection')


def store_stage(directory, stage, rows):
    for name in filenames(stage):
        shard = rows
        if stage == 'tuning':
            arm = name.removeprefix('tuning-').removesuffix('.json')
            shard = {k: v for k, v in rows.items() if k.startswith(arm + '/')}
        write(directory/name, {'protocol': PROTOCOL, 'sources': source_hashes(), 'rows': shard})


def fixtures():
    # Synthetic result records only; no tuning/calibration/confirmation observations.
    tuning = {key: {'status': 'ok', 'metrics': {'coordinates': {
        c: {'excess_mse': float(1 + abs(int(key.split('/')[1]) - 17))}
        for c in COORDINATES}}} for key in KEYS['tuning']}
    calibration = {key: {'status': 'ok', 'modes': {mode: {
        'maxima': {c: [.5] * 50 for c in ('quiet', 'noisy')}, 'gate_means': [.1, .2, .3, .4]}
        for mode in ('fixed', 'closed')}} for key in KEYS['calibration']}

    def metric(kinds=(), hit=False):
        return {'block_count': 0, 'block_total': 50, 'point_count': 0, 'point_total': 5000,
                'gate_initial': 0., 'gate_mean': .1, 'events': [
                    {'index': 2000 + 2000*i, 'kind': k, 'hit': hit, 'latency': 0 if hit else 100}
                    for i, k in enumerate(kinds)]}

    modes = {mode: {'core': {'quiet': metric(), 'noisy': metric(),
                            'switch_quiet': metric(('target_down', 'target_up'), True),
                            'switch_noisy': metric(('target_down', 'target_up'), True)},
                    'noise_jump': {'noise_jump': metric(('noise_increase', 'noise_decrease'))},
                    'drift': {'drift': metric()}, 'exactly_quiet': {'exactly_quiet': metric()}}
             for mode in ('fixed', 'closed')}
    diagnostic = {key: {'status': 'ok', 'modes': copy.deepcopy(modes)} for key in KEYS['diagnostics']}
    performance = {}
    for key in KEYS['performance']:
        value = .5 if key.startswith('candidate/') else 1.
        coordinates = {'core': COORDINATES, 'noise_jump': ('noise_jump',),
                       'drift': ('drift',), 'exactly_quiet': ('exactly_quiet',)}
        performance[key] = {'status': 'ok', 'fixtures': {name: {'coordinates': {
            c: {'post_mse': value, 'excess_mse': value,
                'windows': {'noise_increase': value, 'noise_decrease': value, 'drift': value}}
            for c in names}} for name, names in coordinates.items()}}
    return tuning, calibration, diagnostic, performance


def policy_checks():
    registration_check()
    assert all(len(g) == 48 for g in GRIDS.values())
    assert [len(KEYS[s]) for s in ('tuning', 'calibration', 'diagnostics', 'performance')] == [3840, 48, 96, 192]
    partitions = list(SEEDS.values())
    assert all(not set(a) & set(b) for i, a in enumerate(partitions) for b in partitions[i+1:])
    assert all(min(s) >= 40000 and max(s) < 45000 for s in partitions)
    assert {'lr': .004, 'gain': 64.} in GRIDS['candidate']
    tuning, calibration, diagnostic, performance = fixtures()
    assert tuning_screen(tuning)['status'] == 'eligible'

    def prefer(arm, index):
        altered = copy.deepcopy(tuning)
        for seed in SEEDS['tuning']:
            for m in altered[f'{arm}/{index}/{seed}']['metrics']['coordinates'].values():
                m['excess_mse'] = .1
        return altered

    boundary = prefer('candidate', 23)
    screen = tuning_screen(boundary)
    assert screen['status'] == 'search_inconclusive' and screen['detector_allowed']
    assert screen['added_step_amplitude']['candidate'] == .004 * 1024
    assert tuning_screen(prefer('historical', 47))['status'] == 'eligible'
    assert tuning_screen(prefer('single', 23))['status'] == 'search_inconclusive'
    assert tuning_screen(prefer('sgd', 0))['status'] == 'search_inconclusive'
    zero = tuning_screen(prefer('candidate', 16))
    assert zero['status'] == 'tuning_negative' and not zero['detector_allowed']
    assert tuning_screen(prefer('candidate', 0))['status'] == 'tuning_negative'
    bad = copy.deepcopy(tuning)
    for key in bad:
        if key.startswith('adam/'):
            bad[key] = {'status': 'nonfinite', 'reason': 'synthetic divergence'}
    assert not tuning_screen(bad)['detector_allowed']
    rejects(lambda: tuning_screen({k: v for k, v in tuning.items() if k != next(iter(tuning))}))
    bad = copy.deepcopy(tuning)
    next(iter(bad.values()))['metrics']['coordinates']['quiet']['excess_mse'] = float('nan')
    rejects(lambda: tuning_screen(bad))
    manifest = make_manifest(boundary, calibration)
    assert manifest['thresholds']['candidate']['fixed'] == .5
    compare([.1, .2, .3, .4], manifest['constants'], 'calibration constants')
    allow_diagnostics(manifest)
    rejects(lambda: allow_performance(manifest, {'status': 'detector_pass'}))
    eligible = make_manifest(tuning, calibration)
    allow_performance(eligible, {'status': 'detector_pass'})
    rejects(lambda: allow_performance(eligible, {'status': 'detector_negative'}))
    bad = copy.deepcopy(calibration)
    bad[next(iter(bad))] = {'status': 'nonfinite', 'reason': 'synthetic failure'}
    rejects(lambda: allow_diagnostics(make_manifest(tuning, bad)))
    bad = copy.deepcopy(calibration)
    next(iter(bad.values()))['modes']['fixed']['maxima']['quiet'].pop()
    rejects(lambda: make_manifest(tuning, bad))
    with tempfile.TemporaryDirectory(dir='.', prefix='.uncommitted-gain-') as tmp:
        path = Path(tmp)
        write(path/'manifest.json', eligible)
        rejects(lambda: diagnostics(path))
        assert not (path/'diagnostics.json').exists()
    assert detector_cell([4]*32, [5]*32, True)['pass']
    assert not detector_cell([3]*32, [5]*32, True)['pass']
    assert detector_cell([5]*32, [100]*32)['pass']
    assert not detector_cell([6]*32, [100]*32)['pass']
    rejects(lambda: detector_cell([float('nan')], [1]))
    decision = detector_decision(diagnostic)
    assert decision['status'] == 'detector_pass' and len(decision['cells']) == 16
    # Each direction/regime is mandatory. Eight misses cross 80%; a good direction cannot hide it.
    failed = copy.deepcopy(diagnostic)
    for seed in SEEDS['diagnostics'][:8]:
        event = failed[f'candidate/{seed}']['modes']['fixed']['core']['switch_noisy']['events'][1]
        event.update(hit=False, latency=100)
    assert detector_decision(failed)['status'] == 'detector_negative'
    bad = copy.deepcopy(diagnostic)
    bad['candidate/43000']['modes']['closed']['core']['quiet']['block_total'] = 49
    rejects(lambda: detector_decision(bad))
    bad = copy.deepcopy(diagnostic)
    bad['candidate/43000']['modes']['closed']['core']['switch_quiet']['events'].pop()
    rejects(lambda: detector_decision(bad))
    bad = copy.deepcopy(diagnostic)
    bad['candidate/43000']['modes']['closed']['core']['quiet']['block_count'] = float('nan')
    rejects(lambda: detector_decision(bad))
    assert contrast([10.]*32, [9.]*32, True)['pass']
    assert not contrast([10.]*32, [9.01]*32, True)['pass']
    assert contrast([1.25]*32, [1.375]*32, False)['pass']
    assert not contrast([1.25]*32, [1.376]*32, False)['pass']
    positive = performance_decision(performance)
    assert positive['status'] == 'positive' and len(positive['cells']) == 44
    bad = copy.deepcopy(performance)
    for key in bad:
        if key.startswith('constant/'):
            bad[key]['fixtures']['core']['coordinates']['switch_noisy']['post_mse'] = 0.
            bad[key]['fixtures']['core']['coordinates']['switch_quiet']['post_mse'] = 0.
    assert performance_decision(bad)['status'] == 'learning_negative'
    rejects(lambda: performance_decision({k: v for k, v in performance.items() if not k.startswith('constant/')}))
    # Exercise every legitimate endpoint and forbidden-stage rejection without drawing observations.
    for rows, cal, diag, perf, expected in (
            (prefer('candidate', 16), None, None, None, 'tuning_negative'),
            (boundary, calibration, None, None, 'awaiting_diagnostics'),
            (boundary, calibration, diagnostic, None, 'search_inconclusive'),
            (boundary, calibration, failed, None, 'detector_negative'),
            (tuning, calibration, diagnostic, performance, 'positive')):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp)
            (path/'source-snapshots').mkdir()
            frozen = make_manifest(rows, cal)
            write(path/'manifest.json', frozen)
            store_stage(path, 'tuning', rows)
            if cal is not None:
                store_stage(path, 'calibration', cal)
            if diag is not None:
                diag = copy.deepcopy(diag)
                for row in diag.values():
                    row['manifest_digest'] = digest(frozen)
                store_stage(path, 'diagnostics', diag)
                write(path/'diagnostic-decision.json', {'manifest_digest': digest(frozen),
                      'evidence_digest': digest(diag), **detector_decision(diag)})
            if perf is not None:
                perf = copy.deepcopy(perf)
                for row in perf.values():
                    row['manifest_digest'] = digest(frozen)
                store_stage(path, 'performance', perf)
            summary = publish_report(path)
            assert summary['status'] == expected
            publish_report(path, check=True)
            if perf is None:
                write(path/'performance.json', {})
                rejects(lambda: publish_report(path))
    print('PASS gain policy: equal budgets, search/detector separation, calibration, all 16/44 cells, stage and manifest enforcement', flush=True)


def archive_checks(directory):
    summary = publish_report(directory, check=True)
    require_committed(directory/'manifest.json')
    for stage in summary['reached']:
        for name in filenames(stage):
            envelope = json.loads((directory/name).read_text())
            assert set(envelope['sources']) == set(SOURCES)
            for source, fingerprint in envelope['sources'].items():
                blob = (directory/'source-snapshots'/(fingerprint + '.txt')).read_bytes()
                assert hashlib.sha256(blob).hexdigest() == fingerprint, source
                assert Path(source).read_bytes() == blob, source
        print('PASS gain archive', stage, summary['counts'][stage], 'rows', flush=True)
    return summary


def reproduce(directory, summary):
    warmup()
    expected_manifest = json.loads((directory/'manifest.json').read_text())
    actual_rows = {}
    with tempfile.TemporaryDirectory(prefix='brainsim-gain-reproduction-') as tmp:
        out = Path(tmp)
        for stage in summary['reached']:
            rows = {}
            for key, wanted in read_stage(directory, stage).items():
                pieces = key.split('/')
                arm, seed = pieces[0], int(pieces[-1])
                if stage == 'tuning':
                    row = tuning_row(seed, arm, GRIDS[arm][int(pieces[1])])
                elif stage == 'calibration':
                    row = calibration_row(seed, arm, expected_manifest['screen']['selected'][arm])
                elif stage == 'diagnostics':
                    row = diagnostic_row(seed, arm, expected_manifest)
                else:
                    row = performance_row(seed, arm, expected_manifest)
                compare(scientific(wanted), scientific(row), stage + '/' + key)
                rows[key] = row
            actual_rows[stage] = rows
            store_stage(out, stage, rows)
            print('PASS gain reproduction', stage, len(rows), 'scientific rows', flush=True)
        actual_manifest = make_manifest(actual_rows['tuning'], actual_rows.get('calibration'))
        assert set(actual_manifest) == set(expected_manifest)
        for key in expected_manifest.keys() - {'tuning_digest', 'calibration_digest'}:
            compare(expected_manifest[key], actual_manifest[key], 'manifest/' + key)
        write(out/'manifest.json', actual_manifest)
        for stage in ('diagnostics', 'performance'):
            if stage in actual_rows:
                for row in actual_rows[stage].values():
                    row['manifest_digest'] = digest(actual_manifest)
                store_stage(out, stage, actual_rows[stage])
        if 'diagnostics' in actual_rows:
            write(out/'diagnostic-decision.json', {'manifest_digest': digest(actual_manifest),
                  'evidence_digest': digest(actual_rows['diagnostics']), **detector_decision(actual_rows['diagnostics'])})
        (out/'source-snapshots').mkdir()
        actual_summary = publish_report(out)
        for stage, decision in summary['decisions'].items():
            excluded = ('manifest_digest', 'evidence_digest')
            compare({k: v for k, v in decision.items() if k not in excluded},
                    {k: v for k, v in actual_summary['decisions'][stage].items() if k not in excluded},
                    'decision/' + stage)
        for key in summary.keys() - {'manifest_digest', 'decisions'}:
            compare(summary[key], actual_summary[key], 'summary/' + key)
    print('PASS full follow-up reproduction; unreached stages were not sampled', flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--evidence', type=Path)
    parser.add_argument('--reproduce', action='store_true')
    args = parser.parse_args()
    if args.reproduce and not args.evidence:
        parser.error('--reproduce requires --evidence')
    instrument_checks()
    learning_checks()
    policy_checks()
    if args.evidence:
        summary = archive_checks(args.evidence)
        if args.reproduce:
            reproduce(args.evidence, summary)


if __name__ == '__main__':
    main()
