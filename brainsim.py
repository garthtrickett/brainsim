"""
brainsim -- the mainline design.

Carries only what survived testing. Every non-obvious constant cites the
experiment that set it. Components that were proposed and FAILED are absent,
and named at the bottom so they don't get re-proposed.
"""
import numpy as np


class BrainSim:
    # ---- constants, each traceable to an experiment -------------------------
    LEAK      = 0.85     # membrane, ~20ms
    TRACE_D   = 0.80     # spike trace, ~50ms
    ELIG_D    = 0.995    # 09: tau~200. A tau~10 trace collapses to chance as
                         # soon as anything fills the action->reward gap.
    VALUE_LR  = 0.02     # 02: RPE baseline. Raw reward instead => chance.
    EBAR_LR   = 0.05     # 02: credit the deviation, not the habit (1.00 vs 0.82)
    NOISE     = 0.35     # 02: exploration. Remove it => chance.
    LR        = 0.05
    WMAX      = 1.0
    # 01 validated threshold homeostasis at a 1% target -- on a RECURRENT net
    # with no k-WTA. Here competition forces exactly k/n cells to fire, so a 1%
    # target is a rate competition structurally forbids: the controller ratchets
    # thresholds up forever (1.00 -> 6.42) and accuracy sits at 0.58. The target
    # is set from k/n in __init__. A constant is only valid in the architecture
    # it was measured in.
    ETA_TH    = 0.02
    SCALE_EVERY = 1000   # 06: NOT 100. The two homeostatic controllers need ~10x
                         # separation or they fight (rate dips to 0.0080 by 60k).
    SLEEP_EVERY = 50     # 13: sleep cadence, in decisions
    SLEEP_REPLAY = 60    # 13: replayed episodes per sleep
    SLEEP_ETA = 0.05     # 13: gradient step size inside sleep
    DOWNSCALE = 0.98     # step 9: shrink all, preserve the order

    def __init__(self, n_in=40, n_hidden=80, n_motor=2, k=6, seed=0):
        self.rng = np.random.default_rng(seed)
        self.n_in, self.n_hidden, self.n_motor, self.k = n_in, n_hidden, n_motor, k
        r = self.rng
        self.W_in  = (r.random((n_hidden, n_in)) < 0.25) * r.random((n_hidden, n_in)) * 1.2
        self.W_out = np.full((n_motor, n_hidden), 0.25)
        self.thresh = np.ones(n_hidden)
        self._reset_dynamics()
        self.ebar  = np.zeros((n_motor, n_hidden))
        self.elig  = np.zeros((n_motor, n_hidden))
        self.elig_w = 0.0   # accumulated EMA weight; see reward()
        self.value = 0.0
        self.rate  = np.zeros(n_hidden)
        self.TARGET_RATE = k / n_hidden   # NOT the 0.01 from 01; see above
        self.buffer, self.ticks, self.decisions = [], 0, 0
        self._out_budget = np.abs(self.W_out).sum(axis=1).copy()

    def _reset_dynamics(self):
        self.vh = np.zeros(self.n_hidden); self.vm = np.zeros(self.n_motor)
        self.trh = np.zeros(self.n_hidden); self.fh = np.zeros(self.n_hidden)
        self.votes = np.zeros(self.n_motor)

    # ---- 5: pretrained encoder. NOT USED BY DEFAULT -- it HURTS here. -------
    def pretrain_encoder(self, patterns, steps=6000, eta=0.02):
        """Competitive learning: local, unsupervised, no labels.

        DO NOT ENABLE without re-measuring. In isolation (11) this improved
        sample efficiency in all 3 seeds. In the ASSEMBLED system it is worse,
        consistently, over 6 seeds and both gradient settings:

            sleep-grad on :  pretrained 0.85  vs  random 0.98
            sleep-grad off:  pretrained 0.72  vs  random 0.85

        Kept because the isolated result is real and the reversal is the
        interesting part -- an intervention that helps a component can harm the
        system it is placed in. The mechanism was never established either way
        (11 also refuted decorrelation, my proposed explanation).
        """
        for _ in range(steps):
            x = patterns[self.rng.integers(len(patterns))]
            si = (self.rng.random(self.n_in) < 0.6 * x).astype(float)
            v = self.W_in @ si
            win = v >= np.partition(v, -self.k)[-self.k]
            self.W_in[win] += eta * (si - self.W_in[win])
        np.clip(self.W_in, 0, None, out=self.W_in)

    # ---- the loop -----------------------------------------------------------
    def step(self, x):
        """One tick. Returns motor spikes."""
        self.ticks += 1
        si = (self.rng.random(self.n_in) < 0.6 * x).astype(float)

        # 4/5: motor integrates last tick's hidden spikes, plus exploration noise
        self.vm = self.vm * self.LEAK + self.W_out @ self.fh \
                  + self.rng.normal(0, self.NOISE, self.n_motor)
        fm = (self.vm > 1.0).astype(float); self.vm[fm > 0] = 0

        # 2: leaky integrate and fire
        self.vh = self.vh * self.LEAK + self.W_in @ si

        # 3: compete. Only the best-driven K survive. Without this, two different
        #    inputs give near-identical patterns (02: cos .81 -> .93) and nothing
        #    downstream can separate them -- accuracy 1.00 -> 0.52.
        thr = np.partition(self.vh, -self.k)[-self.k]
        self.fh = ((self.vh >= thr) & (self.vh > self.thresh)).astype(float)
        self.vh[self.fh > 0] = 0

        self.trh = self.trh * self.TRACE_D + self.fh
        # EMA, not a running sum: keeps magnitude independent of the time
        # constant. A plain sum at tau~200 accumulates ~200x a single outer
        # product and saturates W_out -- the bug that invalidated experiment E.
        self.elig = self.elig * self.ELIG_D + (1 - self.ELIG_D) * np.outer(fm, self.trh)
        self.elig_w = self.elig_w * self.ELIG_D + (1 - self.ELIG_D)
        self.votes += fm

        # 8: homeostasis
        self.rate += 0.001 * (self.fh - self.rate)
        self.thresh += self.ETA_TH * (self.rate - self.TARGET_RATE)
        np.clip(self.thresh, 0.05, 20.0, out=self.thresh)
        if self.ticks % self.SCALE_EVERY == 0:
            cur = np.abs(self.W_out).sum(axis=1)
            scale = np.where(cur > 1e-9, self._out_budget / np.maximum(cur, 1e-9), 1.0)
            self.W_out *= scale[:, None]
        return fm

    def decide(self):
        v = self.votes.copy(); self.votes[:] = 0
        if v[0] == v[1]:
            return int(self.rng.random() < 0.5)
        return int(np.argmax(v))

    # ---- 6/7: feel, then learn ---------------------------------------------
    def reward(self, r, action=None):
        """Deliver reward. NM is reward MINUS what was expected (02: raw reward
        instead of RPE => chance, because it never stops reinforcing the known)."""
        self.value += self.VALUE_LR * (r - self.value)
        nm = r - self.value
        # Normalise by accumulated weight -> a true weighted MEAN outer product,
        # matching 02's e/TICKS at any decay. A raw EMA reaches only 1-d^T of
        # steady state (14% over a 30-tick trial at d=.995), making every update
        # ~7x too small: the local rule then tops out at 0.66 instead of 1.00,
        # and the sleep gradient silently covers for it.
        elig = self.elig / max(self.elig_w, 1e-9)
        de = elig - self.ebar
        self.ebar += self.EBAR_LR * (elig - self.ebar)
        self.W_out += self.LR * nm * de
        np.clip(self.W_out, 0, self.WMAX, out=self.W_out)
        # Consume the tag. Tag-and-capture: once the neuromodulator cashes the
        # eligibility, it is spent. Without this the tau~200 trace bleeds across
        # trials (200 ticks = 6.7 trials), averaging both classes together and
        # contaminating the update direction -- accuracy 0.58 vs 0.97.
        self.elig[:] = 0.0
        self.elig_w = 0.0
        if action is not None:
            self.buffer.append((self.trh.copy(), elig.copy(), nm, action, r))
        self.decisions += 1
        if self.decisions % self.SLEEP_EVERY == 0:
            self.sleep()

    # ---- 9: sleep -----------------------------------------------------------
    def sleep(self):
        """Body offline. Replay, then a gradient pass, then downscale and prune.

        13: replay alone gives +0.05 (acc@400); the gradient adds +0.06 on top of
        MATCHED replay, better in 5/5 seeds. Replay is uniform, NOT prioritised --
        12 found prioritising buys +0.03 retention for -0.19 plasticity.
        Scope: W_out is one linear layer, so this is a delta rule, not deep
        backprop. Nothing here establishes that backprop helps a deep net.
        """
        if len(self.buffer) < self.SLEEP_REPLAY:
            return
        idx = self.rng.choice(len(self.buffer), size=self.SLEEP_REPLAY)
        for j in idx:
            trh, elig, nm, act, r = self.buffer[j]
            de = elig - self.ebar
            self.ebar += self.EBAR_LR * (elig - self.ebar)
            self.W_out += self.LR * nm * de                      # local replay
            z = trh / 30.0
            tgt = act if r > 0.5 else 1 - act                    # what reward said
            p = np.exp(self.W_out @ z - (self.W_out @ z).max()); p /= p.sum()
            g = p.copy(); g[tgt] -= 1.0
            self.W_out -= self.SLEEP_ETA * np.outer(g, z)        # gradient pass
        np.clip(self.W_out, 0, self.WMAX, out=self.W_out)
        self.W_out *= self.DOWNSCALE
        self.W_out[self.W_out < 1e-3] = 0.0
        if len(self.buffer) > 2000:
            self.buffer = self.buffer[-2000:]

    # ---- 1: copy the weights. A brain cannot; a matrix can. -----------------
    def save(self, path):
        np.savez(path, W_in=self.W_in, W_out=self.W_out, thresh=self.thresh,
                 ebar=self.ebar, value=self.value)

    def load(self, path):
        d = np.load(path)
        self.W_in, self.W_out = d['W_in'], d['W_out']
        self.thresh, self.ebar, self.value = d['thresh'], d['ebar'], float(d['value'])
        self._reset_dynamics()

    # ---- 2: merge. CLONES ONLY. --------------------------------------------
    @staticmethod
    def merge(models):
        """Average W_out across agents that share an ancestor.

        10: merging clones works (0.81 vs 0.75 solo); merging independently-grown
        nets lands at CHANCE (0.53) because neuron 7 means something different in
        each. Guarded below rather than documented and hoped for.

        Measured IN THE MAINLINE (5 seeds, 8 agents x 300 trials):
            solo 0.95  ->  merged 0.98  (ceiling 1.00), better in 4/5 seeds.
        Still lossy -- in the simplified loop of 10, merging 8x250 gave 0.81
        where ONE agent on those same 2000 trials gave 1.00. This buys
        wall-clock, not sample efficiency.
        """
        ref = models[0].W_in
        for m in models[1:]:
            if not np.array_equal(m.W_in, ref):
                raise ValueError(
                    "merge() requires a shared encoder (common ancestor). "
                    "Merging independently-initialised agents yields chance "
                    "performance -- see experiments/10_clone_merge.py.")
        out = BrainSim(models[0].n_in, models[0].n_hidden, models[0].n_motor,
                       models[0].k, seed=0)
        out.W_in = ref.copy()
        out.W_out = np.mean([m.W_out for m in models], axis=0)
        # thresh is averaged too: each clone's controller settled at its own
        # operating point, and the mean of two working controllers is not
        # guaranteed to be one. Measured fine here; re-check if you change the
        # homeostasis.
        out.thresh = np.mean([m.thresh for m in models], axis=0)
        return out


# ---- what is deliberately NOT here -----------------------------------------
# CURIOSITY / surprise-as-intrinsic-reward: tested at 0.1/0.3/1.0/3.0 across two
#   environments (07, 08). No effect survived a control check.
# Prioritised replay: 12 buys +0.03 retention for -0.19 plasticity.
# A BANK of eligibility traces: 09 -- one long trace beats it. The bank's update
#   direction averages its traces, and at long delays the fast ones hold nothing
#   but interference.
