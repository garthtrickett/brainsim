"""Registered confirmation with immutable provenance (no tuning stage)."""
import argparse
import hashlib
import json
from pathlib import Path

import numpy as np

import reference
from study_io import Evidence
from study_v3_burst import SOURCES as BURST_SOURCES
from study_v3_slice1 import require_committed, write
from v3_slice1_decisions import digest, finite

DIRECTORY = Path('results/q5')
SOURCES = sorted(set(BURST_SOURCES + ['brainsim.py', 'tasks.py', 'fastsim.py',
    'reference.py', 'reference.json', 'baselines.py', 'DESIGN-q5-rank1.md',
    'q5_rank1.py', 'study_q5.py', 'report_q5.py', 'check_q5.py']))
ARMS = ('shipped', 'rank1')
SEEDS = tuple(range(8))
TASKS = {name: (mk, nact, dec, tail, runner)
         for (name, mk, nact, dec, tail, runner) in reference.SUITE}
PROTOCOL = {'id': 'q5-rank1-20260911-v2',
            'registration_commit': '67ae15bce7173cec7dacd774f8cae24a16ccff25',
            'registration_sha256': '19274936fd8a53552d61667d14b731611a2fdc19907d0d9f7b9794b8c5d7df64'}


def source_hashes():
    return {p: hashlib.sha256(Path(p).read_bytes()).hexdigest() for p in SOURCES}


def registration_check():
    if source_hashes()['DESIGN-q5-rank1.md'] != PROTOCOL['registration_sha256']:
        raise ValueError('registered protocol changed')


def measure(task, arm, seed, manifest=None):
    mk, nact, dec, tail, runner = TASKS[task]
    over = {} if arm == 'shipped' else {'RANK1_ELIG': True}
    score = reference.brainsim_run(mk, nact, dec, tail, seed, runner, **over)
    row = {'status': 'ok', 'task': task, 'arm': arm, 'seed': seed,
           'score': float(score)}
    if manifest is not None:
        row['manifest_digest'] = digest(manifest)
    if not np.isfinite(row['score']):
        return {'status': 'nonfinite', 'reason': f'{task}/{arm}/{seed}'}
    return row


def write_manifest(directory):
    manifest = {'protocol': PROTOCOL, 'sources': source_hashes(),
                'arms': list(ARMS), 'seeds': list(SEEDS),
                'tasks': {name: {'decisions': TASKS[name][2], 'tail': TASKS[name][3],
                                 'n_actions': TASKS[name][1], 'runner': TASKS[name][4]}
                          for name in TASKS}}
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
    reference.use_fast()
    evidence = Evidence(directory/'confirmation.json', SOURCES, PROTOCOL)
    for task in TASKS:
        for arm in ARMS:
            for seed in SEEDS:
                key = f'{task}/{arm}/{seed}'
                evidence.measure(key, lambda t=task, a=arm, s=seed: measure(t, a, s, manifest))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('stage', choices=('confirm', 'report'))
    parser.add_argument('--directory', type=Path, default=DIRECTORY)
    args = parser.parse_args()
    if args.stage == 'report':
        from report_q5 import publish_report
        publish_report(args.directory)
    else:
        {'confirm': confirm}[args.stage](args.directory)


if __name__ == '__main__':
    main()
