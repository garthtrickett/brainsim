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
from v3_adwin import run as adwin_run
from v3_persistent import FIXTURES, fixture
from v3_slice1_streams import learning_metrics
from v4_robust import ARMS, FAMILIES, GRIDS, run
from v4_robust_policy import KEYS, PROTOCOL, SEEDS, complete, digest, finite, select

DIRECTORY = Path('results/v4-robust')
SOURCES = sorted(set(BURST_SOURCES + ['DESIGN-v4-robust.md', 'v4_robust.py',
    'v3_adwin.py', 'v3_forgetting.py', 'v3_retention.py', 'v3_retention_policy.py', 'study_v3_retention.py',
    'report_v3_retention.py', 'v4_robust_policy.py', 'study_v4_robust.py',
    'report_v4_robust.py', 'check_v4_robust.py']))
LIE = {'delay_lo': 0, 'delay_hi': 8, 'miss': .1, 'false': .001}


def source_hashes():
    return {p: hashlib.sha256(Path(p).read_bytes()).hexdigest() for p in SOURCES}


def registration_check():
    if source_hashes()['DESIGN-v4-robust.md'] != PROTOCOL['registration_sha256']:
        raise ValueError('registered protocol changed')


@lru_cache(maxsize=200)
def observations(seed, name):
    data = fixture(seed, name)
    # This cached, observations-only array cannot be mutated by a controller.
    data.y.flags.writeable = False
    return data


def lie_rng(seed, fixture_ordinal, coordinate):
    return np.random.default_rng(np.random.SeedSequence([seed, 186000+fixture_ordinal, coordinate]))


def build_lies(data, seed, fixture_ordinal):
    """Frozen sloppy schedule: delayed true events, misses, false alarms."""
    alarms = np.zeros_like(data.y)
    kinds = {}
    steps = len(data.y)
    for j, events in enumerate(data.events):
        rng = lie_rng(seed, fixture_ordinal, j)
        for start, kind in events:
            if kind.startswith('target_') or kind in ('drift_start', 'drift_end'):
                if rng.random() < LIE['miss']:
                    continue
                shifted = min(max(0, start+int(rng.integers(LIE['delay_lo'], LIE['delay_hi']+1))), steps-1)
                alarms[shifted, j] = 1.
                kinds[(shifted, j)] = 'delayed'
        realized = (rng.random(steps) < LIE['false']).astype(float)
        for t in np.flatnonzero(realized).tolist():
            alarms[t, j] = 1.
            kinds[(t, j)] = kinds.get((t, j), 'false')
    return alarms, kinds


def memory_metrics(data, result, arm, kinds):
    predictions, flags, norms, counts = result
    records = {}
    for j, coordinate in enumerate(data.coordinates):
        indices = np.flatnonzero(flags[:, j]).tolist()
        if arm in ('window', 'sgd', 'adwin'):
            raise ValueError('graded memory requires the graded arms')
        records[coordinate] = {'kind': 'graded', 'reset_count': len(indices),
            'resets': [{'index': t, 'kind': kinds.get((t, j), 'false')} for t in indices],
            'alarm_total': int(flags[:, j].sum()),
            'gain_levels': sorted(set(counts[:, j].tolist())),
            'events': []}
    return records


def single_memory(data, result, arm):
    predictions, flags, norms, widths, removed = result
    records = {}
    for j, coordinate in enumerate(data.coordinates):
        from study_v3_retention import window_record
        record = window_record(result[1][:, j], result[3][:, j], result[4][:, j], data.events[j])
        record['kind'] = 'window' if arm != 'sgd' else 'exponential'
        if arm == 'sgd':
            record.update(resets=[], reset_count=0)
            record.update({k: None for k in ('width_mean', 'width_min', 'width_max', 'width_final', 'total_discarded')})
        records[coordinate] = record
    return records


def simulation(seed, name, arm, config, alarm=None):
    data = observations(seed, name)
    if arm in ('window', 'sgd', 'adwin'):
        return data, run(data.y, arm, config)
    if arm == 'adwin_gated':
        if alarm is None:
            raise ValueError('generating control configuration required')
        alarms = adwin_run(data.y, alarm['delta'], alarm['clock'])[1]
        kinds = {}
        trues = sorted({t for ev in data.events for t, k in ev
                        if k.startswith('target_') or k in ('drift_start', 'drift_end')})
        for j in range(len(data.coordinates)):
            for t in np.flatnonzero(alarms[:, j]).tolist():
                kinds[(t, j)] = 'delayed' if any(t-8 <= s <= t for s in trues) else 'false'
        return data, (run(data.y, arm, config, alarms=alarms), kinds)
    alarms, kinds = build_lies(data, seed, FIXTURES.index(name))
    return data, (run(data.y, arm, config, alarms=alarms), kinds)


def measure_row(seed, arm, config, alarm=None, manifest=None):
    row = {'status': 'ok', 'config': config, 'privileged_timing': arm not in ('window', 'sgd', 'adwin'),
           'fixtures': {}, 'memory': {}}
    if manifest is not None:
        row['manifest_digest'] = digest(manifest)
    for name in FIXTURES:
        data, result = simulation(seed, name, arm, config, alarm)
        if arm in ('graded', 'adwin_gated'):
            result, kinds = result
        else:
            kinds = {}
        if not all(np.isfinite(np.asarray(x)).all() for x in result):
            return {**{k: v for k, v in row.items() if k not in ('fixtures', 'memory')},
                    'status': 'nonfinite', 'reason': name+' trajectory'}
        with np.errstate(over='ignore', invalid='ignore'):
            metrics = learning_metrics(data, *result[:3])
        if not finite(metrics):
            return {**{k: v for k, v in row.items() if k not in ('fixtures', 'memory')},
                    'status': 'nonfinite', 'reason': name+' metrics'}
        row['fixtures'][name] = metrics
        if arm in ('graded', 'adwin_gated'):
            row['memory'][name] = memory_metrics(data, result, arm, kinds)
        else:
            row['memory'][name] = single_memory(data, result, arm)
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
        if row.get('config') != expected or row.get('privileged_timing') is not (arm not in ('window', 'sgd', 'adwin')):
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
                             measure_row(s, a, c, alarm if a == 'adwin_gated' else None, manifest))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('stage', choices=('tune', 'confirm', 'report'))
    parser.add_argument('--directory', type=Path, default=DIRECTORY)
    args = parser.parse_args()
    if args.stage == 'report':
        from report_v4_robust import publish_report
        publish_report(args.directory)
    else:
        {'tune': tune, 'confirm': confirm}[args.stage](args.directory)


if __name__ == '__main__':
    main()
