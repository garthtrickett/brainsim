"""Corrected step 9: same six winners, explicit current and legacy task labels."""
import argparse
import json
import numpy as np
import tasks
from fastsim import FastBrainSim
from study_io import Evidence, paired_summary


def legacy_task(seed):
    task = tasks.Compositional(4, 4, seed=seed, held_out=0)
    task.label = {(i, j): (i+j) % 4 for i, j in task.train}
    return task


CASES = {
    'legacy-additive-4x4': legacy_task,
    'shape-4x4': lambda seed: tasks.Compositional(4, 4, seed=seed, held_out=0),
    'volatile-4': lambda seed: tasks.Volatile(4, 300, seed=seed),
    'xor-2': lambda seed: tasks.Conjunctive(seed=seed),
    'nway-8': lambda seed: tasks.NWay(8, seed=seed),
}


def measure(mk, seed, pools):
    task = mk(seed)
    a = FastBrainSim(n_motor=task.n_actions, seed=seed); a.POOLS = pools
    # A separate agent checks realised activity without altering the task run.
    probe = FastBrainSim(n_motor=task.n_actions, seed=seed); probe.POOLS = pools
    rng = np.random.default_rng(seed)
    obs = mk(seed).reset(rng)
    firing = []
    for _ in range(100):
        probe.step(obs); probe._flush(); firing.append(float(probe.fh.sum()))
    hist = tasks.run(a, task, 4000, seed=seed)
    return {'score': float(hist[-1000:].mean()), 'early': float(hist[:1000].mean()),
            'nominal_winners': a.k, 'observed_mean_winners': float(np.mean(firing)),
            'observed_max_winners': max(firing)}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--seeds', type=int, default=6)
    parser.add_argument('--out', default='results/v1-pools.json')
    args = parser.parse_args()
    evidence = Evidence(args.out, ['brainsim.py', 'fastsim.py', 'tasks.py', 'study_pools.py', 'study_io.py'],
                        {'seeds': args.seeds, 'pools': [1, 2, 3, 6], 'k': 6, 'hidden': 80,
                         'decisions': 4000, 'tail': 1000, 'task_seed': 'paired to agent seed'})
    for name, mk in CASES.items():
        scores = {p: [] for p in (1, 2, 3, 6)}
        for seed in range(args.seeds):
            def controls():
                floor = tasks.random_policy(mk(seed), 4000, seed=seed)[-1000:].mean()
                ceiling = tasks.oracle(mk(seed), 4000, seed=seed)[-1000:].mean()
                return {'floor': float(floor), 'ceiling': float(ceiling)}
            evidence.measure(f'{name}/controls/{seed}', controls)
            for p in scores:
                row = evidence.measure(f'{name}/P{p}/{seed}', lambda: measure(mk, seed, p))
                scores[p].append(row['score'])
        for p in (2, 3, 6):
            print('CONTRAST', name, p, json.dumps(paired_summary(scores[1], scores[p])), flush=True)


if __name__ == '__main__': main()
