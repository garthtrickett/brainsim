"""Registered persistent-detector gates; fixed policies and complete seed partitions."""
import hashlib
import json
import math

import numpy as np

from v3_persistent import CONFIGS, DETECTORS

PROTOCOL = {'id': 'v3-persistent-20260909-v1',
            'registration_commit': 'fc78d253bd3101b5a8d804f111cf89fe1a423f79',
            'registration_sha256': '6c64064ce2aa347379b55bf21218ffbecd4ffb3a23d7c7fd946802d9e7962daa'}
SEEDS = {'development': tuple(range(50000, 50008)), 'calibration': tuple(range(51000, 51016)),
         'diagnostics': tuple(range(53000, 53032)), 'performance': tuple(range(54000, 54032))}
CONTROLS = tuple(a for a in CONFIGS if a != 'candidate')
KEYS = {stage: {f'{a}/{s}' for a in (CONFIGS if stage == 'performance' else DETECTORS)
                for s in SEEDS[stage]} for stage in ('calibration', 'diagnostics', 'performance')}


def complete(rows, stage):
    if set(rows) != KEYS[stage] or not finite(rows):
        raise ValueError('incomplete/non-finite ' + stage)
    if any(r.get('status') not in ('ok', 'nonfinite') for r in rows.values()):
        raise ValueError('unknown row status')


def scientific(value):
    if isinstance(value, dict):
        return {k: scientific(v) for k, v in value.items() if k not in ('seconds', 'elapsed_seconds')}
    if isinstance(value, list):
        return [scientific(v) for v in value]
    return value


def digest(value):
    return hashlib.sha256(json.dumps(scientific(value), sort_keys=True, allow_nan=False).encode()).hexdigest()


def finite(value):
    if isinstance(value, dict):
        return all(finite(v) for v in value.values())
    if isinstance(value, list):
        return all(finite(v) for v in value)
    return not isinstance(value, float) or math.isfinite(value)


def interval(values):
    values = np.asarray(values, dtype=float)
    if values.ndim != 1 or not len(values) or not np.isfinite(values).all():
        raise ValueError('finite seed values required')
    indices = np.random.default_rng(55000).integers(0, len(values), (10000, len(values)))
    return np.quantile(values[indices].mean(axis=1), [.025, .975]).tolist()


def detector_cell(counts, denominators, minimum=False):
    if not counts or len(counts) != len(denominators):
        raise ValueError('complete detector counts required')
    if any(not np.isfinite(c) or not np.isfinite(d) or d <= 0 or c < 0 or c > d
           for c, d in zip(counts, denominators)):
        raise ValueError('invalid detector counts')
    values = np.array(counts) / np.array(denominators)
    mean = float(values.mean())
    return {'count': int(sum(counts)), 'total': int(sum(denominators)),
            'rate': mean, 'interval95': interval(values),
            'pass': bool(mean >= .8 if minimum else mean <= .05)}


def contrast(control, candidate, improvement):
    control, candidate = np.asarray(control), np.asarray(candidate)
    if control.shape != candidate.shape or not np.isfinite(control).all() or not np.isfinite(candidate).all():
        raise ValueError('finite paired samples required')
    delta = candidate - control
    bounds = interval(delta)
    allowed = max(.002, .1 * float(control.mean()))
    passed = (candidate.mean() <= .9 * control.mean() and bounds[1] < 0.) if improvement else bounds[1] <= allowed
    return {'control': float(control.mean()), 'candidate': float(candidate.mean()),
            'delta': float(delta.mean()), 'interval95': bounds, 'allowed': allowed,
            'pass': bool(passed)}


def detector_decision(rows, arm='candidate'):
    complete(rows, 'diagnostics')
    if arm not in DETECTORS:
        raise ValueError('unknown detector')
    if any(rows[f'{arm}/{s}']['status'] != 'ok' for s in SEEDS['diagnostics']):
        return {'status': 'detector_negative', 'reason': 'non-finite trajectory', 'cells': {}}
    cells = {}
    specs = [('core', c, ('target_down', 'target_up'), True) for c in ('switch_quiet', 'switch_noisy')]
    specs += [('noise_jump', 'noise_jump', ('noise_increase', 'noise_decrease'), False)]
    specs += [('mixed', c, ('target_down', 'target_up'), True) for c in ('increase_first', 'decrease_first')]
    for mode in ('fixed', 'closed'):
        for coord in ('quiet', 'noisy'):
            metrics = [rows[f'{arm}/{s}']['modes'][mode]['core'][coord] for s in SEEDS['diagnostics']]
            if any(m['block_total'] != 50 or type(m['block_count']) is not int for m in metrics):
                raise ValueError('invalid stationary counts')
            cells[f'{mode}/{coord}/blocks'] = detector_cell([m['block_count'] for m in metrics], [50]*32)
        for name, coord, kinds, detection in specs:
            for kind in kinds:
                counts, latencies = [], []
                for seed in SEEDS['diagnostics']:
                    events = rows[f'{arm}/{seed}']['modes'][mode][name][coord]['events']
                    matches = [e for e in events if e['kind'] == kind]
                    if len(matches) != 1:
                        raise ValueError('missing/duplicate event')
                    event = matches[0]
                    if type(event['hit']) is not bool or type(event['latency']) is not int or not (
                            0 <= event['latency'] < 100 if event['hit'] else event['latency'] == 100):
                        raise ValueError('invalid event hit/latency')
                    counts.append(int(event['hit'])); latencies.append(event['latency'])
                cell = detector_cell(counts, [1]*32, detection)
                cell.update(latency=float(np.mean(latencies)), latency_interval95=interval(latencies))
                cells[f'{mode}/{coord}/{kind}'] = cell
    assert len(cells) == 24
    return {'status': 'detector_pass' if all(c['pass'] for c in cells.values()) else 'detector_negative',
            'cells': cells}


def performance_decision(rows):
    complete(rows, 'performance')
    if any(r['status'] != 'ok' for r in rows.values()):
        return {'status': 'learning_negative', 'reason': 'non-finite required trajectory', 'cells': {}}
    specs = [('primary', [('core', c, 'post_mse', None) for c in ('switch_quiet', 'switch_noisy')] +
                         [('mixed', c, 'post_mse', None) for c in ('increase_first', 'decrease_first')], True)]
    specs += [(c, [('core', c, 'post_mse' if c.startswith('switch_') else 'excess_mse', None)], False)
              for c in ('quiet', 'noisy', 'switch_quiet', 'switch_noisy')]
    specs += [(c, [(c, c, 'excess_mse', None)], False) for c in ('noise_jump', 'drift', 'exactly_quiet')]
    specs += [(f'{n}/{w}', [(n, n, 'windows', w)], False) for n, w in
              (('noise_jump', 'noise_increase'), ('noise_jump', 'noise_decrease'), ('drift', 'drift'))]
    specs += [(f'mixed/{c}/{field}', [('mixed', c, field, None)], False)
              for c in ('increase_first', 'decrease_first') for field in ('post_mse', 'stable_mse')]

    def values(arm, fields):
        result = []
        for seed in SEEDS['performance']:
            data = rows[f'{arm}/{seed}']['fixtures']
            result.append(float(np.mean([data[n]['coordinates'][c][f][w] if w else
                                         data[n]['coordinates'][c][f] for n, c, f, w in fields])))
        return result

    cells = {f'{arm}/{label}': contrast(values(arm, fields), values('candidate', fields), improvement)
             for arm in CONTROLS for label, fields, improvement in specs}
    assert len(cells) == 105
    return {'status': 'positive' if all(c['pass'] for c in cells.values()) else 'learning_negative', 'cells': cells}
