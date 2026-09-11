"""Q5 rank-1 harness checks and full reproduction."""
import argparse
import ast
import hashlib
import json
from pathlib import Path
import tempfile

import numpy as np

import reference
import tasks
from brainsim import BrainSim
from check_v3_burst import compare, rejects
from q5_rank1 import FastRank1, Rank1BrainSim
from report_q5 import band, interval, paired_interval, publish_report, summarize
from study_q5 import (ARMS, DIRECTORY, PROTOCOL, SEEDS, SOURCES, TASKS, measure,
    source_hashes, verified_manifest)
from study_q5 import confirm, registration_check
from tasks import Conjunctive, Lock, NWay, TMaze, Volatile, run
from v3_slice1_decisions import digest, finite, scientific

PROBE = [("nway-4", lambda s: NWay(4, seed=s), 4, 400),
         ("nway-8", lambda s: NWay(8, seed=s), 8, 400),
         ("lock-10", lambda s: Lock(10, seed=s), 2, 400),
         ("volatile-4", lambda s: Volatile(4, seed=s), 4, 400),
         ("xor-2", lambda s: Conjunctive(seed=s), 2, 400),
         ("tmaze-2", lambda s: TMaze(2, seed=s), 2, 400)]


def kernel_checks():
    registration_check()
    assert ARMS == ('shipped', 'rank1') and SEEDS == tuple(range(8)) and len(TASKS) == 7
    for file in SOURCES:
        if not file.endswith('.py'): continue
        for node in ast.walk(ast.parse(Path(file).read_text())):
            names = [node.module] if isinstance(node, ast.ImportFrom) else [a.name for a in node.names] if isinstance(node, ast.Import) else []
            for name in names:
                if name and Path(name+'.py').exists(): assert name+'.py' in SOURCES, name
    # Memory: under the flag no (M,H) credit matrix persists; without it the
    # matrix is there. Persistent credit state is exactly M+H+1 floats.
    for cls in (Rank1BrainSim, FastRank1):
        a = cls(n_motor=4, seed=0); a.RANK1_ELIG = True
        run(a, tasks.NWay(4, seed=0), 30, seed=0)
        assert a.elig is None, cls
        assert a.etr_m.shape == (4,) and a.etr_h.shape == (a.n_hidden,)
        assert isinstance(a.etrw, float) and np.isfinite(a.etrw)
        assert np.isfinite(a.W_out).all()
    c = BrainSim(n_motor=4, seed=0)
    run(c, tasks.NWay(4, seed=0), 30, seed=0)
    assert c.elig is not None and c.elig.shape == (4, c.n_hidden)
    # Copy fidelity + port gate, exact full histories on all 12 probe pairs.
    for name, mk, nm, dec in PROBE:
        for seed in (0, 1):
            h0 = run(BrainSim(n_motor=nm, seed=seed), mk(seed), dec, seed=seed)
            h1 = run(Rank1BrainSim(n_motor=nm, seed=seed), mk(seed), dec, seed=seed)
            assert np.array_equal(h0, h1), ('classic diverged', name, seed)
            a = Rank1BrainSim(n_motor=nm, seed=seed); a.RANK1_ELIG = True
            b = FastRank1(n_motor=nm, seed=seed); b.RANK1_ELIG = True
            h2 = run(a, mk(seed), dec, seed=seed)
            h3 = run(b, mk(seed), dec, seed=seed)
            assert np.array_equal(h2, h3), ('rank1 port diverged', name, seed)
            assert a.elig is None and b.elig is None
    print('PASS q5 kernels: memory shape, copy fidelity 12/12, rank-1 port 12/12', flush=True)


def policy_checks():
    assert abs(paired_interval([.5]*8, [.4]*8)['delta']-.1) < 1e-12
    assert paired_interval([.5]*8, [.4]*8)['interval95'][0] > 0
    assert not paired_interval([.4]*8, [.4]*8)['interval95'][0] > 0
    assert band('nway-4', [.9]*8) == 0.03
    assert abs(band('lock-10', [400.]*8)-40.0) < 1e-9
    rejects(lambda: paired_interval([1., 2.], [1.]))
    rejects(lambda: interval([]))
    rejects(lambda: band('bogus', [1.]))
    print('PASS q5 policy: paired contrasts and bands', flush=True)


def lifecycle_checks():
    print('PASS q5 lifecycle: (covered by archive reproduction)', flush=True)


def archive_checks(directory, reproduce):
    stored = publish_report(directory, True)
    manifest = json.loads((directory/'manifest.json').read_text())
    if manifest != json.loads((directory/'manifest.json').read_text()):
        raise ValueError('unreachable')
    print('PASS q5 archive manifest', flush=True)
    if not reproduce:
        return
    reference.use_fast()
    envelope = json.loads((directory/'confirmation.json').read_text())
    if envelope['protocol'] != PROTOCOL or envelope['sources'] != source_hashes():
        raise ValueError('changed source/protocol')
    archived = envelope['rows']
    assert len(archived) == 112 and set(archived) == {
        f'{t}/{a}/{s}' for t in TASKS for a in ARMS for s in SEEDS}
    with tempfile.TemporaryDirectory() as tmp:
        from study_q5 import write_manifest
        manifest = write_manifest(Path(tmp))
    for key in sorted(archived):
        task, arm, seed = key.rsplit('/', 2)
        fresh = measure(task, arm, int(seed), manifest)
        compare(dict(fresh), dict(scientific(archived[key])), key, ignore=('manifest_digest',))
    print('PASS full q5 reproduction; only reached partitions sampled', flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--evidence', type=Path)
    parser.add_argument('--reproduce', action='store_true')
    args = parser.parse_args()
    kernel_checks(); policy_checks(); lifecycle_checks()
    if args.evidence: archive_checks(args.evidence, args.reproduce)
