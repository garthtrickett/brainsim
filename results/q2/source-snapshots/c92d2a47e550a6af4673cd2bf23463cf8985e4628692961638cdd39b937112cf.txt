"""Registered confirmation with immutable provenance (no tuning stage)."""
import argparse
import hashlib
import json
from pathlib import Path

import numpy as np

import reference
import tasks
from q2_rule import RULES, TAUS, FastRule
from study_io import Evidence
from study_v3_burst import SOURCES as BURST_SOURCES
from study_v3_slice1 import require_committed, write
from v3_slice1_decisions import digest, finite

DIRECTORY = Path('results/q2')
SOURCES = sorted(set(BURST_SOURCES + ['brainsim.py', 'tasks.py', 'fastsim.py',
    'reference.py', 'reference.json', 'baselines.py', 'DESIGN-q2-tau.md',
    'q2_rule.py', 'study_q2.py', 'report_q2.py', 'check_q2.py']))
CONTROL = ('full', 200)
SEEDS = tuple(range(8))
SCREEN_TASK = 'lock-10'
GUARD_TASKS = ('nway-8', 'volatile-4')
TASKS = {name: (mk, nact, dec, tail, runner)
         for (name, mk, nact, dec, tail, runner) in reference.SUITE}
PROTOCOL = {'id': 'q2-tau-20260911-v1',
            'registration_commit': '54c706ee2a1e9750c732d14bcdb6f2dea73deee9',
            'registration_sha256': '42c5f093dd0e2c687031e6108cac63e83371db56678a0677de0a3bc7897d1689'}


def source_hashes():
    return {p: hashlib.sha256(Path(p).read_bytes()).hexdigest() for p in SOURCES}


def registration_check():
    if source_hashes()['DESIGN-q2-tau.md'] != PROTOCOL['registration_sha256']:
        raise ValueError('registered protocol changed')


def measure(task, rule, tau, seed, manifest=None):
    mk, nact, dec, tail, runner = TASKS[task]
    # Agent class + ELIG_D ARE the treatment; runners, factories, scoring
    # are the reference instrument verbatim (brainsim_run body, explicit
    # class so the Rule restore path is the one under test).
    agent = FastRule(n_motor=nact, seed=seed)
    agent.MODE = rule
    agent.ELIG_D = TAUS[tau]
    hist = tasks.run_within(agent, mk(), dec, seed=seed) if runner == "within" \
        else tasks.run(agent, mk(), dec, seed=seed)
    score = reference.score(hist, tail)
    row = {'status': 'ok', 'task': task, 'rule': rule, 'tau': tau,
           'seed': seed, 'score': float(score)}
    if manifest is not None:
        row['manifest_digest'] = digest(manifest)
    if not np.isfinite(row['score']):
        return {'status': 'nonfinite', 'reason': f'{task}/{rule}/{tau}/{seed}'}
    return row


def write_manifest(directory):
    manifest = {'protocol': PROTOCOL, 'sources': source_hashes(),
                'rules': list(RULES), 'taus': sorted(TAUS),
                'control': list(CONTROL), 'seeds': list(SEEDS),
                'screen_task': SCREEN_TASK, 'guard_tasks': list(GUARD_TASKS),
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
    evidence = Evidence(directory/'screen.json', SOURCES, PROTOCOL)
    for rule in RULES:
        for tau in sorted(TAUS):
            for seed in SEEDS:
                key = f'{SCREEN_TASK}/{rule}/{tau}/{seed}'
                evidence.measure(key, lambda r=rule, t=tau, s=seed: measure(SCREEN_TASK, r, t, s, manifest))


def confirm_guard(directory, rule, tau):
    if (rule, tau) == CONTROL or rule not in RULES or tau not in TAUS:
        raise ValueError('guard needs an adopted non-control arm')
    manifest = verified_manifest(directory)
    evidence = Evidence(directory/'guard.json', SOURCES, PROTOCOL)
    for task in GUARD_TASKS:
        for seed in SEEDS:
            key = f'{task}/{rule}/{tau}/{seed}'
            evidence.measure(key, lambda t=task, r=rule, u=tau, s=seed: measure(t, r, u, s, manifest))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('stage', choices=('screen', 'guard', 'report'))
    parser.add_argument('--rule', default=None)
    parser.add_argument('--tau', type=int, default=None)
    parser.add_argument('--directory', type=Path, default=DIRECTORY)
    args = parser.parse_args()
    if args.stage == 'report':
        from report_q2 import publish_report
        publish_report(args.directory)
    elif args.stage == 'screen':
        confirm_screen(args.directory)
    else:
        if args.rule is None or args.tau is None:
            raise ValueError('guard needs --rule and --tau')
        confirm_guard(args.directory, args.rule, args.tau)


if __name__ == '__main__':
    main()
