# brainsim

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
