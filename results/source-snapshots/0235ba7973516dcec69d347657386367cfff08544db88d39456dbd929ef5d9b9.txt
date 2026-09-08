"""Steps 11/12/13a/13c: opt-in arms, calibrated horizons, external scores only."""
import argparse
import json
import numpy as np
import tasks
from fastsim import FastBrainSim
from research_agents import CuriousAgent, ContextReplayAgent, DynaAgent
from transition_model import ObservedTask
from study_io import Evidence, paired_summary
from study_pools import legacy_task


CASES = {
    'legacy-additive-4x4': (legacy_task, 4000, 1000, 'run'),
    'lock-10': (lambda seed: tasks.Lock(10, seed=seed), 12000, 0, 'run'),
    'volatile-4': (lambda seed: tasks.Volatile(4, 300, seed=seed), 4000, 1000, 'run'),
    'xor-2': (lambda seed: tasks.Conjunctive(seed=seed), 4000, 1000, 'run'),
    'nway-8': (lambda seed: tasks.NWay(8, seed=seed), 4000, 1000, 'run'),
    'nway-4': (lambda seed: tasks.NWay(4, seed=seed), 4000, 1000, 'run'),
    'tmaze-within-30': (lambda seed: tasks.TMazeWithin(delay_ticks=30, seed=seed), 6000, 1500, 'within'),
    'tmaze-within-60': (lambda seed: tasks.TMazeWithin(delay_ticks=60, seed=seed), 6000, 1500, 'within'),
}
ARMS = {
    'curiosity': ['off', 'bonus-0.1', 'bonus-0.5'],
    'replay': ['off', 'context', 'shuffled'],
    'dyna': ['off', 'real', 'model'],
    'failure': ['off', 'fail-0.1', 'gain-0.9', 'fail-0.5', 'gain-0.5'],
}


def make_agent(study, arm, actions, seed):
    options = {'n_motor': actions, 'seed': seed}
    if study == 'curiosity':
        return CuriousAgent(**options, curiosity=0.0 if arm == 'off' else float(arm.split('-')[1]))
    if study == 'replay': return ContextReplayAgent(**options, query=arm)
    if study == 'dyna': return DynaAgent(**options, planning=arm)
    agent = FastBrainSim(**options)
    if arm.startswith('fail-'): agent.TRANSMISSION_FAILURE = float(arm.split('-')[1])
    if arm.startswith('gain-'): agent.TRANSMISSION_GAIN = float(arm.split('-')[1])
    return agent


def measure(study, name, arm, seed):
    mk, decisions, tail, runner = CASES[name]
    task = mk(seed)
    agent = make_agent(study, arm, task.n_actions, seed)
    if study == 'curiosity': task = ObservedTask(task, agent.observer.observe)
    hist = (tasks.run_within if runner == 'within' else tasks.run)(agent, task, decisions, seed=seed)
    assert np.isfinite(agent.W_out).all() and np.isfinite(agent.W_wm).all()
    for episode, total in agent.episodes:
        assert total == sum(item[2] for item in episode)
        assert all(item[2] in (0.0, 1.0) for item in episode)
    row = {'score': float(hist[-tail:].mean()) if tail else float(hist.sum()),
           'first_reward': int(np.flatnonzero(hist)[0]+1) if hist.any() else None,
           'early_rewards': float(hist[:4000].sum()), 'last_1000': float(hist[-1000:].mean()),
           'finite': True, 'external_episode_rewards': True}
    if study == 'curiosity':
        row['bonus_total'] = agent.bonus_total
        row['model'] = agent.observer.summary()
    if study == 'dyna':
        row['backups'] = agent.backups
        row['model_errors'] = np.mean(agent.model_errors[-2000:], axis=0).tolist()
        row['observed_state_action_pairs'] = len(agent.support)
    return row


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('study', choices=ARMS)
    parser.add_argument('--seeds', type=int, default=6)
    parser.add_argument('--seed-start', type=int, default=0)
    parser.add_argument('--tasks', nargs='+', choices=CASES)
    parser.add_argument('--arms', nargs='+')
    parser.add_argument('--out')
    args = parser.parse_args()
    names = args.tasks or (['lock-10', 'volatile-4', 'xor-2', 'nway-8'] if args.study == 'failure'
                           else ['lock-10'])
    arms = args.arms or ARMS[args.study]
    assert all(arm in ARMS[args.study] for arm in arms)
    evidence = Evidence(args.out or f'results/v1-{args.study}.json',
                        ['brainsim.py', 'fastsim.py', 'tasks.py', 'research_agents.py',
                         'transition_model.py', 'study_learning.py', 'study_io.py', 'study_pools.py'],
                        {'study': args.study, 'seeds': args.seeds, 'seed_start': args.seed_start,
                         'tasks': names, 'arms': arms, 'task_seed': 'paired to agent seed'})
    for name in names:
        scores = {arm: [] for arm in arms}
        for seed in range(args.seed_start, args.seed_start+args.seeds):
            mk, dec, tail, _ = CASES[name]
            def controls():
                f = tasks.random_policy(mk(seed), dec, seed=seed)
                c = tasks.oracle(mk(seed), dec, seed=seed)
                return {'floor': float(f[-tail:].mean()) if tail else float(f.sum()),
                        'ceiling': float(c[-tail:].mean()) if tail else float(c.sum())}
            evidence.measure(f'{name}/controls/{seed}', controls)
            for arm in arms:
                row = evidence.measure(f'{name}/{arm}/{seed}', lambda: measure(args.study, name, arm, seed))
                scores[arm].append(row['score'])
        if 'off' in scores:
            for arm in arms:
                if arm != 'off':
                    print('CONTRAST', name, arm, json.dumps(paired_summary(scores['off'], scores[arm])), flush=True)
        if args.study == 'failure':
            for p, gain in [('0.1', '0.9'), ('0.5', '0.5')]:
                if f'gain-{gain}' in scores and f'fail-{p}' in scores:
                    print('STOCHASTIC VS ATTENUATION', name, p, json.dumps(
                        paired_summary(scores[f'gain-{gain}'], scores[f'fail-{p}'])), flush=True)
        if args.study == 'dyna' and 'real' in scores and 'model' in scores:
            print('MODEL VS REAL', name, json.dumps(paired_summary(scores['real'], scores['model'])), flush=True)


if __name__ == '__main__': main()
