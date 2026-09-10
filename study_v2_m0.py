"""Registered confirmation with immutable provenance (no tuning stage)."""
import argparse
import hashlib
import json
from pathlib import Path

import numpy as np

from study_io import Evidence
from study_v3_burst import SOURCES as BURST_SOURCES
from study_v3_slice1 import require_committed, write
from v2_m0 import CLASSES, SEEDS, TRIALS, run_arm
from v3_slice1_decisions import digest, finite

DIRECTORY = Path('results/v2-m0')
SOURCES = sorted(set(BURST_SOURCES + ['DESIGN-v2-m0-motor.md', 'v2_m0.py',
    'brainsim.py', 'tasks.py', 'study_v2_m0.py',
    'report_v2_m0.py', 'check_v2_m0.py']))
ARMS = ('pertick', 'aggregate', 'shipped')
PROTOCOL = {'id': 'v2-m0-motor-20260910-v1',
            'registration_commit': 'ee68bcdda1f376904074316584e2a78bc67cdf64',
            'registration_sha256': '8a744d5eaa5bafbcdd8535a291a0a6c8493123122e1d6e2808729ae7f61c3bba'}


def source_hashes():
    return {p: hashlib.sha256(Path(p).read_bytes()).hexdigest() for p in SOURCES}


def registration_check():
    if source_hashes()['DESIGN-v2-m0-motor.md'] != PROTOCOL['registration_sha256']:
        raise ValueError('registered protocol changed')


def measure(ncls, arm, seed, manifest=None):
    correct, winners = run_arm(arm, ncls, seed, TRIALS)
    row = {'status': 'ok', 'arm': arm, 'ncls': ncls, 'seed': seed,
           'accuracy': float(correct.mean()),
           'winner_rate': float((winners >= 0).mean()),
           'ticks': int(len(correct))}
    if manifest is not None:
        row['manifest_digest'] = digest(manifest)
    if not np.isfinite(row['accuracy']) or not 0. <= row['accuracy'] <= 1.:
        return {'status': 'nonfinite', 'reason': f'{arm}/{ncls}'}
    return row


def write_manifest(directory):
    manifest = {'protocol': PROTOCOL, 'sources': source_hashes(),
                'arms': list(ARMS), 'seeds': list(SEEDS), 'classes': list(CLASSES),
                'trials': TRIALS}
    manifest = json.loads(json.dumps(manifest))
    path = directory/'manifest.json'
    if path.exists() and json.loads(path.read_text()) != manifest:
        raise ValueError('frozen manifest changed')
    write(path, manifest)
    return manifest


def verified_manifest(directory):
    registration_check()
    for source in SOURCES:
        require_committed(Path(source))
    require_committed(directory/'manifest.json')
    manifest = json.loads((directory/'manifest.json').read_text())
    if manifest['protocol'] != PROTOCOL or manifest['sources'] != source_hashes():
        raise ValueError('manifest differs from registration')
    return manifest


def confirm(directory):
    manifest = verified_manifest(directory)
    evidence = Evidence(directory/'confirmation.json', SOURCES, PROTOCOL)
    for ncls in CLASSES:
        for arm in ARMS:
            for seed in SEEDS:
                key = f'{ncls}/{arm}/{seed}'
                evidence.measure(key, lambda c=ncls, a=arm, s=seed: measure(c, a, s, manifest))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('stage', choices=('confirm', 'report'))
    parser.add_argument('--directory', type=Path, default=DIRECTORY)
    args = parser.parse_args()
    if args.stage == 'report':
        from report_v2_m0 import publish_report
        publish_report(args.directory)
    else:
        {'confirm': confirm}[args.stage](args.directory)


if __name__ == '__main__':
    main()
