"""Registered confirmation with immutable provenance (no tuning stage)."""
import argparse
import hashlib
import json
from pathlib import Path

import numpy as np

import reference
import tasks
from fastsim import FastBrainSim
from q5_rank1 import FastRank1
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
            'registration_commit': '7d5ce72a70880306b11d4f2c205e22d02db9f122',
            'registration_sha256': '8738791d19168fa3215be357e049b65eb726d9f849dfa48501c6d8347ac602b3'}


def source_hashes():
    return {p: hashlib.sha256(Path(p).read_bytes()).hexdigest() for p in SOURCES}


def registration_check():
    if source_hashes()['DESIGN-q5-rank1.md'] != PROTOCOL['registration_sha256']:
        raise ValueError('registered protocol changed')


def measure(task, arm, seed, manifest=None):
    mk, nact, dec, tail, runner = TASKS[task]
    # Agent class IS the treatment: the rank-1 algebra lives in the subclass
    # fork (frozen-source constraint, see registration). Runners, task
    # factories, and scoring are the reference instrument verbatim.
    cls = FastRank1 if arm == 'rank1' else FastBrainSim
    agent = cls(n_motor=nact, seed=seed)
    if arm == 'rank1':
        agent.RANK1_ELIG = True
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
