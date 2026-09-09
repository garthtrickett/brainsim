"""Bounded follow-up orchestration, reusing immutable slice1 simulation functions."""
import argparse
import hashlib
import json
from pathlib import Path

import numpy as np

from study_io import Evidence
from study_v3_slice1 import (calibration_row, diagnostic_row, performance_row,
                             require_committed, tuning_row, write)
from v3_gain_policy import (ARMS, GATED, GRIDS, KEYS, PROTOCOL, SEEDS, complete,
                            detector_decision, digest, tuning_screen)
from v3_slice1_learning import warmup

DIRECTORY = Path('results/v3-gain-followup')
SOURCES = ['DESIGN-v3-gain-followup.md', 'DESIGN-v3-slice1.md', 'requirements.txt', 'v3_gain_policy.py', 'study_v3_gain.py',
           'study_v3_slice1.py', 'v3_slice1_streams.py', 'v3_slice1_learning.py',
           'v3_slice1_decisions.py', 'v3_gate.py', 'study_io.py']


def source_hashes():
    return {p: hashlib.sha256(Path(p).read_bytes()).hexdigest() for p in SOURCES}


def registration_check():
    if source_hashes()['DESIGN-v3-gain-followup.md'] != PROTOCOL['registration_sha256']:
        raise ValueError('registered follow-up protocol changed')


def filenames(stage):
    return [f'tuning-{a}.json' for a in ARMS] if stage == 'tuning' else [stage + '.json']


def stage_exists(directory, stage):
    return any((directory/name).exists() for name in filenames(stage))


def read_stage(directory, stage):
    rows = {}
    for name in filenames(stage):
        data = json.loads((directory/name).read_text())
        if data['sources'] != source_hashes() or data['protocol'] != PROTOCOL:
            raise ValueError('source/protocol mismatch: ' + name)
        if set(rows) & set(data['rows']):
            raise ValueError('duplicate evidence keys')
        if stage == 'tuning':
            arm = name.removeprefix('tuning-').removesuffix('.json')
            if any(not k.startswith(arm + '/') for k in data['rows']):
                raise ValueError('wrong tuning shard')
        rows.update(data['rows'])
    complete(rows, stage)
    if stage in ('diagnostics', 'performance'):
        identity = digest(json.loads((directory/'manifest.json').read_text()))
        if any(r.get('manifest_digest') != identity for r in rows.values()):
            raise ValueError('confirmation belongs to another manifest')
    return rows


def make_manifest(tuning, calibration=None):
    screen = tuning_screen(tuning)
    manifest = {'protocol': PROTOCOL, 'sources': source_hashes(), 'seeds': SEEDS,
                'expected_counts': {s: len(k) for s, k in KEYS.items()},
                'screen': screen, 'tuning_digest': digest(tuning), 'calibration_status': 'not_run'}
    if screen['detector_allowed']:
        if calibration is None:
            raise ValueError('complete calibration required before freezing')
        complete(calibration, 'calibration')
        manifest['calibration_digest'] = digest(calibration)
        if any(row['status'] != 'ok' for row in calibration.values()):
            manifest['calibration_status'] = 'nonfinite'
        else:
            for row in calibration.values():
                for mode in ('fixed', 'closed'):
                    values = row['modes'][mode]
                    if len(values['gate_means']) != 4 or any(
                            len(values['maxima'][c]) != 50 for c in ('quiet', 'noisy')):
                        raise ValueError('wrong calibration coordinate/block count')
            manifest['calibration_status'] = 'ok'
            manifest['thresholds'] = {a: {mode: float(np.quantile([
                x for s in SEEDS['calibration'] for c in ('quiet', 'noisy')
                for x in calibration[f'{a}/{s}']['modes'][mode]['maxima'][c]],
                .99, method='higher')) for mode in ('fixed', 'closed')} for a in GATED}
            manifest['constants'] = np.mean([calibration[f'candidate/{s}']['modes']['closed']['gate_means']
                                             for s in SEEDS['calibration']], axis=0).tolist()
    elif calibration is not None:
        raise ValueError('calibration forbidden after tuning-only rejection')
    return json.loads(json.dumps(manifest))


def verified_manifest(directory):
    registration_check()
    require_committed(directory/'manifest.json')
    require_committed(directory/'report-source.json')
    report_hash = hashlib.sha256(Path('report_v3_gain.py').read_bytes()).hexdigest()
    if json.loads((directory/'report-source.json').read_text()) != {'report_v3_gain.py': report_hash}:
        raise ValueError('report source changed after freezing')
    manifest = json.loads((directory/'manifest.json').read_text())
    tuning = read_stage(directory, 'tuning')
    calibration = read_stage(directory, 'calibration') if manifest['screen']['detector_allowed'] else None
    if manifest != make_manifest(tuning, calibration):
        raise ValueError('frozen manifest differs from complete evidence')
    return manifest


def evidence(directory, filename):
    return Evidence(directory/filename, SOURCES, PROTOCOL)


def prepare(directory):
    registration_check()
    if any(stage_exists(directory, s) for s in ('diagnostics', 'performance')):
        raise ValueError('cannot reopen tuning after confirmation')
    for arm in ARMS:
        data = evidence(directory, f'tuning-{arm}.json')
        for index, config in enumerate(GRIDS[arm]):
            for seed in SEEDS['tuning']:
                data.measure(f'{arm}/{index}/{seed}', lambda arm=arm, seed=seed, config=config:
                             tuning_row(seed, arm, config))
    tuning = read_stage(directory, 'tuning')
    screen = tuning_screen(tuning)
    calibration = None
    if screen['detector_allowed']:
        data = evidence(directory, 'calibration.json')
        for arm in GATED:
            for seed in SEEDS['calibration']:
                data.measure(f'{arm}/{seed}', lambda arm=arm, seed=seed:
                             calibration_row(seed, arm, screen['selected'][arm]))
        calibration = read_stage(directory, 'calibration')
    elif stage_exists(directory, 'calibration'):
        raise ValueError('forbidden calibration evidence')
    manifest = make_manifest(tuning, calibration)
    path = directory/'manifest.json'
    if path.exists() and json.loads(path.read_text()) != manifest:
        raise ValueError('frozen manifest changed; a new experiment is required')
    write(path, manifest)
    print('SEARCH', screen['status'], screen['reasons'], screen['selected'], flush=True)
    print('Commit manifest before diagnostics.', flush=True)


def allow_diagnostics(manifest):
    if not manifest['screen']['detector_allowed'] or manifest['calibration_status'] != 'ok':
        raise ValueError('detector prerequisite failed')


def diagnostic_result(directory, manifest):
    rows = read_stage(directory, 'diagnostics')
    return {'manifest_digest': digest(manifest), 'evidence_digest': digest(rows), **detector_decision(rows)}


def diagnostics(directory):
    manifest = verified_manifest(directory)
    allow_diagnostics(manifest)
    if stage_exists(directory, 'performance'):
        raise ValueError('cannot reopen diagnostics after performance')
    data = evidence(directory, 'diagnostics.json')
    for arm in GATED:
        for seed in SEEDS['diagnostics']:
            data.measure(f'{arm}/{seed}', lambda arm=arm, seed=seed: diagnostic_row(seed, arm, manifest))
    result = diagnostic_result(directory, manifest)
    write(directory/'diagnostic-decision.json', result)
    print('DETECTOR', result['status'], flush=True)


def allow_performance(manifest, decision):
    allow_diagnostics(manifest)
    if manifest['screen']['status'] != 'eligible' or decision['status'] != 'detector_pass':
        raise ValueError('performance requires adequate search AND passing detection')


def performance(directory):
    manifest = verified_manifest(directory)
    decision = diagnostic_result(directory, manifest)
    if json.loads((directory/'diagnostic-decision.json').read_text()) != decision:
        raise ValueError('stale diagnostic decision')
    allow_performance(manifest, decision)
    data = evidence(directory, 'performance.json')
    for arm in ARMS + ('constant',):
        for seed in SEEDS['performance']:
            data.measure(f'{arm}/{seed}', lambda arm=arm, seed=seed: performance_row(seed, arm, manifest))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('stage', choices=('prepare', 'diagnostics', 'performance', 'report'))
    parser.add_argument('--out-dir', type=Path, default=DIRECTORY)
    args = parser.parse_args()
    if args.stage == 'report':
        from report_v3_gain import publish_report
        publish_report(args.out_dir)
    else:
        warmup()
        {'prepare': prepare, 'diagnostics': diagnostics, 'performance': performance}[args.stage](args.out_dir)


if __name__ == '__main__':
    main()
