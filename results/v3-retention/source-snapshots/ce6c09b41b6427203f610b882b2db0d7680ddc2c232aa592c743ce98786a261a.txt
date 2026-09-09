"""Registered finite tuning and independent confirmation with immutable provenance."""
import argparse
from functools import lru_cache
import hashlib
import json
from pathlib import Path

import numpy as np

from study_io import Evidence
from study_v3_burst import SOURCES as BURST_SOURCES
from study_v3_slice1 import require_committed, write
from v3_retention import (ARMS, FAMILIES, GRIDS, random_uniforms, run)
from v3_retention_policy import KEYS, PROTOCOL, SEEDS, complete, digest, finite, select
from v3_persistent import FIXTURES, fixture
from v3_slice1_streams import learning_metrics

DIRECTORY = Path('results/v3-retention')
SOURCES = sorted(set(BURST_SOURCES + ['DESIGN-v3-retention.md', 'v3_retention.py',
    'v3_adwin.py', 'v3_forgetting.py', 'v3_retention_policy.py', 'study_v3_retention.py',
    'report_v3_retention.py', 'check_v3_retention.py']))


def source_hashes():
    return {p: hashlib.sha256(Path(p).read_bytes()).hexdigest() for p in SOURCES}


def registration_check():
    if source_hashes()['DESIGN-v3-retention.md'] != PROTOCOL['registration_sha256']:
        raise ValueError('registered protocol changed')


@lru_cache(maxsize=200)
def observations(seed, name):
    data = fixture(seed, name)
    # This cached, observations-only array cannot be mutated by a controller.
    data.y.flags.writeable = False
    return data


def oracle_triggers(data):
    """Privileged timing is constructed ONLY in the evaluator; no target values."""
    triggers = np.zeros_like(data.y)
    for j, events in enumerate(data.events):
        for start, kind in events:
            if kind.startswith('target_'):
                triggers[start, j] = 1.
    return triggers


def request_events(flags, events):
    hits = []
    for start, kind in events:
        found = np.flatnonzero(flags[start:start+100])
        hits.append({'index': start, 'kind': kind, 'hit': bool(len(found)),
                     'latency': int(found[0]) if len(found) else 100})
    return hits


def window_record(flags, widths, removed, events):
    indices = np.flatnonzero(flags).tolist()
    return {'reset_count': len(indices), 'resets': [{'index': t,
        'width_before': int(widths[t-1]) if t else 0, 'width_after': int(widths[t]),
        'discarded': int(removed[t])} for t in indices],
        'width_mean': float(np.mean(widths[1000:])), 'width_final': int(widths[-1]),
        'width_min': int(widths[1000:].min()), 'width_max': int(widths[1000:].max()),
        'total_discarded': int(removed.sum()), 'events': request_events(flags, events)}


def memory_metrics(data, result, arm):
    records = {}
    for j, coordinate in enumerate(data.coordinates):
        if arm == 'sgd':
            records[coordinate] = {'kind': 'exponential', 'reset_count': 0, 'resets': [],
                'width_mean': None, 'width_final': None, 'width_min': None, 'width_max': None,
                'total_discarded': None, 'events': request_events(result[1][:, j], data.events[j])}
            continue
        flags = result[1][:, j]
        if arm in ('retain', 'random_fallback'):
            record = window_record(flags, result[3][:, j], result[4][:, j], data.events[j])
            record['kind'] = 'dual'
            slow_widths, slow_removed = result[5][:, j], result[6][:, j]
            record.update(adwin_width_mean=float(np.mean(slow_widths[1000:])),
                adwin_width_final=int(slow_widths[-1]), adwin_width_min=int(slow_widths[1000:].min()),
                adwin_width_max=int(slow_widths[1000:].max()),
                adwin_total_discarded=int(slow_removed.sum()),
                regime_fast_share=float(np.mean(result[7][1000:, j])))
        else:
            record = window_record(flags, result[3][:, j], result[4][:, j], data.events[j])
            record['kind'] = 'window'
        records[coordinate] = record
    return records


def simulation(seed, name, arm, config, probability=None):
    data = observations(seed, name)
    kwargs = {}
    if arm in ('retain', 'oracle_nofallback'):
        kwargs['triggers'] = oracle_triggers(data)
    elif arm == 'random_fallback':
        kwargs.update(uniforms=random_uniforms(seed, FIXTURES.index(name), len(data.y), len(data.coordinates)),
                      probability=probability)
    return data, run(data.y, arm, config, **kwargs)


def measure_row(seed, arm, config, probability=None, manifest=None):
    row = {'status': 'ok', 'config': config, 'privileged_timing': arm in ('retain', 'oracle_nofallback'),
           'fixtures': {}, 'memory': {}}
    if manifest is not None:
        row['manifest_digest'] = digest(manifest)
    for name in FIXTURES:
        data, result = simulation(seed, name, arm, config, probability)
        if not all(np.isfinite(np.asarray(x)).all() for x in result):
            return {**{k: v for k, v in row.items() if k not in ('fixtures', 'memory')},
                    'status': 'nonfinite', 'reason': name+' trajectory'}
        with np.errstate(over='ignore', invalid='ignore'):
            metrics = learning_metrics(data, *result[:3])
        if not finite(metrics):
            return {**{k: v for k, v in row.items() if k not in ('fixtures', 'memory')},
                    'status': 'nonfinite', 'reason': name+' metrics'}
        row['fixtures'][name] = metrics
        row['memory'][name] = memory_metrics(data, result, arm)
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
        if row.get('config') != expected or row.get('privileged_timing') is not (arm in ('retain', 'oracle_nofallback')):
            raise ValueError('row configuration/privilege mismatch')
        if manifest is not None and row.get('manifest_digest') != digest(manifest):
            raise ValueError('row belongs to another manifest')
    return rows


def make_manifest(rows):
    result = {'protocol': PROTOCOL, 'sources': source_hashes(), 'seeds': SEEDS,
              'grids': GRIDS, 'screen': select(rows),
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
                             measure_row(s, a, c, probability if a == 'random_fallback' else None, manifest))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('stage', choices=('tune', 'confirm', 'report'))
    parser.add_argument('--directory', type=Path, default=DIRECTORY)
    args = parser.parse_args()
    if args.stage == 'report':
        from report_v3_retention import publish_report
        publish_report(args.directory)
    else:
        {'tune': tune, 'confirm': confirm}[args.stage](args.directory)


if __name__ == '__main__':
    main()
