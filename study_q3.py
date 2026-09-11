"""Registered confirmation with immutable provenance (no tuning stage)."""
import argparse
import hashlib
import json
from pathlib import Path

import numpy as np

import tasks
from fastsim import FastBrainSim
from study_io import Evidence
from study_v3_burst import SOURCES as BURST_SOURCES
from study_v3_slice1 import require_committed, write
from v3_slice1_decisions import digest, finite

DIRECTORY = Path('results/q3')
SOURCES = sorted(set(BURST_SOURCES + ['brainsim.py', 'tasks.py', 'fastsim.py',
    'DESIGN-q3-pools.md', 'study_q3.py', 'report_q3.py', 'check_q3.py']))
CELLS = ([(80, 6, p, c) for p in (1, 2, 3, 6) for c in (4, 9, 16)] +
         [(160, 12, p, c) for p in (1, 4) for c in (9, 16)])
SEEDS = tuple(range(320, 328))
DECISIONS, TAIL = 4000, 1000
PROTOCOL = {'id': 'q3-pools-20260911-v1',
            'registration_commit': '0efb3d541921ef7716ec5f4727e120ac575194d5',
            'registration_sha256': 'b6fc2c8dc71f7543ad030345759267fe53da8ae54d8f0ef5108ad07cbf556c4e'}


def source_hashes():
    return {p: hashlib.sha256(Path(p).read_bytes()).hexdigest() for p in SOURCES}


def registration_check():
    if source_hashes()['DESIGN-q3-pools.md'] != PROTOCOL['registration_sha256']:
        raise ValueError('registered protocol changed')


def combos_n(combos):
    if combos == 4: return 2
    if combos == 9: return 3
    if combos == 16: return 4
    raise ValueError(f'combos must be 4, 9, or 16, got {combos}')


def measure(hidden, k, pools, combos, seed, manifest=None):
    n = combos_n(combos)
    agent = FastBrainSim(n_hidden=hidden, k=k, n_motor=4, seed=seed)
    agent.POOLS = pools
    hist = tasks.run(agent, tasks.Compositional(n, n, seed=0, held_out=0),
                     DECISIONS, seed=seed)
    score = float(np.asarray(hist)[-TAIL:].mean())
    row = {'status': 'ok', 'hidden': hidden, 'k': k, 'pools': pools,
           'combos': combos, 'seed': seed, 'score': score}
    if manifest is not None:
        row['manifest_digest'] = digest(manifest)
    if not np.isfinite(row['score']) or not 0. <= row['score'] <= 1.:
        return {'status': 'nonfinite', 'reason': f'{hidden}/{pools}/{combos}/{seed}'}
    return row


def write_manifest(directory):
    manifest = {'protocol': PROTOCOL, 'sources': source_hashes(),
                'cells': [list(c) for c in CELLS], 'seeds': list(SEEDS),
                'decisions': DECISIONS, 'tail': TAIL}
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
    for (hidden, k, pools, combos) in CELLS:
        for seed in SEEDS:
            key = f'{hidden}/{k}/{pools}/{combos}/{seed}'
            evidence.measure(key, lambda h=hidden, kk=k, p=pools, c=combos, s=seed:
                             measure(h, kk, p, c, s, manifest))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('stage', choices=('confirm', 'report'))
    parser.add_argument('--directory', type=Path, default=DIRECTORY)
    args = parser.parse_args()
    if args.stage == 'report':
        from report_q3 import publish_report
        publish_report(args.directory)
    else:
        {'confirm': confirm}[args.stage](args.directory)


if __name__ == '__main__':
    main()
