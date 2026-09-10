"""Frozen finite menus, tuning objective and complete independent comparison gates."""
import numpy as np

from v3_burst import ARMS, FAMILIES, GRIDS, START, random_probability
from v3_slice1_decisions import digest, finite, scientific

PROTOCOL = {'id': 'v3-burst-20260909-v1',
            'registration_commit': '1c45603b7c7e7ad3d44c4a3ba822d95b7bac05c5',
            'registration_sha256': 'ef249ae9dcf9afe8822ee2c0f188f2e780596450b7fcc6881028191b3e8a4d5c'}
SEEDS = {'development': tuple(range(70000, 70008)), 'tuning': tuple(range(71000, 71008)),
         'confirmation': tuple(range(73000, 73032))}
KEYS = {'tuning': {f'{a}/{i}/{s}' for a in FAMILIES for i in range(12) for s in SEEDS['tuning']},
        'confirmation': {f'{a}/{s}' for a in ARMS for s in SEEDS['confirmation']}}
CONTROLS = ('adam', 'sgd', 'continuous', 'random')
SPECS = [('primary', [('core', c, 'post_mse', None) for c in ('switch_quiet', 'switch_noisy')] +
                      [('mixed', c, 'post_mse', None) for c in ('increase_first', 'decrease_first')])]
SPECS += [(c, [('core', c, 'post_mse' if c.startswith('switch_') else 'excess_mse', None)])
          for c in ('quiet', 'noisy', 'switch_quiet', 'switch_noisy')]
SPECS += [(c, [(c, c, 'excess_mse', None)]) for c in ('noise_jump', 'drift', 'exactly_quiet')]
SPECS += [(f'{n}/{w}', [(n, n, 'windows', w)]) for n, w in
          (('noise_jump', 'noise_increase'), ('noise_jump', 'noise_decrease'), ('drift', 'drift'))]
SPECS += [(f'mixed/{c}/{f}', [('mixed', c, f, None)]) for c in ('increase_first', 'decrease_first')
          for f in ('post_mse', 'stable_mse')]


def complete(rows, stage):
    if set(rows) != KEYS[stage] or not finite(rows):
        raise ValueError('incomplete/non-finite '+stage)
    if any(r.get('status') not in ('ok', 'nonfinite') for r in rows.values()):
        raise ValueError('unknown row status')


def metric_values(row):
    result = {}
    for label, fields in SPECS:
        values = [row['fixtures'][n]['coordinates'][c][f][w] if w else
                  row['fixtures'][n]['coordinates'][c][f] for n, c, f, w in fields]
        if any(type(v) not in (int, float) or not np.isfinite(v) or v < 0 for v in values):
            raise ValueError('invalid learning metric')
        result[label] = float(np.mean(values))
    return result


def objective(row):
    values = metric_values(row)
    return .5*(values['primary']+np.mean([values[k] for k, _ in SPECS[1:]]))


def select(rows):
    complete(rows, 'tuning')
    selected, indices, scores, reasons = {}, {}, {}, []
    for arm in FAMILIES:
        scores[arm] = []
        for i in range(12):
            trials = [rows[f'{arm}/{i}/{s}'] for s in SEEDS['tuning']]
            scores[arm].append(float(np.mean([objective(r) for r in trials]))
                               if all(r['status'] == 'ok' for r in trials) else None)
        valid = [i for i, score in enumerate(scores[arm]) if score is not None]
        if not valid:
            reasons.append(arm+': no finite complete configuration')
            continue
        index = min(valid, key=lambda i: scores[arm][i])
        selected[arm], indices[arm] = dict(GRIDS[arm][index]), index
    result = {'status': 'tuning_inconclusive' if reasons else 'eligible', 'reasons': reasons,
              'selected': selected, 'indices': indices, 'objectives': scores}
    if not reasons:
        chosen = [rows[f'burst/{indices["burst"]}/{s}'] for s in SEEDS['tuning']]
        counts = [r['activity'][n][c]['start_count'] for r in chosen for n in r['activity'] for c in r['activity'][n]]
        if len(counts) != 9*8 or any(type(c) is not int or c < 0 for c in counts):
            raise ValueError('incomplete burst frequency evidence')
        count, opportunities = sum(counts), (6000-START)*9*8
        result['random_frequency'] = {'starts': count, 'coordinate_time': opportunities,
                                      'probability': random_probability(count, opportunities, selected['burst']['duration'])}
        selected['oracle_matched'] = dict(selected['burst'])
        selected['random'] = dict(selected['burst'])
    return result


def interval(values):
    values = np.asarray(values, dtype=float)
    if values.ndim != 1 or not len(values) or not np.isfinite(values).all():
        raise ValueError('finite seed values required')
    indices = np.random.default_rng(75000).integers(0, len(values), (10000, len(values)))
    return np.quantile(values[indices].mean(axis=1), [.025, .975]).tolist()


def contrast(control, candidate, improvement):
    control, candidate = np.asarray(control), np.asarray(candidate)
    if control.shape != candidate.shape or control.ndim != 1 or not len(control) or not np.isfinite(control).all() or not np.isfinite(candidate).all():
        raise ValueError('finite paired samples required')
    delta = candidate-control
    bounds, allowed = interval(delta), max(.002, .1*float(control.mean()))
    passed = (candidate.mean() <= .9*control.mean() and bounds[1] < 0) if improvement else bounds[1] <= allowed
    return {'control': float(control.mean()), 'candidate': float(candidate.mean()),
            'delta': float(delta.mean()), 'interval95': bounds, 'allowed': allowed, 'pass': bool(passed)}


def performance_decision(rows, candidate='burst'):
    complete(rows, 'confirmation')
    if candidate not in ('burst', 'oracle', 'oracle_matched'):
        raise ValueError('invalid candidate')
    controls = CONTROLS if candidate == 'burst' else ('adam', 'sgd')
    prefix = 'learning' if candidate == 'burst' else 'oracle'
    if any(rows[f'{a}/{s}']['status'] != 'ok' for a in (candidate,)+controls for s in SEEDS['confirmation']):
        return {'status': prefix+'_negative', 'reason': 'non-finite required trajectory', 'cells': {}}
    metrics = {a: [metric_values(rows[f'{a}/{s}']) for s in SEEDS['confirmation']] for a in (candidate,)+controls}
    cells = {f'{a}/{k}': contrast([m[k] for m in metrics[a]], [m[k] for m in metrics[candidate]], k == 'primary')
             for a in controls for k, _ in SPECS}
    status = ('learning_positive' if candidate == 'burst' else 'oracle_pass') if all(c['pass'] for c in cells.values()) else prefix+'_negative'
    return {'status': status, 'cells': cells}


def detector_decision(rows):
    """Twelve raw signal cells, explanatory only; no duplicate observer/learner copy."""
    complete(rows, 'confirmation')
    if any(rows[f'burst/{s}']['status'] != 'ok' for s in SEEDS['confirmation']):
        return {'status': 'detector_negative', 'cells': {}, 'reason': 'non-finite candidate'}
    specs = [('core', c, None, False) for c in ('quiet', 'noisy')]
    specs += [(n, c, k, k.startswith('target_')) for n, coords, kinds in (
        ('core', ('switch_quiet', 'switch_noisy'), ('target_down', 'target_up')),
        ('mixed', ('increase_first', 'decrease_first'), ('target_down', 'target_up')),
        ('noise_jump', ('noise_jump',), ('noise_increase', 'noise_decrease')))
        for c in coords for k in kinds]
    cells = {}
    for name, coord, kind, minimum in specs:
        counts, latencies = [], []
        for seed in SEEDS['confirmation']:
            metric = rows[f'burst/{seed}']['detector'][name][coord]
            if kind is None:
                if metric['block_total'] != 50 or type(metric['block_count']) is not int or not 0 <= metric['block_count'] <= 50:
                    raise ValueError('invalid block counts')
                counts.append(metric['block_count'])
            else:
                events = [e for e in metric['events'] if e['kind'] == kind]
                if len(events) != 1:
                    raise ValueError('missing/duplicate detector event')
                event = events[0]
                if type(event['hit']) is not bool or type(event['latency']) is not int or not (
                        0 <= event['latency'] < 100 if event['hit'] else event['latency'] == 100):
                    raise ValueError('invalid detector event')
                counts.append(int(event['hit'])); latencies.append(event['latency'])
        denominator = 50 if kind is None else 1
        values = np.array(counts)/denominator
        cell = {'count': sum(counts), 'total': denominator*32, 'rate': float(values.mean()),
                'interval95': interval(values), 'pass': bool(values.mean() >= .8 if minimum else values.mean() <= .05)}
        if latencies:
            cell.update(latency=float(np.mean(latencies)), latency_interval95=interval(latencies))
        cells[f'{name}/{coord}/{kind or "blocks"}'] = cell
    return {'status': 'detector_pass' if all(c['pass'] for c in cells.values()) else 'detector_negative', 'cells': cells}
