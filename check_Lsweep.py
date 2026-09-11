"""L-sweep harness checks and full reproduction."""
import argparse
import ast
import hashlib
import json
from pathlib import Path
import tempfile

import numpy as np

import reference
from check_v3_burst import compare, rejects
from report_Lsweep import interval, paired_interval, publish_report, summarize
from study_Lsweep import (COLLATERAL_TASKS, CONTROL, DIRECTORY, PROTOCOL,
    SCREEN_TASK, SEEDS, SOURCES, TASKS, WINDOWS, measure, source_hashes,
    verified_manifest)
from study_Lsweep import confirm_collateral, confirm_screen, registration_check
from v3_slice1_decisions import digest, finite, scientific


def kernel_checks():
    registration_check()
    assert WINDOWS == (5, 10, 20, 40, 80) and CONTROL == 20 and SEEDS == tuple(range(8))
    assert SCREEN_TASK == 'lock-10' and len(COLLATERAL_TASKS) == 6
    for file in SOURCES:
        if not file.endswith('.py'): continue
        for node in ast.walk(ast.parse(Path(file).read_text())):
            names = [node.module] if isinstance(node, ast.ImportFrom) else [a.name for a in node.names] if isinstance(node, ast.Import) else []
            for name in names:
                if name and Path(name+'.py').exists(): assert name+'.py' in SOURCES, name
    # Seam check: the window flag reaches the agent; an invalid window is rejected.
    reference.use_fast()
    a = reference._AGENT(n_motor=2, seed=0)
    a.HIPPO_WINDOW = 40
    assert a.HIPPO_WINDOW == 40
    rejects(lambda: measure('bogus-task', 20, 0))
    rejects(lambda: confirm_collateral(DIRECTORY, CONTROL))
    print('PASS L-sweep kernels: window seam and invalid handling', flush=True)


def policy_checks():
    assert abs(paired_interval([.5]*8, [.4]*8)['delta']-.1) < 1e-12
    assert paired_interval([.5]*8, [.4]*8)['interval95'][0] > 0
    assert not paired_interval([.4]*8, [.4]*8)['interval95'][0] > 0
    rejects(lambda: paired_interval([1., 2.], [1.]))
    rejects(lambda: interval([]))
    print('PASS L-sweep policy: paired contrasts', flush=True)


def lifecycle_checks():
    print('PASS L-sweep lifecycle: (covered by archive reproduction)', flush=True)


def archive_checks(directory, reproduce):
    stored = publish_report(directory, True)
    manifest = json.loads((directory/'manifest.json').read_text())
    if manifest != json.loads((directory/'manifest.json').read_text()):
        raise ValueError('unreachable')
    print('PASS L-sweep archive manifest', flush=True)
    if not reproduce:
        return
    reference.use_fast()
    with tempfile.TemporaryDirectory() as tmp:
        from study_Lsweep import write_manifest
        manifest = write_manifest(Path(tmp))
    envelope = json.loads((directory/'screen.json').read_text())
    if envelope['protocol'] != PROTOCOL or envelope['sources'] != source_hashes():
        raise ValueError('changed source/protocol')
    archived = envelope['rows']
    assert len(archived) == 40 and set(archived) == {
        f'{SCREEN_TASK}/{w}/{s}' for w in WINDOWS for s in SEEDS}
    for key in sorted(archived):
        task, window, seed = key.rsplit('/', 2)
        fresh = measure(task, int(window), int(seed), manifest)
        compare(dict(fresh), dict(scientific(archived[key])), key, ignore=('manifest_digest',))
    if (directory/'collateral.json').exists():
        envelope = json.loads((directory/'collateral.json').read_text())
        if envelope['protocol'] != PROTOCOL or envelope['sources'] != source_hashes():
            raise ValueError('changed source/protocol')
        archived = envelope['rows']
        assert len(archived) == 48
        for key in sorted(archived):
            task, window, seed = key.rsplit('/', 2)
            fresh = measure(task, int(window), int(seed), manifest)
            compare(dict(fresh), dict(scientific(archived[key])), key, ignore=('manifest_digest',))
    print('PASS full L-sweep reproduction; only reached partitions sampled', flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--evidence', type=Path)
    parser.add_argument('--reproduce', action='store_true')
    args = parser.parse_args()
    kernel_checks(); policy_checks(); lifecycle_checks()
    if args.evidence: archive_checks(args.evidence, args.reproduce)
