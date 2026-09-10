"""Registered calibration and confirmation with immutable provenance."""
import argparse
import hashlib
import json
from pathlib import Path

import numpy as np

from study_io import Evidence
from study_v3_burst import SOURCES as BURST_SOURCES
from study_v3_slice1 import require_committed, write
from brainsim import BrainSim
from v3_slice1_decisions import digest
import tasks
from v5_tasks import NoisyVolatile

DIRECTORY = Path('results/v5')
SOURCES = sorted(set(BURST_SOURCES + ['DESIGN-v5-embodied.md', 'v5_tasks.py', 'brainsim.py',
    'tasks.py', 'study_v5.py', 'report_v5.py', 'check_v5.py']))
PROTOCOL = {'id': 'v5-embodied-20260910-v1',
            'registration_commit': '36616fcb8bbaf8bd38b899bf73ad9bf2473ca94f',
            'registration_sha256': '74d193556a945d0853ac31634f6f5abe29d6015df88a60dce66d396fcb4bfb8a'}
DECISIONS = 2100
TICKS = 30
LEVELS = (0.25, 0.5)
CALIBRATION_SEEDS = (100, 101, 102)
CONFIRMATION_SEEDS = tuple(range(110, 118))
CALIBRATION_TASK_SEED = 100
CONFIRMATION_TASK_SEED = 110
ARMS = {'baseline': {}, 'burstA': {'VBURST': (1.0, 2., 50)}, 'burstB': {'VBURST': (1.5, 4., 100)},
        'burst_oracle': {'VBURST': (1.0, 2., 50), 'VBURST_ORACLE': True},
        'dualV': {'DUALV': True}, 'dualV_oracle': {'DUALV': True, 'DUALV_ORACLE': True}}
ENDO = {'burstA': 'burst_oracle', 'burstB': 'burst_oracle', 'dualV': 'dualV_oracle'}


def source_hashes():
    return {p: hashlib.sha256(Path(p).read_bytes()).hexdigest() for p in SOURCES}


def registration_check():
    if source_hashes()['DESIGN-v5-embodied.md'] != PROTOCOL['registration_sha256']:
        raise ValueError('registered protocol changed')


def make_task(sigma, seed):
    return NoisyVolatile(4, 300, sigma=sigma, seed=seed)


def run_agent(agent, task, decisions, seed, harvest=False):
    """Mirror of tasks.run with switch injection and trajectory harvest."""
    rng = np.random.default_rng(seed)
    switches = set(task.switch_points(decisions))
    obs = task.reset(rng)
    hist, marks = [], []
    for t in range(decisions):
        for _ in range(TICKS):
            agent.step(obs)
        action = agent.decide()
        obs, reward, done = task.step(action)
        agent.reward(reward, action=action, done=done, switch=(t in switches))
        hist.append(reward)
        if done:
            obs = task.reset(rng)
    out = {'rewards': np.array(hist)}
    if harvest:
        marks = list(agent.burst_marks)
    out = {'rewards': np.array(hist)}
    if harvest:
        out.update(vol=np.array(agent.vol_hist), lr=np.array(agent.lr_hist),
                   noise=np.array(agent.noise_hist), marks=marks,
                   w_v_norm=float(np.linalg.norm(agent.w_v)),
                   w_vf_norm=float(np.linalg.norm(agent.w_vf)))
    return out


def build_agent(arm, seed):
    agent = BrainSim(n_motor=4, seed=seed)
    for key, value in ARMS[arm].items():
        setattr(agent, key, value)
    return agent


def tail_mean(rewards):
    return float(np.asarray(rewards)[-len(rewards)//4:].mean())


def manifest_digest(manifest):
    return digest(manifest)


def calibrate(directory):
    registration_check()
    for source in SOURCES:
        require_committed(Path(source))
    evidence = Evidence(directory/'calibration.json', SOURCES, PROTOCOL)
    rows = {}
    for sigma in LEVELS:
        floor = [float(tasks.random_policy(make_task(sigma, CALIBRATION_TASK_SEED), DECISIONS, seed=s).mean())
                 for s in CALIBRATION_SEEDS]
        ceiling = [float(tasks.oracle(make_task(sigma, CALIBRATION_TASK_SEED), DECISIONS, seed=s).mean())
                   for s in CALIBRATION_SEEDS]
        base = []
        for s in CALIBRATION_SEEDS:
            task = make_task(sigma, CALIBRATION_TASK_SEED)
            agent = build_agent('baseline', s)
            base.append(tail_mean(run_agent(agent, task, DECISIONS, seed=s)['rewards']))
        floor_mean, ceiling_mean, base_mean = float(np.mean(floor)), float(np.mean(ceiling)), float(np.mean(base))
        span = ceiling_mean-floor_mean
        position = (base_mean-floor_mean)/span if span > 1e-9 else 0.
        rows[str(sigma)] = {'floor': floor, 'ceiling': ceiling, 'baseline': base,
                            'position': position, 'usable': bool(.1 <= position <= .9)}
    manifest = {'protocol': PROTOCOL, 'sources': source_hashes(),
                'usable': sorted(float(s) for s, r in rows.items() if r['usable'])}
    if not manifest['usable']:
        manifest['status'] = 'no_usable_task'
    else:
        manifest['status'] = 'eligible'
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
    require_committed(directory/'calibration.json')
    manifest = json.loads((directory/'manifest.json').read_text())
    calibration = json.loads((directory/'calibration.json').read_text())
    if calibration['manifest'] != manifest or manifest['protocol'] != PROTOCOL:
        raise ValueError('manifest differs from calibration')
    if manifest['status'] != 'eligible':
        raise ValueError('calibration prerequisite failed; confirmation forbidden')
    return manifest


def confirm(directory):
    manifest = verified_manifest(directory)
    evidence = Evidence(directory/'confirmation.json', SOURCES, PROTOCOL)
    for sigma in manifest['usable']:
        for arm in ARMS:
            for seed in CONFIRMATION_SEEDS:
                key = f'{sigma}/{arm}/{seed}'
                def row(s=seed, a=arm, g=sigma):
                    task = make_task(g, CONFIRMATION_TASK_SEED)
                    agent = build_agent(a, s)
                    out = run_agent(agent, task, DECISIONS, seed=s, harvest=True)
                    return {'status': 'ok', 'config': json.loads(json.dumps(ARMS[a])), 'arm': a, 'sigma': g, 'seed': s,
                            'tail': tail_mean(out['rewards']), 'rewards': out['rewards'].tolist(),
                            'vol': out['vol'].tolist(), 'lr': out['lr'].tolist(), 'noise': out['noise'].tolist(),
                            'marks': [[int(t), k] for t, k in out['marks']],
                            'w_v_norm': out['w_v_norm'], 'w_vf_norm': out['w_vf_norm'],
                            'manifest_digest': manifest_digest(manifest)}
                evidence.measure(key, row)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('stage', choices=('calibrate', 'confirm', 'report'))
    parser.add_argument('--directory', type=Path, default=DIRECTORY)
    args = parser.parse_args()
    if args.stage == 'report':
        from report_v5 import publish_report
        publish_report(args.directory)
    else:
        {'calibrate': calibrate, 'confirm': confirm}[args.stage](args.directory)


if __name__ == '__main__':
    main()
