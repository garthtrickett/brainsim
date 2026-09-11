"""Registered budgets, complete-cell decisions and seed-level statistics."""
import hashlib
import json
import math

import numpy as np

from v3_slice1_learning import ARMS, GATED, GRIDS
from v3_slice1_streams import COORDINATES, SEEDS

PROTOCOL = {'id': 'v3-slice1-mean-20260909-v1',
            'registration_commit': '70f0449db3ecd7288773f8dcbf8547283ff1c7f6',
            'plan_commit': 'b05a41d6a898a2f87a9161d5f45aa94eb85c619d'}
REQUIRED = ('sgd', 'adam', 'single', 'candidate')
CONTROLS = ('sgd', 'adam', 'single', 'constant')
KEYS = {
    'tuning': {f'{a}/{i}/{s}' for a in ARMS for i in range(24) for s in SEEDS['tuning']},
    'calibration': {f'{a}/{s}' for a in GATED for s in SEEDS['calibration']},
    'diagnostics': {f'{a}/{s}' for a in GATED for s in SEEDS['diagnostics']},
    'performance': {f'{a}/{s}' for a in ARMS + ('constant',) for s in SEEDS['performance']},
}


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


def complete(rows, stage):
    if set(rows) != KEYS[stage] or not finite(rows):
        raise ValueError(f'incomplete/non-finite {stage} evidence')
    if any(row.get('status') not in ('ok', 'nonfinite') for row in rows.values()):
        raise ValueError(f'unknown {stage} row status')


def tuning_screen(rows):
    complete(rows, 'tuning')
    selected, objectives, reasons = {}, {}, []
    for arm in ARMS:
        objectives[arm] = []
        for i, config in enumerate(GRIDS[arm]):
            trials = [rows[f'{arm}/{i}/{s}'] for s in SEEDS['tuning']]
            value = None
            if all(row['status'] == 'ok' for row in trials):
                value = float(np.mean([row['metrics']['coordinates'][c]['excess_mse'] for row in trials
                                       for c in COORDINATES]))
            objectives[arm].append(value)
        valid = [i for i, x in enumerate(objectives[arm]) if x is not None]
        if not valid:
            reasons.append(f'{arm}: no complete finite configuration')
            continue
        index = min(valid, key=lambda i: objectives[arm][i])
        selected[arm] = GRIDS[arm][index]
        if arm in REQUIRED:
            rate = selected[arm]['lr']
            if rate in (GRIDS[arm][0]['lr'], GRIDS[arm][-1]['lr']):
                reasons.append(f'{arm}: selected learning rate {rate:g} is a search boundary')
            if selected[arm].get('gain') == 64.:
                reasons.append(f'{arm}: selected gain 64 is a search boundary')
    status = 'tuning_inconclusive' if reasons else 'eligible'
    if status == 'eligible' and selected['candidate']['gain'] == 0.:
        status = 'tuning_negative'
        reasons.append('candidate gain=0: tuning-only screen; no independent confirmation')
    return {'status': status, 'reasons': reasons, 'selected': selected, 'objectives': objectives}


def interval(values):
    values = np.asarray(values, dtype=float)
    if values.ndim != 1 or not len(values) or not np.isfinite(values).all():
        raise ValueError('finite seed values required')
    indices = np.random.default_rng(35000).integers(0, len(values), (10000, len(values)))
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


def detector_decision(rows):
    complete(rows, 'diagnostics')
    if any(rows[f'candidate/{s}']['status'] != 'ok' for s in SEEDS['diagnostics']):
        return {'status': 'detector_negative', 'reason': 'non-finite candidate trajectory', 'cells': {}}
    cells = {}
    for mode in ('fixed', 'closed'):
        for name in ('quiet', 'noisy'):
            metrics = [rows[f'candidate/{s}']['modes'][mode]['core'][name] for s in SEEDS['diagnostics']]
            if any(m['block_total'] != 50 for m in metrics):
                raise ValueError('wrong stationary denominator')
            cells[f'{mode}/{name}/blocks'] = detector_cell([m['block_count'] for m in metrics], [50] * 32)
        for name, fixture_name, kinds in (
                ('switch_quiet', 'core', ('target_down', 'target_up')),
                ('switch_noisy', 'core', ('target_down', 'target_up')),
                ('noise_jump', 'noise_jump', ('noise_increase', 'noise_decrease'))):
            for kind in kinds:
                counts, latencies = [], []
                for s in SEEDS['diagnostics']:
                    events = rows[f'candidate/{s}']['modes'][mode][fixture_name][name]['events']
                    event = [e for e in events if e['kind'] == kind]
                    if len(event) != 1:
                        raise ValueError('missing/duplicate required event')
                    counts.append(int(event[0]['hit']))
                    latencies.append(event[0]['latency'])
                cell = detector_cell(counts, [1] * 32, kind.startswith('target_'))
                cell['latency'] = float(np.mean(latencies))
                cell['latency_interval95'] = interval(latencies)
                cells[f'{mode}/{name}/{kind}'] = cell
    assert len(cells) == 16
    return {'status': 'detector_pass' if all(c['pass'] for c in cells.values()) else 'detector_negative',
            'cells': cells}


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


def performance_decision(rows):
    complete(rows, 'performance')
    required = ('candidate',) + CONTROLS
    if any(rows[f'{a}/{s}']['status'] != 'ok' for a in required for s in SEEDS['performance']):
        return {'status': 'learning_negative', 'reason': 'non-finite required trajectory', 'cells': {}}

    def values(arm, fixture_name, coordinates, field, window=None):
        result = []
        for seed in SEEDS['performance']:
            data = rows[f'{arm}/{seed}']['fixtures'][fixture_name]['coordinates']
            result.append(float(np.mean([data[c][field][window] if window else data[c][field]
                                         for c in coordinates])))
        return result

    specifications = [('primary', 'core', ('switch_quiet', 'switch_noisy'), 'post_mse', None, True)]
    specifications += [(c, 'core', (c,), 'post_mse' if c.startswith('switch_') else 'excess_mse', None, False)
                       for c in ('quiet', 'noisy', 'switch_quiet', 'switch_noisy')]
    for name in ('noise_jump', 'drift', 'exactly_quiet'):
        specifications.append((name, name, (name,), 'excess_mse', None, False))
    for window, name in [('noise_increase', 'noise_jump'), ('noise_decrease', 'noise_jump'), ('drift', 'drift')]:
        specifications.append((f'{name}/{window}', name, (name,), 'windows', window, False))
    cells = {}
    for control in CONTROLS:
        for label, name, coords, field, window, improvement in specifications:
            cells[f'{control}/{label}'] = contrast(values(control, name, coords, field, window),
                                                    values('candidate', name, coords, field, window), improvement)
    return {'status': 'positive' if all(c['pass'] for c in cells.values()) else 'learning_negative', 'cells': cells}


def expected_stages(status):
    if status in ('tuning_inconclusive', 'tuning_negative'):
        return ('tuning',)
    if status in ('detector_pass', 'detector_negative'):
        return ('tuning', 'calibration', 'diagnostics')
    if status in ('positive', 'learning_negative'):
        return tuple(KEYS)
    raise ValueError(f'not a closure disposition: {status}')
