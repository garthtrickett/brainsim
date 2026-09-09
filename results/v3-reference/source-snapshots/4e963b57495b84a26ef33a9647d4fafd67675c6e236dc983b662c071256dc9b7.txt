"""Staged slice1 runner with committed manifests and enforced scientific prerequisites."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import time

import numpy as np

from study_io import Evidence
from v3_slice1_decisions import (KEYS, PROTOCOL, complete, detector_decision, digest,
                                  finite, performance_decision, tuning_screen)
from v3_slice1_learning import ARMS, GATED, GRIDS, run, warmup
from v3_slice1_streams import BURN, FIXTURES, SEEDS, diagnostic_metrics, fixture, learning_metrics, maxima

SOURCES = ['DESIGN-v3-slice1.md', 'v3_slice1_streams.py', 'v3_slice1_learning.py',
           'v3_slice1_decisions.py', 'study_v3_slice1.py', 'v3_gate.py', 'study_io.py']
DIRECTORY = Path('results/v3-slice1')


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix('.tmp')
    temporary.write_text(json.dumps(value, indent=2, allow_nan=False) + '\n')
    temporary.replace(path)


def validate_registration():
    blob = subprocess.check_output(['git', 'show',
                                    PROTOCOL['registration_commit'] + ':DESIGN-v3-slice1.md'])
    if blob != Path('DESIGN-v3-slice1.md').read_bytes():
        raise ValueError('registered protocol was modified')


def source_hashes():
    return {s: hashlib.sha256(Path(s).read_bytes()).hexdigest() for s in SOURCES}


def load(directory, stage):
    data = json.loads((directory/(stage + '.json')).read_text())
    if data['protocol'] != PROTOCOL or data['sources'] != source_hashes():
        raise ValueError('changed source/protocol in ' + stage)
    complete(data['rows'], stage)
    if stage in ('diagnostics', 'performance'):
        expected = digest(json.loads((directory/'manifest.json').read_text()))
        if any(row.get('manifest_digest') != expected for row in data['rows'].values()):
            raise ValueError('confirmation rows belong to a different manifest')
    return data['rows']


def simulation(seed, name, arm, config, constants=None, observer=False):
    data = fixture(seed, name)
    if arm == 'constant':
        constants = constants if name == 'core' else [float(np.mean(constants))]
    result = run(data.y, arm, config, constants, observer)
    return data, result


def tuning_row(seed, arm, config):
    start = time.perf_counter()
    data, result = simulation(seed, 'core', arm, config)
    if not all(np.isfinite(x).all() for x in result):
        return {'status': 'nonfinite', 'reason': 'non-finite optimizer trajectory'}
    with np.errstate(over='ignore', invalid='ignore'):
        metrics = learning_metrics(data, *result)
    if not finite(metrics):
        return {'status': 'nonfinite', 'reason': 'non-finite squared-error metric'}
    return {'status': 'ok', 'metrics': metrics, 'elapsed_seconds': time.perf_counter() - start}


def calibration_row(seed, arm, config):
    modes = {}
    for mode in ('fixed', 'closed'):
        data, result = simulation(seed, 'core', arm, config, observer=mode == 'fixed')
        if not all(np.isfinite(x).all() for x in result):
            return {'status': 'nonfinite', 'reason': f'non-finite {mode} calibration trajectory'}
        gates = result[1]
        modes[mode] = {'maxima': {c: maxima(gates[BURN:, i]).tolist()
                                  for i, c in enumerate(('quiet', 'noisy'))},
                       'gate_means': gates[BURN:].mean(axis=0).tolist()}
    return {'status': 'ok', 'modes': modes}


def make_manifest(tuning, calibration=None):
    screen = tuning_screen(tuning)
    manifest = {'protocol': PROTOCOL, 'sources': source_hashes(), 'seeds': SEEDS,
                'expected_counts': {s: len(k) for s, k in KEYS.items()},
                'screen': screen, 'tuning_digest': digest(tuning)}
    if screen['status'] == 'eligible':
        if calibration is None:
            raise ValueError('eligible tuning requires complete calibration')
        complete(calibration, 'calibration')
        if any(row['status'] != 'ok' for row in calibration.values()):
            # The protocol has no automatic calibration-failure rescue path.
            raise ValueError('calibration non-finite; diagnose before further work')
        thresholds = {}
        for arm in GATED:
            thresholds[arm] = {}
            for mode in ('fixed', 'closed'):
                blocks = [x for s in SEEDS['calibration'] for c in ('quiet', 'noisy')
                          for x in calibration[f'{arm}/{s}']['modes'][mode]['maxima'][c]]
                thresholds[arm][mode] = float(np.quantile(blocks, .99, method='higher'))
        manifest['thresholds'] = thresholds
        manifest['constants'] = np.mean([calibration[f'candidate/{s}']['modes']['closed']['gate_means']
                                         for s in SEEDS['calibration']], axis=0).tolist()
        manifest['calibration_digest'] = digest(calibration)
    return json.loads(json.dumps(manifest))


def require_committed(path):
    path = path.resolve()
    root = Path(subprocess.check_output(['git', 'rev-parse', '--show-toplevel'], text=True).strip())
    relative = path.relative_to(root)
    blob = subprocess.check_output(['git', 'show', f'HEAD:{relative.as_posix()}'], stderr=subprocess.DEVNULL)
    if blob != path.read_bytes():
        raise ValueError('manifest must be committed unchanged before confirmation')


def verified_manifest(directory):
    validate_registration()
    path = directory/'manifest.json'
    require_committed(path)
    manifest = json.loads(path.read_text())
    tuning = load(directory, 'tuning')
    calibration = load(directory, 'calibration') if manifest['screen']['status'] == 'eligible' else None
    if manifest != make_manifest(tuning, calibration):
        raise ValueError('manifest differs from sources, tuning or calibration')
    if manifest['screen']['status'] != 'eligible':
        raise ValueError('tuning prerequisite failed; confirmation forbidden')
    return manifest


def evidence(directory, stage):
    return Evidence(directory/(stage + '.json'), SOURCES, PROTOCOL)


def prepare(directory):
    validate_registration()
    if any((directory/(s + '.json')).exists() for s in ('diagnostics', 'performance')):
        raise ValueError('cannot reopen prepare after confirmation')
    tuning = evidence(directory, 'tuning')
    for arm in ARMS:
        for index, config in enumerate(GRIDS[arm]):
            for seed in SEEDS['tuning']:
                tuning.measure(f'{arm}/{index}/{seed}', lambda seed=seed, arm=arm, config=config:
                               tuning_row(seed, arm, config))
    screen = tuning_screen(tuning.data['rows'])
    calibration = None
    if screen['status'] == 'eligible':
        calibration = evidence(directory, 'calibration')
        for arm in GATED:
            for seed in SEEDS['calibration']:
                calibration.measure(f'{arm}/{seed}', lambda seed=seed, arm=arm:
                                    calibration_row(seed, arm, screen['selected'][arm]))
    elif (directory/'calibration.json').exists():
        raise ValueError('unexpected calibration after tuning stop')
    manifest = make_manifest(tuning.data['rows'], calibration.data['rows'] if calibration else None)
    path = directory/'manifest.json'
    if path.exists() and json.loads(path.read_text()) != manifest:
        raise ValueError('frozen manifest changed; use a new experiment')
    write(path, manifest)
    print('SCREEN', json.dumps(screen), flush=True)
    print('Manifest must be committed before confirmation.', flush=True)


def diagnostic_row(seed, arm, manifest):
    modes = {}
    config = manifest['screen']['selected'][arm]
    for mode in ('fixed', 'closed'):
        modes[mode] = {}
        for name in FIXTURES:
            data, result = simulation(seed, name, arm, config, observer=mode == 'fixed')
            if not all(np.isfinite(x).all() for x in result):
                return {'status': 'nonfinite', 'manifest_digest': digest(manifest),
                        'reason': f'non-finite {mode}/{name} trajectory'}
            modes[mode][name] = diagnostic_metrics(data, result[1], manifest['thresholds'][arm][mode])
    return {'status': 'ok', 'manifest_digest': digest(manifest), 'modes': modes}


def diagnostics(directory):
    manifest = verified_manifest(directory)
    if (directory/'performance.json').exists():
        raise ValueError('cannot reopen diagnostics after performance')
    data = evidence(directory, 'diagnostics')
    for arm in GATED:
        for seed in SEEDS['diagnostics']:
            data.measure(f'{arm}/{seed}', lambda seed=seed, arm=arm: diagnostic_row(seed, arm, manifest))
    decision = detector_decision(data.data['rows'])
    write(directory/'diagnostic-decision.json', {'manifest_digest': digest(manifest),
                                               'evidence_digest': digest(data.data['rows']), **decision})
    print('DETECTOR', decision['status'], flush=True)


def require_detection(directory, manifest):
    rows = load(directory, 'diagnostics')
    expected = {'manifest_digest': digest(manifest), 'evidence_digest': digest(rows), **detector_decision(rows)}
    if json.loads((directory/'diagnostic-decision.json').read_text()) != expected:
        raise ValueError('diagnostic decision differs from complete evidence')
    if expected['status'] != 'detector_pass':
        raise ValueError('detector prerequisite failed; performance forbidden')


def performance_row(seed, arm, manifest):
    start = time.perf_counter()
    fixtures = {}
    config = manifest['screen']['selected']['candidate' if arm == 'constant' else arm]
    for name in FIXTURES:
        data, result = simulation(seed, name, arm, config, manifest['constants'] if arm == 'constant' else None)
        if not all(np.isfinite(x).all() for x in result):
            return {'status': 'nonfinite', 'manifest_digest': digest(manifest),
                    'reason': f'non-finite {name} trajectory'}
        with np.errstate(over='ignore', invalid='ignore'):
            fixtures[name] = learning_metrics(data, *result)
    if not finite(fixtures):
        return {'status': 'nonfinite', 'manifest_digest': digest(manifest),
                'reason': 'non-finite squared-error metric'}
    return {'status': 'ok', 'manifest_digest': digest(manifest), 'fixtures': fixtures,
            'elapsed_seconds': time.perf_counter() - start}


def performance(directory):
    manifest = verified_manifest(directory)
    require_detection(directory, manifest)
    data = evidence(directory, 'performance')
    for arm in ARMS + ('constant',):
        for seed in SEEDS['performance']:
            data.measure(f'{arm}/{seed}', lambda seed=seed, arm=arm: performance_row(seed, arm, manifest))
    print('PERFORMANCE', performance_decision(data.data['rows'])['status'], flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('stage', choices=('prepare', 'diagnostics', 'performance', 'report'))
    parser.add_argument('--out-dir', type=Path, default=DIRECTORY)
    args = parser.parse_args()
    if args.stage == 'report':
        from report_v3_slice1 import publish_report
        publish_report(args.out_dir)
        return
    warmup()
    {'prepare': prepare, 'diagnostics': diagnostics, 'performance': performance}[args.stage](args.out_dir)


if __name__ == '__main__':
    main()
