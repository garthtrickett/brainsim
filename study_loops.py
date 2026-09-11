"""Registered confirmation with immutable provenance (no tuning stage)."""
import argparse
import hashlib
import json
from pathlib import Path

import numpy as np

import reference
import tasks
from loops_rule import FastLoops
from study_io import Evidence
from study_v3_burst import SOURCES as BURST_SOURCES
from study_v3_slice1 import require_committed, write
from v3_slice1_decisions import digest, finite

DIRECTORY = Path('results/loops')
SOURCES = sorted(set(BURST_SOURCES + ['brainsim.py', 'tasks.py', 'fastsim.py',
    'reference.py', 'reference.json', 'baselines.py', 'DESIGN-loops-probe.md',
    'loops_rule.py', 'study_loops.py', 'report_loops.py', 'check_loops.py']))
ARMS = ('loops-LR', 'loops-full')
LOOPTASKS = ('volatile-4', 'lock-10', 'nway-8')
SEEDS = tuple(range(8))
TASKS = {name: (mk, nact, dec, tail, runner)
         for (name, mk, nact, dec, tail, runner) in reference.SUITE}
PROTOCOL = {'id': 'loops-20260911-v1',
            'registration_commit': '04a1ceac93d67f98deb6e991d9ffad9e86f9d71f',
            'registration_sha256': '38b08dbc7728ae4d3021aed3a3ce8c1fba534683117c29dc90274c6065d154a0'}


def source_hashes():
    return {p: hashlib.sha256(Path(p).read_bytes()).hexdigest() for p in SOURCES}


def registration_check():
    if source_hashes()['DESIGN-loops-probe.md'] != PROTOCOL['registration_sha256']:
        raise ValueError('registered protocol changed')


def measure(task, arm, seed, manifest=None):
    mk, nact, dec, tail, runner = TASKS[task]
    # Agent MODE IS the treatment; runners, factories, scoring are the
    # reference instrument verbatim.
    agent = FastLoops(n_motor=nact, seed=seed)
    agent.MODE = arm
    hist = tasks.run_within(agent, mk(), dec, seed=seed) if runner == "within" \
        else tasks.run(agent, mk(), dec, seed=seed)
    score = reference.score(hist, tail)
    row = {'status': 'ok', 'task': task, 'arm': arm, 'seed': seed,
           'score': float(score)}
    if manifest is not None:
        row['manifest_digest'] = digest(manifest)
    if not np.isfinite(row['score']):
        return {'status': 'nonfinite', 'reason': f'{task}/{arm}/{seed}'}
    return row


def write_manifest(directory):
    manifest = {'protocol': PROTOCOL, 'sources': source_hashes(),
                'arms': list(ARMS), 'tasks': list(LOOPTASKS),
                'seeds': list(SEEDS),
                'spec': {name: {'decisions': TASKS[name][2], 'tail': TASKS[name][3],
                                'n_actions': TASKS[name][1], 'runner': TASKS[name][4]}
                         for name in LOOPTASKS}}
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
    for task in LOOPTASKS:
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
        from report_loops import publish_report
        publish_report(args.directory)
    else:
        {'confirm': confirm}[args.stage](args.directory)


if __name__ == '__main__':
    main()
