"""Registered confirmation with immutable provenance (no tuning stage)."""
import argparse
import hashlib
import json
from pathlib import Path

import numpy as np

from study_io import Evidence
from study_v3_burst import SOURCES as BURST_SOURCES
from study_v3_slice1 import require_committed, write
from v3_slice1_decisions import digest
import tasks
from v5_tasks import NoisyVolatile
from v6_agent import ExploreAgent

DIRECTORY = Path('results/v6')
SOURCES = sorted(set(BURST_SOURCES + ['DESIGN-v6-explore.md', 'v5_tasks.py', 'brainsim.py',
    'tasks.py', 'v6_agent.py', 'study_v6.py', 'report_v6.py', 'check_v6.py']))
PROTOCOL = {'id': 'v6-explore-20260910-v1',
            'registration_commit': 'c3901e62ed734b64fe73ea96b05d42097ce124fd',
            'registration_sha256': '330f4a2741a38a6c8bd59ff9a1242d7c652677a47db9c481eed4214dac252c9b'}
TASKS = {'volatile': 2100, 'noisy': 2100, 'lock': 12000}
ARMS = {'baseline': {}, 'exploreA': {'EXPLORE_K': 0.5}, 'exploreB': {'EXPLORE_K': 2.0},
        'exploreOracle': {'EXPLORE_ORACLE': 0.1}}
ENDO = {'exploreA': 'exploreOracle', 'exploreB': 'exploreOracle'}
FROZEN_BOUNDS = {'volatile': (0.251, 1.0), 'noisy': (0.2495, 1.0), 'lock': (12.5, 1333.0)}
AGENT_SEEDS = tuple(range(130, 138))
TASK_SEED = 130


def source_hashes():
    return {p: hashlib.sha256(Path(p).read_bytes()).hexdigest() for p in SOURCES}


def registration_check():
    if source_hashes()['DESIGN-v6-explore.md'] != PROTOCOL['registration_sha256']:
        raise ValueError('registered protocol changed')


def make_task(name, seed):
    if name == 'volatile':
        return tasks.Volatile(4, 300, seed=seed)
    if name == 'noisy':
        return NoisyVolatile(4, 300, sigma=0.5, seed=seed)
    if name == 'lock':
        return tasks.Lock(10, seed=seed)
    raise ValueError('unknown task')


def run_agent(agent, task, decisions, seed, oracle=False, harvest=False):
    """Mirror of tasks.run with correct-label injection and harvest."""
    rng = np.random.default_rng(seed)
    obs = task.reset(rng)
    hist = []
    for _ in range(decisions):
        for _ in range(30):
            agent.step(obs)
        action = agent.decide(correct=task.correct() if oracle else None)
        obs, reward, done = task.step(action)
        agent.reward(reward, action=action, done=done)
        hist.append(reward)
        if done:
            obs = task.reset(rng)
    out = {'rewards': np.array(hist)}
    if harvest:
        out.update(margins=np.array(agent.margin_hist),
                   deviations=[[int(a), bool(d)] for a, d in agent.dev_hist])
    return out


def score(task_name, rewards):
    rewards = np.asarray(rewards)
    if task_name == 'lock':
        return float(rewards.sum())
    return float(rewards[-len(rewards)//4:].mean())


def build_agent(arm, seed, n_motor):
    agent = ExploreAgent(n_motor=n_motor, seed=seed)
    for key, value in ARMS[arm].items():
        setattr(agent, key, value)
    return agent


CALIBRATION_AGENT_SEEDS = (120, 121, 122)
CALIBRATION_TASK_SEED = 120


def calibrate(directory):
    registration_check()
    for source in SOURCES:
        require_committed(Path(source))
    evidence = Evidence(directory/'calibration.json', SOURCES, PROTOCOL)
    rows = {}
    for name, decisions in TASKS.items():
        floor = [float(tasks.random_policy(make_task(name, CALIBRATION_TASK_SEED), decisions, seed=s).mean())
                 for s in CALIBRATION_AGENT_SEEDS]
        ceiling = [float(tasks.oracle(make_task(name, CALIBRATION_TASK_SEED), decisions, seed=s).mean())
                   for s in CALIBRATION_AGENT_SEEDS]
        base = []
        for s in CALIBRATION_AGENT_SEEDS:
            task = make_task(name, CALIBRATION_TASK_SEED)
            agent = build_agent('baseline', s, task.n_actions)
            base.append(score(name, run_agent(agent, task, decisions, seed=s)['rewards']))
        floor_mean, ceiling_mean, base_mean = float(np.mean(floor)), float(np.mean(ceiling)), float(np.mean(base))
        span = ceiling_mean-floor_mean
        position = (base_mean-floor_mean)/span if span > 1e-9 else 0.
        rows[name] = {'floor': floor, 'ceiling': ceiling, 'baseline': base,
                      'position': position, 'usable': bool(.1 <= position <= .9)}
    manifest = {'protocol': PROTOCOL, 'sources': source_hashes(),
                'usable': sorted(n for n, r in rows.items() if r['usable'])}
    manifest['status'] = 'eligible' if manifest['usable'] else 'no_usable_task'
    evidence.data['rows'] = rows
    evidence.data['manifest'] = manifest
    tmp = evidence.path.with_suffix('.tmp')
    tmp.write_text(json.dumps(evidence.data, indent=2)+'\n')
    tmp.replace(evidence.path)
    path = directory/'manifest.json'
    if path.exists() and json.loads(path.read_text()) != manifest:
        raise ValueError('frozen manifest changed')
    write(path, manifest)
    print('CALIBRATION', manifest['status'], manifest['usable'], flush=True)
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


def write_manifest(directory):
    manifest = {'protocol': PROTOCOL, 'sources': source_hashes(), 'tasks': TASKS,
                'arms': ARMS, 'agent_seeds': list(AGENT_SEEDS), 'task_seed': TASK_SEED,
                'frozen_bounds': FROZEN_BOUNDS, 'usable': ['volatile', 'noisy', 'lock'],
                'status': 'eligible'}
    manifest = json.loads(json.dumps(manifest))
    path = directory/'manifest.json'
    if path.exists() and json.loads(path.read_text()) != manifest:
        raise ValueError('frozen manifest changed')
    write(path, manifest)
    return manifest


def measure(task_name, arm, seed, decisions, manifest=None):
    task = make_task(task_name, TASK_SEED)
    agent = build_agent(arm, seed, task.n_actions)
    out = run_agent(agent, task, decisions, seed,
                    oracle=(arm == 'exploreOracle'), harvest=True)
    row = {'status': 'ok', 'config': ARMS[arm], 'arm': arm, 'task': task_name, 'seed': seed,
           'score': score(task_name, out['rewards']), 'rewards': out['rewards'].tolist(),
           'margins': out['margins'].tolist(), 'deviations': out['deviations'],
           'n_motor': agent.n_motor}
    if manifest is not None:
        row['manifest_digest'] = digest(manifest)
    if not all(np.isfinite(np.asarray(row[k])).all() for k in ('rewards', 'margins')):
        return {'status': 'nonfinite', 'reason': task_name+' trajectory'}
    return row


def confirm(directory):
    manifest = verified_manifest(directory)
    evidence = Evidence(directory/'confirmation.json', SOURCES, PROTOCOL)
    for task_name, decisions in TASKS.items():
        for arm in ARMS:
            for seed in AGENT_SEEDS:
                key = f'{task_name}/{arm}/{seed}'
                evidence.measure(key, lambda s=seed, a=arm, t=task_name, d=decisions:
                                 measure(t, a, s, d, manifest))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('stage', choices=('calibrate', 'confirm', 'report'))
    parser.add_argument('--directory', type=Path, default=DIRECTORY)
    args = parser.parse_args()
    if args.stage == 'report':
        from report_v6 import publish_report
        publish_report(args.directory)
    else:
        {'calibrate': calibrate, 'confirm': confirm}[args.stage](args.directory)


if __name__ == '__main__':
    main()
