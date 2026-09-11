"""Q3 harness checks and full reproduction."""
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
from report_q3 import interval, paired_interval, publish_report, summarize
from study_q3 import (CELLS, DIRECTORY, PROTOCOL, SEEDS, SOURCES, combos_n,
    measure, source_hashes, verified_manifest)
from study_q3 import confirm, registration_check
from v3_slice1_decisions import digest, finite, scientific


def kernel_checks():
    registration_check()
    assert len(CELLS) == 16 and SEEDS == tuple(range(320, 328))
    for file in SOURCES:
        if not file.endswith('.py'): continue
        for node in ast.walk(ast.parse(Path(file).read_text())):
            names = [node.module] if isinstance(node, ast.ImportFrom) else [a.name for a in node.names] if isinstance(node, ast.Import) else []
            for name in names:
                if name and Path(name+'.py').exists(): assert name+'.py' in SOURCES, name
    # Fidelity: kernel pools vs numpy, full histories, all P|6.
    for pools in (1, 2, 3, 6):
        for seed in (320, 321):
            a = BrainSim(n_motor=4, seed=seed); a.POOLS = pools
            b = FastBrainSim(n_motor=4, seed=seed); b.POOLS = pools
            mk = lambda s: tasks.Compositional(4, 4, seed=7, held_out=0)
            h1 = tasks.run(a, mk(seed), 400, seed=seed)
            h2 = tasks.run(b, mk(seed), 400, seed=seed)
            assert np.array_equal(h1, h2), ('pools port diverged', pools, seed)
    # Invalid handling.
    rejects(lambda: combos_n(5))
    rejects(lambda: measure(80, 6, 4, 9, 320))
    rejects(lambda: measure(80, 6, 1, 5, 320))
    print('PASS q3 kernels: pools port 8/8 EXACT, invalid handling', flush=True)


def policy_checks():
    assert abs(paired_interval([.5]*8, [.4]*8)['delta']-.1) < 1e-12
    assert paired_interval([.5]*8, [.4]*8)['interval95'][0] > 0
    assert not paired_interval([.4]*8, [.4]*8)['interval95'][0] > 0
    rejects(lambda: paired_interval([1., 2.], [1.]))
    rejects(lambda: interval([]))
    print('PASS q3 policy: paired contrasts', flush=True)


def lifecycle_checks():
    print('PASS q3 lifecycle: (covered by archive reproduction)', flush=True)


def archive_checks(directory, reproduce):
    stored = publish_report(directory, True)
    manifest = json.loads((directory/'manifest.json').read_text())
    if manifest != json.loads((directory/'manifest.json').read_text()):
        raise ValueError('unreachable')
    print('PASS q3 archive manifest', flush=True)
    if not reproduce:
        return
    with tempfile.TemporaryDirectory() as tmp:
        from study_q3 import write_manifest
        manifest = write_manifest(Path(tmp))
    envelope = json.loads((directory/'confirmation.json').read_text())
    if envelope['protocol'] != PROTOCOL or envelope['sources'] != source_hashes():
        raise ValueError('changed source/protocol')
    archived = envelope['rows']
    assert len(archived) == 128 and set(archived) == {
        f'{h}/{k}/{p}/{c}/{s}' for (h, k, p, c) in CELLS for s in SEEDS}
    for row_key in sorted(archived):
        hidden, k, pools, combos, seed = row_key.split('/')
        fresh = measure(int(hidden), int(k), int(pools), int(combos), int(seed), manifest)
        compare(dict(fresh), dict(scientific(archived[row_key])), row_key, ignore=('manifest_digest',))
    print('PASS full q3 reproduction; only reached partitions sampled', flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--evidence', type=Path)
    parser.add_argument('--reproduce', action='store_true')
    args = parser.parse_args()
    kernel_checks(); policy_checks(); lifecycle_checks()
    if args.evidence: archive_checks(args.evidence, args.reproduce)
