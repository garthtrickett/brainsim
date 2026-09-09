"""Causal bounded-rate controllers; true event metadata belongs to the evaluator."""
import numpy as np
from numba import njit

from v3_persistent import run as detector_run
from v3_reference import controlled_adam
from v3_slice1_learning import run as plain_run

THRESHOLD = .4690234346011377
START, QUIET = 146, 16
FAMILIES = ('burst', 'oracle', 'continuous', 'adam', 'sgd')
ARMS = FAMILIES + ('oracle_matched', 'random')
BURSTS = [{'lr': lr, 'factor': factor, 'duration': duration, 'beta2': .999}
          for lr in (.004, .016, .032) for factor in (2., 8.) for duration in (16, 64)]
GRIDS = {'burst': BURSTS, 'oracle': [dict(c) for c in BURSTS],
         'continuous': [{'lr': lr, 'gain': gain, 'beta2': .999}
                        for lr in (.004, .016, .032) for gain in (0., 8., 32., 64.)],
         'adam': [{'lr': lr, 'beta2': beta2} for lr in (.001, .004, .016, .032, .064, .128)
                  for beta2 in (.999, .9999)],
         'sgd': [{'lr': lr} for lr in (.0001, .0004, .001, .004, .008, .016,
                                     .035743040182210514, .064, .128, .256, .512, 1.)]}


def reference_gates(y):
    return detector_run(y, 'candidate', observer=True)[1]


@njit(cache=True)
def pulse_schedule(signal, duration, detected):
    """Detected q needs quiet rearming; external triggers need a fixed cooldown."""
    active, starts = np.zeros_like(signal), np.zeros_like(signal)
    for j in range(signal.shape[1]):
        remaining, quiet, cooldown = 0, 0, 0
        armed = True
        for t in range(START, len(signal)):
            if remaining:
                active[t, j] = 1.
                remaining -= 1
                continue
            if detected:
                if not armed:
                    quiet = quiet+1 if signal[t, j] <= THRESHOLD else 0
                    if quiet == QUIET:
                        armed = True
                    continue
                trigger = signal[t, j] > THRESHOLD
            else:
                if cooldown:
                    cooldown -= 1
                    continue
                trigger = signal[t, j] > 0.
            if trigger:
                active[t, j] = starts[t, j] = 1.
                remaining = duration-1
                armed, quiet, cooldown = False, 0, QUIET
    return active, starts


def random_uniforms(seed, fixture_ordinal, steps, width):
    return np.column_stack([np.random.default_rng(np.random.SeedSequence(
        [seed, 76000+fixture_ordinal, j])).random(steps) for j in range(width)])


def random_probability(starts, opportunities, duration):
    if type(starts) is not int or type(opportunities) is not int or starts < 0 or opportunities <= 0:
        raise ValueError('invalid frequency counts')
    f = starts/opportunities
    denominator = 1.-f*(duration+QUIET-1)
    if denominator <= 0:
        raise ValueError('invalid renewal frequency')
    p = f/denominator
    if not np.isfinite(p) or not 0. <= p <= 1.:
        raise ValueError('invalid renewal probability')
    return p


def run(y, arm, config, *, gates=None, triggers=None, uniforms=None, probability=None):
    """Only evaluator-owned oracle arms accept privileged trigger arrays."""
    y = np.asarray(y, dtype=np.float64)
    if y.ndim != 2 or not y.shape[0] or not y.shape[1] or not np.isfinite(y).all():
        raise ValueError('finite nonempty observations required')
    if arm not in ARMS or not np.isfinite(list(config.values())).all() or config['lr'] <= 0:
        raise ValueError('invalid arm/configuration')
    if arm not in ('oracle', 'oracle_matched') and triggers is not None:
        raise ValueError('privileged triggers forbidden for deployable arms')
    zero = np.zeros_like(y)
    if arm in ('adam', 'sgd'):
        return (*plain_run(y, arm, config), zero)
    if arm in ('burst', 'continuous'):
        gates = reference_gates(y) if gates is None else np.asarray(gates, dtype=float)
        if gates.shape != y.shape or not np.isfinite(gates).all() or np.any((gates < 0) | (gates > 1)):
            raise ValueError('invalid causal reference gates')
    if arm == 'continuous':
        return (*controlled_adam(y, gates, config['lr'], config['gain'], config['beta2']), zero)
    duration = config['duration']
    if type(duration) is not int or duration < 1 or config['factor'] < 1:
        raise ValueError('invalid burst duration/factor')
    if arm == 'burst':
        active, starts = pulse_schedule(gates, duration, True)
    else:
        if arm == 'random':
            uniforms = np.asarray(uniforms)
            if uniforms.shape != y.shape or not np.isfinite(uniforms).all() or np.any((uniforms < 0) | (uniforms >= 1)):
                raise ValueError('valid independent uniforms required')
            if probability is None or not np.isfinite(probability) or not 0 <= probability <= 1:
                raise ValueError('frozen random probability required')
            signal = (uniforms < probability).astype(float)
        else:
            signal = np.asarray(triggers)
            if signal.shape != y.shape or not np.isfinite(signal).all() or np.any((signal != 0) & (signal != 1)):
                raise ValueError('binary evaluator oracle triggers required')
        active, starts = pulse_schedule(signal, duration, False)
    return (*controlled_adam(y, active, config['lr'], config['factor']-1., config['beta2']), starts)
