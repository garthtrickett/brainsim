"""Run calibration/tuning, freeze selection, then run independent confirmation.

python study_v3_gate.py prepare
# Review/commit results/v3/selection.json before confirmation.
python study_v3_gate.py confirm
"""
import argparse
import hashlib
import json
from pathlib import Path

import numpy as np

from study_io import Evidence
from v3_gate import (ARM_IDS, BURN, CALIBRATION_SEEDS, CONFIRMATION_SEEDS,
                     DIAGNOSTIC, GRIDS, LEARNING, SWITCHES, TUNING_SEEDS,
                     block_maxima, diagnostic_metrics, fixed_gates,
                     learning_metrics, simulate, stream)

SOURCES = ['DESIGN-v3-gate.md', 'v3_gate.py', 'study_v3_gate.py', 'study_io.py']
PROTOCOL = 'v3-centered-gate-20260909-v1'


def scientific(value):
    """Remove only runtime measurements; preserve every scientific observation."""
    if isinstance(value, dict):
        return {k: scientific(v) for k, v in value.items() if k != 'seconds'}
    if isinstance(value, list):
        return [scientific(v) for v in value]
    return value


def digest_rows(data):
    return hashlib.sha256(json.dumps(scientific(data['rows']), sort_keys=True).encode()).hexdigest()


def calibration_row(seed):
    result = {}
    for condition in ('quiet', 'noisy'):
        values = fixed_gates(stream(seed, condition)[0])
        result[condition] = {
            arm: {'block_maxima': block_maxima(values[i, BURN:]).tolist(),
                  'gate_mean': float(values[i, BURN:].mean())}
            for i, arm in enumerate(('single', 'dual'))}
    return result


def learning_row(seed, arm, config):
    result = {}
    for condition in LEARNING:
        y, theta = stream(seed, condition)
        prediction, gate = simulate(y, ARM_IDS[arm], config['lr'],
                                    config.get('beta2', .999), config.get('gain', 0.))
        result[condition] = learning_metrics(y, theta, prediction, gate,
                                              condition.startswith('switch_'))
    return result


def selection_from(calibration, tuning):
    thresholds = {}
    for condition in ('quiet', 'noisy'):
        thresholds[condition] = {}
        for arm in ('single', 'dual'):
            blocks = [x for row in calibration['rows'].values()
                      for x in row[condition][arm]['block_maxima']]
            thresholds[condition][arm] = float(np.quantile(blocks, .99, method='higher'))
    selected, objectives = {}, {}
    for arm, configs in GRIDS.items():
        objectives[arm] = [float(np.mean([
            tuning['rows'][f'{arm}/{index}/{seed}'][condition]['excess_mse']
            for seed in TUNING_SEEDS for condition in LEARNING]))
            for index in range(len(configs))]
        selected[arm] = configs[int(np.argmin(objectives[arm]))]
    return {'protocol': PROTOCOL, 'thresholds': thresholds, 'selected': selected,
            'tuning_objectives': objectives, 'calibration_digest': digest_rows(calibration),
            'tuning_digest': digest_rows(tuning)}


def prepare(directory):
    calibration = Evidence(directory/'calibration.json', SOURCES, PROTOCOL + '/calibration')
    for seed in CALIBRATION_SEEDS:
        calibration.measure(str(seed), lambda seed=seed: calibration_row(seed))
    tuning = Evidence(directory/'tuning.json', SOURCES, PROTOCOL + '/tuning')
    for arm, configs in GRIDS.items():
        for index, config in enumerate(configs):
            for seed in TUNING_SEEDS:
                tuning.measure(f'{arm}/{index}/{seed}',
                               lambda seed=seed, arm=arm, config=config:
                               learning_row(seed, arm, config))
    selection = selection_from(calibration.data, tuning.data)
    path = directory/'selection.json'
    content = json.dumps(selection, indent=2) + '\n'
    if path.exists() and path.read_text() != content:
        raise ValueError('frozen selection differs; use a new evidence directory')
    temporary = path.with_suffix('.tmp')
    temporary.write_text(content)
    temporary.replace(path)
    print('FROZEN', json.dumps(selection['selected']), flush=True)
    print('Commit selection before first confirmation execution.', flush=True)


def diagnostic_row(seed, thresholds):
    result = {}
    for condition in DIAGNOSTIC:
        values = fixed_gates(stream(seed, condition)[0])
        regime = 'noisy' if 'noisy' in condition or condition == 'noise_jump' else 'quiet'
        events = SWITCHES if condition not in ('quiet', 'noisy') else ()
        result[condition] = {
            arm: diagnostic_metrics(values[i], thresholds[regime][arm], events)
            for i, arm in enumerate(('single', 'dual'))}
    return result


def confirm(directory):
    selection_path = directory/'selection.json'
    selection = json.loads(selection_path.read_text())
    calibration = json.loads((directory/'calibration.json').read_text())
    tuning = json.loads((directory/'tuning.json').read_text())
    if selection != selection_from(calibration, tuning):
        raise ValueError('selection does not match calibration/tuning')
    sources = SOURCES + [str(selection_path)]
    diagnostic = Evidence(directory/'diagnostic.json', sources, PROTOCOL + '/diagnostic')
    for seed in CONFIRMATION_SEEDS:
        diagnostic.measure(str(seed), lambda seed=seed:
                           diagnostic_row(seed, selection['thresholds']))
    learning = Evidence(directory/'confirmation.json', sources, PROTOCOL + '/confirmation')
    for arm, config in selection['selected'].items():
        for seed in CONFIRMATION_SEEDS:
            learning.measure(f'{arm}/{seed}', lambda seed=seed, arm=arm, config=config:
                             learning_row(seed, arm, config))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('stage', choices=('prepare', 'confirm'))
    parser.add_argument('--out-dir', type=Path, default=Path('results/v3'))
    args = parser.parse_args()
    # Compile outside recorded per-row timings, warming each compiled path.
    for arm in ARM_IDS.values():
        simulate(np.array([1., 2.]), arm, .01, .999, 1.)
    fixed_gates(np.array([1., 2.]))
    if args.stage == 'prepare':
        prepare(args.out_dir)
    else:
        confirm(args.out_dir)


if __name__ == '__main__':
    main()
