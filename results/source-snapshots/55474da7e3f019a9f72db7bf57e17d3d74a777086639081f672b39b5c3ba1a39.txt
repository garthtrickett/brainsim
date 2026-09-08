"""Step 11's forward-model premise: score predictions before each online update."""
import json
import numpy as np
import tasks
from fastsim import FastBrainSim
from transition_model import ObservedTask, TransitionObserver
from study_io import Evidence, paired_summary


def measure(seed):
    agent = FastBrainSim(seed=seed)
    observer = TransitionObserver(40, 2)
    task = ObservedTask(tasks.Lock(10, seed=seed), observer.observe)
    hist = tasks.run(agent, task, 12000, seed=seed)
    row = observer.summary()
    row.update({'external_reward': float(hist.sum()), 'observations': observer.count,
                'first_reward': int(np.flatnonzero(hist)[0]+1) if hist.any() else None})
    return row


if __name__ == '__main__':
    evidence = Evidence('results/v1-model.json',
                        ['brainsim.py', 'fastsim.py', 'tasks.py', 'transition_model.py', 'study_model.py'],
                        {'seeds': 8, 'decisions': 12000, 'tail': 2000,
                         'evaluation': 'prequential: predict before updating on each transition'})
    rows = [evidence.measure(str(s), lambda: measure(s)) for s in range(8)]
    print('ACTION MODEL VS STATE ONLY', json.dumps(paired_summary(
        [r['state_only_mse'] for r in rows], [r['next_mse'] for r in rows])), flush=True)
