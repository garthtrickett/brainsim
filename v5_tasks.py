"""Noisy-volatile tasks: Volatile with stationary observation noise.

tasks.py stays frozen; this module wraps it. The wrapper draws only from its
own noise RNG, so the base task's RNG — patterns and permutation schedule —
is bit-identical to the plain Volatile at equal seeds.
"""
import numpy as np

import tasks


class NoisyVolatile:
    """N-way whose mapping permutes every `switch_every` trials, seen through
    Gaussian observation noise. Tests the noise/change contrast: stationary
    noise must not fire change responses, permutations must."""

    def __init__(self, n=4, switch_every=300, sigma=0.25, seed=0):
        self.base = tasks.Volatile(n, switch_every, seed=seed)
        self.sigma = float(sigma)
        if not self.sigma >= 0:
            raise ValueError('nonnegative noise required')
        self.noise_rng = np.random.default_rng([seed, 5000+int(round(self.sigma*100))])
        self.n_actions = self.base.n_actions
        self.switch_every = self.base.switch_every
        self.name = f"noisy-volatile-{n}@{switch_every}s{sigma:g}"

    def _noisy(self, obs):
        if self.sigma == 0:
            return obs
        return obs+self.noise_rng.normal(0., self.sigma, obs.shape)

    def reset(self, rng):
        return self._noisy(self.base.reset(rng))

    def step(self, a):
        obs, reward, done = self.base.step(a)
        return self._noisy(obs), reward, done

    def correct(self):
        return self.base.correct()

    def switch_points(self, decisions):
        return list(range(self.switch_every, decisions, self.switch_every))
