"""Registered finite tuning and independent confirmation with immutable provenance."""
import argparse
from functools import lru_cache
import hashlib
import json
from pathlib import Path

import numpy as np

from study_io import Evidence
from study_v3_burst import SOURCES as BURST_SOURCES
from study_v3_drift import boundary_kind, enriched_schedule
from study_v3_slice1 import require_committed, write
from study_v3_slope import entry_flags, memory_metrics
from v3_burst import random_probability
from v3_slope import run
from v3_slopebench import FIXTURES, ORDINAL, fixture, random_uniforms, ramp_metrics
from v3_slopebench_policy import GRIDS, KEYS, PROTOCOL, SEEDS, complete, digest, finite, select
from v3_slice1_streams import learning_metrics

DIRECTORY = Path('results/v3-slopebench')
SOURCES = sorted(set(BURST_SOURCES + ['DESIGN-v3-slopebench.md', 'v3_slopebench.py',
    'v3_adwin.py', 'v3_forgetting.py', 'v3_retention.py', 'v3_retention_policy.py',
    'report_v3_retention.py', 'study_v3_retention.py', 'v3_slope.py', 'v3_slope_policy.py',
    'report_v3_slope.py', 'study_v3_slope.py', 'v3_drift.py', 'v3_drift_policy.py', 'report_v3_drift.py',
    'study_v3_drift.py', 'v3_slopebench_policy.py', 'study_v3_slopebench.py',
    'report_v3_slopebench.py', 'check_v3_slopebench.py']))


def source_hashes():
    return {p: hashlib.sha256(Path(p).read_bytes()).hexdigest() for p in SOURCES}


def registration_check():
    if source_hashes()['DESIGN-v3-slopebench.md'] != PROTOCOL['registration_sha256']:
        raise ValueError('registered protocol changed')


@lru_cache(maxsize=200)
def observations(seed, name):
    data = fixture(seed, name)
    # This cached, observations-only array cannot be mutated by a controller.
    data.y.flags.writeable = False
    return data


def simulation(seed, name, arm, config, probability=None):
    data = observations(seed, name)
    kwargs = {}
    if arm in ('slope', 'oracle_nofallback'):
        kwargs['schedule'] = enriched_schedule(data)
        if arm == 'slope':
            kwargs['enter'] = entry_flags(data)
    elif arm == 'random_slope':
        kwargs.update(uniforms=random_uniforms(seed, ORDINAL[name], len(data.y), len(data.coordinates)),
                      probability=probability)
    return data, run(data.y, arm, config, **kwargs)


def measure_row(seed, arm, config, probability=None, manifest=None):
    row = {'status': 'ok', 'config': config, 'privileged_timing': arm not in ('window', 'sgd', 'adwin'),
           'fixtures': {}, 'memory': {}}
    if manifest is not None:
        row['manifest_digest'] = digest(manifest)
    for name in FIXTURES:
        data, result = simulation(seed, name, arm, config, probability)
        if not all(np.isfinite(np.asarray(x)).all() for x in result):
            return {**{k: v for k, v in row.items() if k not in ('fixtures', 'memory')},
                    'status': 'nonfinite', 'reason': name+' trajectory'}
        with np.errstate(over='ignore', invalid='ignore'):
            metrics = ramp_metrics(data, result[0], result[2]) if name not in ('core', 'mixed') else learning_metrics(data, *result[:3])
        if not finite(metrics):
            return {**{k: v for k, v in row.items() if k not in ('fixtures', 'memory')},
                    'status': 'nonfinite', 'reason': name+' metrics'}
        row['fixtures'][name] = metrics
        records = memory_metrics(data, result, arm)
        if arm not in ('window', 'sgd', 'adwin'):
            for j, coordinate in enumerate(data.coordinates):
                kinds = [boundary_kind(data, t, j) if arm != 'random_slope' else 'random'
                         for t in [r['index'] for r in records[coordinate]['resets']]]
                for entry, kind in zip(records[coordinate]['resets'], kinds):
                    entry['kind'] = kind
        row['memory'][name] = records
    if not finite(row):
        raise ValueError('non-finite explanatory record')
    return row


def enriched_frequency():
    """Pool enriched requests over tuning seeds; the schedule needs no learner."""
    count, opportunities = 0, 6000*9*8
    for seed in SEEDS['tuning']:
        for name in FIXTURES:
            count += int(enriched_schedule(observations(seed, name)).sum())
    return {'starts': count, 'coordinate_time': opportunities,
            'probability': random_probability(count, opportunities, 1)}


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
        if row.get('config') != expected or row.get('privileged_timing') is not (arm not in ('window', 'sgd', 'adwin')):
            raise ValueError('row configuration/privilege mismatch')
        if manifest is not None and row.get('manifest_digest') != digest(manifest):
            raise ValueError('row belongs to another manifest')
    return rows


def make_manifest(rows):
    screen = select(rows)
    screen['random_frequency'] = enriched_frequency()
    result = {'protocol': PROTOCOL, 'sources': source_hashes(), 'seeds': SEEDS,
              'grids': GRIDS, 'screen': screen,
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
    for arm in ('window', 'sgd', 'adwin'):
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
    for arm in ('window', 'sgd', 'adwin', 'slope', 'oracle_nofallback', 'random_slope'):
        config = manifest['screen']['selected'][arm]
        for seed in SEEDS['confirmation']:
            evidence.measure(f'{arm}/{seed}', lambda s=seed, a=arm, c=config:
                             measure_row(s, a, c, probability if a == 'random_slope' else None, manifest))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('stage', choices=('tune', 'confirm', 'report'))
    parser.add_argument('--directory', type=Path, default=DIRECTORY)
    args = parser.parse_args()
    if args.stage == 'report':
        from report_v3_slopebench import publish_report
        publish_report(args.directory)
    else:
        {'tune': tune, 'confirm': confirm}[args.stage](args.directory)


if __name__ == '__main__':
    main()
