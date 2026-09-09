# Registered V4 robustness under frozen lies experiment

Protocol `v4-robust-20260909-v1`. The operator authorized the inversion of
the V3 program: instead of better detectors for fragile learners, a robust
learner for sloppy detectors. A frozen sloppy-schedule generator with stated
error rates replaces every oracle; a finite menu of graded-response learners
must beat the fast trackers under those fixed lies. No perfect-timing arm
exists anywhere in this study — not as candidate, not as reference, not as
diagnostic. Register before study observations. Preserve all earlier
protocols, scientific sources, evidence and seventeen CI workflows. No
dependency or agent/default change.

## Hypothesis and why this follows the V3 line

V3 proved that change-gated learning works under granted timing (±2–8 steps
for abrupt, ±256 for drift boundaries) and fails under observed timing
(false alarms destroy stability in both lines). Read one way, that closes
the subject. Read the righter way, it indicts the learner's fragility, not
the alarms: V3 asked whether sloppy alarms can drive a learner that needs
perfect ones. This experiment asks the inverted question — which learners
still win when the schedule lies on a fixed, pre-stated profile.

The philosophy is already running in this repository, untested: the v1 agent
computes a global surprise broadcast (`NM = r − V(s)`) and its ADAPTIVE flag
turns reward-rate volatility into learning-rate and noise changes. Sloppy
noticing with robust response, in an embodied loop. This
study stays in the supervised fixtures where measurement is exact;
embodiment is explicitly out of scope and belongs to a v2-scale program, not
this registration.

Falsifier, stated in advance: no graded design beats the fast trackers under
the fixed lies while preserving stability. A pass reports the first win in
the chain that assumes nothing perfect; it still authorizes only a
separately authorized benchmark with real alarms, never integration.

## The frozen lies

The schedule generator is fixed here and never tuned to flatter a candidate.
Per true abrupt-target or drift-boundary event, independently per
coordinate: delay uniform integer [0,8], miss probability 0.1, plus
Bernoulli(0.001) false alarms per step independent of everything. No
suppression, no rearming, no memory across events. Clipping to [0,5999];
collisions merge by set semantics. The delay band covers the top of ADWIN's
measured alarm latencies (means 1.55–5.34 on retention confirmation seeds);
the miss rate is above the observed zero; the false rate matches the
observed ~2–6 per noisy run. Every number above traces to frozen evidence,
not to a sweep. Sharpening these lies later to rescue a learner would be V3
with better PR, and this paragraph exists to forbid it: the profile is
frozen at registration.

## Learner semantics

All policies predict each coordinate's y[t] before seeing it (initial
prediction 0), then update. Causal, per-coordinate, no future samples.

**graded candidate:** plain SGD tracker with base rate lr=0.128 (the
control-selected value, frozen), modulated multiplicatively by recent alarms:
lr_t = 0.128·(1+G·s_t), where s_t counts alarms in the trailing W_s
observations (s_t = 0 most steps). Menu over gain G in [1,2,4,8] and window
W_s in [8,32,128] (12 configurations): ordinary SGD when quiet, boosted when
recent alarms say otherwise. No momentum beyond SGD's own update, no second
moment, no window mean, no reset.

**adwin_gated:** the selected graded config driven by real ADWIN shrink
alarms (delta=.1, clock=1, the control-selected setting) instead of
synthetic lies. Diagnostic; the operating point the synthetic profile
approximates. It cannot pass or fail anything.

**window/sgd/adwin:** the unchanged y-only controls; they receive no schedule
of any kind.

The candidate's schedule is synthetic but evaluator-built from true times
plus noise — privileged in construction, fixed in profile. What is being
tested is response shape under stated lies, not timing recovery: a pass does
not claim deployability, and the ADWIN-gated diagnostic exists precisely to
keep that distinction visible.

## ADWIN baseline and scope

Unchanged from the forgetting study, including the bounded-input disclaimer
and the pre-data slow-implementation agreement.

## Fixed finite menus and objective

Four searched families, each **12 configurations × 8 paired seeds × all five
fixtures** (384 tuning rows): graded (G×W_s), window, SGD and ADWIN2 on
unchanged menus. Order breaks exact objective ties (inherited grids only for
the trio).

Reuse the EXACT drift-study fixtures/metrics (core, noise_jump, drift,
exactly_quiet, mixed) and selection objective: P is the equal mean post-200
MSE over core quiet/noisy switching and both mixed coordinates; R comprises
the same 14 cells. Select minimum seed-mean (P+mean(R))/2 for every searched
family.

A configuration with any non-finite tuning trajectory/metric is ineligible,
with its failure retained. Finish all 384 rows. If any family lacks a
complete finite configuration, close tuning_inconclusive and forbid
confirmation. Otherwise freeze all selected configurations, the frozen lie
profile, RNG domains, source identity and complete tuning evidence in a
committed manifest BEFORE independent confirmation.

## Partitions, confirmation and disposition

| Partition | Seeds | Rows |
| --- | --- | --- |
| Development only | 180000–180007 | unit/synthetic only |
| Tuning | 181000–181007 | 4×12×8 = 384 |
| Independent confirmation | 183000–183031 | 5×32 = 160 |
| Bootstrap RNG only | 185000 | 10000 whole-seed resamples |

All seed ranges and the 186000+ lie RNG domains are fresh, including unused
reservations of previous studies. Do not reopen old studies or substitute
seeds. Run all 160 confirmation rows if tuning permits: graded, window, sgd,
adwin, adwin_gated. Do not stop measuring any arm based on another arm's
outcome.

Candidate graded faces 45 comparisons against window, SGD and ADWIN: primary
≥10% improvement with paired 95% upper < 0, and every one of the 14
retention cells with paired upper ≤ max(.002,.1*control mean). All 45 must
pass for learning_positive; otherwise learning_negative. The ADWIN-gated arm
is reported with the same instrument as a diagnostic; it can authorize
nothing and rescue nothing. Every final disposition closes this registration
with no automatic next experiment, mechanism change, default change or agent
integration. A positive justifies only a separately authorized benchmark
with real alarms, never integration.

Report alarm counts per fixture family (granted vs realized), gain
trajectories, and the fraction of steps each gain level fires. A failed
result limits this finite graded family under these fixed lies — not graded
response in general, and not other lie profiles.

## Evidence, implementation phases and refinement

Archive every policy/seed's learning metrics and actual update norms by
fixture; per-coordinate realized lie records (delays, misses, false alarms
against true events), gain trajectories, and update norms. Always expose
finite-seed counts and expected versus realized lie activity.

Phases: (1) register/refine; (2) implement/test and commit all scientific
sources; (3) tune all 384/freeze manifest; (4) confirm all 160; (5) reproduce
every reached row, manifest, selection and report; (6) publish a draft
codex/** PR, monitor all eighteen workflows at exact HEAD, mark ready and
merge when green and reviews resolved. Use separate v4_robust runtime/policy/
study/report/check modules plus an eighteenth workflow. Reuse frozen
forgetting/ADWIN functions without monkeypatching module globals. Preserve
all earlier files except README/PLAN/V3 status pointers.

Before observations verify lie-generator parity on hand-built event sequences
(uniform delay bounds, miss/drop behavior, false-alarm rate and independence,
clipping, collision merging, prefix and coordinate causality, domain
separation, no true-index leakage beyond granted construction, no schedule
access in window/sgd/adwin); graded-gain parity on hand-worked traces
including the quiet (gain 1, ordinary SGD) and saturated regimes; all menus,
common objective, finite/tie selection; all 45 vetoes; missing/invalid/
non-finite records, changed sources, uncommitted manifests and forbidden
confirmation. Snapshot all transitive local code, report/check sources,
applicable protocols and pinned requirements. No source change after
observations except a diagnosed, explicitly reported instrument defect.
Registration SHA is immutable.

Reproduce all reached rows if eligible at rtol1e-11/atol1e-13; only execution
timing and regenerated input digests are exempt. All seventeen prior studies'
evidence must also reproduce unchanged, and all seventeen prior workflows
remain intact. Statistical intervals are descriptive; finite menus, small
synthetic fixtures and synthetic lies cannot establish population
guarantees or general neural-memory utility. No new dependencies are needed.
