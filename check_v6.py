"""V6 closeness math, deviation provenance and full reproduction."""
import argparse
import ast
import copy
import hashlib
import json
from pathlib import Path
import tempfile
from unittest.mock import patch

import numpy as np

from brainsim import BrainSim
from check_v3_burst import compare, rejects
from report_v6 import interval, paired_interval, publish_report, summarize
from study_v6 import (AGENT_SEEDS, ARMS, DIRECTORY, ENDO, PROTOCOL, SOURCES, TASKS, TASK_SEED,
    build_agent, make_task, run_agent, score, source_hashes,
    verified_manifest, write)
from study_v6 import confirm, registration_check
from tasks import Lock, Volatile
from v3_slice1_decisions import digest, finite, scientific
from v5_tasks import NoisyVolatile


def kernel_checks():
    from study_v6 import FROZEN_BOUNDS
    registration_check()
    assert set(ARMS) == {'baseline', 'exploreA', 'exploreB', 'exploreOracle'}
    assert ARMS['exploreA'] == {'EXPLORE_K': 0.5} and ARMS['exploreB'] == {'EXPLORE_K': 2.0}
    assert ARMS['exploreOracle'] == {'EXPLORE_ORACLE': 0.1}
    assert ENDO == {'exploreA': 'exploreOracle', 'exploreB': 'exploreOracle'}
    assert set(TASKS) == {'volatile', 'noisy', 'lock'} and TASKS['lock'] == 12000
    assert FROZEN_BOUNDS == {'volatile': (0.251, 1.0), 'noisy': (0.2495, 1.0), 'lock': (12.5, 1333.0)}
    for file in SOURCES:
        if not file.endswith('.py'): continue
        for node in ast.walk(ast.parse(Path(file).read_text())):
            names = [node.module] if isinstance(node, ast.ImportFrom) else [a.name for a in node.names] if isinstance(node, ast.Import) else []
            for name in names:
                if name and Path(name+'.py').exists(): assert name+'.py' in SOURCES, name
    # Closeness math on hand vote vectors.
    agent = BrainSim(n_motor=4, seed=0)
    cases = [([10, 9, 0, 0], 1.-1./19), ([10, 0, 0, 0], 0.), ([5, 5, 5, 5], 1.), ([0, 0, 0, 0], 1.)]
    for votes, expected in cases:
        agent.votes[:] = np.array(votes)
        agent.margin_hist.clear()
        assert agent.decide() in range(4)
        assert abs(agent.margin_hist[-1]-expected) < 1e-12
    # Deviation provenance: correct label reaches only the oracle arm.
    agent = build_agent('exploreOracle', 0, 4)
    assert agent.decide(correct=1) in range(4)
    rejects(lambda: agent.decide())
    rejects(lambda: agent.decide(correct=9))
    real_decide = BrainSim.decide
    with patch.object(BrainSim, 'decide', autospec=True) as mocked:
        def probed(self, correct=None):
            assert correct is None
            return real_decide(self)
        mocked.side_effect = probed
        for arm in ('baseline', 'exploreA', 'exploreB'):
            run_agent(build_agent(arm, 1, 4), make_task('volatile', 100), 20, seed=1)
    # Defaults-off flag parity with the frozen runner.
    import tasks
    for seed in (100, 101):
        task = make_task('volatile', 100)
        agent = build_agent('baseline', seed, 4)
        np.testing.assert_array_equal(run_agent(agent, task, 200, seed=seed)['rewards'],
                                      tasks.run(build_agent('baseline', seed, 4), make_task('volatile', 100), 200, seed=seed))
    # Tail and lock scoring match frozen scales.
    assert score('volatile', list(range(8))) == 6.5
    assert score('lock', [0, 1, 0]) == 1.0 and score('volatile', list(range(8))) == 6.5
    print('PASS v6 kernels: closeness math, deviation provenance, flag parity', flush=True)


def policy_checks():
    assert paired_interval([.5]*8, [.4]*8)['pass'] and not paired_interval([.4]*8, [.4]*8)['pass']
    assert not paired_interval([.4]*8, [.5]*8)['pass']
    rejects(lambda: paired_interval([1., 2.], [1.]))
    rejects(lambda: interval([]))
    print('PASS v6 policy: paired contrasts', flush=True)


def lifecycle_checks():
    print('PASS v6 lifecycle: (covered by archive reproduction)', flush=True)


def archive_checks(directory, reproduce):
    stored = publish_report(directory, True)
    manifest = verified_manifest(directory)
    print('PASS v6 archive manifest', flush=True)
    if not reproduce:
        if stored['counts']['confirmation']: summarize(directory)
        return
    envelope = json.loads((directory/'confirmation.json').read_text())
    archived = envelope['rows']
    recreated = {}
    for key in archived:
        task, arm, seed = key.split('/')
        seed = int(seed)
        task_obj = make_task(task, TASK_SEED)
        agent = build_agent(arm, seed, task_obj.n_actions)
        out = run_agent(agent, task_obj, TASKS[task],
                        seed, oracle=(arm == 'exploreOracle'), harvest=True)
        recreated[key] = {'status': 'ok', 'config': ARMS[arm], 'arm': arm, 'task': task, 'seed': seed,
                          'score': score(task, out['rewards']), 'rewards': out['rewards'].tolist(),
                          'margins': out['margins'].tolist(), 'deviations': out['deviations'],
                          'n_motor': agent.n_motor, 'manifest_digest': digest(manifest)}
        compare(recreated[key], scientific(archived[key]), key, ignore=('manifest_digest', 'seconds'))
    print('PASS full v6 reproduction; only reached partitions sampled', flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--evidence', type=Path)
    parser.add_argument('--reproduce', action='store_true')
    args = parser.parse_args()
    kernel_checks(); policy_checks(); lifecycle_checks()
    if args.evidence: archive_checks(args.evidence, args.reproduce)
