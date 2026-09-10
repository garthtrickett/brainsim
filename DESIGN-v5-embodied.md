# Registered V5 embodied volatility experiment

Protocol `v5-embodied-20260910-v1`. The operator authorized the embodiment
of the V3 toolkit: graft switch-gated learning bursts and dual-timescale
value estimates onto the frozen v1 agent, driven by its endogenous surprise
signals, and test them on noisy-volatile tasks the deterministic suite
cannot probe. No oracle drives any deployable arm; oracle-timed twins exist
only as privileged upper bounds, per the PGATE precedent. Register before
study observations. Preserve all earlier protocols, scientific sources,
evidence and nineteen CI workflows. No dependency change; agent defaults
unchanged; all new knobs default off.

## Hypothesis and why this follows V4

V4 proved graded response holds adaptation under fixed lies but cannot buy
selectivity, and priced the remaining gap as alarm selectivity — a detector
program closed twice. The way out is not a better fixture alarm. The v1
agent already computes its own graded surprise (`NM = r − V(s)`) and turns
reward-rate volatility into learning-rate and exploration changes (ADAPTIVE:
volatile-4 0.278 → 0.419, with the documented trade against nway-8 and
lock). What was never tested — because the frozen suite is deterministic,
as V3-NEXT records — is whether that endogenous machinery, extended with
the V3 toolkit, handles the noise/change contrast the toys were built for.
This experiment puts the toolkit where the surprise already lives and
measures task scores, not gate diagnostics.

Falsifier, stated in advance: no toolkit arm beats the frozen ADAPTIVE
baseline on usable noisy-volatile tasks while its oracle twin shows
headroom. A pass must clear a paired interval above zero AND the oracle
twin must clear it by more (else the task, not the arm, did the work). Any
positive justifies only a separately authorized embodiment benchmark, never
a default change.

## Tasks: noisy-volatile calibrations first

New module `v5_tasks.py` (tasks.py stays frozen): NoisyVolatile wraps
Volatile(n=4, switch_every=300) and adds i.i.d. Gaussian observation noise
σ ∈ {0.25, 0.5} to every presented pattern, from an independent RNG stream
that preserves the base task's RNG. Two task instances, calibrated
independently. Switch times stay unannounced; noise is stationary within a
run. Nothing else about the task changes.

**Calibration stage (frozen code, before any intervention comparison).** On
each noise level, with 2100 decisions (7 contingency switches — enough to
measure switch-gated effects at half the compute of the 4000-decision v1
scale; a measured 4000-decision volatile run costs ~14s, which would push
full CI reproduction past the 30-minute workflow budget): floor from
`random_policy`, ceiling from `oracle`, baseline from the frozen agent
(ADAPTIVE defaults), each on paired seeds. A task is USABLE only if the baseline sits 10–90% of the way
from floor to ceiling — the calibration precedent that cost 20 minutes on
an uncalibrated 8-class task. Unusable tasks close as tuning_inconclusive
for that level: no intervention runs there, no retrospective σ adjustment,
no pooling across levels to rescue a floor. Intervention comparisons run
only on usable levels.

## Intervention arms (agent flags, all default off)

On brainsim.py, additive constants only; defaults keep every existing
number bit-identical (the frozen 56-score reference must still pass
unchanged, enforced by the existing workflow):

- **baseline:** frozen defaults, ADAPTIVE on. The bar everything clears.
- **burst-endo:** the agent's own reward-rate volatility gap (the ADAPTIVE
  `vol` scalar, same computation, no new detector) crossing a fixed
  threshold fires an LR burst: the post-ADAPTIVE effective rate ×F for the
  next D decisions — phasic on tonic — then immediate rearm with no cooldown
  (self-limiting as vol decays). The burst scales POLICY updates only, per
  the PGATE precedent; value, traces and replay stay untouched. Two menu
  settings, (τ,F,D) = (1.0,2,50) and (1.5,4,100) — modest and strong,
  pre-stated, not tuned.
- **burst-oracle:** identical burst engine driven by true contingency-switch
  indices read from task state (decision boundaries where `t % 300 == 0`).
  Privileged bound only (PGATE precedent): if this does not beat baseline,
  the task cannot reward timing and endo failure means nothing.
- **dualV:** fast/slow value blend — a second V(s) head at LR 0.5 (10×
  VALUE_W_LR, same normalized delta rule on the same inputs), predicting
  from the fast head for 50 decisions after any modest-setting burst
  trigger, otherwise the slow head. Addresses the documented weakness that
  V(s) must relearn every state after a permutation.
- **dualV-oracle:** same blend on oracle switch times. Privileged bound.

Six arms, eight paired agent/task seeds, usable noise levels only. Paired
design throughout: every seed runs every arm, and all contrasts are
seed-paired differences with bootstrap 95% intervals, unadjusted for the
three endo comparisons. Tail reward rate (last quarter of decisions) is the
metric, matching calibration. A positive for
ANY endo arm counts, with all three endo results reported side by side —
no cherry-picking, no correction theater at n=8.

## Partitions, confirmation and disposition

All seed ranges are fresh; v1's 0–7 agent seeds and seed-zero tasks are not
reused for measurement:

| Partition | Seeds | Runs |
| --- | --- | --- |
| Calibration | agent 100–102 / task 100 | floors, ceilings, baselines × 2 levels |
| Independent confirmation | agent 110–117 / task 110 | 6 arms × 8 seeds per usable level |
| Bootstrap RNG only | 205000 | 10000 whole-seed resamples |

Do not reopen v1 studies or substitute seeds. Run all confirmation rows only
on usable levels and only if calibration permits. Advancement requires, per
usable level: an endo arm paired interval strictly above zero against
baseline AND the corresponding oracle twin strictly above the endo arm
(headroom proof), with no frozen-suite regression (`check_reference.py`
56/56 in CI). If an oracle twin fails to beat baseline, that level's
comparisons are void — a task defect, not a negative — and the level closes
without a verdict. Missing/malformed evidence remains incomplete. Every
final disposition closes this registration with no automatic next
experiment, mechanism change, default change or agent integration.

## Evidence, implementation phases and refinement

Archive every seed's per-decision reward histories, surprise/LR/noise
trajectories, burst trigger indices with endo/oracle provenance, value-head
estimates, and realized switch/noise schedules. Always expose finite-seed
counts.

Phases: (1) register/refine; (2) implement/test and commit all scientific
sources; (3) calibrate floors/ceilings/baselines and freeze the usable set;
(4) confirm all intervention rows; (5) reproduce every reached row, manifest,
selection and report; (6) publish a draft PR from the implementation branch,
monitor all twenty workflows at exact HEAD, mark ready and merge when green
and reviews resolved. Use separate v5_tasks/study/check/report modules plus a twentieth
workflow. Reuse frozen agent/task/evaluator functions; additive flags only,
no default changes, no monkeypatching of module globals. Preserve all earlier
files except README/PLAN/V3 status pointers.

Before observations verify calibration math on hand traces (floor/ceiling/
position/USABLE rule), flag parity (defaults-off reproduces the frozen
reference exactly), burst-oracle bound semantics, endo trigger provenance
(no switch-index access outside oracle arms), paired-seed discipline,
causal tick boundaries, invalid/non-finite records, changed sources,
uncommitted manifests and forbidden confirmation. Snapshot all transitive
local code, report/check sources, applicable protocols and pinned
requirements. No source change after observations except a diagnosed,
explicitly reported instrument defect. Registration SHA is immutable.

Reproduce all reached rows if eligible at rtol1e-11/atol1e-13; only execution
timing and regenerated input digests are exempt. All nineteen prior studies'
evidence must also reproduce unchanged, and all nineteen prior workflows
remain intact. Paired bootstrap intervals are descriptive; eight seeds and
synthetic tasks cannot establish population guarantees, embodiment in
general, or superiority over deep learning. No new dependencies are needed.
