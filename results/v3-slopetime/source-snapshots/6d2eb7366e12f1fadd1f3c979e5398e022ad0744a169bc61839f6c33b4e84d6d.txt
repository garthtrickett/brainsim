# Registered V3 slope-timing experiment

Protocol `v3-slopetime-20260909-v1`. The operator authorized a deployability
test for the slope win: the frozen OLS-128 trend regime gated by observable
ADWIN alarm times instead of granted drift boundaries. No new estimator, no
detector arm, equal small tuning budgets, fresh confirmation, and a 45-cell
advancement gate against the deployable trio. Register before study
observations. Preserve all earlier protocols, scientific sources, evidence
and thirteen CI workflows. No dependency or agent/default change.

## Hypothesis and why this follows slope

The slope study closed the first full V3 positive under granted drift
boundaries (75/75, drift 0.000088 vs 0.000227 SGD). The tolerance study
showed abrupt timing must land within ±2–8 steps — a bar ADWIN's own alarms
cannot meet. Drift boundaries are a different question: ramps are ~2000
steps long, so the timing the slope regime needs may be loose enough for
observed alarms. This experiment replaces granted boundaries with ADWIN
shrink alarms at the concurrently selected control config and asks whether
anything of the slope win survives.

Falsifier, stated in advance: if the observable-gated slope policy cannot
beat the deployable trackers while preserving stability, trend following
stays a privileged result — useful as diagnosis, unusable as policy. If it
passes, this is the first deployable composition win in the chain. Either
outcome closes this registration with no automatic follow-up.

## Learner semantics

The trend estimator is frozen (OLS-128); the dual base is frozen (K_fast=4,
W_fast=32, ADWIN2 delta=.1, clock 1). What is searched is the slope horizon
Hs: after an ADWIN alarm, the policy predicts from the trend estimator while
steps-since-alarm ≤ Hs, then exits. Fast/ADWIN selection is otherwise
unchanged (fast mean within H=32 of the latest request, ADWIN mean
otherwise), and fast takes priority over slope inside its window: the proven
abrupt behavior is preserved deliberately, with the slope regime filling the
slow tail. Rationale: slope fitting across a step change overshoots, while
fast windows already own the first 32 steps; reversing the priority would
risk the retention wins for no reason. The run will say whether the
compromise works — on drift fixtures alarms arrive roughly every 27 steps,
so a short Hs may leave slope starved and a long Hs may smear steps.

**Schedule ownership.** ADWIN alarms are computed from observable data only,
by the standalone control run at its selected configuration — the same
best-foot-forward rule as the tolerance study. No arm sees target values,
noise labels, ramp slopes, true boundaries, or future samples. The
candidate's schedule is deployable; the reference arm below is not, and the
two dispositions never mix.

**Arms.** slope_adwin (OLS-128 + Hs menu on observed alarms; the registered
candidate, deployable); reference (OLS-128 on granted enriched boundaries —
the slope-study policy exactly — diagnostic baseline); random_slope (frozen
estimator and selected Hs on Bernoulli requests, diagnostic timing control);
oracle_nofallback (fast base on observed alarms, diagnostic mechanism
control); window, SGD and ADWIN2 y-only controls on their unchanged menus,
receiving no schedule of any kind.

## ADWIN baseline and scope

The paper-based ADWIN2 implementation, Eq.(3.1) threshold, bucket compression
and bounded-input disclaimer are unchanged from the forgetting study. A
separate slow implementation using explicit bucket contents must agree before
study data. Established prior art, not a new proposed detector.

## Fixed finite menus and objective

Four searched families, each **12 configurations × 8 paired seeds × all five
fixtures** (384 tuning rows). Only the horizon is searched; everything else
is frozen. Order below breaks exact objective ties.

- slope_horizon: Hs in [16,32,64,128,256,512,1024,2048,3000,4000,5000,6000]
  (12). Hs=6000 is the always-slope endpoint after the first alarm.
- window: W in [1,2,4,8,16,32,64,128,256,512,1024,6000] (unchanged).
- sgd: lr in [.0001,.0004,.001,.004,.008,.016,.035743040182210514,
  .064,.128,.256,.512,1] (unchanged).
- adwin: delta in [.0001,.001,.01,.1], then clock in [1,8,32], Cartesian product
  (unchanged); five buckets per size, minimum subwindow 5, grace 10 fixed.

These are finite menus, not global optimization. Report endpoint selections;
no automatic extension or post-result boundary veto. All four receive equal
configuration/seed/fixture budgets, not identical CPU costs. Record measured
execution times.

Random-request probability is frozen from the SELECTED slope_horizon tuning
requests, counted evaluator-side on tuning seeds: pool counts N over
S=6000*9*8, f=N/S, p=f/(1-16*f), p=0 if N=0, finite 0<=p<=1, no clipping,
opportunities from t0, 16-update suppression.

Reuse the EXACT nine-coordinate fixtures/metrics and selection objective of
all predecessors: P is the equal mean post-200 MSE over core quiet/noisy
switching and both mixed coordinates; R comprises the same 14 cells. Select
minimum seed-mean (P+mean(R))/2 for every searched family.

A configuration with any non-finite tuning trajectory/metric is ineligible,
with its failure retained. Finish all 384 rows. If any family lacks a
complete finite configuration, close tuning_inconclusive and forbid
confirmation. Otherwise freeze all selected configurations, random p, the
alarm-generating control config, RNG domains, source identity and complete
tuning evidence in a committed manifest BEFORE independent confirmation.

## Partitions, confirmation and disposition

| Partition | Seeds | Rows |
| --- | --- | --- |
| Development only | 140000–140007 | unit/synthetic only |
| Tuning | 141000–141007 | 4×12×8 = 384 |
| Independent confirmation | 143000–143031 | 7×32 = 224 |
| Bootstrap RNG only | 145000 | 10000 whole-seed resamples |

All seed ranges and the 146000+ RNG domains are fresh, including unused
reservations of previous studies. Do not reopen old studies or substitute
seeds. Run all 224 confirmation rows if tuning permits: slope_adwin, window,
sgd, adwin, reference, random_slope, oracle_nofallback. There is no detector
calibration in this study. Do not stop measuring any arm based on another
arm's outcome.

Candidate slope_adwin faces 45 comparisons against window, SGD and ADWIN:
primary ≥10% improvement with paired 95% upper < 0, and every one of the 14
retention cells with paired upper ≤ max(.002,.1*control mean). All 45 must
pass for learning_positive; otherwise learning_negative. The reference,
random and no-fallback arms are reported with the same instrument as
diagnostics; none can advance the candidate or rescue a failure. Every final
disposition closes this registration with no automatic next experiment,
mechanism change, default change or agent integration. A positive reports the
first deployable composition win and justifies only a separately authorized
broader benchmark, never integration.

Report regime use rates (fast/slope/ADWIN share per condition, drift
fixtures separately), alarm counts per fixture family, and realized versus
expected random activity. Distinguish observed alarms from granted times from
random requests in every record. A failed result limits this finite horizon
menu, not all forms of observable-gated trend tracking.

## Evidence, implementation phases and refinement

Archive every policy/seed's learning metrics and actual update norms by
fixture; per-coordinate alarm indices with observed/granted/random
provenance, event hit/latency against true changes and drift boundaries,
estimator states and regime at each prediction, and realized versus expected
random activity. Always expose finite-seed counts and expected versus
realized schedule activity.

Phases: (1) register/refine; (2) implement/test and commit all scientific
sources; (3) tune all 384/freeze manifest; (4) confirm all 224; (5) reproduce
every reached row, manifest, selection and report; (6) publish a draft
codex/** PR, monitor all fourteen workflows at exact HEAD, mark ready and
merge when green and reviews resolved. Use separate v3_slopetime runtime/
policy/study/report/check modules plus a fourteenth workflow. Reuse frozen
slope/retention/forgetting/ADWIN functions without monkeypatching module
globals. Preserve all earlier files except README/PLAN/V3 status pointers.

Before observations verify horizon-regime parity on hand-built alarm
sequences (entry/exit at Hs boundaries, fast-priority overlap, always-slope
endpoint, pre-request convention); frozen estimator parity against the slope
 kernels at matched config; alarm provenance from the selected control
config; all menus, common objective, finite/tie selection; all 45 vetoes;
missing/invalid/non-finite records, changed sources, uncommitted manifests
and forbidden confirmation. Snapshot all transitive local code, report/check
sources, applicable protocols and pinned requirements. No source change after
observations except a diagnosed, explicitly reported instrument defect.
Registration SHA is immutable.

Reproduce all reached rows if eligible at rtol1e-11/atol1e-13; only execution
timing and regenerated input digests are exempt. All thirteen prior studies'
evidence must also reproduce unchanged, and all thirteen prior workflows
remain intact. Statistical intervals are descriptive; finite menus, small
synthetic fixtures and observed alarms cannot establish population
guarantees or general neural-memory utility. No new dependencies are needed.
