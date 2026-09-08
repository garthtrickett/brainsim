# brainsim — history

How the design got to where it is. Chronological, Parts 1-12. **This is the more
valuable half of the documentation and must not be trimmed.**

Five mechanisms were validated honestly and later turned harmful when the regime
around them moved. Three verdicts reversed outright. Two designs were shelved
unbuilt. Six task instruments turned out to be measuring something other than
their name. A reader who sees only the final state learns none of that, and is
liable to re-add the pretrained encoder, rebuild the basal ganglia, or trust a
single-seed result.

For what the design **is**, see `README.md`.

The simplest AI I could design that works the way a brain works rather than the
way an LLM works — then implemented, ablated, and corrected until each part
earned its place or was cut.

The design is one loop that never stops. Learning happens *inside* it. That is
the whole difference from a transformer: this thing is changed by every second
it is alive, whereas an LLM is a photograph of a mind that finished changing
before you met it.

Nothing here is a useful model. It is a study of which brain mechanisms are
load-bearing and which are decoration, with numbers attached.

## The design

```text
# One tick ~ 1 ms. No train/infer split: this loop IS the model,
# and it rewrites itself while it runs.
# The design is a hierarchy of timescales. That is the trick.
#
#   v       membrane       ~20 ms   "what I'm hearing right now"
#   trace   spike trace    ~50 ms   "I fired a moment ago"
#   elig    eligibility    ~1 s     "I might deserve credit for this"
#   NM      neuromodulator ~200 ms  "...you did / you didn't"
#   rate    firing average ~minutes "am I pulling my weight?"
#   sleep   consolidation  ~hours   "keep what mattered, shrink the rest"

NEU  = [{v:0, thresh:1, fired:0, trace:0, rate:0,
         exc: i < 0.8*N} for i in 1..N]   # Dale's law: sign is fixed for life
SYN  = sparse_random()                    # .w .elig .ebar .delay in 1..20 ticks
BODY = {energy, temp, damage}             # set-points this thing must defend

loop forever:

  # 1 -- SENSE
  for n in SENSORY: n.inbox += encode(read_sensor(n))

  # 2 -- FIRE
  for n in NEU:
      n.v = n.v*LEAK + n.inbox + noise()  # noise is the ONLY source of "try
      n.inbox = 0                         # something different". Delete it and
      n.fired = n.v > n.thresh            # learning stops dead at chance.
      if n.fired: n.v = 0; n.refractory = 5

  # 3 -- COMPETE   (the inhibitory 20%, doing the real work)
  #  Without this, two different inputs produce nearly the SAME activity
  #  pattern (cos 0.81 -> 0.93) and nothing downstream can tell them apart.
  for pool in POOLS: keep top-K firing; silence the rest

  # 4 -- PROPAGATE
  for s in SYN where s.pre.fired:
      at (now + s.delay): s.post.inbox += (s.pre.exc ? +s.w : -G*s.w)

  # 5 -- ACT
  for m in MOTOR: actuate(m, m.trace)     # muscles integrate a rate, not a spike

  # 6 -- FEEL   dopamine is not reward, it is reward you didn't expect
  need    = distance(BODY, setpoints)
  reward  = need_before - need_now        # the body, and ONLY the body
  value  += 0.02 * (reward - value)
  NM      = reward - value                # broadcast to every synapse at once

  #  A world model runs alongside, learned by a LOCAL delta rule:
  surprise  = |sensed_now - predicted_last_tick|
  Wp       += LRp * outer(signed_error, trace)    # post-error x pre-activity
  predicted = Wp @ trace
  #  VALIDATED as a change detector. NOT wired into reward -- see below.

  # 7 -- LEARN   three factors, every one of them local
  for s in SYN where s.pre.exc:
      s.elig += s.pre.trace * s.post.fired   # pre-then-post -> credit
      s.elig -= s.post.trace * s.pre.fired   # post-then-pre -> blame
      s.elig *= ELIG_DECAY                   # tag fades over ~10 ticks
      s.ebar += 0.05 * (s.elig - s.ebar)     # what this synapse USUALLY does
      s.w    += LR * NM * (s.elig - s.ebar)  # credit the deviation, not the habit
  #  Nothing here knows the network's shape, its output, or any error signal.
  #  A synapse sees two neurons and one chemical. No backprop.

  # 8 -- STAY ALIVE
  for n in NEU:
      n.rate   += (n.fired - n.rate) / MINUTES
      n.thresh += ETA * (n.rate - TARGET_RATE)
  every 1000 ticks:                        # NOT 100 -- the two controllers need
      rescale incoming excitatory weights  # ~10x separation or they fight
      of each neuron to a fixed sum

  # 9 -- SLEEP
  pressure += weight_changed_this_tick     # you get tired by learning
  if pressure > THRESHOLD:
      unplug(SENSORY, MOTOR)               # dreaming needs the body offline
      repeat: replay(a stored burst, 10x speed, with its remembered NM)
      for s in SYN: s.w *= 0.98            # downscale ALL, preserve the ORDER
      prune(s where s.w ~ 0)
      pressure = 0
```

## What is load-bearing

Discrimination task, chance = 0.50, full design reaches 0.99-1.00 over four seeds
(`experiments/02_learning.py`):

| removed | accuracy | why it breaks |
|---|---|---|
| *(nothing)* | **1.00** | |
| local competition | 0.52 | representations collapse together; unlearnable |
| RPE -> raw reward | 0.50 | never stops reinforcing what it already does |
| eligibility trace | 0.53 | credit arrives after the cause is gone |
| noise | 0.50 | nothing to reinforce; no exploration |
| deviation term (`- ebar`) | 0.82 | reinforces habit alongside signal |

Network stability, target rate 0.0100/tick (`01_stability.py`, `06_controllers.py`):

| removed | result |
|---|---|
| *(nothing)* | settles at 0.0102 |
| threshold homeostasis | **90% of neurons go permanently silent** |
| inhibition | 0.0295, 3x target, synchronous bursts hitting 61% of the net |
| synaptic scaling | **51.6% of excitatory synapses pin at the ceiling**, cv 1.53 -> 0.89 |

That last row is the sneakiest failure in the repo: the firing rate reads a
perfectly healthy 0.0103 while representational capacity quietly drains away.

## What got cut or demoted

**`CURIOSITY` (surprise as intrinsic reward) — cut.** Tested at 0.1 / 0.3 / 1.0 /
3.0 across two environments. No effect survived a control check. The world model
itself is real (error 0.275 -> 0.190 against a noise floor of 0.096, so about
half the reducible structure; surprise jumps back to 0.258 within 300 ticks of
the world's rules changing) — but the wire from surprise into reward is not
justified by anything measured here, so it is left out.

**Refractory period — kept on a demoted claim.** My original justification
(bounds firing rate) is wrong: lateral inhibition already does that. Its real
contribution is rotating which cells win across ticks — 87% of cells used vs
80%, top-5% spike share 10.0% vs 17.8%. No measurable task effect.

## Known hard limit

`ELIG_DECAY = 0.90` gives the eligibility trace a time constant of ~10 ticks.
That is the longest causal chain the design can learn: cause and reward must
fall within ~10 ms of each other. A 13-step combination lock is provably
unlearnable — measured performance is identical to random policy (1.75 rewards
observed vs 1.53 expected by chance, `08_curiosity_lock.py`).

Step 9's sleep replay is the intended answer (compress a long sequence so the
trace can span it). It is **untested**, and is the most interesting untested
part of the design.

## A note on method

Six experiments, five of which were invalid on the first attempt:

- **04** swept input drive x1/x3/x8 and got *bit-identical* results — k-WTA
  selects by rank, so it is invariant to uniform gain. The manipulation did nothing.
- **07** and its predecessor both gave the control an environment it explored
  completely (30/30 states by tick 5000). A positive result was impossible.
- **06** ran to T=40k to fix a drift first measured at T=60k. Every config read
  "healthy" because the problem had not started yet.
- **08** put the task outside the design's credit-assignment horizon, so every
  condition performed at chance.

Every one of them returned a plausible number. None raised an error. The check
that caught them was always the same: *could the control condition have moved at
all?* Superseded versions are kept in `superseded/` rather than deleted.

## Running

```sh
pip install numpy
python3 experiments/02_learning.py     # the main ablation, ~2 min
```

Each script prints its own table and is self-contained. Recorded output for every
experiment is in `results/`. Runtimes range from ~1 to ~20 minutes.


---

# Part 2: importing silicon's advantages

Six proposals for giving the brain-shaped design some of what deep nets have,
without importing what makes them frozen, dense and ungrounded. Each was then
tested. **Not one survived in the form it was proposed.**

| # | proposal | verdict |
|---|---|---|
| 1 | copy the weights | true by construction; a brain cannot do this, a matrix can |
| 2 | parallel clones + merge | **half-holds.** Merging needs shared ancestry. Pooling is lossy |
| 3 | prioritised replay | **not supported.** +0.03 retention for -0.19 plasticity |
| 4 | multi-timescale traces | **inverted.** One long trace beats the bank I recommended |
| 5 | pretrained encoder | **works, wrong reason.** Gains are real; decorrelation is not the cause |
| 6 | gradient in the sleep slot | **supported**, for a one-layer readout only |

## 2 -- clone merging (`10_clone_merge.py`)

```
        solo   merged-CLONES   merged-INDEP   ceiling
mean    0.75       0.81            0.53        1.00
```

Merging independently-grown nets lands at chance: neuron 7 means something
different in each, so averaging destroys both. Clones of a common ancestor merge
fine. But the number that matters is the ceiling: 8 agents x 250 trials merged
gives **0.81**, while ONE agent trained on those same 2000 trials gives **1.00**.
Naive weight averaging recovers about a quarter of the gap. Pooling buys
wall-clock, not sample efficiency -- which is not what the proposal claimed.

## 3 -- prioritised replay (`12_prioritised_replay.py`)

12 seeds, of which only 4 exhibited any forgetting to prevent:

```
              A_retained   B_learned
none             0.68        0.95
uniform          0.63        0.91
prioritised      0.71        0.76
```

+0.03 retention at a cost of -0.19 on new learning. Per-seed the effect is
incoherent (+0.20, +0.01, +0.03, -0.14). An earlier 3-seed run showed +0.20 and
looked convincing; it was one lucky seed. Also worth noting: 8 of 12 seeds showed
no forgetting at all, so any future test here needs tasks *designed* to interfere.

## 4 -- eligibility trace horizon (`09_trace_horizon.py`, `14_lock_with_slow_trace.py`)

Delayed reward, with real interference filling the gap:

```
mode                D=0    D=20   D=60   D=150   mean
fast only (tau~10)  0.92   0.57   0.52   0.50    0.63
slow only (tau~200) 0.85   0.82   0.82   0.71    0.80
bank (10/33/200)    0.92   0.88   0.63   0.68    0.78
```

The horizon limit is real: a single fast trace collapses to chance as the gap
fills. But the *bank* I proposed loses to simply using one longer trace. Its
update direction is the average of its traces, and at long delays the fast ones
contain nothing but interference, so averaging signal with noise degrades it.
Equal weighting is the wrong design.

And the fix does **not** rescue the combination lock that motivated it (2.00 vs
1.53 expected by chance; two of three seeds produce byte-identical trajectories,
so the change did nothing at all there). The original diagnosis in `08` was
wrong: the lock fails because ~2 rewards in 25000 actions means there is almost
no learning signal to propagate. Trace length is irrelevant when NM is ~0.

## 5 -- pretrained sensory encoder (`11_pretrained_encoder.py`)

```
      overlap random -> pretrained    acc@200/400/900 random -> pretrained
s0      0.788 -> 0.862  [GATE FAILED]  0.54/0.53/0.84 -> 0.54/0.64/0.92
s1      0.630 -> 0.276  [OK]           0.79/0.95/0.99 -> 0.87/0.99/1.00
s2      0.682 -> 0.679  [~unchanged]   0.67/0.92/0.98 -> 0.80/0.95/1.00
```

Accuracy improves in every seed, largest early -- the sample-efficiency claim
holds. But overlap went UP in one seed and was unchanged in another, so
decorrelation is NOT the mechanism. The intervention works; my explanation for
why was wrong, and I do not know the real one.

## 6 -- gradient descent in the sleep slot (`13_sleep_gradient.py`)

The elegant part of the proposal: silicon's training run and the brain's sleep
occupy the same slot, so gradient learning can go there without touching the
always-on local loop.

```
means (acc@200 / 400 / 900)
local-only     0.73 / 0.87 / 0.95
local-replay   0.78 / 0.92 / 0.96     <- controls for the extra updates
sleep-grad     0.83 / 0.98 / 1.00
```

The first version of this test was confounded: the gradient arm got 60 extra
updates the control never did, so the win might have been replay rather than
gradient. With update counts matched, replay explains part (+0.05) and the
gradient adds more on top (+0.06), better in 5 of 5 seeds. Supported -- but this
is a ONE-LAYER readout, so it shows an error-driven update beating a
reward-modulated Hebbian one, not that backprop helps a deep network.

## Method note for part 2

Every experiment carries a sanity gate that must pass before its headline number
counts -- ceiling must exceed solo, pretraining must change overlap, the control
must actually forget. Those gates rejected results in 3 of 6 experiments, and in
one case (claim 5) revealed a real effect with a wrong explanation, which no
amount of staring at the accuracy column would have caught.

Of six claims, one was inverted by its own test, one dissolved under more seeds,
one worked for the wrong reason, one held only half, one needed a confound
controlled before it meant anything, and one needed no test. The mechanistic
reasoning that produced the ranking was decent at picking which interventions do
*something* and unreliable at explaining *why* -- and the why is what you would
use to design the next round.


---

# Part 3: the mainline (`brainsim.py`)

The validated upgrades, assembled into one runnable implementation. `python3 demo.py`.

**Assembling individually-validated components broke it.** First assembly scored
0.58 where a subset of the same parts reaches 1.00 in `02_learning.py`. Nothing
was wrong with any single piece; both failures were interactions:

- **`TARGET_RATE` did not transfer.** 01 validated threshold homeostasis at a 1%
  target on a recurrent net with **no k-WTA**. Under competition, k/n = 7.5% of
  cells fire by construction, so a 1% target asks for a rate competition
  forbids: thresholds ratcheted 1.00 -> 6.42. Now set from `k/n_hidden`.
- **The long trace bled across trials.** tau~200 spans 6.7 trials of 30 ticks, so
  eligibility averaged both classes together. Fixed by *consuming* the tag when
  the neuromodulator cashes it (tag-and-capture). Worth 0.58 -> 0.97.

With both fixed, the long trace is decisively right: **0.99 (tau~200) vs 0.74
(tau~10)** -- 09's finding reproduced in the assembled system, which it was not
before.

## A magnitude bug, twice, in opposite directions

A raw eligibility *sum* at tau~200 accumulates ~200x one outer product and
saturates the weights (this invalidated experiment E). Switching to an EMA fixed
that and introduced the inverse: an EMA reaches only `1-d^T` = 14% of steady
state over a 30-tick trial, making updates ~7x too small. The local rule then
topped out at 0.66 and **the sleep gradient silently covered for it** -- the
gradient looked worth +0.34 when it is worth +0.13.

Both versions ran fine and produced plausible numbers. The fix is to divide by
accumulated EMA weight, giving a true weighted mean at any decay, so a trace's
time constant and its magnitude are finally independent.

## Final validation

```
learns                       0.65 -> 0.98
local rule alone                     0.85     (02 gets 1.00 without the
+ sleep gradient                     0.98      homeostatic machinery)
save / load round-trip       0.95 -> 0.98
clone merge, 5 seeds         solo 0.95 -> merged 0.98, better in 4/5
merge guard                  raises ValueError on non-clones
```

| # | proposal | in the mainline? |
|---|---|---|
| 1 | copy the weights | **yes** -- `save`/`load` |
| 2 | clone merge | **yes**, guarded: refuses non-clones rather than failing silently |
| 3 | prioritised replay | **no** -- but uniform replay stays in sleep |
| 4 | long eligibility trace | **yes** -- tau~200, 0.99 vs 0.74 |
| 5 | pretrained encoder | **no** -- subsumed by #6 (see Part 3b; earlier "harmful" was an artifact) |
| 6 | gradient in the sleep slot | **yes**, +0.13 |

## The result worth keeping

**Claim 5 passed a clean 3-seed test with a sanity gate, in isolation, and makes
the assembled system worse**: 0.98 -> 0.85 with the gradient on, 0.85 -> 0.72
with it off, consistent across 6 seeds and both settings. Nothing about the
isolated experiment was wrong. The benefit simply does not survive contact with
the other components. `pretrain_encoder()` is kept with both sets of numbers in
its docstring and a do-not-enable note, because the reversal is more informative
than either result alone.

Claim 2 nearly went the same way: the demo's single-seed merge check said merging
*hurt* (0.65 vs 0.73). Measured properly over 5 seeds with solo and ceiling
controls, it helps (0.98 vs 0.95). One seed was wrong in the other direction that
time -- which is the same lesson, not a different one.

## Not claimed

The local rule reaches 0.85 in the mainline against 1.00 in `02_learning.py`. The
likely cost is the homeostatic machinery -- threshold adaptation, synaptic
scaling, the 0.98 downscale each sleep -- that 02 does not have and that exists
for stability reasons validated in 01/03/06. That is a measured
performance-for-stability trade, not an optimised one.

Everything here is validated on **one two-class discrimination task**, which is
thin ground for a design with this many interacting parts.


---

# Part 3b: the homeostasis was the problem

Part 3 shipped with the local rule at 0.85 against 02_learning.py's 1.00, blamed
on "the homeostatic machinery", and left unoptimised. That attribution was wrong.
Ablating each piece (`15_homeostasis_cost.py`, local rule only, 5 seeds):

```
  mainline as shipped          0.90
    - threshold homeostasis    0.98      <- removing it closes the gap
    - synaptic scaling         0.81      <- removing it HURTS
    - sleep downscale          0.92
    - pruning                  0.90      <- bit-identical: a no-op
    - ALL FOUR (gate)          0.58      <- collapses; they interact
```

They pull in opposite directions, so "the homeostatic machinery" was never one
thing. Three corrections:

**Threshold homeostasis is counterproductive here, and now defaults to 0.**
It exists to stop cells going silent. Over 3000 trials it *causes* more silence
than it prevents (`16_threshold_homeostasis.py`):

```
  ETA_TH=0.02   acc 0.99   fire_rate 0.0318   silent 23%   thresh drifts to 2.21
  ETA_TH=0      acc 1.00   fire_rate 0.0750   silent 15%   thresh stays 1.00
```

It is per-cell: winners fire often, so their thresholds get pushed UP, while
k-WTA goes on selecting by rank -- penalising exactly the informative cells.
0.0750 is k/n, the rate competition enforces by construction. 01's result still
holds for RECURRENT nets; the constant is kept for them.

**Pruning is a no-op.** `np.clip(W_out, 0, ...)` already sets weights to exactly
zero, so nothing is ever left below the threshold. Ablating it is bit-identical.

**Synaptic scaling is load-bearing for LEARNING**, not only against saturation:
removing it drops the local rule 0.90 -> 0.81. Part 2 had it filed the other way.

## Claim 5 was wrongly convicted

Part 3's headline -- "an intervention that passes in isolation and makes the
assembled system worse" -- was measured with ETA_TH=0.02. With the bad default
removed (`17_claim5_recheck`, 6 seeds):

```
  sleep-grad on   pretrained 0.95  vs random 0.97   (@400; both 1.00 late)
  sleep-grad off  pretrained 0.84  vs random 0.75   (@400; both 0.96 late)
```

It HELPS the local rule by +0.09 and is neutral once the gradient is on. It stays
off by default because the mainline ships the gradient, which subsumes it -- not
because it does damage. The subsumption hypothesis I recorded as REFUTED in Part 2
was refuted against a broken baseline and is now supported.

## The pattern worth keeping instead

Three mechanisms have now proved redundant or harmful *specifically because of
k-WTA*, each validated honestly on the recurrent net first:

- the refractory period (04) -- competition already bounds firing rate
- `TARGET_RATE=0.01` (Part 3) -- competition forbids that rate outright
- threshold homeostasis (15/16) -- competition selects by rank, so equalising
  thresholds only penalises informative cells

The rule is sharper than "re-measure constants in a new architecture". **Adding
one mechanism can retire another entirely**, and the retired one keeps running,
still looking principled, still costing you -- and it can convict an innocent
third component, as it did claim 5.

Mainline after the fix: **learns 0.58 -> 1.00**, gap to 02 closed.


---

# Part 4: the two-class ceiling was a bug, not a limit

Everything through Part 3b was validated on ONE two-class task solved at 1.00.
Pushed to more classes, the design collapses to near chance -- and six
hypotheses were needed to find out why. Five were wrong.

```
   classes   shipped (local)   action-gated
      2          1.000            1.000
      4          0.323            0.959
      8          0.152            0.900
```

## What it was not

- **not the sign constraint.** W_out is clamped non-negative, so a cell can only
  give evidence FOR a class. Allowing negative weights: 0.317 vs 0.323. No effect,
  so Dale's law on the readout is free.
- **not representation.** Hidden codes were separable the whole time, and MORE so
  at 4/8 classes (overlap 0.549) than at 2 (0.622).
- **not initialisation symmetry** (0.332 vs 0.323), **not the deviation term**
  (0.314 vs 0.323 -- though removing it does cost 1.00 -> 0.949 at 2 classes,
  confirming 02).

## What it was

Instrumentation, not reasoning, found it (`18_class_cliff_diagnostic.py`):

```
              acc     motor firing   vote margin   hidden overlap   W_out spread
  2 classes  1.000    1.71/2 (85%)       7.7           0.622           0.402
  4 classes  0.318    3.37/4 (84%)       0.6           0.549           0.031
  8 classes  0.150    6.62/8 (83%)       0.6           0.554           0.023
```

`elig = outer(fm, trh)` credits EVERY motor cell that fired, not the one chosen.
At 2 classes the count difference still favours the winner. At 4+ the counts are
nearly equal, so the update is nearly uniform, W_out never differentiates (0.03
vs 0.58), the vote margin sits at 0.6 spikes -- a coin flip -- and the loop is
self-locking: no differentiation, no margin, no differentiated credit.

## The fix is non-local, and two local alternatives failed

`ACTION_GATED=True` credits the SELECTED action. It is the one non-local element
in the design: a synapse cannot know what the whole network chose. Defaulted ON
because a strictly local rule caps at binary choice, with a flag to turn it off.

Two local mechanisms were tried:

- **motor k-WTA** (1-of-N per tick, `19_local_alternatives.py`): 0.319 / 0.158.
  Per-tick winners smear credit; the decision is a 30-tick aggregate.
- **commitment** (accumulate to a bound, then lock, `20_commitment.py`):
  0.350 / 0.168, and bimodal across seeds (0.50/1.00/0.50 at 2 classes). Locking
  on noise is self-fulfilling: only the locked cell fires, so only it gets credit
  and it cannot escape. Traded smeared credit for a deadlock.

So the honest statement is: **within this design, aligning credit to a
trial-level decision requires a non-local signal.** That is a real limit of the
biological premise, not a detail.

## Two retractions

**"Too hard" was wrong.** Six task configurations were declared too hard during
calibration. The task was fine; the learning rule was broken above N=2. The
instrument was reporting a defect in itself.

**The port was broken, and the control caught it.** Shipping action-gating into
brainsim.py first gave 0.243 at 8 classes against the standalone's 0.919, because
`z = self.trh / 30.0` (the FINAL tick's trace) was copied from the sleep-gradient
path instead of the tested running mean. Without the standalone number to compare
against, 0.243 vs 0.125 chance would have read as "helps a bit, does not scale" --
a finding about the method rather than a bug in the port. Second occurrence of
this exact error today; the first invalidated experiment E.


---

# Part 5: the fix can be local after all

Part 4 shipped ACTION_GATED as the default -- the one non-local element -- because
a strictly local rule capped at binary choice. That is no longer true.

**TAGGATE**: a synapse tags only if its own cell clears a threshold set by a
pooled inhibitory interneuron. Winner-take-all on CREDIT over the trial, not on
firing per tick (which is where motor k-WTA failed). A cell needs only its own
activity and one pooled inhibitory signal -- both local.

```
                        2 cls    4 cls    8 cls
  no-gate baseline      1.000    0.323    0.152
  TAGGATE (shipped)     1.000    0.838    0.592
  ACTION_GATED (ref)    1.000    0.959    0.900
```

Recovers 81% of the gap at 4 classes, 59% at 8, and breaks nothing at 2.
ACTION_GATED remains available as an opt-in accuracy mode.

## THETA had to be 1.0, and that nearly buried the result

The first sweep tried THETA of 0.80 and 0.95 and looked like a dead end. A smoke
test explained why: motor traces sit at `[9.53 9.48 9.53 9.48]` -- **0.5% apart**,
so any threshold below ~0.99 admits every cell and gates nothing. The mechanism
was never engaged. Exact-max selection is the real WTA.

## The gate window trades alignment against exploration

The gate reads `trm`; the decision is `argmax(votes)` over the whole trial. Too
short a trace and the gate tags whoever leads at that instant, not the eventual
winner. Too long and an early lead locks in and cannot be overturned -- costly
with more competitors, since the early leader is right only 1/N of the time.

```
                  8 classes   4 classes
    TRM_D=0.90      0.672       0.602
    TRM_D=0.97      0.592       0.838     <- default: best average, no collapse
    TRM_D=0.99      0.244       0.959     <- MATCHES the non-local reference at 4
    TRM_D=1.0       0.292       0.503     <- never forgets; early lead locks in
    ACTION_GATED    0.900       0.959
```

**Tuned to its task the local mechanism matches the non-local one exactly**
(0.959 vs 0.959 at 4 classes, seeds 0.96/0.96/0.96). The optimum inverts between
4 and 8 classes, so the default is the robust middle rather than either peak.
TRM_D=1.0 -- the predicted answer -- is worse than both its neighbours everywhere.

PERSIST (recurrent self-excitation) is in but OFF: +0.28 at 4 classes, -0.07 at 8,
near-nothing alone. A default whose sign depends on the task is a coin flip.

## Method note

An earlier version of this experiment used a SUBCLASS that reimplemented step()
and silently dropped synaptic scaling, degrading every row including the
reference (ACTION_GATED read 0.792/0.632 instead of its true 0.959/0.900). Caught
only because the reference had a known value. The mechanisms now live in BrainSim
itself and are toggled by attribute -- one implementation, nothing to drift.
Second occurrence of this exact error; the first invalidated experiment E.

**Five of the failures in this project were timescale mismatches**: membrane,
eligibility, homeostasis cadence, gate window, decision window. That is the
signature failure mode of this design, not a series of unrelated bugs.


---

# Part 7: neuromodulators — half of the proposal survived

Promoted ahead of the hippocampus because `volatile-4` sat at 0.276 against a
0.250 floor on a task the design solves at 0.834 when stationary: it does not
degrade under non-stationarity, it collapses to chance.

```
                     volatile-4   nway-4    lock-10
  baseline             0.2763     0.8340     0.0000
  + V(s)               0.4720     0.9610     0.0003   <- SHIPPED
  + adaptive LR/noise  0.2873     0.9350     0.0003
  + both               0.2600     0.9837     0.0003
```

**`V(s)` ships.** A learned linear value readout from the hidden trace replaces
one global scalar baseline -- striatal value coding, learned by a local delta
rule. It improves every task and regresses none: nway-4 0.834 -> 0.961, nway-8
0.659 -> 0.769, volatile-4 0.276 -> 0.472, xor-2 unchanged.

**`ADAPTIVE` does not.** It adds nothing on the task it was built for (0.287 vs
0.276) and CANCELS the V(s) gain when combined (0.260 vs 0.472 alone). Two
adaptive signals fighting over the same variable -- the same failure as the
duelling homeostatic controllers in Part 3b. **Two controllers on one variable
is this project's second recurring failure mode**, after timescale mismatch.

## Two bugs, both caught by a 3-line smoke test

**The value readout diverged.** ||zbar||^2 ~ 100 (6 active units, trace ~5), so a
plain delta rule at LR=0.05 predicts V~5 for r=1 after ONE step; accuracy 0.04
against a 0.25 floor. Normalised LMS fixes it. Third magnitude bug of this exact
shape, after the eligibility sum (200x too large) and the EMA (7x too small).

**The volatility signal fired permanently.** I cited Behrens -- learning rate
should track volatility, not noise -- then implemented a detector on |RPE|, which
is large simply because reward is binary. That IS noise. It doubled LR and
exploration forever: 0.015 against a 0.25 floor. It now watches for a sustained
gap between fast and slow REWARD RATE, which spikes at a switch and decays.

Neither was visible from reading the code; both look reasonable.

## A horizon artifact, corrected

A 1200-decision diagnostic showed V(s) at 0.313 against a 0.417 baseline and I
flagged it as a likely loss. At the calibrated 4000 decisions it is 0.472 vs
0.276 -- a clear win. The short check had not converged. Trust the calibrated
length over the quick one.


---

# Part 9: hippocampus — the sparse-reward wall breaks

`lock-10` had been the project's hard failure since it first returned at chance:
9.5 rewards in 12000 decisions against a ~12 floor and ~1333 ceiling.

**9.50 -> 333.50 rewards. 35x. From 0.7% of ceiling to 25%.**

```
  no replay (baseline)          9.50
  rev, no trace, TD           333.50   <- SHIPPED
  fwd, no trace, TD             4.17   <- direction matters 80x
  rev, no trace, NO TD          2.83   <- bootstrapping essential
  rev, compressed trace, TD   115.50   <- the trace COSTS 3x
  rev, uncompressed trace, TD 133.00
```

The mechanism is **reverse replay with TD bootstrapping**. Both are necessary;
either alone collapses. Reverse works for the standard reason: updating backwards
leaves each state's successor already fresh, so credit crosses a whole episode in
one pass instead of one step per pass.

## The borrowed biology held; the invented mechanism did not

Reverse replay is a documented hippocampal phenomenon (Foster & Wilson 2006) and
it carries an 80x effect. Time-compressed trace-spanning was MY contribution, was
the design document's headline, survived a six-probe refinement loop, and is
worse than useless -- removing the trace entirely takes 115.5 to 333.5.

The refinement loop caught five wrong assumptions and missed this one because it
probed the PREMISES and never the MECHANISM CLAIM. The arithmetic I verified most
carefully -- trace 0.222 uncompressed vs 0.860 compressed -- was correct and
irrelevant, since the trace should not have been there at all.

## The regression suite earned itself

Ungated, replay damaged three other tasks: nway-4 0.961->0.890, xor-2
0.722->0.518, volatile-4 0.472->0.305. All are single-step episodes, where
reverse replay has no sequence to work on and merely duplicates the online
update -- and on a volatile task replays contingencies that have since changed.

Gating on `len(episode) >= 2` removed every regression at zero cost. This is the
fourth time a module validated on its target broke something else, and the first
time it was caught before shipping.


---

# Part 10: a five-line bug, and three conclusions that flipped

`decide()` was written when `n_motor` was always 2 and never updated when it
became a parameter:

```python
if v[0] == v[1]:                     # compares only the FIRST TWO
    return int(self.rng.random() < 0.5)   # returns 0 or 1, ignoring actions 2..n-1
```

Vote counts are small integers, so ties are common. **Every n>2 result in this
project was measured with a decision rule that sometimes discarded the vote and
coin-flipped between actions 0 and 1.**

Found by a prediction failing *impossibly*: at `TRM_D=1.0` the gate's accumulator
and the decision's accumulator are the SAME ARRAY, so agreement had to be 100%.
It measured 38.8%. A vague prediction ("alignment should improve") would have
read 38.8% as a disappointing-but-plausible result.

## What changed

```
              before   after
  nway-4       0.961   0.999      tagged==chosen  89.6% -> 97.4%
  nway-8       0.769   0.938      tagged==chosen  67.3% -> 82.3%
  xor-2        0.722   0.721      (2 actions, unaffected -- correct)
  lock-10      333.5   330.8      (2 actions, unaffected -- correct)
```

## Three conclusions flipped

**Step 3 (basal ganglia) is SHELVED, unbuilt.** Its entire justification was a
0.100 gap at nway-8. Post-fix the gap is **0.018** (0.938 vs 0.956). The probes
had already weakened both rationales: signed weights recover only 22% of what
remains, and selection was never the failure -- credit alignment was.
Disinhibition and Go/NoGo would have been an elaborate answer to a tie-breaker.

**`V(s)` is a TRADE, not the clean win step 1 claimed.** Post-fix: nway-8 +0.103,
xor-2 +0.054, lock-10 essential (330.8 vs 65.6), **volatile-4 -0.125**. The step 1
claim "improves every task and regresses none" is retracted.

**`ADAPTIVE` now SHIPS.** Step 1 rejected it for cancelling `V(s)`; that was
measured under the bug. Corrected, they are complementary -- `V(s)` must relearn
every state when contingencies permute and `ADAPTIVE` is the repair:
volatile 0.278 -> 0.419.

## The pattern

Each original measurement was CORRECT IN THE REGIME IT WAS TAKEN IN. None was
sloppy. The regime changed underneath them. That is the measurement-scope rule
applied to one's own shipped results, and it is now the third time tonight a
verdict reversed when its substrate moved (the sleep gradient at n=3 vs n=6;
V(s); ADAPTIVE).


---

# Part 11: step 4 — the cerebellum was a deletion

The plan said "name the sleep gradient as the third learning system". Naming is
descriptive and cannot be wrong, which makes it useless as a step. The real
question: **does the thing I would be naming still work?**

It was validated in Part 3 at +0.06 over MATCHED local replay, 5/5 seeds --
before `V(s)`, before the hippocampus, before the `decide()` fix. Four regime
changes. It is now net negative.

```
                             nway-8    xor-2   volatile      lock-10
  shipped                     0.882    0.756      0.419        282.4
  - local replay              0.967    0.756      0.271        419.4
  - local replay - downscale  0.988    0.722      0.450        433.2   <- SHIPPED
  - ALL sleep                   --       --         --          60.2   <- collapse
```

`sleep()` now reduces to **hippocampal replay alone**. The local replay loop (which
contained the gradient pass) and the 0.98 downscale are both off. The downscale
was the worst of them: it shrank exactly the weights replay had just
strengthened, costing 151 rewards on the lock.

Final: nway-8 **+0.106**, volatile **+0.031**, lock-10 **+150.8 (53%)**,
xor-2 -0.034, nway-4 and tmaze unchanged.

## The arm I nearly read without checking

`- ALL sleep` scored best on nway-8 (0.988) in the decomposition. It also
**collapses the lock to 60.2** because it kills hippocampal replay too -- they
live in the same method. I had not measured the lock under that arm. Reading the
decomposition table alone would have deleted the mechanism that broke the
sparse-reward wall.

## Fifth of its kind

Fifth mechanism validated honestly and later turned harmful when the regime
moved, after the refractory period, `TARGET_RATE=0.01`, threshold homeostasis,
and the pretrained encoder. The pattern is not carelessness in the original
measurement -- each was correct when taken. It is that **nothing re-checks a
shipped component when the thing around it changes.**


---

# Part 12: step 5 — working memory, and four wrong interfaces

`tmaze-2d3` was at floor (0.124 vs 0.123). Two things had to be fixed before a
module could even be evaluated.

## The task was not a memory test

An ORACLE with the cue handed to it at decision time reached **54% of ceiling**.
Memory could not be the missing piece if perfect memory does not help. Suppressing
learning on the unscored steps took cue-visible from 54% to **99%** -- so
`tmaze-2d3` was measuring *tolerance of irrelevant decisions*, with memory buried
underneath.

That is an architectural gap worth naming on its own: **the design cannot absorb
decisions that do not matter.** An unrewarded arbitrary action draws a negative
RPE that corrupts a policy sharing hidden units with the step that counts. The
lock survives multi-step episodes only because every state there has a correct
action. `TMazeWithin` fixes the confound at the task level: cue, delay and choice
become phases within ONE scored decision. Calibrated: cue-visible 1.000,
cue-hidden 0.505 against a 0.504 floor -- a clean 0.50 gap only memory can close.

## The mechanism was right first time; the interface was wrong four times

| attempt | memory task | everything else |
|---|---|---|
| shared `W_out` | 0.897 | lock **-94%** |
| separate zero-init pathway | 0.998 | lock -86% |
| replay corrects both pathways | 0.996 | lock -95% -- *worse*, refuting my diagnosis |
| residual (orthogonal to current input) | 1.000 | lock **+49**, volatile below floor |
| + normalised update | 0.999 | shipped |

Sharing `W_out` injected memory through weights trained for `fh`. A separate
pathway still duplicated it wherever `wm` is a scaled copy of `trh` (constant
observation within a decision). The residual -- feeding the pathway only what the
current input does not explain -- silences it exactly there. The final
normalisation is the **fourth** magnitude bug of the same shape in this project,
after the eligibility sum, the EMA, and `V(s)`: an unnormalised delta rule lets
weights grow until a near-zero input produces a large drive.

**A new module's interface is a design decision with its own failure modes,
independent of whether the module works.**

## Shipped

```
  tmaze-within d30   0.529 -> 0.999      d60  0.505 -> 0.999
  xor-2              0.761 -> 0.839
  nway-4/8           within noise
  volatile-4         0.463 -> 0.424
  lock-10            419.0 -> 339.8  (-19%, still 34x the no-replay baseline)
```
