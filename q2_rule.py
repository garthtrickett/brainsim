"""Q2 consumption-rule harness (subclass fork; v1 sources frozen).

Experiment-41 mechanism with the full reward signature: the chosen rule
restores a kept fraction of the cashed trace after super().reward()
(which zeroes it). Modes: full (keep 0, shipped), none (keep all --
decay alone), proportional (keep 1-min(1,|RPE|)). Tau rides ELIG_D via
the setattr seam. Study pins shipped defaults otherwise; in particular
PGATE stays "off", under which super().reward() always consumes, so the
restore-after-return is exact.
"""
from brainsim import BrainSim
from fastsim import FastBrainSim

RULES = ('full', 'none', 'proportional')
TAUS = {100: 0.99, 200: 0.995, 400: 0.9975}


class Rule(BrainSim):
    MODE = 'full'

    def reward(self, r, action=None, done=True, policy_bonus=0.0, switch=False):
        if self.MODE == 'full':
            super().reward(r, action=action, done=done,
                           policy_bonus=policy_bonus, switch=switch)
            return
        self._saved = self.elig.copy()
        self._saved_w = self.elig_w
        if self.MODE == 'none':
            keep = 1.0
        elif self.MODE == 'proportional':
            zbar = self.trh_sum / max(self.trh_n, 1)
            nm = abs(r - float(self.w_v @ zbar))
            keep = float(max(0.0, 1.0 - min(1.0, nm)))
        else:
            raise ValueError(f'unknown consumption rule {self.MODE}')
        super().reward(r, action=action, done=done,
                       policy_bonus=policy_bonus, switch=switch)
        self.elig[:] = self._saved * keep
        self.elig_w = self._saved_w * keep


class FastRule(FastBrainSim, Rule):
    """Buffered steps + shared numba kernel (FastBrainSim) with the
    consumption-rule reward (Rule). MRO: flush/observe/decide from
    FastBrainSim, reward resolves to Rule.reward. The kernel never sees
    modes -- restore happens at reward time in Python on the same arrays
    the kernel mutates in place. No new code by design."""
