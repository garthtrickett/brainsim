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
    # 17/18: readout weights are clamped NON-NEGATIVE. Fine for 2 classes, where
    # relative magnitude alone separates them. With N classes the readout cannot
    # represent "this cell means NOT class 3", which may be why the design stalls
    # near chance past 2 classes. Set WMIN=-WMAX to allow inhibitory readout.
    WMIN      = 0.0
    # 01 validated threshold homeostasis at a 1% target -- on a RECURRENT net
    # with no k-WTA. Here competition forces exactly k/n cells to fire, so a 1%
    # target is a rate competition structurally forbids: the controller ratchets
    # thresholds up forever (1.00 -> 6.42) and accuracy sits at 0.58. The target
    # is set from k/n in __init__. A constant is only valid in the architecture
    # it was measured in.
    # 15: OFF in this architecture. Validated in 01 on a RECURRENT net, where
    # without it 90% of cells went silent. In the feedforward + k-WTA path it is
    # counterproductive: it is per-cell, so winners get their thresholds pushed
    # UP for firing often while k-WTA keeps selecting by rank -- penalising the
    # informative cells. Measured over 3000 trials:
    #     ETA_TH=0.02 -> fire_rate 0.0318, 23% cells silent, thresh drifts to 2.21
    #     ETA_TH=0    -> fire_rate 0.0750 (= k/n, as k-WTA enforces), 15% silent
    # It causes MORE silence than it prevents, and costs sample efficiency
    # (0.90 vs 0.98 at 1200 trials; both reach ~1.00 by 3000).
    # Re-enable for recurrent architectures, where 01's result applies.
    ETA_TH    = 0.0
    # 06: NOT 100 -- at 100 it fought the threshold controller (rate dipped to
    # 0.0080 by 60k). 15: it is also load-bearing for LEARNING here, not just for
    # saturation: removing it drops the local rule 0.90 -> 0.81.
    SCALE_EVERY = 1000
    SLEEP_EVERY = 50     # 13: sleep cadence, in decisions
    SLEEP_REPLAY = 60    # 13: replayed episodes per sleep
    SLEEP_ETA = 0.05     # 13: gradient step size inside sleep
    DOWNSCALE = 0.98     # step 9: shrink all, preserve the order
    # 15: a NO-OP as configured -- np.clip(W_out, 0, ...) already sets weights to
    # exactly 0, so nothing is ever left below the threshold. Ablating it gives
    # bit-identical results. Kept because pruning is real in the design; it just
    # has nothing to do while the clip does the work.
    PRUNE_BELOW = 1e-3
    # 18: THE ONE NON-LOCAL ELEMENT IN THIS DESIGN. Credit the action that was
    # SELECTED rather than every motor cell that happened to fire. Without it the
    # design cannot exceed binary choice:
    #        classes    local    action-gated
    #           2       1.000       1.000
    #           4       0.323       0.923
    #           8       0.152       0.919
    # Diagnosis: 3.37 of 4 motor cells fire per tick, so outer(fm, trh) credits
    # nearly all of them, W_out never differentiates (spread 0.03 vs 0.58) and the
    # vote margin stays at 0.6 spikes -- a coin flip. Hidden codes were separable
    # all along (overlap 0.549), so this was credit assignment, not capacity.
    # Two LOCAL alternatives were tried and both failed:
    #   motor k-WTA (1-of-N per tick):  0.319 / 0.158 -- per-tick winners smear
    #       credit across cells; the decision is a 30-tick aggregate.
    #   commitment (lock in at a bound): 0.350 / 0.168 -- locks on noise, then
    #       only the locked cell can fire, so it cannot escape. Bimodal seeds.
    # 21 SUPERSEDES the decision to default this ON. A LOCAL mechanism (TAGGATE)
    # recovers most of the benefit, so the design no longer has to give up
    # locality to exceed binary choice:
    #       classes   local   TAGGATE   persist+gate   ACTION_GATED
    #          4      0.323    0.602       0.877          0.959
    #          8      0.152    0.672       0.600          0.900
    # TAGGATE recovers 70% of the gap at 8 classes and 87% at 4 (with persist).
    # Enable ACTION_GATED for maximum accuracy, accepting one non-local signal.
    ACTION_GATED = False   # 21: superseded as the default -- see TAGGATE below

    # --- brain-plausible alternatives to ACTION_GATED (19/21). Default OFF. ---
    # Added to BrainSim itself rather than a subclass: a subclass that
    # reimplemented step() silently dropped synaptic scaling and degraded every
    # row of its own experiment, reference included.
    # 21: PERSIST is NOT reliably useful -- +0.28 at 4 classes, -0.07 at 8, and
    # near-nothing alone. Off by default; try it if 4-way is your case.
    PERSIST  = False     # recurrent self-excitation + pooled lateral inhibition:
    SELF_EXC = 0.15      # amplifies an early (noise-driven) lead and sustains it
    INHIB    = 0.10      # to reward, so credit and decision coincide in TIME
    TAGGATE  = True      # tag only if this cell clears a threshold set by the
    THETA    = 1.0       # pooled interneuron -> winner-take-all on CREDIT.
                         # 21: measured motor traces are [9.53 9.48 9.53 9.48] --
                         # 0.5% apart -- so any THETA below ~0.99 admits every
                         # cell and gates nothing. Exact-max is the real WTA.
    # 22: the gate window trades ALIGNMENT against EXPLORATION, and the optimum
    # moves with the number of choices. A long trace matches the gate's winner to
    # the decision (argmax over the whole trial); too long and an early lead locks
    # in and cannot be overturned -- costly with more competitors, since the early
    # leader is right only 1/N of the time.
    #                 8 classes   4 classes
    #   TRM_D=0.90      0.672       0.602
    #   TRM_D=0.97      0.592       0.838     <- default: best average, no collapse
    #   TRM_D=0.99      0.244       0.959     <- MATCHES non-local ACTION_GATED at 4
    #   TRM_D=1.0       0.292       0.503     <- never forgets; early lead locks in
    #   ACTION_GATED    0.900       0.959
    # Tune to your N: 0.99 for 4-way (matches non-local exactly), 0.90 for 8-way.
    TRM_D    = 0.97

    # --- hippocampus: episodic store + replay (29). Default OFF pending test.
    # Two DIFFERENT mechanisms for backward credit, deliberately separable:
    #  (a) an eligibility trace spanning the replayed episode -- needs COMPRESSION,
    #      because 10 steps x 30 ticks leaves the trace at 0.222 but x3 leaves 0.860;
    #  (b) TD bootstrapping through V(s) in reverse order -- propagates credit via
    #      the value function and does NOT need compression.
    # The design doc leaned on (a); (b) is the standard answer. The ablation must
    # tell them apart or "hippocampus" is just a label on an oversampled buffer.
    HIPPO           = True    # SHIPPED (29): lock-10 rewards 9.5 -> 333.5, 35x
    HIPPO_REVERSE   = True    # ESSENTIAL: reverse 333.5 vs forward 4.2 (80x).
                              # Updating backwards means each state's successor is
                              # already fresh, so credit crosses the whole episode
                              # in ONE pass. Forward moves it one step per pass.
    HIPPO_TRACE     = False   # REFUTED. The design's headline claim was that time
                              # compression lets an eligibility trace span an
                              # episode. Both the trace and the compression are
                              # HARMFUL: no trace 333.5, compressed trace 115.5,
                              # uncompressed trace 133.0. Kept as a flag because
                              # the refutation is worth preserving.
    HIPPO_TICKS     = 3       # only used when HIPPO_TRACE is on
    HIPPO_BOOTSTRAP = True    # ESSENTIAL: with TD 333.5, without 2.8
    HIPPO_PRIORITY  = True    # sample episodes ~ reward; buffer is ~2000 junk runs
    HIPPO_N         = 8       # episodes per sleep. N=24 scores higher on average
                              # (377.5) but is bimodal -- 2 of 6 seeds collapse to
                              # ~2. Robust beats peak, as with TRM_D.
    HIPPO_GAMMA     = 0.9
    HIPPO_LR        = 0.05
    HIPPO_CAP       = 400     # episode store size
    # The lock only signals done at the GOAL -- a wrong action resets the state
    # but does not end the episode. Without a window the "episode" is the whole
    # run from session start to reward: thousands of steps of mostly failure.
    # A finite episodic window is also the biologically right answer: the
    # hippocampus holds a recent trajectory, not a lifetime.
    HIPPO_WINDOW    = 20      # steps retained before the outcome
    # Replay only SEQUENCES. Reverse replay exists to move credit ACROSS steps;
    # a 1-step episode has no sequence, so replaying it just duplicates the
    # online update -- and on a volatile task it replays contingencies that have
    # since changed. Measured cost of not gating this: nway-4 0.961 -> 0.890,
    # xor-2 0.722 -> 0.518, volatile-4 0.472 -> 0.305.
    HIPPO_MIN_LEN   = 2

    # --- neuromodulators beyond dopamine (25). Default OFF pending validation.
    # `volatile-4` sits at 0.276 vs a 0.250 floor on a task the design solves at
    # 0.834 when stationary: a fixed LR and fixed exploration are a hard wall.
    # 25: SHIPPED. Striatal V(s) -- a learned linear value readout from the
    # hidden trace, replacing one global scalar baseline. Local: delta rule,
    # post-error x pre-activity, normalised by ||z||^2 (a plain delta rule
    # diverges: ||zbar||^2 ~ 100 predicts V~5 for r=1 in one step).
    #   volatile-4  0.276 -> 0.472     nway-4  0.834 -> 0.961
    # Does NOT help lock-10 (still ~0.000): sparse reward is the hippocampus.
    VALUE_STATE = True
    VALUE_W_LR  = 0.05
    # 32: SHIPPED. Step 1 rejected this for "cancelling V(s)" -- measured under
    # the broken decide(). In the corrected regime they are COMPLEMENTARY:
    # V(s) must relearn every state when contingencies permute, and volatility-
    # driven LR/noise is exactly the repair.
    #                volatile   nway-4   nway-8   xor-2    lock-10
    #   V(s)            0.278    0.999    0.924   0.707      330.8
    #   V(s)+ADAPTIVE   0.419    0.999    0.882   0.756      282.4
    # A real trade: +0.141 volatile, +0.049 xor, -0.042 nway-8, -15% lock.
    # Shipped because volatile at 0.278 is 4% off its floor (near-failing) and
    # 0.419 is 23%, while the lock stays at 30x baseline. Robust beats peak.
    ADAPTIVE    = True   # NE/ACh: volatility from reward-rate change -> LR, noise
    SURP_F, SURP_S = 0.10, 0.005   # fast/slow |RPE| averages
    LR_GAIN, NOISE_GAIN, VOL_CAP = 1.5, 1.5, 2.0

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
        # running mean of trh across the trial. NOT self.trh/30: that is the
        # FINAL tick's trace, one noisy sample, and using it drops 8-class
        # accuracy from 0.92 to 0.24.
        self.trh_sum = np.zeros(n_hidden); self.trh_n = 0
        self.trm = np.zeros(n_motor)      # motor activity trace
        self.w_v = np.zeros(n_hidden)     # striatal value weights V(s)
        self.surp_f = self.surp_s = 0.0   # fast / slow REWARD RATE averages
        self.noise_eff = self.NOISE       # NE-modulated exploration
        self.value = 0.0
        self.rate  = np.zeros(n_hidden)
        self.TARGET_RATE = k / n_hidden   # NOT the 0.01 from 01; see above
        self.buffer, self.ticks, self.decisions = [], 0, 0
        self.episode, self.episodes = [], []   # current episode, episodic store
        self._out_budget = np.abs(self.W_out).sum(axis=1).copy()

    def _reset_dynamics(self):
        self.vh = np.zeros(self.n_hidden); self.vm = np.zeros(self.n_motor)
        self.trh = np.zeros(self.n_hidden); self.fh = np.zeros(self.n_hidden)
        self.votes = np.zeros(self.n_motor)

    # ---- 5: pretrained encoder. Off by default -- SUBSUMED, not harmful. ----
    def pretrain_encoder(self, patterns, steps=6000, eta=0.02):
        """Competitive learning: local, unsupervised, no labels.

        Verdict revised twice; the earlier "it HURTS" was an artifact of a bad
        default (ETA_TH=0.02, which 15 showed is itself counterproductive here).

            with ETA_TH=0.02:  pretrained 0.85 vs random 0.98  (grad on)
                               pretrained 0.72 vs random 0.85  (grad off)
            with ETA_TH=0:     pretrained 0.95 vs random 0.97  (grad on, @400)
                               pretrained 0.84 vs random 0.75  (grad off, @400)

        So it HELPS the local rule (+0.09 sample efficiency), and is NEUTRAL once
        the sleep gradient is on because the gradient reaches ceiling either way.
        The mainline ships with the gradient on, so this is off by default as
        redundant -- not because it does damage. Enable it if you disable
        SLEEP_ETA. 11 also refuted decorrelation as the mechanism; still unknown.
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
        drive = self.W_out @ self.fh + self.rng.normal(0, self.noise_eff, self.n_motor)
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
        thr = np.partition(self.vh, -self.k)[-self.k]
        self.fh = ((self.vh >= thr) & (self.vh > self.thresh)).astype(float)
        self.vh[self.fh > 0] = 0

        self.trh = self.trh * self.TRACE_D + self.fh
        self.trh_sum += self.trh; self.trh_n += 1
        # EMA, not a running sum: keeps magnitude independent of the time
        # constant. A plain sum at tau~200 accumulates ~200x a single outer
        # product and saturates W_out -- the bug that invalidated experiment E.
        if self.TAGGATE:
            m = self.trm.max()
            gate = (self.trm >= self.THETA * m).astype(float) if m > 0 else np.ones(self.n_motor)
        else:
            gate = 1.0
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

    def decide(self):
        """Argmax over votes, ties broken uniformly among ALL joint winners.

        BUG (fixed 30): this compared only v[0] and v[1] and, on a tie between
        those two, returned 0 or 1 at random -- discarding the vote entirely and
        ignoring actions 2..n-1 even when one of them won outright. Written when
        n_motor was always 2, never updated when it became a parameter. Vote
        counts are small integers so ties are common: at TRM_D=1.0, where trm and
        votes are the SAME array, tagged-equals-chosen measured 38.8% instead of
        100%. Every n>2 result in the project was depressed by this.
        """
        v = self.votes.copy(); self.votes[:] = 0
        winners = np.flatnonzero(v == v.max())
        if len(winners) == 1:
            return int(winners[0])
        return int(winners[self.rng.integers(len(winners))])

    # ---- 6/7: feel, then learn ---------------------------------------------
    def store_and_replay(self, z, action, r, done):
        """Episodic memory: bind (state, action, outcome), replay on completion."""
        self.episode.append((z.copy(), int(action), float(r)))
        if len(self.episode) > self.HIPPO_WINDOW:
            self.episode = self.episode[-self.HIPPO_WINDOW:]
        if not done:
            return
        total = sum(x[2] for x in self.episode)
        if len(self.episode) >= self.HIPPO_MIN_LEN:
            self.episodes.append((self.episode, total))
        keep_len = len(self.episode)
        self.episode = []
        if keep_len < self.HIPPO_MIN_LEN:
            return
        if len(self.episodes) > self.HIPPO_CAP:
            # evict the least valuable, not the oldest: the rewarded episodes are
            # 1-3 in 4000 and must survive.
            self.episodes.sort(key=lambda e: e[1])
            self.episodes = self.episodes[1:]
        if total <= 0:
            return                      # replay is triggered BY reward
        for _ in range(self.HIPPO_N):
            self._replay_one()

    def _replay_one(self):
        if not self.episodes: return
        if self.HIPPO_PRIORITY:
            w = np.array([e[1] for e in self.episodes], dtype=float) + 1e-3
            idx = int(self.rng.choice(len(self.episodes), p=w / w.sum()))
        else:
            idx = int(self.rng.integers(len(self.episodes)))
        ep = self.episodes[idx][0]
        decay = (self.ELIG_D ** self.HIPPO_TICKS) if self.HIPPO_TRACE else 0.0
        elig = np.zeros_like(self.W_out)
        order = list(reversed(ep)) if self.HIPPO_REVERSE else list(ep)
        vnext = 0.0                                  # terminal value
        for (z, a, r) in order:
            v = float(self.w_v @ z)
            nm = (r + self.HIPPO_GAMMA * vnext - v) if self.HIPPO_BOOTSTRAP else (r - v)
            elig *= decay
            elig[a] += z
            self.W_out += self.HIPPO_LR * nm * elig
            self.w_v += self.VALUE_W_LR * nm * z / (z @ z + 1e-6)
            vnext = float(self.w_v @ z)              # fresh, hence reverse order
        np.clip(self.W_out, self.WMIN, self.WMAX, out=self.W_out)

    def reward(self, r, action=None, done=True):
        """Deliver reward. NM is reward MINUS what was expected (02: raw reward
        instead of RPE => chance, because it never stops reinforcing the known)."""
        zbar = self.trh_sum / max(self.trh_n, 1)
        if self.VALUE_STATE:
            # V(s) from cortical input, as striatum does -- not one global mean.
            # A scalar baseline is useless when reward arrives 2x in 25,000 acts.
            v = float(self.w_v @ zbar)
            nm = r - v
            # NORMALISED delta rule. A plain one diverges here: ||zbar||^2 ~ 100
            # (6 active units, trace ~5), so LR=0.05 predicts V~5 for r=1 after a
            # single step and accuracy collapses to 0.04 against 0.25 chance.
            # Dividing by ||z||^2 makes the step scale-free. Third magnitude bug
            # of this kind in the project -- see the eligibility sum and EMA.
            self.w_v += self.VALUE_W_LR * (r - v) * zbar / (zbar @ zbar + 1e-6)
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
            lr = self.LR
        if self.ACTION_GATED and action is not None:
            z = self.trh_sum / max(self.trh_n, 1)
            de = np.zeros_like(self.W_out)
            de[action] = z - self.ebar[action]
            self.ebar[action] += self.EBAR_LR * (z - self.ebar[action])
            self.W_out += lr * nm * de
            np.clip(self.W_out, self.WMIN, self.WMAX, out=self.W_out)
            self.elig[:] = 0.0; self.elig_w = 0.0
            self.buffer.append((z.copy(), de.copy(), nm, action, r))
            self.trh_sum[:] = 0.0; self.trh_n = 0
            self.decisions += 1
            if self.HIPPO: self.store_and_replay(zbar, action, r, done)
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
        self.ebar += self.EBAR_LR * (elig - self.ebar)
        self.W_out += lr * nm * de
        np.clip(self.W_out, self.WMIN, self.WMAX, out=self.W_out)
        # Consume the tag. Tag-and-capture: once the neuromodulator cashes the
        # eligibility, it is spent. Without this the tau~200 trace bleeds across
        # trials (200 ticks = 6.7 trials), averaging both classes together and
        # contaminating the update direction -- accuracy 0.58 vs 0.97.
        self.elig[:] = 0.0
        self.elig_w = 0.0
        if action is not None:
            self.buffer.append((self.trh.copy(), elig.copy(), nm, action, r))
        self.decisions += 1
        if self.HIPPO and action is not None:
            self.store_and_replay(zbar, action, r, done)
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
        # Hippocampal replay is OFFLINE: at every rest period, not only at the
        # moment of reward. Reward-triggered replay alone gives 8-32 events in a
        # whole run -- nowhere near turning 2 rewards into 2000 learning events.
        # 240 sleeps x HIPPO_N is what actually delivers that.
        if self.HIPPO and self.episodes:
            for _ in range(self.HIPPO_N): self._replay_one()
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
        np.clip(self.W_out, self.WMIN, self.WMAX, out=self.W_out)
        self.W_out *= self.DOWNSCALE
        if self.PRUNE_BELOW: self.W_out[self.W_out < self.PRUNE_BELOW] = 0.0
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
