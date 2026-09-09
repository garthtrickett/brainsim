"""Registered calibration, committed-manifest confirmation and conditional performance."""
import argparse
import hashlib
import json
from pathlib import Path

import numpy as np

from study_io import Evidence
from study_v3_slice1 import require_committed, write
from v3_persistent import CONFIGS, DETECTORS, FIXTURES, fixture, run, warmup
from v3_persistent_policy import (KEYS, PROTOCOL, SEEDS, complete, detector_decision,
                                   digest, finite)
from v3_slice1_streams import BURN, diagnostic_metrics, learning_metrics, maxima

DIRECTORY = Path('results/v3-persistent')
SOURCES = ['DESIGN-v3-persistent.md', 'DESIGN-v3-slice1.md', 'requirements.txt',
           'v3_persistent.py', 'v3_persistent_policy.py', 'study_v3_persistent.py',
           'report_v3_persistent.py', 'study_io.py', 'study_v3_slice1.py',
           'v3_slice1_streams.py', 'v3_slice1_learning.py', 'v3_slice1_decisions.py', 'v3_gate.py']


def source_hashes():
    return {p: hashlib.sha256(Path(p).read_bytes()).hexdigest() for p in SOURCES}


def registration_check():
    if source_hashes()['DESIGN-v3-persistent.md'] != PROTOCOL['registration_sha256']:
        raise ValueError('registered protocol changed')


def simulation(seed, name, arm, mode='closed', constants=None):
    data = fixture(seed, name)
    if arm == 'constant' and name != 'core':
        constants = np.full(len(data.coordinates), np.mean(constants))
    result = run(data.y, arm, observer=mode == 'fixed', constants=constants)
    return data, result


def calibration_row(seed, arm):
    modes = {}
    for mode in ('fixed', 'closed'):
        data, result = simulation(seed, 'core', arm, mode)
        if not all(np.isfinite(x).all() for x in result):
            return {'status': 'nonfinite', 'reason': mode + ' trajectory'}
        gates = result[1]
        modes[mode] = {'maxima': {c: maxima(gates[BURN:, j]).tolist()
                                 for j, c in enumerate(('quiet', 'noisy'))},
                       'gate_means': gates[BURN:].mean(axis=0).tolist()}
    return {'status': 'ok', 'modes': modes}


def diagnostic_row(seed, arm, manifest):
    modes = {}
    identity = digest(manifest)
    for mode in ('fixed', 'closed'):
        modes[mode] = {}
        for name in FIXTURES:
            data, result = simulation(seed, name, arm, mode)
            if not all(np.isfinite(x).all() for x in result):
                return {'status': 'nonfinite', 'manifest_digest': identity, 'reason': mode + '/' + name}
            modes[mode][name] = diagnostic_metrics(data, result[1], manifest['thresholds'][arm][mode])
    return {'status': 'ok', 'manifest_digest': identity, 'modes': modes}


def performance_row(seed, arm, manifest):
    fixtures = {}
    identity = digest(manifest)
    for name in FIXTURES:
        data, result = simulation(seed, name, arm, constants=manifest['constants'] if arm == 'constant' else None)
        if not all(np.isfinite(x).all() for x in result):
            return {'status': 'nonfinite', 'manifest_digest': identity, 'reason': name + ' trajectory'}
        with np.errstate(over='ignore', invalid='ignore'):
            metrics = learning_metrics(data, *result)
        if not finite(metrics):
            return {'status': 'nonfinite', 'manifest_digest': identity, 'reason': name + ' metrics'}
        fixtures[name] = metrics
    return {'status': 'ok', 'manifest_digest': identity, 'fixtures': fixtures}


def read_stage(directory, stage):
    envelope = json.loads((directory/(stage + '.json')).read_text())
    if envelope['protocol'] != PROTOCOL or envelope['sources'] != source_hashes():
        raise ValueError('changed source/protocol')
    rows = envelope['rows']
    complete(rows, stage)
    if stage != 'calibration':
        identity = digest(json.loads((directory/'manifest.json').read_text()))
        if any(r.get('manifest_digest') != identity for r in rows.values()):
            raise ValueError('confirmation belongs to another manifest')
    return rows


def make_manifest(rows):
    complete(rows, 'calibration')
    manifest = {'protocol': PROTOCOL, 'sources': source_hashes(), 'seeds': SEEDS, 'configs': CONFIGS,
                'calibration_digest': digest(rows), 'expected_counts': {s: len(k) for s, k in KEYS.items()},
                'status': 'eligible' if all(r['status'] == 'ok' for r in rows.values()) else 'calibration_inconclusive'}
    if manifest['status'] == 'eligible':
        for row in rows.values():
            for mode in ('fixed', 'closed'):
                data = row['modes'][mode]
                if len(data['gate_means']) != 4 or any(len(data['maxima'][c]) != 50 for c in ('quiet', 'noisy')):
                    raise ValueError('wrong calibration coordinate/block count')
        manifest['thresholds'] = {a: {m: float(np.quantile([
            v for s in SEEDS['calibration'] for c in ('quiet', 'noisy')
            for v in rows[f'{a}/{s}']['modes'][m]['maxima'][c]], .99, method='higher'))
            for m in ('fixed', 'closed')} for a in DETECTORS}
        manifest['constants'] = np.mean([rows[f'candidate/{s}']['modes']['closed']['gate_means']
                                         for s in SEEDS['calibration']], axis=0).tolist()
    return json.loads(json.dumps(manifest))


def verified_manifest(directory):
    registration_check()
    require_committed(directory/'manifest.json')
    for source in SOURCES:
        require_committed(Path(source))
    manifest = json.loads((directory/'manifest.json').read_text())
    if manifest != make_manifest(read_stage(directory, 'calibration')):
        raise ValueError('manifest changed from calibration evidence')
    if manifest['status'] != 'eligible':
        raise ValueError('calibration prerequisite failed')
    return manifest


def prepare(directory):
    registration_check()
    for source in SOURCES:
        require_committed(Path(source))
    if any((directory/(s + '.json')).exists() for s in ('diagnostics', 'performance')):
        raise ValueError('cannot reopen calibration after confirmation')
    evidence = Evidence(directory/'calibration.json', SOURCES, PROTOCOL)
    for arm in DETECTORS:
        for seed in SEEDS['calibration']:
            evidence.measure(f'{arm}/{seed}', lambda arm=arm, seed=seed: calibration_row(seed, arm))
    manifest = make_manifest(read_stage(directory, 'calibration'))
    path = directory/'manifest.json'
    if path.exists() and json.loads(path.read_text()) != manifest:
        raise ValueError('frozen manifest changed')
    write(path, manifest)
    print('CALIBRATION', manifest['status'], 'Commit manifest before diagnostics.', flush=True)


def diagnostic_result(directory, manifest):
    rows = read_stage(directory, 'diagnostics')
    return {'manifest_digest': digest(manifest), 'evidence_digest': digest(rows),
            **detector_decision(rows)}


def diagnostics(directory):
    manifest = verified_manifest(directory)
    if (directory/'performance.json').exists():
        raise ValueError('cannot reopen diagnostics after performance')
    evidence = Evidence(directory/'diagnostics.json', SOURCES, PROTOCOL)
    for arm in DETECTORS:
        for seed in SEEDS['diagnostics']:
            evidence.measure(f'{arm}/{seed}', lambda arm=arm, seed=seed: diagnostic_row(seed, arm, manifest))
    decision = diagnostic_result(directory, manifest)
    write(directory/'diagnostic-decision.json', decision)
    print('DETECTOR', decision['status'], flush=True)


def require_detection(directory, manifest):
    decision = diagnostic_result(directory, manifest)
    if json.loads((directory/'diagnostic-decision.json').read_text()) != decision:
        raise ValueError('stale diagnostic decision')
    if decision['status'] != 'detector_pass':
        raise ValueError('detector prerequisite failed; performance forbidden')


def performance(directory):
    manifest = verified_manifest(directory)
    require_detection(directory, manifest)
    evidence = Evidence(directory/'performance.json', SOURCES, PROTOCOL)
    for arm in CONFIGS:
        for seed in SEEDS['performance']:
            evidence.measure(f'{arm}/{seed}', lambda arm=arm, seed=seed: performance_row(seed, arm, manifest))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('stage', choices=('prepare', 'diagnostics', 'performance', 'report'))
    parser.add_argument('--out-dir', type=Path, default=DIRECTORY)
    args = parser.parse_args()
    if args.stage == 'report':
        from report_v3_persistent import publish_report
        publish_report(args.out_dir)
    else:
        warmup()
        {'prepare': prepare, 'diagnostics': diagnostics, 'performance': performance}[args.stage](args.out_dir)


if __name__ == '__main__':
    main()
