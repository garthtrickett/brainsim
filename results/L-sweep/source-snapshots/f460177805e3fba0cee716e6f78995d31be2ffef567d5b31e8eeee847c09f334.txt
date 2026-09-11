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

DIRECTORY = Path('results/L-sweep')
SOURCES = sorted(set(BURST_SOURCES + ['brainsim.py', 'tasks.py', 'fastsim.py',
    'reference.py', 'reference.json', 'baselines.py', 'DESIGN-L-sweep.md',
    'study_Lsweep.py', 'report_Lsweep.py', 'check_Lsweep.py']))
WINDOWS = (5, 10, 20, 40, 80)
CONTROL = 20
SEEDS = tuple(range(8))
SCREEN_TASK = 'lock-10'
COLLATERAL_TASKS = ('nway-4', 'nway-8', 'xor-2', 'volatile-4',
                    'tmaze-within-30', 'tmaze-within-60')
TASKS = {name: (mk, nact, dec, tail, runner)
         for (name, mk, nact, dec, tail, runner) in reference.SUITE}
PROTOCOL = {'id': 'L-sweep-20260911-v1',
            'registration_commit': '4b81dce0f75408b0ac6ac9f1728204739fdbd8df',
            'registration_sha256': '744eac78657582e14d0af7275112fcb8d4403a9bc87fed54a600d0eb58c2f580'}


def source_hashes():
    return {p: hashlib.sha256(Path(p).read_bytes()).hexdigest() for p in SOURCES}


def registration_check():
    if source_hashes()['DESIGN-L-sweep.md'] != PROTOCOL['registration_sha256']:
        raise ValueError('registered protocol changed')


def measure(task, window, seed, manifest=None):
    mk, nact, dec, tail, runner = TASKS[task]
    score = reference.brainsim_run(mk, nact, dec, tail, seed, runner,
                                   HIPPO_WINDOW=window)
    row = {'status': 'ok', 'task': task, 'window': window, 'seed': seed,
           'score': float(score)}
    if manifest is not None:
        row['manifest_digest'] = digest(manifest)
    if not np.isfinite(row['score']):
        return {'status': 'nonfinite', 'reason': f'{task}/{window}/{seed}'}
    return row


def write_manifest(directory):
    manifest = {'protocol': PROTOCOL, 'sources': source_hashes(),
                'windows': list(WINDOWS), 'control': CONTROL,
                'seeds': list(SEEDS), 'screen_task': SCREEN_TASK,
                'collateral_tasks': list(COLLATERAL_TASKS),
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


def confirm_screen(directory):
    manifest = verified_manifest(directory)
    reference.use_fast()
    evidence = Evidence(directory/'screen.json', SOURCES, PROTOCOL)
    for window in WINDOWS:
        for seed in SEEDS:
            key = f'{SCREEN_TASK}/{window}/{seed}'
            evidence.measure(key, lambda w=window, s=seed: measure(SCREEN_TASK, w, s, manifest))


def confirm_collateral(directory, winner):
    if winner not in WINDOWS or winner == CONTROL:
        raise ValueError('collateral needs a non-control winner window')
    manifest = verified_manifest(directory)
    reference.use_fast()
    evidence = Evidence(directory/'collateral.json', SOURCES, PROTOCOL)
    for task in COLLATERAL_TASKS:
        for seed in SEEDS:
            key = f'{task}/{winner}/{seed}'
            evidence.measure(key, lambda t=task, w=winner, s=seed: measure(t, w, s, manifest))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('stage', choices=('screen', 'collateral', 'report'))
    parser.add_argument('--winner', type=int, default=None)
    parser.add_argument('--directory', type=Path, default=DIRECTORY)
    args = parser.parse_args()
    if args.stage == 'report':
        from report_Lsweep import publish_report
        publish_report(args.directory)
    elif args.stage == 'screen':
        confirm_screen(args.directory)
    else:
        if args.winner is None: raise ValueError('collateral needs --winner')
        confirm_collateral(args.directory, args.winner)


if __name__ == '__main__':
    main()
