"""Registered finite tuning and independent confirmation with immutable provenance."""
import argparse
from functools import lru_cache
import hashlib
import json
from pathlib import Path

import numpy as np

from study_io import Evidence
from study_v3_burst import SOURCES as BURST_SOURCES
from study_v3_retention import request_events, window_record
from study_v3_slice1 import require_committed, write
from v3_adwin import run as adwin_run
from v3_tolerance import ARMS, FAMILIES, FROZEN, GRIDS, run
from v3_tolerance_policy import KEYS, PROTOCOL, SEEDS, complete, digest, finite, select
from v3_persistent import FIXTURES, fixture
from v3_slice1_streams import learning_metrics

DIRECTORY = Path('results/v3-tolerance')
SOURCES = sorted(set(BURST_SOURCES + ['DESIGN-v3-tolerance.md', 'v3_tolerance.py',
    'v3_adwin.py', 'v3_forgetting.py', 'v3_retention.py', 'v3_retention_policy.py',
    'report_v3_retention.py', 'study_v3_retention.py', 'v3_tolerance_policy.py', 'study_v3_tolerance.py',
    'report_v3_tolerance.py', 'check_v3_tolerance.py']))
LEVELS = {'jitter_2': 0, 'jitter_8': 1, 'jitter_16': 2, 'jitter_32': 3, 'jitter_128': 4,
          'drop_10': 5, 'drop_50': 6, 'add_0005': 7, 'add_0020': 8}
PARAMS = {'jitter_2': 2, 'jitter_8': 8, 'jitter_16': 16, 'jitter_32': 32, 'jitter_128': 128,
          'drop_10': .1, 'drop_50': .5, 'add_0005': .0005, 'add_0020': .002}


def source_hashes():
    return {p: hashlib.sha256(Path(p).read_bytes()).hexdigest() for p in SOURCES}


def registration_check():
    if source_hashes()['DESIGN-v3-tolerance.md'] != PROTOCOL['registration_sha256']:
        raise ValueError('registered protocol changed')


@lru_cache(maxsize=200)
def observations(seed, name):
    data = fixture(seed, name)
    # This cached, observations-only array cannot be mutated by a controller.
    data.y.flags.writeable = False
    return data


def schedule_rng(seed, level, fixture_ordinal, coordinate):
    return np.random.default_rng(np.random.SeedSequence(
        [seed, 116000+LEVELS[level]*100+fixture_ordinal, coordinate]))


def build_schedule(data, arm, seed, fixture_ordinal, alarm=None):
    """Evaluator-owned schedules; true times, perturbed times, or observed alarms."""
    steps, width = data.y.shape
    if arm == 'reference':
        return true_triggers(data)
    if arm == 'adwin_schedule':
        if alarm is None:
            raise ValueError('generating control configuration required')
        return adwin_run(data.y, alarm['delta'], alarm['clock'])[1]
    schedule = np.zeros_like(data.y)
    if arm.startswith('jitter_'):
        bound = PARAMS[arm]
        for j, events in enumerate(data.events):
            draws = schedule_rng(seed, arm, fixture_ordinal, j)
            for start, kind in events:
                if kind.startswith('target_'):
                    shifted = min(max(0, start+int(draws.integers(-bound, bound+1))), steps-1)
                    schedule[shifted, j] = 1.
    elif arm.startswith('drop_'):
        for j, events in enumerate(data.events):
            draws = schedule_rng(seed, arm, fixture_ordinal, j)
            for start, kind in events:
                if kind.startswith('target_') and draws.random() >= PARAMS[arm]:
                    schedule[start, j] = 1.
    elif arm.startswith('add_'):
        for j in range(width):
            schedule[:, j] = (schedule_rng(seed, arm, fixture_ordinal, j).random(steps) < PARAMS[arm]).astype(float)
    else:
        raise ValueError('unknown scheduled arm')
    return schedule


def memory_metrics(data, result, arm, provenance):
    records = {}
    for j, coordinate in enumerate(data.coordinates):
        if arm == 'sgd':
            records[coordinate] = {'kind': 'exponential', 'reset_count': 0, 'resets': [],
                'width_mean': None, 'width_final': None, 'width_min': None, 'width_max': None,
                'total_discarded': None, 'events': request_events(result[1][:, j], data.events[j]),
                'provenance': provenance}
            continue
        flags = result[1][:, j]
        if arm in FAMILIES:
            record = window_record(flags, result[3][:, j], result[4][:, j], data.events[j])
            record['kind'] = 'window'
        else:
            record = window_record(flags, result[3][:, j], result[4][:, j], data.events[j])
            record['kind'] = 'dual'
            slow_widths, slow_removed = result[5][:, j], result[6][:, j]
            record.update(adwin_width_mean=float(np.mean(slow_widths[1000:])),
                adwin_width_final=int(slow_widths[-1]), adwin_width_min=int(slow_widths[1000:].min()),
                adwin_width_max=int(slow_widths[1000:].max()),
                adwin_total_discarded=int(slow_removed.sum()),
                regime_fast_share=float(np.mean(result[7][1000:, j])))
        record['provenance'] = provenance
        records[coordinate] = record
    return records


def true_triggers(data):
    """Privileged true times, constructed ONLY in the evaluator; no target values."""
    triggers = np.zeros_like(data.y)
    for j, events in enumerate(data.events):
        for start, kind in events:
            if kind.startswith('target_'):
                triggers[start, j] = 1.
    return triggers


def simulation(seed, name, arm, config, alarm=None):
    data = observations(seed, name)
    if arm in FAMILIES:
        return data, run(data.y, arm, config)
    return data, run(data.y, arm, config,
                     schedule=build_schedule(data, arm, seed, FIXTURES.index(name), alarm))


def measure_row(seed, arm, config, alarm=None, manifest=None):
    row = {'status': 'ok', 'config': config, 'privileged_timing': arm not in FAMILIES,
           'fixtures': {}, 'memory': {}}
    if manifest is not None:
        row['manifest_digest'] = digest(manifest)
    for name in FIXTURES:
        data, result = simulation(seed, name, arm, config, alarm)
        if not all(np.isfinite(np.asarray(x)).all() for x in result):
            return {**{k: v for k, v in row.items() if k not in ('fixtures', 'memory')},
                    'status': 'nonfinite', 'reason': name+' trajectory'}
        with np.errstate(over='ignore', invalid='ignore'):
            metrics = learning_metrics(data, *result[:3])
        if not finite(metrics):
            return {**{k: v for k, v in row.items() if k not in ('fixtures', 'memory')},
                    'status': 'nonfinite', 'reason': name+' metrics'}
        row['fixtures'][name] = metrics
        row['memory'][name] = memory_metrics(data, result, arm,
            'none' if arm in FAMILIES else 'observed' if arm == 'adwin_schedule' else arm)
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
        if row.get('config') != expected or row.get('privileged_timing') is not (arm not in FAMILIES):
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
    alarm = manifest['screen']['selected']['adwin']
    for arm in ARMS:
        config = manifest['screen']['selected'][arm]
        for seed in SEEDS['confirmation']:
            evidence.measure(f'{arm}/{seed}', lambda s=seed, a=arm, c=config:
                             measure_row(s, a, c, alarm if a == 'adwin_schedule' else None, manifest))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('stage', choices=('tune', 'confirm', 'report'))
    parser.add_argument('--directory', type=Path, default=DIRECTORY)
    args = parser.parse_args()
    if args.stage == 'report':
        from report_v3_tolerance import publish_report
        publish_report(args.directory)
    else:
        {'tune': tune, 'confirm': confirm}[args.stage](args.directory)


if __name__ == '__main__':
    main()
