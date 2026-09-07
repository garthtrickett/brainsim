# Plan

Where the project is, what to build next, and in what order. Ordering is by
**what we can measure**, not by what would help most in principle — five of the
six hypotheses tested on 2026-09-06/07 were wrong, and every unmeasurable result
came back plausible.

## Current state

Fully local. `TAGGATE` (winner-take-all on credit via a pooled inhibitory
threshold) replaced the non-local `ACTION_GATED` as the default.

```
                    2 cls    4 cls    8 cls
no-gate baseline    1.000    0.323    0.152
TAGGATE (shipped)   1.000    0.838    0.592
ACTION_GATED (opt)  1.000    0.959    0.900
```

Known limits, all measured:
- **Sparse reward defeats it.** Combination lock: ~2 rewards in 25,000 actions,
  so NM ~ 0 and there is no learning signal. Performance = random policy.
- **8-class gap.** 0.592 local vs 0.900 non-local.
- **Only `W_out` is plastic.** `W_in` is fixed; pretraining it is subsumed.
- **No cross-trial state.** Every trial is independent.

## Order of work

### 0. Harder tasks  <- IN PROGRESS
Everything is validated on synthetic pattern classification. Steps 5 and 6 have
no task that would exercise them, so building them now means no way to tell if
they work. Needs: a sparse-reward task, a volatile-reward task, a
representation-limited task, and a memory task — behind ONE task API and ONE
runner, so no experiment reimplements the loop.

Each task must ship with its chance level and a calibration showing the current
design lands in a usable band (not floor, not ceiling). Ablations on an
uncalibrated task are noise; that mistake cost 20 minutes on 2026-09-07.

### 1. Hippocampus — episodic store + time-compressed sequence replay
Targets the one failure we measured. Store the rare rewarded episode as a bound
conjunction; replay it hundreds of times offline. Turns 2 rewards into 2,000
learning events, and time-compressed replay collapses a 13-step sequence into a
window a short eligibility trace can span. Grows the existing sleep buffer:
dentate-style sparse separation (far sparser than k=6/80), CA3 recurrence,
prioritised replay of surprising/rewarded episodes.
Validates on: the combination lock (state-observable, so replay alone can crack
it — no working memory needed).

### 2. Neuromodulators beyond dopamine
State-dependent value baseline + NE-style adaptive noise. Cheap, attacks the
SAME failure as step 1, validates on the same tasks. A single global `value`
scalar is close to useless when reward arrives twice in 25,000 actions.
Validates on: sparse-reward and volatile tasks.

### 3. Basal-ganglia selection
Disinhibition (default blocked, winner released) + opponent Go/NoGo channels,
replacing `argmax(votes)`. Expect it to **retire `TAGGATE`** — anticipate that:
a new mechanism making an older one redundant is this project's most repeated
pattern (k-WTA retired the refractory period, `TARGET_RATE`, and threshold
homeostasis).
Validates on: the 8-class gap.

### 4. Cerebellum — consolidation, not capability
The sleep gradient already IS error-driven supervised learning with a teaching
signal. Naming it as a third learning system clarifies the architecture before
the two largest changes. Near-zero risk.

### 5. Predictive-coding hierarchy
The deepest structural gap but NOT the binding constraint: we measured that
representation was never the bottleneck (hidden codes separable at 0.549, better
than the 2-class case that worked at 0.622). It changes the representations every
prior result depends on, so it needs step 0's representation-limited task first.

### 6. PFC working memory, BG-gated
Depends on step 3 for the gate and step 0 for a partially-observable task.
Our failed `commitment` experiment belongs here: commitment is a PFC state held
deliberately and released by a gate, not a motor-layer trick.

## Method rules (earned the hard way)

- **Calibrate the task before ablating.** Floor and ceiling both make ablations
  meaningless.
- **Every experiment carries a gate** that must pass before its headline number
  counts. Gates rejected results in 3 of 6 experiments in Part 2.
- **Keep the reference number.** A broken port returns a plausible result, not an
  error. Twice: a reimplemented training loop, and a subclass that dropped
  synaptic scaling.
- **Never n=1.** Single-seed results were wrong three times, in both directions.
- **State every new module's timescale relative to the others.** Five failures
  were timescale mismatches: membrane, eligibility, homeostasis cadence, gate
  window, decision window.
