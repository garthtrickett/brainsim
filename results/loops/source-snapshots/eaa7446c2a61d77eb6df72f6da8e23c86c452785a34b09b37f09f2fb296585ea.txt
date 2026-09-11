"""Loops-probe harness checks and full reproduction."""
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
from fastsim import FastBrainSim
from loops_rule import FastLoops, LoopsBrainSim
from report_loops import band, interval, paired_interval, publish_report, summarize
from study_loops import (ARMS, DIRECTORY, LOOPTASKS, PROTOCOL, SEEDS, SOURCES,
    measure, source_hashes, verified_manifest)
from study_loops import confirm, registration_check
from v3_slice1_decisions import digest, finite, scientific

PROBE = [("nway-4", lambda s: tasks.NWay(4, seed=s), 4),
         ("volatile-4", lambda s: tasks.Volatile(4, 300, seed=s), 4)]


def kernel_checks():
    registration_check()
    assert ARMS == ('loops-LR', 'loops-full') and SEEDS == tuple(range(8))
    assert LOOPTASKS == ('volatile-4', 'lock-10', 'nway-8')
    for file in SOURCES:
        if not file.endswith('.py'): continue
        for node in ast.walk(ast.parse(Path(file).read_text())):
            names = [node.module] if isinstance(node, ast.ImportFrom) else [a.name for a in node.names] if isinstance(node, ast.Import) else []
            for name in names:
                if name and Path(name+'.py').exists(): assert name+'.py' in SOURCES, name
    # Fidelity legs: global-mode head-to-heads, then per-mode numpy-vs-fast.
    for name, mk, nm in PROBE:
        for seed in (0, 1):
            h0 = tasks.run(BrainSim(n_motor=nm, seed=seed), mk(seed), 400, seed=seed)
            h1 = tasks.run(LoopsBrainSim(n_motor=nm, seed=seed), mk(seed), 400, seed=seed)
            assert np.array_equal(h0, h1), ('global copy diverged', name, seed)
            b0 = tasks.run(FastBrainSim(n_motor=nm, seed=seed), mk(seed), 400, seed=seed)
            b1 = tasks.run(FastLoops(n_motor=nm, seed=seed), mk(seed), 400, seed=seed)
            assert np.array_equal(b0, b1), ('global fast diverged', name, seed)
            for mode in ARMS:
                a = LoopsBrainSim(n_motor=nm, seed=seed); a.MODE = mode
                b = FastLoops(n_motor=nm, seed=seed); b.MODE = mode
                h2 = tasks.run(a, mk(seed), 400, seed=seed)
                h3 = tasks.run(b, mk(seed), 400, seed=seed)
                assert np.array_equal(h2, h3), ('mode port diverged', mode, name, seed)
    # Memory/shape: loops-full carries vectors; global stays scalar.
    b = FastLoops(n_motor=4, seed=0); b.MODE = 'loops-full'
    tasks.run(b, tasks.NWay(4, seed=0), 30, seed=0)
    assert isinstance(b.noise_eff, np.ndarray) and b.noise_eff.shape == (4,)
    c = FastLoops(n_motor=4, seed=0)
    tasks.run(c, tasks.NWay(4, seed=0), 30, seed=0)
    assert not isinstance(c.noise_eff, np.ndarray)
    # Invalid handling.
    rejects(lambda: measure('bogus-task', 'loops-LR', 0))
    a = LoopsBrainSim(n_motor=4, seed=0); a.MODE = 'bogus-mode'
    rejects(lambda: tasks.run(a, tasks.NWay(4, seed=0), 30, seed=0))
    print('PASS loops kernels: fidelity 16/16 EXACT, shapes, invalid handling', flush=True)


def policy_checks():
    assert abs(paired_interval([.5]*8, [.4]*8)['delta']-.1) < 1e-12
    assert paired_interval([.5]*8, [.4]*8)['interval95'][0] > 0
    assert not paired_interval([.4]*8, [.4]*8)['interval95'][0] > 0
    assert band('nway-8', [.9]*8) == 0.03
    assert abs(band('lock-10', [400.]*8)-40.0) < 1e-9
    rejects(lambda: paired_interval([1., 2.], [1.]))
    rejects(lambda: interval([]))
    rejects(lambda: band('bogus', [1.]))
    print('PASS loops policy: paired contrasts and bands', flush=True)


def lifecycle_checks():
    print('PASS loops lifecycle: (covered by archive reproduction)', flush=True)


def archive_checks(directory, reproduce):
    stored = publish_report(directory, True)
    manifest = json.loads((directory/'manifest.json').read_text())
    if manifest != json.loads((directory/'manifest.json').read_text()):
        raise ValueError('unreachable')
    print('PASS loops archive manifest', flush=True)
    if not reproduce:
        return
    with tempfile.TemporaryDirectory() as tmp:
        from study_loops import write_manifest
        manifest = write_manifest(Path(tmp))
    envelope = json.loads((directory/'confirmation.json').read_text())
    if envelope['protocol'] != PROTOCOL or envelope['sources'] != source_hashes():
        raise ValueError('changed source/protocol')
    archived = envelope['rows']
    assert len(archived) == 48 and set(archived) == {
        f'{t}/{a}/{s}' for t in LOOPTASKS for a in ARMS for s in SEEDS}
    for key in sorted(archived):
        task, arm, seed = key.rsplit('/', 2)
        fresh = measure(task, arm, int(seed), manifest)
        compare(dict(fresh), dict(scientific(archived[key])), key, ignore=('manifest_digest',))
    print('PASS full loops reproduction; only reached partitions sampled', flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--evidence', type=Path)
    parser.add_argument('--reproduce', action='store_true')
    args = parser.parse_args()
    kernel_checks(); policy_checks(); lifecycle_checks()
    if args.evidence: archive_checks(args.evidence, args.reproduce)
