"""Registered finite tuning and independent confirmation with immutable provenance."""
import argparse
from functools import lru_cache
import hashlib
import json
from pathlib import Path

import numpy as np

from study_io import Evidence
from study_v3_reference import SOURCES as REFERENCE_SOURCES, explanatory_events
from study_v3_slice1 import require_committed, write
from v3_burst import (ARMS, FAMILIES, GRIDS, START, THRESHOLD, random_uniforms,
                      reference_gates, run)
from v3_burst_policy import KEYS, PROTOCOL, SEEDS, complete, digest, finite, select
from v3_persistent import FIXTURES, fixture
from v3_slice1_streams import diagnostic_metrics, learning_metrics

DIRECTORY = Path('results/v3-burst')
SOURCES = sorted(set(REFERENCE_SOURCES + ['study_v3_reference.py', 'v3_reference_policy.py',
    'results/v3-reference/manifest.json', 'DESIGN-v3-burst.md', 'v3_burst.py', 'v3_burst_policy.py', 'study_v3_burst.py',
    'report_v3_burst.py', 'check_v3_burst.py', 'report_v3_slice1.py']))


def source_hashes():
    return {p: hashlib.sha256(Path(p).read_bytes()).hexdigest() for p in SOURCES}


def registration_check():
    if source_hashes()['DESIGN-v3-burst.md'] != PROTOCOL['registration_sha256']:
        raise ValueError('registered protocol changed')


@lru_cache(maxsize=200)
def observations(seed, name):
    data = fixture(seed, name)
    gates = reference_gates(data.y)
    # These cached, observations-only arrays cannot be mutated by a controller.
    data.y.flags.writeable = gates.flags.writeable = False
    return data, gates


def oracle_triggers(data):
    """Privileged timing is constructed ONLY in the evaluator; no target values."""
    triggers = np.zeros_like(data.y)
    for j, events in enumerate(data.events):
        for start, kind in events:
            if kind.startswith('target_'):
                triggers[start, j] = 1.
    return triggers


def activity_metrics(data, active, starts):
    records = {}
    for j, coordinate in enumerate(data.coordinates):
        indices = np.flatnonzero(starts[:, j]).tolist()
        events = []
        for start, kind in data.events[j]:
            hits = np.flatnonzero(starts[start:start+100, j])
            events.append({'index': start, 'kind': kind, 'hit': bool(len(hits)),
                           'latency': int(hits[0]) if len(hits) else 100})
        records[coordinate] = {'starts': indices, 'start_count': len(indices),
            'active_updates': int(np.count_nonzero(active[:, j])),
            'duty_cycle': float(np.count_nonzero(active[START:, j])/(len(active)-START)),
            'events': events}
    return records


def simulation(seed, name, arm, config, probability=None):
    data, gates = observations(seed, name)
    kwargs = {}
    if arm in ('burst', 'continuous'):
        kwargs['gates'] = gates
    elif arm in ('oracle', 'oracle_matched'):
        kwargs['triggers'] = oracle_triggers(data)
    elif arm == 'random':
        kwargs.update(uniforms=random_uniforms(seed, FIXTURES.index(name), len(data.y), len(data.coordinates)),
                      probability=probability)
    return data, gates, run(data.y, arm, config, **kwargs)


def measure_row(seed, arm, config, probability=None, manifest=None):
    row = {'status': 'ok', 'config': config, 'privileged_timing': arm in ('oracle', 'oracle_matched'),
           'fixtures': {}, 'activity': {}}
    if manifest is not None:
        row['manifest_digest'] = digest(manifest)
    if arm == 'burst' and manifest is not None:
        row.update(detector={}, explanatory_events={})
    for name in FIXTURES:
        data, gates, result = simulation(seed, name, arm, config, probability)
        if not all(np.isfinite(x).all() for x in result):
            return {**{k: v for k, v in row.items() if k not in ('fixtures', 'activity', 'detector', 'explanatory_events')},
                    'status': 'nonfinite', 'reason': name+' trajectory'}
        with np.errstate(over='ignore', invalid='ignore'):
            metrics = learning_metrics(data, *result[:3])
        if not finite(metrics):
            return {**{k: v for k, v in row.items() if k not in ('fixtures', 'activity', 'detector', 'explanatory_events')},
                    'status': 'nonfinite', 'reason': name+' metrics'}
        row['fixtures'][name] = metrics
        active = result[1] if arm in ('burst', 'oracle', 'oracle_matched', 'random') else np.zeros_like(data.y)
        row['activity'][name] = activity_metrics(data, active, result[3])
        if arm == 'burst' and manifest is not None:
            row['detector'][name] = diagnostic_metrics(data, gates, THRESHOLD)
            row['explanatory_events'][name] = explanatory_events(data, result[0], gates)
    if not finite(row):
        raise ValueError('non-finite explanatory record')
    return row


def read_stage(directory, stage):
    envelope = json.loads((directory/(stage+'.json')).read_text())
    if envelope['protocol'] != PROTOCOL or envelope['sources'] != source_hashes():
        raise ValueError('changed source/protocol')
    rows = envelope['rows']
    complete(rows, stage)
    manifest = json.loads((directory/'manifest.json').read_text()) if stage == 'confirmation' else None
    for key, row in rows.items():
        parts = key.split('/')
        arm = parts[0]
        expected = GRIDS[arm][int(parts[1])] if stage == 'tuning' else manifest['screen']['selected'][arm]
        if row.get('config') != expected or row.get('privileged_timing') is not (arm in ('oracle', 'oracle_matched')):
            raise ValueError('row configuration/privilege mismatch')
        if manifest is not None and row.get('manifest_digest') != digest(manifest):
            raise ValueError('row belongs to another manifest')
    return rows


def make_manifest(rows):
    result = {'protocol': PROTOCOL, 'sources': source_hashes(), 'seeds': SEEDS,
              'threshold': THRESHOLD, 'grids': GRIDS, 'screen': select(rows),
              'tuning_digest': digest(rows), 'expected_counts': {s: len(k) for s, k in KEYS.items()}}
    return json.loads(json.dumps(result, allow_nan=False))


def verified_manifest(directory):
    registration_check()
    for source in SOURCES:
        require_committed(Path(source))
    require_committed(directory/'manifest.json')
    require_committed(directory/'tuning.json')
    manifest = json.loads((directory/'manifest.json').read_text())
    if manifest != make_manifest(read_stage(directory, 'tuning')):
        raise ValueError('manifest differs from tuning')
    if manifest['screen']['status'] != 'eligible':
        raise ValueError('tuning prerequisite failed; confirmation forbidden')
    return manifest


def tune(directory):
    registration_check()
    for source in SOURCES:
        require_committed(Path(source))
    if (directory/'confirmation.json').exists():
        raise ValueError('cannot reopen tuning after confirmation')
    evidence = Evidence(directory/'tuning.json', SOURCES, PROTOCOL)
    for arm in FAMILIES:
        for i, config in enumerate(GRIDS[arm]):
            for seed in SEEDS['tuning']:
                evidence.measure(f'{arm}/{i}/{seed}', lambda s=seed, a=arm, c=config: measure_row(s, a, c))
    manifest = make_manifest(read_stage(directory, 'tuning'))
    path = directory/'manifest.json'
    if path.exists() and json.loads(path.read_text()) != manifest:
        raise ValueError('frozen manifest changed')
    write(path, manifest)
    print('TUNING', manifest['screen']['status'], 'Commit complete evidence/manifest before confirmation.', flush=True)


def confirm(directory):
    manifest = verified_manifest(directory)
    evidence = Evidence(directory/'confirmation.json', SOURCES, PROTOCOL)
    probability = manifest['screen']['random_frequency']['probability']
    for arm in ARMS:
        config = manifest['screen']['selected'][arm]
        for seed in SEEDS['confirmation']:
            evidence.measure(f'{arm}/{seed}', lambda s=seed, a=arm, c=config:
                             measure_row(s, a, c, probability if a == 'random' else None, manifest))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('stage', choices=('tune', 'confirm', 'report'))
    parser.add_argument('--directory', type=Path, default=DIRECTORY)
    args = parser.parse_args()
    if args.stage == 'report':
        from report_v3_burst import publish_report
        publish_report(args.directory)
    else:
        {'tune': tune, 'confirm': confirm}[args.stage](args.directory)


if __name__ == '__main__':
    main()
