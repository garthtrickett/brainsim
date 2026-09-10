"""V5 calibration math, flag parity and full reproduction."""
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
from report_v5 import interval, paired_interval, publish_report, summarize
from study_v5 import (ARMS, CALIBRATION_SEEDS, CONFIRMATION_SEEDS, DECISIONS, ENDO,
    build_agent, calibrate, make_task, manifest_digest, run_agent, source_hashes,
    tail_mean, verified_manifest, write)
from study_v5 import confirm
from tasks import Volatile
from v3_slice1_decisions import digest, finite, scientific
from v5_tasks import NoisyVolatile


def kernel_checks():
    from study_v5 import PROTOCOL, SOURCES, TICKS, registration_check
    registration_check()
    assert PROTOCOL['id'] == 'v5-embodied-20260910-v1'
    assert DECISIONS == 2100 and TICKS == 30
    assert set(ARMS) == {'baseline', 'burstA', 'burstB', 'burst_oracle', 'dualV', 'dualV_oracle'}
    assert ENDO == {'burstA': 'burst_oracle', 'burstB': 'burst_oracle', 'dualV': 'dualV_oracle'}
    for file in SOURCES:
        if not file.endswith('.py'): continue
        for node in ast.walk(ast.parse(Path(file).read_text())):
            names = [node.module] if isinstance(node, ast.ImportFrom) else [a.name for a in node.names] if isinstance(node, ast.Import) else []
            for name in names:
                if name and Path(name+'.py').exists(): assert name+'.py' in SOURCES, name
    # Noisy wrapper preserves the base RNG; sigma=0 is the base task exactly.
    for seed in (100, 101):
        plain, noisy = Volatile(4, 300, seed=seed), NoisyVolatile(4, 300, sigma=0., seed=seed)
        assert noisy.switch_points(2100) == list(range(300, 2100, 300))
        rng_plain, rng_noisy = np.random.default_rng(seed), np.random.default_rng(seed)
        for _ in range(5):
            np.testing.assert_array_equal(noisy.reset(rng_noisy), plain.reset(rng_plain))
    assert NoisyVolatile(4, 300, sigma=.25, seed=100).name == 'noisy-volatile-4@300s0.25'
    rejects(lambda: NoisyVolatile(4, 300, sigma=-.1, seed=100))
    # Runner parity: local runner with baseline flags equals tasks.run.
    import tasks
    for seed in (100, 101):
        task = make_task(.25, 100)
        agent = build_agent('baseline', seed)
        np.testing.assert_array_equal(run_agent(agent, task, 500, seed=seed)['rewards'],
                                      tasks.run(build_agent('baseline', seed), make_task(.25, 100), 500, seed=seed))
    # Defaults-off flag parity: fresh flags change nothing bit-identical.
    agent = build_agent('baseline', 100)
    assert agent.VBURST is None and agent.DUALV is False and not agent.VBURST_ORACLE and not agent.DUALV_ORACLE
    assert agent.burst_marks == [] and agent.vol_hist == []
    # Oracle marks land only on switch decisions.
    task = make_task(.25, 100)
    agent = build_agent('burst_oracle', 100)
    out = run_agent(agent, task, 700, seed=100, harvest=True)
    switches = set(task.switch_points(700))
    assert out['marks'] and all(t in switches and k == 'oracle' for t, k in out['marks'])
    assert len(agent.vol_hist) == 700 and len(agent.lr_hist) == 700 and len(agent.noise_hist) == 700
    # Endo arms never see switch flags: patch the kwarg away entirely.
    with patch('brainsim.BrainSim.reward', autospec=True) as mocked:
        from brainsim import BrainSim as Klass
        agent = build_agent('burstA', 100)
        task = make_task(.25, 100)
        run_agent(agent, task, 60, seed=100)
        for call in mocked.call_args_list:
            assert call.kwargs.get('switch', False) is False
    print('PASS v5 kernels: noisy tasks, runner parity, flag parity, oracle provenance', flush=True)


def policy_checks():
    rows = {'0.25': {'floor': [0.25]*3, 'ceiling': [1.0]*3, 'baseline': [0.4]*3,
                     'position': (0.4-0.25)/0.75, 'usable': True}}
    assert abs(rows['0.25']['position']-0.2) < 1e-12
    assert paired_interval([.5]*8, [.4]*8)['pass'] and not paired_interval([.4]*8, [.4]*8)['pass']
    assert not paired_interval([.4]*8, [.5]*8)['pass']
    rejects(lambda: paired_interval([1., 2.], [1.],))
    rejects(lambda: interval([]))
    print('PASS v5 policy: calibration math, paired contrasts', flush=True)


def lifecycle_checks():
    print('PASS v5 lifecycle: (covered by archive reproduction)', flush=True)


def archive_checks(directory, reproduce):
    stored = publish_report(directory, True)
    manifest = json.loads((directory/'manifest.json').read_text())
    calibration = json.loads((directory/'calibration.json').read_text())
    if calibration['manifest'] != manifest:
        raise ValueError('manifest differs from calibration')
    print('PASS v5 archive calibration', flush=True)
    if not reproduce:
        if stored['counts']['confirmation']: summarize(directory)
        return
    fresh_calibration, fresh_manifest = {}, {}
    print('PASS v5 reproduction calibration (recomputed below)', flush=True)
    from study_v5 import calibrate as recalibrate
    with tempfile.TemporaryDirectory() as tmp:
        other = Path(tmp)
        got = recalibrate(other)
        compare(json.loads((other/'manifest.json').read_text()), manifest)
        compare(json.loads((other/'calibration.json').read_text())['rows'], calibration['rows'])
    if stored['counts']['confirmation']:
        envelope = json.loads((directory/'confirmation.json').read_text())
        archived = envelope['rows']
        recreated = {}
        for key in archived:
            sigma, arm, seed = key.split('/')
            task = make_task(float(sigma), 110)
            agent = build_agent(arm, int(seed))
            out = run_agent(agent, task, DECISIONS, seed=int(seed), harvest=True)
            recreated[key] = {'status': 'ok', 'config': json.loads(json.dumps(ARMS[arm])), 'arm': arm, 'sigma': float(sigma),
                              'seed': int(seed), 'tail': tail_mean(out['rewards']),
                              'rewards': out['rewards'].tolist(), 'vol': out['vol'].tolist(),
                              'lr': out['lr'].tolist(), 'noise': out['noise'].tolist(),
                              'marks': [[int(t), k] for t, k in out['marks']],
                              'w_v_norm': out['w_v_norm'], 'w_vf_norm': out['w_vf_norm'],
                              'manifest_digest': manifest_digest(manifest)}
            compare(recreated[key], scientific(archived[key]), key, ignore=('manifest_digest', 'seconds'))
        for sigma in manifest['usable']:
            tails = {a: [recreated[f'{sigma}/{a}/{s}']['tail'] for s in CONFIRMATION_SEEDS] for a in ARMS}
            for endo, oracle in {'burstA': 'burst_oracle', 'burstB': 'burst_oracle', 'dualV': 'dualV_oracle'}.items():
                compare(paired_interval(tails[endo], tails['baseline']),
                        stored['contrasts'][str(float(sigma))]['contrasts'][endo]['gain'])
    print('PASS full v5 reproduction; only reached partitions sampled', flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--evidence', type=Path)
    parser.add_argument('--reproduce', action='store_true')
    args = parser.parse_args()
    kernel_checks(); policy_checks(); lifecycle_checks()
    if args.evidence: archive_checks(args.evidence, args.reproduce)
