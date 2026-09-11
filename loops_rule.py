"""Parallel-loops probe as a subclass fork -- v1 sources stay frozen.

Three frozen manifests (v2-m0, v5, v6) pin brainsim.py byte-for-byte, so the
loop algebra cannot land in BrainSim itself. This file carries the exact
BrainSim.reward() text (AST-extracted from the frozen source) with per-action
neuromodulator loops behind a subclass flag. Provenance: kernel check (i)
gates LoopsBrainSim(global) against BrainSim head-to-head EXACT, so the ONLY
differences under test are the loop algebra; the numba kernel in fastsim.py
is shared (default-off path identical). See DESIGN-loops-probe.md.
"""
import numpy as np

from brainsim import BrainSim
from fastsim import FastBrainSim


class LoopsBrainSim(BrainSim):
    """BrainSim with optional per-action neuromodulator loops.

    MODE 'global' (default): shipped single-loop behavior, line-identical.
    MODE 'loops-LR': each action tracks its own fast/slow reward-rate
      averages; the W_out update uses a per-action LR vector while
      exploration noise stays on the shipped global loop (one difference).
    MODE 'loops-full': per-action LR vector AND per-action noise vector.
    The shipped global averages keep running in all modes (vol_hist shape
    preserved); the WM pathway keeps the global lr (VBURST/PGATE precedent:
    bursts scale POLICY updates only).
    """

    MODE = 'global'

    def _loops_init(self):
        if self.MODE not in ('global', 'loops-LR', 'loops-full'):
            raise ValueError(f'unknown loops MODE {self.MODE!r}')
        if self.MODE != 'global' and not hasattr(self, 'surp_fa'):
            self.surp_fa = np.zeros(self.n_motor)
            self.surp_sa = np.zeros(self.n_motor)
            self.noise_fa = np.zeros(self.n_motor)

    def reward(self, r, action=None, done=True, policy_bonus=0.0, switch=False):
        """Deliver reward. NM is reward MINUS what was expected (02: raw reward
        instead of RPE => chance, because it never stops reinforcing the known)."""
        self._loops_init()   # validates MODE; no-op allocation-wise when global
        if self.DUALV and not self.VALUE_STATE:
            raise ValueError('DUALV requires VALUE_STATE')
        zbar = self.trh_sum / max(self.trh_n, 1)
        _wbar = (self.wm_sum / max(self.wm_n, 1)) if self.WM else None
        if self.VALUE_STATE:
            # V(s) from cortical input, as striatum does -- not one global mean.
            # A scalar baseline is useless when reward arrives 2x in 25,000 acts.
            v_slow = float(self.w_v @ zbar)
            if self.DUALV:
                v_fast = float(self.w_vf @ zbar)
                v = v_fast if self.decisions-self.last_trig <= self.DUALV_WIN else v_slow
            else:
                v = v_slow
            nm = r - v
            # NORMALISED delta rule. A plain one diverges here: ||zbar||^2 ~ 100
            # (6 active units, trace ~5), so LR=0.05 predicts V~5 for r=1 after a
            # single step and accuracy collapses to 0.04 against 0.25 chance.
            # Dividing by ||z||^2 makes the step scale-free. Third magnitude bug
            # of this kind in the project -- see the eligibility sum and EMA.
            self.w_v += self.VALUE_W_LR * (r - v) * zbar / (zbar @ zbar + 1e-6)
            if self.DUALV:
                # Fast head, same normalized rule at 10x the rate. Updated on
                # every reward regardless of which head currently predicts.
                self.w_vf += self.DUALV_LR * (r - v) * zbar / (zbar @ zbar + 1e-6)
        else:
            self.value += self.VALUE_LR * (r - self.value)
            nm = r - self.value
        if self.ADAPTIVE:
            # Volatility, not noise: learning should speed up when the world
            # CHANGES, not merely when it is stochastic (Behrens 2007). Fast
            # surprise above its own slow baseline is the change signal.
            # Track REWARD RATE, not |RPE|. |RPE| is large simply because reward
            # is binary -- that is EXPECTED uncertainty (noise), which should NOT
            # raise the learning rate. Using it fired the signal permanently,
            # doubling LR and noise forever and collapsing accuracy to 0.015.
            # A contingency change shows up as a sustained gap between a fast and
            # a slow average of r, which decays once the new rate is learned.
            self.surp_f += self.SURP_F * (r - self.surp_f)
            self.surp_s += self.SURP_S * (r - self.surp_s)
            vol = float(np.clip(abs(self.surp_f - self.surp_s) / (self.surp_s + 0.05),
                                0.0, self.VOL_CAP))
            lr = self.LR * (1 + self.LR_GAIN * vol)
            self.noise_eff = self.NOISE * (1 + self.NOISE_GAIN * vol)
        else:
            vol = 0.0
            lr = self.LR
        if self.MODE != 'global':
            # Parallel loops: the shipped global loop above keeps running
            # (vol_hist shape, VBURST trigger semantics, WM pathway all
            # preserved); per-action averages additionally drive a LR
            # vector, and in loops-full a noise vector. lr_shipped is the
            # scalar the WM pathway keeps using in all modes.
            lr_shipped = lr
            if action is not None:
                a = int(action)
                self.surp_fa[a] += self.SURP_F * (r - self.surp_fa[a])
                self.surp_sa[a] += self.SURP_S * (r - self.surp_sa[a])
                vol_a = np.clip(abs(self.surp_fa - self.surp_sa) / (self.surp_sa + 0.05),
                                0.0, self.VOL_CAP)
                lr = self.LR * (1 + self.LR_GAIN * vol_a)
                if self.MODE == 'loops-full':
                    self.noise_fa = self.NOISE * (1 + self.NOISE_GAIN * vol_a)
                    self.noise_eff = self.noise_fa
            else:
                lr = np.full(self.n_motor, float(lr))
        if self.VBURST is not None or self.DUALV:
            # V5 triggers. Oracle arms fire on true switch flags passed by the
            # evaluator; endo arms fire on the ADAPTIVE vol scalar (tau 1.0 for
            # the dualV head, the burst setting's own tau otherwise).
            # Edge-triggered: triggers arriving mid-burst are ignored, and a
            # burst never extends. Provenance recorded for the evidence.
            oracle_mode = self.VBURST_ORACLE or self.DUALV_ORACLE
            if oracle_mode:
                fired = bool(switch)
            elif self.VBURST is not None:
                fired = vol > self.VBURST[0]
            else:
                fired = vol > 1.0
            if fired:
                if self.VBURST is not None and self.burst_left <= 0:
                    self.burst_left = self.VBURST[2]
                self.last_trig = self.decisions
                self.burst_marks.append((self.decisions, 'oracle' if oracle_mode else 'endo'))
        if self.VBURST is not None and self.burst_left > 0:
            lr = lr * self.VBURST[1]
            self.burst_left -= 1
        self.vol_hist.append(vol if self.ADAPTIVE else 0.0)
        self.lr_hist.append(lr)
        self.noise_hist.append(self.noise_eff)
        if policy_bonus:
            nm += policy_bonus
        # Step 8 gate. Scales the POLICY update only. V(s), the traces, replay
        # and every reset stay untouched -- skipping reward() wholesale is a bug
        # this project has already made once (it skipped the state resets too).
        gate = 1.0
        if self.PGATE in ("oracle", "oracle_carry") and not done:
            gate = 0.0
        if self.ACTION_GATED and action is not None:
            z = self.trh_sum / max(self.trh_n, 1)
            de = np.zeros_like(self.W_out)
            de[action] = z - self.ebar[action]
            self.ebar[action] += self.EBAR_LR * (z - self.ebar[action])
            if self.MODE == 'global':
                self.W_out += lr * nm * de
            else:
                self.W_out += lr[:, None] * nm * de
            np.clip(self.W_out, self.WMIN, self.WMAX, out=self.W_out)
            self.elig[:] = 0.0; self.elig_w = 0.0
            self.buffer.append((z.copy(), de.copy(), nm, action, r))
            self.trh_sum[:] = 0.0; self.trh_n = 0
            if self.WM and not (self.WM_HOLD and not done):
                self.wm[:] = 0.0; self._prev_fh[:] = 0.0
            self.decisions += 1
            if self.HIPPO: self.store_and_replay(zbar, action, r, done, _wbar)
            if self.decisions % self.SLEEP_EVERY == 0: self.sleep()
            return
        # Normalise by accumulated weight -> a true weighted MEAN outer product,
        # matching 02's e/TICKS at any decay. A raw EMA reaches only 1-d^T of
        # steady state (14% over a 30-tick trial at d=.995), making every update
        # ~7x too small: the local rule then tops out at 0.66 instead of 1.00,
        # and the sleep gradient silently covers for it.
        elig = self.elig / max(self.elig_w, 1e-9)
        de = elig - self.ebar
        self.trh_sum[:] = 0.0; self.trh_n = 0
        if self.WM:
            # Separate pathway, separate credit: same three-factor rule, with wm
            # as the presynaptic signal instead of trh.
            wbar = self.wm_sum / max(self.wm_n, 1)
            dw = np.outer(np.eye(self.n_motor)[action], wbar) if action is not None \
                 else np.zeros_like(self.W_wm)
            dew = dw - self.ebar_wm
            self.ebar_wm += self.EBAR_LR * (dw - self.ebar_wm)
            # NORMALISE by input magnitude. Where the residual is near zero
            # (constant observation within a decision) an unnormalised rule lets
            # W_wm grow without bound until a tiny input still produces a large
            # drive -- volatile-4 fell BELOW its floor, 0.411 -> 0.238. Same bug
            # as the V(s) readout, which needed the same fix.
            # WM pathway keeps the shipped global scalar in all modes
            # (VBURST/PGATE precedent: bursts scale POLICY updates only).
            lr_wm = lr_shipped if self.MODE != 'global' else lr
            self.W_wm += gate * lr_wm * nm * dew / (float(wbar @ wbar) + 1e-3)
            np.clip(self.W_wm, -self.WMAX, self.WMAX, out=self.W_wm)
            if not (self.WM_HOLD and not done):
                self.wm[:] = 0.0; self._prev_fh[:] = 0.0
            self.wm_sum[:] = 0.0; self.wm_n = 0
        self.ebar += self.EBAR_LR * (elig - self.ebar)
        if self.MODE == 'global':
            self.W_out += gate * lr * nm * de
        else:
            self.W_out += gate * lr[:, None] * nm * de
        np.clip(self.W_out, self.WMIN, self.WMAX, out=self.W_out)
        # Consume the tag. Tag-and-capture: once the neuromodulator cashes the
        # eligibility, it is spent. Without this the tau~200 trace bleeds across
        # trials (200 ticks = 6.7 trials), averaging both classes together and
        # contaminating the update direction -- accuracy 0.58 vs 0.97.
        if not (self.PGATE == "oracle_carry" and gate == 0.0):
            self.elig[:] = 0.0
            self.elig_w = 0.0
        if action is not None:
            self.buffer.append((self.trh.copy(), elig.copy(), nm, action, r))
        self.decisions += 1
        if self.HIPPO and action is not None:
            self.store_and_replay(zbar, action, r, done, _wbar)
        if self.decisions % self.SLEEP_EVERY == 0:
            self.sleep()

class FastLoops(FastBrainSim, LoopsBrainSim):
    """Buffered steps + shared numba kernel (FastBrainSim) with loop-aware
    reward (LoopsBrainSim). MRO: flush/observe/decide from FastBrainSim,
    reward resolves to LoopsBrainSim.reward. No new code by design."""
