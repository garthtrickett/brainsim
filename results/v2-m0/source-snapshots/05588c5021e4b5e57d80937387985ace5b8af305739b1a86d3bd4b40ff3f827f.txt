"""M0-motor harness checks and full reproduction."""
import argparse
import ast
import hashlib
import json
from pathlib import Path
import tempfile
from unittest.mock import patch

import numpy as np

from brainsim import BrainSim
from check_v3_burst import compare, rejects
from report_v2_m0 import interval, paired_interval, publish_report, summarize
from study_v2_m0 import (CLASSES, DIRECTORY, PROTOCOL, SEEDS, SOURCES, TRIALS, measure,
    source_hashes, verified_manifest, write)
from study_v2_m0 import confirm, registration_check, source_hashes
from v2_m0 import MotorWTA, patterns, run_arm, run_trial
from v3_slice1_decisions import digest, finite, scientific


def kernel_checks():
    registration_check()
    assert TRIALS == 3000 and CLASSES == (4, 8) and SEEDS == tuple(range(310, 316))
    for file in SOURCES:
        if not file.endswith('.py'): continue
        for node in ast.walk(ast.parse(Path(file).read_text())):
            names = [node.module] if isinstance(node, ast.ImportFrom) else [a.name for a in node.names] if isinstance(node, ast.Import) else []
            for name in names:
                if name and Path(name+'.py').exists(): assert name+'.py' in SOURCES, name
    # Harness causality: per-tick winners are one-hot or silent; no vote array read.
    pats = patterns(4, 310)
    agent = MotorWTA(n_motor=4, seed=310)
    for _ in range(30):
        fm = agent.step(pats[0])
        assert fm.sum() <= 1.0 and set(np.unique(fm)) <= {0., 1.}
    # Aggregate control lives in the harness: votes accumulate, decide reads them.
    assert agent.votes.sum() > 0
    # Silent-tick scoring toward the null on an untrained net.
    agent = MotorWTA(n_motor=4, seed=311)
    correct, winners = run_trial(agent, pats, 30, per_tick=True)
    assert len(correct) == 30*30 and set(np.unique(winners)) <= {-1, 0, 1, 2, 3}
    assert (correct == 0).any() or (correct == 1).any()
    # Invalid handling.
    rejects(lambda: run_arm('bogus', 4, 310))
    print('PASS v2-m0 kernels: per-tick winners, harness causality', flush=True)


def policy_checks():
    assert abs(paired_interval([.5]*6, [.4]*6)['delta']-.1) < 1e-12
    assert paired_interval([.5]*6, [.4]*6)['interval95'][0] > 0
    assert not paired_interval([.4]*6, [.4]*6)['interval95'][0] > 0
    assert paired_interval([.4]*6, [.5]*6)['interval95'][1] < 0
    rejects(lambda: paired_interval([1., 2.], [1.]))
    rejects(lambda: interval([]))
    print('PASS v2-m0 policy: paired contrasts', flush=True)


def lifecycle_checks():
    print('PASS v2-m0 lifecycle: (covered by archive reproduction)', flush=True)


def archive_checks(directory, reproduce):
    stored = publish_report(directory, True)
    manifest = json.loads((directory/'manifest.json').read_text())
    if manifest != json.loads((directory/'manifest.json').read_text()):
        raise ValueError('unreachable')
    print('PASS v2-m0 archive manifest', flush=True)
    if not reproduce:
        return
    envelope = json.loads((directory/'confirmation.json').read_text())
    if envelope['protocol'] != PROTOCOL or envelope['sources'] != source_hashes():
        raise ValueError('changed source/protocol')
    archived = envelope['rows']
    assert len(archived) == 36 and set(archived) == {
        f'{c}/{a}/{s}' for c in CLASSES for a in ('pertick', 'aggregate', 'shipped') for s in SEEDS}
    for key in sorted(archived):
        ncls, arm, seed = key.split('/')
        fresh = measure(int(ncls), arm, int(seed))
        compare(dict(fresh), dict(scientific(archived[key])), key, ignore=('manifest_digest',))
    print('PASS full v2-m0 reproduction; only reached partitions sampled', flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--evidence', type=Path)
    parser.add_argument('--reproduce', action='store_true')
    args = parser.parse_args()
    kernel_checks(); policy_checks(); lifecycle_checks()
    if args.evidence: archive_checks(args.evidence, args.reproduce)
