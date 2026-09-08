"""Steps 6/11/13b: does the registered held-out representation gap exist?"""
import copy
import json
import numpy as np
import tasks
from fastsim import FastBrainSim
from study_io import Evidence, paired_summary


def frozen_evaluation(agent, task, seed, decisions=1000):
    model = copy.deepcopy(agent)
    # Run the existing state/reset path, but suppress every weight writer.
    model.LR = model.VALUE_W_LR = model.VALUE_LR = model.EBAR_LR = 0.0
    model.HIPPO = model.ADAPTIVE = False
    model.SLEEP_EVERY = model.SCALE_EVERY = 10**12
    model.ETA_TH = 0.0
    model.noise_eff = model.NOISE
    fields = ('W_in', 'W_out', 'W_wm', 'w_v', 'ebar', 'ebar_wm', 'thresh')
    weights = {f: getattr(model, f).copy() for f in fields}
    hist = tasks.run(model, task, decisions, seed=seed)
    for field in fields:
        np.testing.assert_array_equal(weights[field], getattr(model, field),
                                      err_msg='evaluation changed ' + field)
    return float(hist.mean())


def measure(seed):
    task = tasks.Compositional(4, 4, seed=seed, held_out=4)
    assert len(task.test) == 4 and set(task.train).isdisjoint(task.test)
    assert {task.label[c] for c in task.test} <= {task.label[c] for c in task.train}
    model = FastBrainSim(n_motor=4, seed=seed)
    training = tasks.run(model, task, 4000, seed=seed)
    seen = frozen_evaluation(model, copy.deepcopy(task), seed+1000)
    task.mode = 'test'
    unseen = frozen_evaluation(model, copy.deepcopy(task), seed+2000)
    floor = tasks.random_policy(copy.deepcopy(task), 1000, seed=seed+2000).mean()
    ceiling = tasks.oracle(copy.deepcopy(task), 1000, seed=seed+2000).mean()
    return {'train_tail': float(training[-1000:].mean()), 'seen_frozen': seen,
            'unseen_frozen': unseen, 'test_floor': float(floor), 'test_ceiling': float(ceiling),
            'train_pairs': task.train, 'test_pairs': task.test, 'weights_unchanged': True}


if __name__ == '__main__':
    evidence = Evidence('results/v1-representation.json',
                        ['brainsim.py', 'fastsim.py', 'tasks.py', 'study_representation.py'],
                        {'seeds': 8, 'train': 4000, 'eval': 1000, 'held_out_pairs': 4,
                         'label': 'shape identity', 'eval_weights': 'frozen and asserted'})
    rows = [evidence.measure(str(seed), lambda: measure(seed)) for seed in range(8)]
    print('GENERALISATION VS FLOOR', json.dumps(paired_summary(
        [r['test_floor'] for r in rows], [r['unseen_frozen'] for r in rows])), flush=True)
    print('SEEN', np.mean([r['seen_frozen'] for r in rows]), flush=True)
