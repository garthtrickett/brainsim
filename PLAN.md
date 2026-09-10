# Plan

## V1 investigation closure (2026-09-08)

Remaining bounded investigations are closed; no new default is enabled. This
does not claim every proposed mechanism was implemented. Dispositions:

| Step | Result |
| --- | --- |
| 6 / 11 hierarchy / 13b | Fixed encoder generalises; registered gap absent; mechanisms deferred |
| 7 | Frozen table and accelerated implementation verified |
| 8 | Measured; no default gating change |
| 9 | Corrected fair pool comparison; no reliable gain without regressions |
| 10 | Explicitly deferred to continuous-time v2 |
| 11 model-based replay | Model backups do not beat matched real backups |
| 12 | Curiosity has no reliable external-reward gain |
| 13a | Context retrieval does not beat shuffled queries |
| 13c | Failure does not beat appropriate controls without regressions |

V3 §9's first standalone test is now complete: the registered candidate fails
advancement. See `V3-RESULTS.md`. No agent integration follows, and the further
v3 queue and v2 rewrite remain unactivated. The separately registered
mean-disagreement successor also reached closure: tuning-inconclusive at the
gain search boundary, with confirmation unrun. See `V3-SLICE-1-RESULTS.md`.
The new bounded gain follow-up resolved the search boundary but failed independent
detection when noise increased; performance remains unrun. See
`V3-GAIN-FOLLOWUP-RESULTS.md`. This follow-up is closed; no further item is activated.
A separately authorized persistent-detector test then passed passive observation
but failed six learning-coupled detection cells. It is closed before performance;
see `V3-PERSISTENT-RESULTS.md`. No subsequent item is activated.
The separately authorized reference-detector experiment passed detection but
failed independent learning advancement; see `V3-REFERENCE-RESULTS.md`. All its
stages are complete, with no default change or subsequent item activated.
The separately authorized bounded-burst experiment is also complete: learning-negative
against the strong controls, including a failed full SGD comparison for the tuned
perfect-timing oracle. See `V3-BURST-RESULTS.md`; no subsequent item is activated.
The separately authorized forgetting study is also closed: learning-negative despite
matched-control gains and improved oracle adaptation. Stable/noise tradeoffs remain;
see `V3-FORGETTING-RESULTS.md`. No further experiment or integration is activated.
The separately authorized interference-as-discovery study then tested §11.1
against a hidden-context ground truth and closed discovery-negative: no
localisation beyond the shuffled control, no conditioning benefit over random
splits or pooled prediction. See `V3-DISCOVERY-RESULTS.md`; no subsequent
item is activated.
The separately authorized oracle-schedule retention study then granted true
change times and composed a fast window with ADWIN2: the tradeoff held
(primary 0.083 against every control, every stable/noise cell against ADWIN
passed) but the experiment closed learning-negative on drift, which neither
component tracks. See `V3-RETENTION-RESULTS.md`. No further experiment or
integration is activated.
The separately authorized timing-tolerance study then perturbed the granted
schedule and scheduled the frozen candidate by ADWIN's own alarms: the win
survives ±2 steps and dies by ±8, tighter than any realistic detector, and the
deployable arm failed retention on false alarms. The detector line closes with
that number. See `V3-TOLERANCE-RESULTS.md`. No further experiment or
integration is activated.
The separately authorized drift-boundary study then granted ramp times to the
frozen candidate: drift failed at unchanged values with the enriched schedule
engaged, isolating a mechanism gap rather than an ontology gap. See
`V3-DRIFT-RESULTS.md`. No further experiment or integration is activated.
The separately authorized slope-state study then added a trend regime gated
on granted drift boundaries and closed the first full V3 positive (75/75),
beating SGD on the ramp with everything else preserved. See
`V3-SLOPE-RESULTS.md`. No default change or agent integration follows.
The separately authorized slope-timing study then gated that trend regime by
observed ADWIN alarms instead: false alarms on noise destroyed stability and
the primary win missed its 10% rule. See `V3-SLOPETIME-RESULTS.md`. No
further experiment or integration is activated.
The separately authorized slope broader benchmark then tested steep, shallow
and noisy ramps: steep and noisy pass, but the shallow ramp loses strictly to
the fast window, narrowing the mechanism to non-weak signals. See
`V3-SLOPEBENCH-RESULTS.md`. No further experiment or integration is activated.
The separately authorized kink-guarded slope study then forced fast means
near boundaries: the shallow gap narrowed threefold but the same strict cell
still fails. See `V3-SLOPEGUARD-RESULTS.md`. No further experiment or
integration is activated.
The separately authorized adaptive-window slope study then fit through the
kink with distance-dependent windows: the shallow gap narrowed to 0.000521
without closing, and local fitting stands structurally kink-blind. See
`V3-SLOPEWIN-RESULTS.md`. No further experiment or integration is activated.
The separately authorized drift-timing tolerance study then jittered granted
drift boundaries: the win survives ±256 and dies by ±1024, landing in the
pre-stated middle band that authorizes nothing. See `V3-DRIFTTOL-RESULTS.md`.
No further experiment or integration is activated.
The separately authorized V4 robustness study then tested graded response
under frozen lies: adaptation holds everywhere including primary, with only
stability failing to false alarms. See `V4-ROBUST-RESULTS.md`. No further
experiment or integration is activated.
The separately authorized slope-state study then added a trend regime gated
on granted drift boundaries and closed the first full V3 positive (75/75),
beating SGD on the ramp with everything else preserved. See
`V3-SLOPE-RESULTS.md`. No default change or agent integration follows.
The separately authorized V5 embodied study then grafted bursts and dual
value onto the frozen agent on noisy-volatile tasks: nothing beats the
ADAPTIVE baseline, and even oracle timing mostly shows no headroom. See
`V5-RESULTS.md`. No further experiment or integration is activated.
The separately authorized V6 exploration study then deviated from argmax on
narrow vote margins: harmful everywhere usable, catastrophically on lock,
with epsilon-correct headroom in the hundreds of points. See
`V6-RESULTS.md`. No further experiment or integration is activated.

`V1-RESULTS.md` records the current investigations and supersedes historical
numbers below. `DESIGN-v1-completion.md` contains their preregistered gates.
In particular, the 0.946→0.385 capacity ladder used an additive shape/colour
label; commit fc84358 changed the task to shape identity. It is not a measured
capacity limit of the current task. The corrected pool test evaluates both labels.

The original "Current state" and early per-step tables below are historical
snapshots. Use `README.md` and the unchanged eight-seed `reference.json` for
the shipped baseline, rather than reconstructing defaults from those snapshots.

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

### 0. Harder tasks  <- DONE
Everything is validated on synthetic pattern classification. Steps 5 and 6 have
no task that would exercise them, so building them now means no way to tell if
they work. Needs: a sparse-reward task, a volatile-reward task, a
representation-limited task, and a memory task — behind ONE task API and ONE
runner, so no experiment reimplements the loop.

Each task ships with a MEASURED floor (random policy) and MEASURED ceiling
(oracle), never analytic ones. Calibrated (`23_calibrate_tasks.py`, 4000
decisions, 3 seeds):

```
  task            floor    agent  ceiling   verdict
  nway-4         0.2527   0.8340   1.0000   USABLE (78% up)   <- ablation substrate
  nway-8         0.1221   0.6590   1.0000   USABLE (61% up)   <- ablation substrate
  lock-10        0.0010   0.0000   0.1110   FLOOR   <- target, step 2
  volatile-4     0.2500   0.2763   1.0000   FLOOR   <- target, step 1
  tmaze-2d3      0.1232   0.1267   0.2500   FLOOR   <- target, step 5
  xor-2          0.5011   0.7290   1.0000   USABLE  <- does NOT bind (see step 6)
```

Two usable ablation substrates (headroom in both directions -- the thing every
earlier experiment lacked) and three measured targets.

### 1. Neuromodulators beyond dopamine  <- DONE (half of it)
Moved ahead of the hippocampus. `volatile-4` sits at 0.276 against a 0.250 floor
on a task the design solves at 0.834 when stationary -- it does not degrade under
non-stationarity, it collapses to chance. A fixed learning rate and fixed
exploration are a hard wall, not a tuning shortfall.

Cheaper than step 2 and partly a prerequisite for it: a state-dependent value
baseline is what makes sparse reward learnable at all, since a single global
scalar is useless when reward arrives twice in 25,000 actions. NE-style adaptive
noise, ACh-style adaptive learning rate.
RESULT: half shipped.

```
                     volatile-4   nway-4    lock-10
  baseline             0.2763     0.8340     0.0000
  + V(s)               0.4720     0.9610     0.0003   <- SHIPPED
  + adaptive LR/noise  0.2873     0.9350     0.0003
  + both               0.2600     0.9837     0.0003
```

`V(s)` ships: it improves every task and regresses none (nway-8 0.659->0.769,
xor-2 unchanged). ADAPTIVE does not: it adds nothing on the task it was built
for AND cancels the V(s) gain when combined (0.260 vs 0.472). Two controllers on
one variable -- the second occurrence of that failure mode after the duelling
homeostatic controllers in Part 3b. Watch for it again in step 3.

Neither touched `lock-10`. Sparse reward is entirely step 2's job.

### 2. Hippocampus — episodic store + reverse replay  <- DONE (9.5 -> 333.5)
Targets the headline failure: `lock-10` scores 0.0000 against a 0.0010 floor --
BELOW random, because it learns the wrong thing from near-zero signal. Store the
rare rewarded episode as a bound conjunction and replay it hundreds of times
offline: 2 rewards become 2,000 learning events. Time-compressed replay also
collapses a long sequence into a window a short eligibility trace can span.
Grows the existing sleep buffer: dentate-style sparse separation, CA3 recurrence,
prioritised replay of surprising/rewarded episodes.
Validates on: `lock-10` (state-observable, so replay alone can crack it).

### 3. Basal-ganglia selection  <- SHELVED: its target gap was a bug (0.100 -> 0.018)
Disinhibition (default blocked, winner released) + opponent Go/NoGo channels,
replacing `argmax(votes)`. Expect it to **retire `TAGGATE`** -- anticipate that;
a new mechanism making an older one redundant is this project's most repeated
pattern (k-WTA retired the refractory period, `TARGET_RATE`, and threshold
homeostasis).
Validates on: `nway-8`, where local is 0.592 against 0.900 non-local.

### 4. Cerebellum  <- DONE: the answer was DELETE, not name
The sleep gradient already IS error-driven supervised learning with a teaching
signal. Naming it as a third learning system clarifies the architecture before
the larger changes. Near-zero risk.

### 5. PFC working memory  <- DONE (tmaze 0.51 -> 0.999)
Depends on step 3 for the gate. `tmaze-2d3` is at floor (0.127 vs 0.123) because
nothing persists across decisions. Our failed `commitment` experiment belongs
here: commitment is a PFC state held deliberately and released by a gate, not a
motor-layer trick.

### 6. Predictive-coding hierarchy — CLOSED: defer; fixed encoder passes held-out gate

Rechecked with frozen evaluation weights over eight seeds: unseen 0.751 versus
0.257 chance, seen 0.966. The specified at-chance prerequisite is absent.
This is not a negative experiment on predictive coding itself. See `V1-RESULTS.md`.
Twice now, measurement says representation is not the bottleneck:
- hidden codes were MORE separable at 4/8 classes (0.549) than at the 2-class
  case that worked (0.622);
- `xor-2`, built specifically so a fixed random encoder should fail, is solved at
  0.729. A sparse random projection plus k-WTA is GOOD at conjunctions -- the
  winning set depends on the input combination. That is why random feature
  expansions make XOR separable, and it is the cerebellar granule-layer
  architecture, which exists to build conjunctive codes.

Two attempts to construct a representation-limited task both failed to bind. A
third would need compositional generalisation to UNSEEN combinations or
invariance to nuisance transforms -- and a train/test split the runner does not
have. Do not build this until such a task exists and the current encoder
demonstrably fails on it.

### 5b. Split README.md  <- DONE (README = what it is, HISTORY.md = how it got here)
`README.md` is 794 lines and growing: a chronological log (Parts 1-11) where a
reader has to reconstruct the current defaults from eleven rounds of revisions,
several of which reverse each other. Two documents are needed:

- **README.md** -- what the design IS. Current architecture, current defaults
  with their measured justification, the task suite with floors and ceilings,
  how to run it. A reference, readable without history.
- **HISTORY.md** -- how it got here. Parts 1-11 as they stand, including every
  refutation, retraction and shelved design. This is the more valuable half and
  must not be trimmed: five mechanisms were validated honestly and later turned
  harmful, three verdicts reversed when their regime moved, and two designs were
  shelved unbuilt. A reader who sees only the final state learns none of that.

Do this after step 5 so the split is made once against a settled architecture,
rather than twice.

---

# Next: steps 7-10

Ordered by leverage, after the six-step roadmap closes. The first is
infrastructure rather than science, and that is exactly why it is first.

### 7. Freeze the numbers, then make the suite fast  <- DONE (2026-09-08)

`reference.json`, 8 seeds, external baselines. Port is bit-exact (12/12), 5-8x
faster, full build 470s. **brainsim beats every baseline on nway-4, nway-8,
tmaze and lock-10 -- lock by 38x over the best alternative, with tabular-Q at
0.000 -- and loses xor-2 and volatile-4 to tabular-Q, the one baseline with zero
interference.** See HISTORY.md Part 14.

The dominant failure of this project has not been bad mechanisms -- it has been
**measurement**. Four wrong conclusions from n=3. Six instruments that measured
something other than their name. Five mechanisms validated honestly and later
turned harmful, because **nothing re-checks a shipped component when its
surroundings change**. Every module broke something else, and each was caught
only by remembering to run a 20-minute suite.

Commit a reference table of `(seed, config) -> number`, then make the full suite
run in seconds. Every change is then diffed against everything, automatically,
and regime-drift largely dies as a failure mode. It also makes 50 seeds routine,
which kills the small-n problem. Everything after this is cheaper and safer.

Sequencing note: `numba` has its own RNG and batched draws differ from N separate
draws, so bit-exactness breaks unless random draws are pre-generated in numpy and
passed in as arrays. Design that in from the start, or the reference table cannot
validate the port.

### 8. Plasticity gating  <- DONE (2026-09-08): measured, SHIP NOTHING

Premise confirmed with a clean control (delay=0 at ceiling). But a PRIVILEGED
perfect gate recovers only `delay=1` (0.03 -> 0.65 of ceiling); at `delay>=2` it
does nothing and at `delay>=3` no configuration beats floor. No real gate can
beat the oracle, so the ceiling on step 8 is one narrow case. `WM_HOLD` (the
obvious memory fix) does nothing alone and trades delay=1 for delay=2 when
combined. See `DESIGN-plasticity-gating.md`.

The clean measured gap from step 5: **the design cannot absorb decisions that do
not matter.** An unrewarded arbitrary action draws a negative RPE into a policy
sharing hidden units with the step that counts. An ORACLE with the cue handed to
it still reached only 54% of ceiling on `tmaze-2d3` for this reason alone.

Ready task (the original `tmaze-2d3`), measured gap, and a real biological story:
gating plasticity is precisely what BG->PFC gating does. Should also help
`volatile-4`, the weakest task, by suppressing updates just after a switch.

### 9. Local competitive pools — DONE: corrected measurement, keep default off

Six seeds, five tasks, P=1/2/3/6 and k=6. No pooled setting shows a reliable
capacity gain without regressions. The inherited P=4/8 experiment changed total
sparsity and is archived as confounded. Full evidence: `V1-RESULTS.md`.

Step 6's calibration produced a measured capacity limit:

```
  4 stimulus combinations   train 0.946
  9 combinations            train 0.644
 16 combinations            train 0.385
```

With 80 units and k=6 that is not representation quality -- it is one global
competition forcing everything through a single pool. Local pools fix it AND are
the prerequisite for any scaling, and are what cortex does anyway.

### 10. Embodiment — DEFERRED to the continuous-time v2 fork

This is the disposition specified by the revised rule/substrate split in `V2.md`.
The v1 investigation closure does not claim an embodied or continuous-time agent.

The Part 1 design specified `BODY = {energy, temp, damage}` with reward as
homeostatic error. The implementation takes `reward(r)` from a task. **Embodiment
vanished at first contact with code and never returned.** Largest conceptual gap,
largest work, hence last -- but it is the difference between a learning algorithm
and the thing this project set out to build.

### 11. Predictive coding — CLOSED for v1; model backups do not beat real backups

The representation gate fails (the fixed encoder generalises), step 8 supplies
only a narrow gating result, and model-generated backups score 580.0 versus
596.2 for equal-count real backups on six lock seeds. No new default is enabled.
General precision weighting remains a v3 hypothesis. See `V1-RESULTS.md`.

Shelved twice, and the shelving was sound for the question asked -- but the
question was too narrow. We tested predictive coding as a **representation
learning algorithm** (does a learned encoder beat a fixed random one). That is
one application. In neuroscience it is mostly a hierarchical
prediction-and-error architecture supplying a learning signal to EVERY layer and
a precision-weighted gate on how much to trust each error.

Worse: step 6 probed the PREMISE (is there a representation gap?) and never the
MECHANISM (does PC close anything?). That is the same error that let the
hippocampus ship a headline which was actively harmful.

Three ways back in, one of which converges with step 8:

- **Precision weighting as the plasticity gate.** Step 8 needs a local signal for
  "how much should this decision teach me?" Inverse-variance weighting of
  prediction errors is the predictive-coding account of exactly that. If step 8's
  relevance gate works, precision weighting is its principled generalisation; if
  it fails, PC offers a better-motivated version of the same idea.
- **Generative replay -- a forward model that replays what did NOT happen.**
  Replay is our strongest mechanism (lock 9.5 -> 419) and can only replay what
  occurred. A learned forward model turns replay into planning: Dyna with a
  learned model. Uses the world model built in Part 1 and orphaned when curiosity
  failed. A capability jump, not a tuning gain.
- **An actual hierarchy.** We have ONE hidden layer. Predictive coding needs depth
  to be itself -- predictions descending, errors ascending. Testing it on a single
  layer was never a fair test of the theory.

Sequence after step 8, so its relevance gate either subsumes or motivates this.

### 12. Curiosity — DONE: measured again, keep off

Six lock seeds with external reward scored separately from intrinsic bonuses:
baseline 551.7; coefficients 0.1/0.5 yield 541.3/558.8, with broad paired
intervals spanning zero. No reliable discovery or total-reward improvement.

Cut in Part 2 for showing no effect at 0.1/0.3/1.0/3.0 across two environments.
That verdict predates the working world model, the corrected `decide()`, and the
lock's measured exploration wall -- ~4000 decisions to stumble on reward, and one
seed in five found none at all. Directed exploration is exactly what should help
there. `ADAPTIVE` was cut on similarly sound evidence and reversed once its
regime changed; this deserves the same re-examination.

### 13. LLM / deep-net second pass — CLOSED for v1; no new default

Sequence AFTER step 11, so predictive coding and Forward-Forward compete for the
same gap and can be ablated against each other rather than tested in isolation.

The constraint is what makes this useful: forcing "what problem was this actually
solving?" usually surfaces a biological answer.

**13a. Content-addressed replay -- attention as CA3 pattern completion.**
**DONE, keep off:** context 535.5 versus shuffled 539.8 and baseline 551.7 over
six lock seeds. No demonstrated query-specific benefit. See `V1-RESULTS.md`.
Self-attention is query-key matching: retrieve by similarity to what is being
processed NOW. That is exactly what hippocampal CA3 recurrence does -- partial
cue in, full episode out. Our replay samples by stored priority, which is blind
to the current situation. Smallest change, clearest warrant, and it improves our
strongest component (lock 9.5 -> 419).

**13b. Forward-Forward / contrastive local learning -- for the layer that never
learns.** Our deepest gap is that only `W_out` is plastic. Forward-Forward is the
deep-learning world's OWN backprop-free local rule: two forward passes, positive
and negative data, each layer optimising a local goodness objective. Contrastive
Hebbian learning and equilibrium propagation are the same family. Value here is
that it gives a SECOND independent candidate for the gap step 11 targets -- when
two mechanisms compete for one gap, the ablation means something.

**CLOSED, mechanism deferred:** the shared representation prerequisite fails in
the eight-seed frozen-evaluation test. The fixed encoder generalises above chance
in every seed. This does not experimentally refute Forward-Forward.

**13c. Synaptic failure as dropout -- nearly free.** Dropout was invented as
regularisation; real synapses fail to release 50-90% of the time, more aggressive
than any dropout rate in use. We have noise on motor units but deterministic
synapses. One line, strong warrant, plausibly helps the capacity limit step 9
targets.

**DONE, keep off:** six seeds on five tasks including the original capacity
target, with matched attenuation controls. No reliable stochastic-specific
capacity benefit; 50% failure hurts XOR in all six seeds. `V1-RESULTS.md` records
the full contrasts, including the small nway gain and its stronger control.

Also worth a look: divisive normalisation (Carandini-Heeger -- the brain's
LayerNorm, cheap and well established), and mixture-of-experts routing, which is
BG gating over cortical modules and pairs with step 9's local pools.

**The trap: "recurrence so it can think longer."** Chain-of-thought's analogue is
recurrent deliberation, and cortex is massively recurrent while our hidden layer
is feedforward per tick. But recurrence would interact with k-WTA, the
eligibility trace and replay simultaneously, and the evidence of this project is
that every added mechanism breaks something. Wants step 7's fast suite first, and
its own step rather than a slot in a survey.

**Excluded on principle:** backprop through layers; weight sharing across
positions (no synapse can copy another's weights); a global error vector; and
anything needing the whole dataset at once -- the premise is that learning
happens INSIDE a loop that never stops.

---

# brainsim v3 — the fluctuation thesis

See **`V3.md`**. Written 2026-09-08, nothing built. Orthogonal to the v2
substrate rewrite and testable in v1, which is the point of it.

The claim: **Adam keeps one second moment and always shrinks; brains keep at
least two, at different timescales, and their difference decides whether to
shrink or grow.** A single estimator cannot separate "this is noisy" from "this
just changed", which is exactly why `volatile-4` (0.420) is our worst task.

- §9 — the thesis, and why the original parsimony framing was really Adam
- §10 — the queue: differencing pair, reconsolidation, gate-spike event
  boundaries, variance spectrum, quiet-triggered replay, adaptive timestep
- §11 — further out: interference as a discovery signal, grown structure,
  forgetting as the default

Task work is scoped in **`DESIGN-tasks-v3.md`**: five additions, ordered, with
the finding that the current suite has *no reward noise anywhere* and so cannot
express the distinction §9 exists to make.

**Critical path: the §9 gate vs Adam on a non-stationary supervised toy. No
brainsim involved,** which also gives this project the external evidence it has
never had. Nothing in §10 or §11 starts before that has a number.

V3 absorbs step 8 (plasticity gating) and re-opens step 11 (predictive coding)
on a cheaper claim — temporal differencing with no hierarchy and no top-down.
**Step 7a remains a hard prerequisite**: every V3 prediction is a comparison.

---

# brainsim v2 — a fork, not an iteration

Four changes remove every GLOBAL operation in the design. Anything global is a
scaling killer: it forces every unit to coordinate with every other, and a brain
scales precisely because **no part of it ever waits for the whole.**

| global chokepoint now | v2 |
|---|---|
| every neuron evaluated every tick, 74 of 80 discarded | **event-driven** — only spikes propagate; saves roughly tick-rate ÷ firing-rate |
| k-WTA ranks all units against each other | **local pools** — each group competes within itself |
| trials halt everything every 30 ticks | **continuous time** — no global barrier |
| one neuromodulator scalar for the whole net | **parallel loops**, each with its own signal |

Two further changes are about being BETTER, not bigger, and should not be
confused with the above: recurrent settling dynamics (makes working memory
intrinsic rather than a bolted-on module that took four interface attempts), and
active inference as the foundation (unifies the orphaned world model, externally
supplied reward, and argmax action selection — and restores the Part 1 premise).

## Why a fork — REVISED: only continuous time forks

Checking the "they all interact" claim change by change, five of the six land
incrementally in v1 with parity checks (batching, numba, seed-generated
connectivity, local pools, parallel NM loops). Only **continuous time** breaks
the task interface, the runner, replay's episode definition and eligibility
consumption simultaneously.

So: freeze the reference (7a), land the substrate changes incrementally, run the
rule science (8, 11, 12, 13) on the resulting fast suite, and fork once at the
end for continuous time alone. See `V2.md` for the rule/substrate split.

## Original reasoning, kept

The four changes interact; none can land alone with anything still working. That
breaks the method this project runs on — change one thing, run the suite.

**v2 changes the machine, not the science.**

- **Carried forward:** the task suite (stimulus -> action -> reward ports to
  continuous time with a thin adapter), the measured floors and ceilings, the
  learning RULES that survived ablation (three-factor + RPE, reverse replay with
  TD bootstrapping, `TAGGATE`, `V(s)`), `HISTORY.md`, and the method rules.
- **Rebuilt:** the simulation core, the competition structure, neuromodulation,
  and the loop itself.

The validated rules become **hypotheses to re-test on the new substrate**, not
things to re-derive. That is the return on having ablated them properly.

## The discipline

v1 stays as the reference implementation. **v2 must beat it on the same tasks
against the same floors and ceilings before v1 is retired.** Otherwise there is
no way to distinguish a better architecture from a differently-broken one -- and
the record in HISTORY.md is a long demonstration that this cannot be judged by
reasoning alone.

This puts **step 7 on the critical path**: a frozen `(seed, config) -> number`
table with external baselines is what makes a v2 falsifiable at all.

## Cut, with reasons

- **Predictive coding AS REPRESENTATION LEARNING** -- twice shelved on
  measurement, about to be a third time. Note this is NOT the same as retiring
  predictive coding; see step 11.
- **Volatile-specific tuning** -- symptom, not cause. Step 8 addresses the likely
  cause.
- **Mojo** -- you would be porting an architecture step 9 is about to replace.

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
