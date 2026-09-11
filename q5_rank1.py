"""Q5 rank-1 eligibility as a subclass fork -- v1 sources stay frozen.

Three frozen manifests (v2-m0, v5, v6) pin brainsim.py byte-for-byte, so the
flag cannot land in BrainSim itself without rewriting merged evidence. This
file carries the exact BrainSim.step()/reward() text (AST-extracted from the
frozen source; classic branches unchanged, plus one defensive _credit_init
call at reward() head which is a no-op when the flag is off) with the rank-1
algebra behind a subclass flag. Provenance: kernel check (i) gates
classic-mode exactness against BrainSim head-to-head, so the ONLY difference
under test is the algebra; the numba kernel in fastsim.py is shared
(default-off path identical). If rank-1 matches, landing the flag in v1 --
with deliberate re-freezes -- is a follow-up slice. If it fails, nothing was
integrated.
"""
import numpy as np

from brainsim import BrainSim
from fastsim import FastBrainSim, _ensure_credit


class Rank1BrainSim(BrainSim):
    """BrainSim with an optional rank-1 eligibility rule. Default off."""

    RANK1_ELIG = False

    def _credit_init(self):
        _ensure_credit(self)

    def step(self, x):
        """One tick. Returns motor spikes."""
        self._credit_init()
        self.ticks += 1
        si = (self.rng.random(self.n_in) < 0.6 * x).astype(float)

        # 4/5: motor integrates last tick's hidden spikes, plus exploration noise
        if self.TRANSMISSION_FAILURE:
            mask = self.transmission_rng.random(self.W_out.shape) >= self.TRANSMISSION_FAILURE
            signal = (self.W_out * mask) @ self.fh
        else:
            signal = self.W_out @ self.fh
        drive = self.TRANSMISSION_GAIN * signal + self.rng.normal(0, self.noise_eff, self.n_motor)
        if self.WM:
            # Feed the WM pathway only what the CURRENT input does not already
            # explain. Where the observation is constant within a decision (lock,
            # nway, volatile) wm is a scaled copy of trh, so the pathway merely
            # duplicates W_out -- two controllers on one variable, and lock-10
            # fell 419 -> 58. Removing the component parallel to trh makes the
            # contribution ~0 exactly there, while leaving it intact when wm
            # holds something the input does not (a cue from 40 ticks ago).
            n2 = float(self.trh @ self.trh)
            resid = self.wm - (float(self.wm @ self.trh) / n2) * self.trh if n2 > 1e-9 else self.wm
            self._wm_eff = resid
            drive = drive + self.WM_BETA * (self.W_wm @ resid)
        if self.PERSIST:
            drive += self.SELF_EXC * self.trm - self.INHIB * self.trm.mean()
        self.vm = self.vm * self.LEAK + drive
        fm = (self.vm > 1.0).astype(float); self.vm[fm > 0] = 0
        self.trm = self.trm * self.TRM_D + fm

        # 2: leaky integrate and fire
        self.vh = self.vh * self.LEAK + self.W_in @ si

        # 3: compete. Only the best-driven K survive. Without this, two different
        #    inputs give near-identical patterns (02: cos .81 -> .93) and nothing
        #    downstream can separate them -- accuracy 1.00 -> 0.52.
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
            self.wm_sum += getattr(self, "_wm_eff", self.wm); self.wm_n += 1
        self.trh_sum += self.trh; self.trh_n += 1
        # EMA, not a running sum: keeps magnitude independent of the time
        # constant. A plain sum at tau~200 accumulates ~200x a single outer
        # product and saturates W_out -- the bug that invalidated experiment E.
        if self.TAGGATE:
            m = self.trm.max()
            gate = (self.trm >= self.THETA * m).astype(float) if m > 0 else np.ones(self.n_motor)
        else:
            gate = 1.0
        if self.RANK1_ELIG:
            # Q5: outer product of decayed traces, formed from the same gated
            # motor spikes and hidden trace as the matrix rule -- only the
            # algebra differs (outer of means vs mean of outers).
            self.etr_m = self.etr_m * self.ELIG_D + (1 - self.ELIG_D) * (fm * gate)
            self.etr_h = self.etr_h * self.ELIG_D + (1 - self.ELIG_D) * self.trh
            self.etrw = self.etrw * self.ELIG_D + (1 - self.ELIG_D)
        else:
            self.elig = self.elig * self.ELIG_D + (1 - self.ELIG_D) * np.outer(fm * gate, self.trh)
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

    def reward(self, r, action=None, done=True, policy_bonus=0.0, switch=False):
        """Deliver reward. NM is reward MINUS what was expected (02: raw reward
        instead of RPE => chance, because it never stops reinforcing the known)."""
        self._credit_init()   # defensive: no-op when off or after any tick
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
            self.W_out += lr * nm * de
            np.clip(self.W_out, self.WMIN, self.WMAX, out=self.W_out)
            if self.RANK1_ELIG:
                self.etr_m[:] = 0.0; self.etr_h[:] = 0.0; self.etrw = 0.0
            else:
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
        if self.RANK1_ELIG:
            # Q5: form the outer product on demand from the trace pair. The
            # transient M×H array flows into de/ebar/buffer exactly as elig
            # does; no (M,H) state persists between rewards.
            elig = np.outer(self.etr_m, self.etr_h) / max(self.etrw * self.etrw, 1e-9)
        else:
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
            self.W_wm += gate * lr * nm * dew / (float(wbar @ wbar) + 1e-3)
            np.clip(self.W_wm, -self.WMAX, self.WMAX, out=self.W_wm)
            if not (self.WM_HOLD and not done):
                self.wm[:] = 0.0; self._prev_fh[:] = 0.0
            self.wm_sum[:] = 0.0; self.wm_n = 0
        self.ebar += self.EBAR_LR * (elig - self.ebar)
        self.W_out += gate * lr * nm * de
        np.clip(self.W_out, self.WMIN, self.WMAX, out=self.W_out)
        # Consume the tag. Tag-and-capture: once the neuromodulator cashes the
        # eligibility, it is spent. Without this the tau~200 trace bleeds across
        # trials (200 ticks = 6.7 trials), averaging both classes together and
        # contaminating the update direction -- accuracy 0.58 vs 0.97.
        if not (self.PGATE == "oracle_carry" and gate == 0.0):
            if self.RANK1_ELIG:
                self.etr_m[:] = 0.0; self.etr_h[:] = 0.0; self.etrw = 0.0
            else:
                self.elig[:] = 0.0
                self.elig_w = 0.0
        if action is not None:
            self.buffer.append((self.trh.copy(), elig.copy(), nm, action, r))
        self.decisions += 1
        if self.HIPPO and action is not None:
            self.store_and_replay(zbar, action, r, done, _wbar)
        if self.decisions % self.SLEEP_EVERY == 0:
            self.sleep()

class FastRank1(FastBrainSim, Rank1BrainSim):
    """Buffered steps + shared numba kernel (FastBrainSim) with rank-aware
    reward (Rank1BrainSim). MRO: flush/observe/decide from FastBrainSim,
    reward resolves to Rank1BrainSim.reward. No new code by design."""
