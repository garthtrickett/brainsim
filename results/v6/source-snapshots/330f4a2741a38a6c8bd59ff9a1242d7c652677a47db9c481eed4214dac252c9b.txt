# Registered V6 margin-directed exploration experiment

Protocol `v6-explore-20260910-v1`. The operator authorized the one axis no
study has touched: *where* to explore, not how much. The agent already
accumulates motor votes it never uses except through argmax; narrow vote
margins mark genuine uncertainty, and the frozen runner already randomizes
exact ties. This experiment deviates from argmax preferentially on narrow
margins, with an epsilon-correct oracle twin bounding the value of
exploration itself. Register before study observations. Preserve all
earlier protocols, scientific sources, evidence and twenty CI workflows. No
dependency change; agent defaults unchanged; all new knobs default off.

## Hypothesis and why this follows V5

V5 closed the volatility line: bursts add nothing (strong ones harm),
dual value cannot convert demonstrated headroom, and the ADAPTIVE baseline
stands on noisy-volatile tasks. Every tested mechanism modulated learning
*rate* or *memory* — none touched action *selection*, which still runs
argmax plus undifferentiated motor noise. Exploration is therefore the only
unprobed axis, and vote margins are the observable that should drive it:
post-switch confusion and sparse-lock uncertainty both present as narrow
margins, exactly where random probing beats committed error.

Falsifier, stated in advance: no margin-directed explorer beats the frozen
baseline while the epsilon-correct oracle shows headroom. A pass needs the
paired interval above zero AND the oracle above the explorer (else the task,
not the arm, did the work). Any positive justifies only a separately
authorized benchmark, never a default change.

## Tasks: frozen-usable, no new calibration stage

Three tasks, all usable on frozen numbers (no new calibration measurements
are needed because floors, ceilings and baselines already stand archived):

- volatile-4 (deterministic switching): floor 0.251, baseline 0.371,
  ceiling 1.000 → position ≈16%.
- noisy-volatile-4 σ=0.5 (V5): floor 0.2495, ceiling 1.0000, baseline
  0.3638 → position ≈15%.
- lock-10 (sparse reward, where exploration matters most): floor 12.5,
  baseline 415, ceiling 1333 → position ≈30%.

Decisions follow frozen scales: 2100 for volatile tasks (7 switches),
12000 for lock (total-rewards metric, per the frozen table). If any task's
remeasured baseline in-study falls outside 10–90%, that task closes without
a verdict rather than passing or failing arms on it — the USABLE rule
survives without a calibration stage.

## Intervention arms (subclass flags, frozen base untouched)

V6 adds no code to brainsim.py: exploration lives in a `ExploreAgent`
subclass (`v6_agent.py`), so the frozen agent — and every prior study bound
to it — cannot change. With both flags off, `decide()` delegates to the
frozen implementation (bit-identical by construction, asserted in parity)
while still recording margin traces. All new knobs default off:

- **baseline:** frozen defaults. The bar everything clears.
- **exploreA / exploreB:** at decide time, with probability
  clip(k·closeness, 0, 1) for k = 0.5 / 2.0, return a uniform random action
  instead of argmax.   Closeness from pre-reset votes v:
  1 − (v₁−v₂)/(v₁+v₂) with 0/0 defined as 1 (no spikes is maximal
  uncertainty). Note this differs deliberately from the argmax path on exact
  ties: ties randomize among joint winners only, while a deviation draws
  over all actions including losers — probing losers is the point. Draws come from the agent's own RNG; flags off means zero draws
  and therefore identical streams.
- **exploreOracle:** with probability ε = 0.1 return the correct action,
  else the argmax path. The correct label arrives as a new `decide()`
  keyword (default None); non-oracle arms never receive it, enforced by
  patch test. Privileged bound only: if epsilon-correct exploration does
  not beat baseline, exploration is not the gap and endo failure means
  nothing.

Four arms, eight paired agent/task seeds, all three tasks. Paired design
throughout: every seed runs every arm, all contrasts seed-paired with
bootstrap 95% intervals, unadjusted. Metrics follow frozen scales: tail
reward rate (last quarter) on volatile tasks, total rewards on lock.

## Partitions, confirmation and disposition

| Partition | Seeds | Runs |
| --- | --- | --- |
| Development only | agent 120–127 instrument checks | unit/synthetic only |
| Independent confirmation | agent 130–137 / task 130 | 4 arms × 8 seeds × 3 tasks |
| Bootstrap RNG only | 215000 | 10000 whole-seed resamples |

All seed ranges are fresh; no prior study's agent or task seeds are reused
for measurement. Task seeds: volatile/noisy-volatile/lock constructors take
seed 130; run seeds equal agent seeds (paired). Advancement requires, per
task: an explorer paired interval strictly above zero against baseline AND
the oracle strictly above that explorer, with no frozen-suite regression
(`check_reference.py` 56/56 in CI). A positive for ANY explorer on ANY task
counts, with every explorer on every task reported side by side — no
cherry-picking, no correction theater at n=8. Overall disposition is
learning_positive iff at least one task-level pass exists, otherwise
learning_negative (task closures without verdict apply first). Missing/malformed evidence remains incomplete. Every
final disposition closes this registration with no automatic next
experiment, mechanism change, default change or agent integration.

## Evidence, implementation phases and refinement

Archive every seed's per-decision reward histories, vote-margin (closeness)
trajectories, deviation decisions with endo/oracle provenance, and realized
switch schedules. Always expose finite-seed counts.

Phases: (1) register/refine; (2) implement/test and commit all scientific
sources; (3) confirm all intervention rows; (4) reproduce every reached row,
manifest and report; (5) publish a draft PR from the implementation branch,
monitor all twenty-one workflows at exact HEAD, mark ready and merge when
green and reviews resolved. Use separate study/check/report modules plus a
twenty-first workflow. Reuse frozen agent/task/evaluator functions; additive
flags only, no default changes, no monkeypatching of module globals.
Preserve all earlier files except README/PLAN/V3 status pointers.

Before observations verify USABLE positions from frozen numbers, flag parity
(defaults-off reproduces the frozen reference exactly), closeness math on
hand vote vectors (ties, zeros, unanimous), deviation provenance (correct
label reaches only the oracle arm), paired-seed discipline, causal tick
boundaries, invalid/non-finite records, changed sources, uncommitted
manifests and forbidden confirmation. Snapshot all transitive local code,
report/check sources, applicable protocols and pinned requirements. No
source change after observations except a diagnosed, explicitly reported
instrument defect. Registration SHA is immutable.

Reproduce all reached rows if eligible at rtol1e-11/atol1e-13; only execution
timing and regenerated input digests are exempt. All twenty prior studies'
evidence must also reproduce unchanged, and all twenty prior workflows
remain intact. Paired bootstrap intervals are descriptive; eight seeds and
three tasks cannot establish population guarantees, exploration in general,
or superiority over deep learning. No new dependencies are needed.
