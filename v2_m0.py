"""M0-motor prototype: per-tick 1-of-N actions with no vote aggregate.

Throwaway harness, explicitly not the v2 fork. The MotorWTA step mirrors the
frozen BrainSim.step line-for-line except the motor block (single winner
above threshold, silence otherwise); every other state update is identical
code through shared constants. All three arms share trial structure (30
ticks, one reward, consume-on-reward): only action selection differs.
"""
import numpy as np

from brainsim import BrainSim

TICKS = 30
TRIALS = 3000
CLASSES = (4, 8)
SEEDS = tuple(range(310, 316))


class MotorWTA(BrainSim):
    """1-of-N motor layer; per-tick winners, votes kept for the aggregate arm."""

    def step(self, x):
        self.ticks += 1
        si = (self.rng.random(self.n_in) < 0.6 * x).astype(float)
        if self.TRANSMISSION_FAILURE:
            mask = self.transmission_rng.random(self.W_out.shape) >= self.TRANSMISSION_FAILURE
            signal = (self.W_out * mask) @ self.fh
        else:
            signal = self.W_out @ self.fh
        drive = self.TRANSMISSION_GAIN * signal + self.rng.normal(0, self.noise_eff, self.n_motor)
        if self.WM:
            n2 = float(self.trh @ self.trh)
            resid = self.wm - (float(self.wm @ self.trh) / n2) * self.trh if n2 > 1e-9 else self.wm
            self._wm_eff = resid
            drive = drive + self.WM_BETA * (self.W_wm @ resid)
        if self.PERSIST:
            drive += self.SELF_EXC * self.trm - self.INHIB * self.trm.mean()
        self.vm = self.vm * self.LEAK + drive
        fm = np.zeros(self.n_motor)
        if self.vm.max() > 1.0:
            fm[int(np.argmax(self.vm))] = 1.0
        self.vm[fm > 0] = 0
        self.trm = self.trm * self.TRM_D + fm
        self.vh = self.vh * self.LEAK + self.W_in @ si
        if self.POOLS != 1:
            self._validate_pools()
            self.fh = np.zeros(self.n_hidden)
            kp = self.k // self.POOLS
            for p in range(self.POOLS):
                lo = p * self.n_hidden // self.POOLS
                hi = (p + 1) * self.n_hidden // self.POOLS
                v = self.vh[lo:hi]
                thr = np.partition(v, -kp)[-kp]
                self.fh[lo:hi] = (v >= thr) & (v > self.thresh[lo:hi])
        else:
            thr = np.partition(self.vh, -self.k)[-self.k]
            self.fh = ((self.vh >= thr) & (self.vh > self.thresh)).astype(float)
        self.vh[self.fh > 0] = 0
        self.trh = self.trh * self.TRACE_D + self.fh
        if self.WM:
            if self.WM_GATE == "capacity":
                g = max(0.0, 1.0 - float(np.linalg.norm(self.wm)) / self.WM_CAP)
            elif self.WM_GATE == "change":
                g = 1.0 if float(np.abs(self.fh - self._prev_fh).sum()) > 2 else 0.0
            else:
                g = 1.0
            self.wm = self.wm * self.WM_DECAY + self.WM_LR * g * self.fh
            self._prev_fh = self.fh.copy()
            self.wm_sum += getattr(self, "_wm_eff", self.wm)
            self.wm_n += 1
        self.trh_sum += self.trh
        self.trh_n += 1
        if self.TAGGATE:
            m = self.trm.max()
            gate = (self.trm >= self.THETA * m).astype(float) if m > 0 else np.ones(self.n_motor)
        else:
            gate = 1.0
        self.elig = self.elig * self.ELIG_D + (1 - self.ELIG_D) * np.outer(fm * gate, self.trh)
        self.elig_w = self.elig_w * self.ELIG_D + (1 - self.ELIG_D)
        self.votes += fm
        self.rate += 0.001 * (self.fh - self.rate)
        self.thresh += self.ETA_TH * (self.rate - self.TARGET_RATE)
        np.clip(self.thresh, 0.05, 20.0, out=self.thresh)
        if self.ticks % self.SCALE_EVERY == 0:
            cur = np.abs(self.W_out).sum(axis=1)
            scale = np.where(cur > 1e-9, self._out_budget / np.maximum(cur, 1e-9), 1.0)
            self.W_out *= scale[:, None]
        return fm


def patterns(ncls, seed, density=0.30):
    rng = np.random.default_rng(seed)
    return [(rng.random(40) < density).astype(float) for _ in range(ncls)]


def run_trial(agent, pats, trials, per_tick):
    """One run. Per-tick arm: winners scored per tick, plurality credited.
    Aggregate arms: decide() per trial, action broadcast for scoring."""
    correct, winners = [], []
    for i in range(trials):
        tick_actions = []
        for _ in range(TICKS):
            fm = agent.step(pats[i % len(pats)])
            tick_actions.append(int(fm.argmax()) if fm.sum() > 0 else -1)
        if per_tick:
            counts = np.bincount([a for a in tick_actions if a >= 0], minlength=len(pats))
            action = int(counts.argmax()) if counts.sum() > 0 else int(tick_actions[-1] if tick_actions[-1] >= 0 else 0)
            reward = float(np.mean([a == i % len(pats) for a in tick_actions if a >= 0] or [0.0]))
        else:
            action = agent.decide()
            reward = float(action == i % len(pats))
            tick_actions = [action]*TICKS
        agent.reward(reward, action=action, done=True)
        correct.extend([a == i % len(pats) for a in tick_actions])
        winners.extend(tick_actions)
    return np.array(correct, dtype=float), np.array(winners, dtype=int)


def run_arm(arm, ncls, seed, trials=TRIALS):
    if arm not in ('pertick', 'aggregate', 'shipped'):
        raise ValueError('unknown policy')
    pats = patterns(ncls, seed)
    if arm == 'shipped':
        agent = BrainSim(n_motor=ncls, seed=seed)
        return run_trial(agent, pats, trials, per_tick=False)
    agent = MotorWTA(n_motor=ncls, seed=seed)
    return run_trial(agent, pats, trials, per_tick=(arm == 'pertick'))
