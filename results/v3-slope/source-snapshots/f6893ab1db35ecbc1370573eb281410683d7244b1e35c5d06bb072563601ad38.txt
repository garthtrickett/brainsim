"""Frozen-candidate enriched schedule; drift boundaries granted alongside targets."""
import numpy as np

from v3_forgetting import run as forget_run
from v3_retention import FAST, dual_run, request_schedule

FAMILIES = ('window', 'sgd', 'adwin')
ARMS = FAMILIES + ('retain_drift', 'oracle_nofallback', 'random_drift')
FROZEN = {'delta': .1, 'H': 32}
GRIDS = {'window': [{'window': w} for w in (1, 2, 4, 8, 16, 32, 64, 128, 256, 512, 1024, 6000)],
         'sgd': [{'lr': lr} for lr in (.0001, .0004, .001, .004, .008, .016,
                                       .035743040182210514, .064, .128, .256, .512, 1.)],
         'adwin': [{'delta': d, 'clock': c} for d in (.0001, .001, .01, .1) for c in (1, 8, 32)]}


def random_uniforms(seed, fixture_ordinal, steps, width):
    return np.column_stack([np.random.default_rng(np.random.SeedSequence(
        [seed, 126000+fixture_ordinal, j])).random(steps) for j in range(width)])


def run(y, arm, config, *, schedule=None, uniforms=None, probability=None):
    y = np.asarray(y, dtype=np.float64)
    if y.ndim != 2 or not y.shape[0] or not y.shape[1] or not np.isfinite(y).all():
        raise ValueError('finite nonempty observations required')
    if arm not in ARMS:
        raise ValueError('unknown policy')
    if (schedule is not None or uniforms is not None) and arm in FAMILIES:
        raise ValueError('evaluator schedule forbidden for y-only controls')
    if arm in FAMILIES:
        return forget_run(y, arm, config)
    if arm == 'oracle_nofallback':
        if dict(config) != dict(FAST):
            raise ValueError('fixed fast base required')
        if schedule is None:
            raise ValueError('evaluator schedule required')
        schedule = np.asarray(schedule)
        if schedule.shape != y.shape or not np.isfinite(schedule).all() or np.any((schedule != 0) & (schedule != 1)):
            raise ValueError('binary evaluator schedule required')
        return forget_run(y, 'oracle_matched', dict(FAST), triggers=schedule)
    if dict(config) != dict(FROZEN):
        raise ValueError('frozen candidate configuration required')
    if arm == 'random_drift':
        uniforms = np.asarray(uniforms)
        if uniforms.shape != y.shape or not np.isfinite(uniforms).all() or np.any((uniforms < 0) | (uniforms >= 1)):
            raise ValueError('valid independent uniforms required')
        if probability is None or not np.isfinite(probability) or not 0 <= probability <= 1:
            raise ValueError('valid frozen probability required')
        resets = request_schedule((uniforms < probability).astype(float), 16)
    else:
        if schedule is None:
            raise ValueError('evaluator schedule required')
        schedule = np.asarray(schedule)
        if schedule.shape != y.shape or not np.isfinite(schedule).all() or np.any((schedule != 0) & (schedule != 1)):
            raise ValueError('binary evaluator schedule required')
        resets = schedule
    return dual_run(y, resets, FROZEN['delta'], FROZEN['H'])
