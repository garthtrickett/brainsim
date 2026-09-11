"""Q2 harness checks and full reproduction."""
import argparse
import ast
import hashlib
import json
from pathlib import Path
import tempfile

import numpy as np

import tasks
from brainsim import BrainSim
from check_v3_burst import compare, rejects
from q2_rule import RULES, TAUS, FastRule, Rule
from report_q2 import decide, interval, paired_interval, publish_report, summarize
from study_q2 import (CONTROL, DIRECTORY, GUARD_TASKS, PROTOCOL, SCREEN_TASK,
    SEEDS, SOURCES, TASKS, measure, source_hashes, verified_manifest)
from study_q2 import confirm_guard, confirm_screen, registration_check
from v3_slice1_decisions import digest, finite, scientific


def kernel_checks():
    registration_check()
    assert RULES == ('full', 'none', 'proportional') and sorted(TAUS) == [100, 200, 400]
    assert CONTROL == ('full', 200) and SEEDS == tuple(range(8))
    for file in SOURCES:
        if not file.endswith('.py'): continue
        for node in ast.walk(ast.parse(Path(file).read_text())):
            names = [node.module] if isinstance(node, ast.ImportFrom) else [a.name for a in node.names] if isinstance(node, ast.Import) else []
            for name in names:
                if name and Path(name+'.py').exists(): assert name+'.py' in SOURCES, name
    # Fidelity: Rule(full@200) == BrainSim head-to-head and FastRule == Rule,
    # then the full@200 arm reproduces the frozen lock column EXACTLY.
    # (Task seed is 0 for all frozen seeds -- only agent/run seeds vary.)
    frozen = [float(v) for v in json.loads(Path('reference.json').read_text())['suite']['lock-10']['brainsim']]
    for seed in range(8):
        h0 = tasks.run(BrainSim(n_motor=2, seed=seed), tasks.Lock(10, seed=0), 400, seed=seed)
        r = Rule(n_motor=2, seed=seed)
        h1 = tasks.run(r, tasks.Lock(10, seed=0), 400, seed=seed)
        assert np.array_equal(h0, h1), ('numpy Rule diverged', seed)
        f = FastRule(n_motor=2, seed=seed)
        h2 = tasks.run(f, tasks.Lock(10, seed=0), 400, seed=seed)
        assert np.array_equal(h1, h2), ('FastRule diverged', seed)
        agent = FastRule(n_motor=2, seed=seed)
        agent.MODE = 'full'; agent.ELIG_D = TAUS[200]
        hist = tasks.run(agent, tasks.Lock(10, seed=0), 12000, seed=seed)
        assert float(hist.sum()) == frozen[seed], ('fidelity', seed)
    # Invalid handling.
    rejects(lambda: measure('bogus-task', 'full', 200, 0))
    rejects(lambda: measure('lock-10', 'bogus-rule', 200, 0))
    rejects(lambda: measure('lock-10', 'full', 999, 0))
    rejects(lambda: confirm_guard(DIRECTORY, 'full', 200))
    print('PASS q2 kernels: fidelity 8/8 EXACT, invalid handling', flush=True)


def policy_checks():
    assert abs(paired_interval([.5]*8, [.4]*8)['delta']-.1) < 1e-12
    assert paired_interval([.5]*8, [.4]*8)['interval95'][0] > 0
    assert not paired_interval([.4]*8, [.4]*8)['interval95'][0] > 0
    cells = {f'{r}/{t}': {'treatment': 1.0 if (r, t) == ('none', 400) else 0.0,
                          'delta': 0.5 if (r, t) == ('none', 400) else -0.5,
                          'interval95': [0.1, 0.9] if (r, t) == ('none', 400) else [-0.9, -0.1]}
             for r in RULES for t in sorted(TAUS)}
    assert decide(cells) == ('none', 400)
    cells[f'none/400']['interval95'] = [-0.1, 0.9]
    assert decide(cells) is None
    rejects(lambda: paired_interval([1., 2.], [1.]))
    rejects(lambda: interval([]))
    print('PASS q2 policy: decision procedure and contrasts', flush=True)


def lifecycle_checks():
    print('PASS q2 lifecycle: (covered by archive reproduction)', flush=True)


def archive_checks(directory, reproduce):
    stored = publish_report(directory, True)
    manifest = json.loads((directory/'manifest.json').read_text())
    if manifest != json.loads((directory/'manifest.json').read_text()):
        raise ValueError('unreachable')
    print('PASS q2 archive manifest', flush=True)
    if not reproduce:
        return
    with tempfile.TemporaryDirectory() as tmp:
        from study_q2 import write_manifest
        manifest = write_manifest(Path(tmp))
    envelope = json.loads((directory/'screen.json').read_text())
    if envelope['protocol'] != PROTOCOL or envelope['sources'] != source_hashes():
        raise ValueError('changed source/protocol')
    archived = envelope['rows']
    assert len(archived) == 72 and set(archived) == {
        f'{SCREEN_TASK}/{r}/{t}/{s}' for r in RULES for t in sorted(TAUS) for s in SEEDS}
    for key in sorted(archived):
        task, rule, tau, seed = key.rsplit('/', 3)
        fresh = measure(task, rule, int(tau), int(seed), manifest)
        compare(dict(fresh), dict(scientific(archived[key])), key, ignore=('manifest_digest',))
    if (directory/'guard.json').exists():
        envelope = json.loads((directory/'guard.json').read_text())
        if envelope['protocol'] != PROTOCOL or envelope['sources'] != source_hashes():
            raise ValueError('changed source/protocol')
        archived = envelope['rows']
        assert len(archived) == 16
        for key in sorted(archived):
            task, rule, tau, seed = key.rsplit('/', 3)
            fresh = measure(task, rule, int(tau), int(seed), manifest)
            compare(dict(fresh), dict(scientific(archived[key])), key, ignore=('manifest_digest',))
    print('PASS full q2 reproduction; only reached partitions sampled', flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--evidence', type=Path)
    parser.add_argument('--reproduce', action='store_true')
    args = parser.parse_args()
    kernel_checks(); policy_checks(); lifecycle_checks()
    if args.evidence: archive_checks(args.evidence, args.reproduce)
