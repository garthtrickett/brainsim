# Registered V3 slope-state experiment

Protocol `v3-slope-20260909-v1`. The operator authorized a third-state test
for drift: a trend estimator gated on granted drift boundaries, composed with
the frozen fast-window/ADWIN2 fallback. No detector arm, equal small tuning
budgets, fresh confirmation, and the inherited 75-comparison gate with the
repaired both-perfect veto. Register before study observations. Preserve all
earlier protocols, scientific sources, evidence and twelve CI workflows. No
dependency or agent/default change.

## Hypothesis and why this follows drift

The drift-boundary study engaged its enriched schedule exactly (drift fast
share 0.0128, no more, no less) and drift failed unchanged: the fast window
averages a tilted recent past, ADWIN averages a longer tilted past, and 32
post-boundary observations of either cannot track a ~2000-step ramp neither
state was built to see. The wall is the mechanism. This experiment adds the
missing piece as a third regime: between granted drift boundaries, predict
from a trend estimator instead of either level estimator.

Falsifier, stated in advance: if drift still fails against the fast trackers
with a fitted trend state active on every ramp, slope estimation as composed
here is insufficient — and the program learns that ramps need something other
than local trend following. If drift passes with everything else preserved,
this is the first full positive in the V3 chain. Either outcome closes this
registration with no automatic follow-up.

## Learner semantics

The learner is the frozen retention policy at its selected configuration
(K_fast=4, W_fast=32, ADWIN2 delta=.1, drift-blind clock 1, H=32) with one
addition: a slope regime. On a drift_start request the policy enters the
slope regime and predicts from the trend estimator; on a drift_end or any
abrupt-target request it exits to ordinary dual behavior (fast mean within H
of the latest request, ADWIN mean otherwise). The fast window and ADWIN
instance update on every observation regardless of regime, so exit is
seamless. No momentum beyond the estimator's own recursions, no Adam, no
additional blend parameter.

**Trend estimators (per coordinate, causal, no future samples).** OLS predicts
a+b·t fit by least squares on the most recent W observations (1 ≤ W);
Holt predicts level+trend from exponential recursions with rates (α, β).
Both start from the first available observation; both predict before seeing
y_t and update after. The menu below is the complete family under test.

**Schedule ownership.** The evaluator supplies requests at true abrupt target
changes AND drift-start/end indices, after the current observation arrives
and its pre-update prediction has been scored. Requesting arms receive no
true target value, noise level, ramp slope or future samples, and no requests
on noise transitions. The granted schedule is the experiment's premise, not a
deployable claim: any positive authorizes only a separately authorized
broader benchmark with rediscovered timing, never agent integration.

**Arms.** slope (frozen dual base + trend regime on the enriched schedule);
oracle_nofallback (forgetting learner K=4, W=32 on the enriched schedule, no
trend state); random_slope (frozen slope config on Bernoulli requests from t0
with 16-update suppression, frozen expected frequency); window, SGD and
ADWIN2 y-only controls on their unchanged menus. Random-request arms receive
no true indices. Window, SGD and ADWIN receive no schedule of any kind.

## ADWIN baseline and scope

The paper-based ADWIN2 implementation, Eq.(3.1) threshold, bucket compression
and bounded-input disclaimer are unchanged from the forgetting study. A
separate slow implementation using explicit bucket contents must agree before
study data. Established prior art, not a new proposed detector.

## Fixed finite menus and objective

Four searched families, each **12 configurations × 8 paired seeds × all five
fixtures** (384 tuning rows). The candidate family searches the estimator
only; the dual base stays frozen. Order below breaks exact objective ties.

- slope: OLS with W in [8,16,32,64,128,256], then Holt with (α, β) in
  [(.3,.1),(.5,.2),(.8,.3),(.2,.05),(.5,.05),(.8,.1)], in that order (12).
- window: W in [1,2,4,8,16,32,64,128,256,512,1024,6000] (unchanged).
- sgd: lr in [.0001,.0004,.001,.004,.008,.016,.035743040182210514,
  .064,.128,.256,.512,1] (unchanged).
- adwin: delta in [.0001,.001,.01,.1], then clock in [1,8,32], Cartesian product
  (unchanged); five buckets per size, minimum subwindow 5, grace 10 fixed.

These are finite menus, not global optimization. Report endpoint selections;
no automatic extension or post-result boundary veto. All four receive equal
configuration/seed/fixture budgets, not identical CPU costs. Record measured
execution times.

Random-request probability is frozen from the SELECTED slope-candidate tuning
requests, counted evaluator-side on tuning seeds exactly as in the drift
study (the schedule needs no learner): pool counts N over S=6000*9*8,
f=N/S, p=f/(1-16*f), p=0 if N=0, finite 0<=p<=1, no clipping, opportunities
from t0. Expected pooled frequency is matched, not confirmation counts or
memory age.

Reuse the EXACT nine-coordinate fixtures/metrics and selection objective of
all predecessors: P is the equal mean post-200 MSE over core quiet/noisy
switching and both mixed coordinates; R comprises the same 14 cells. Select
minimum seed-mean (P+mean(R))/2 for every searched family.

A configuration with any non-finite tuning trajectory/metric is ineligible,
with its failure retained. Finish all 384 rows. If any family lacks a
complete finite configuration, close tuning_inconclusive and forbid
confirmation. Otherwise freeze all selected configurations, random p, the
enriched schedule definition, estimator equations, RNG domains, source
identity and complete tuning evidence in a committed manifest BEFORE
independent confirmation.

## Partitions, confirmation and disposition

| Partition | Seeds | Rows |
| --- | --- | --- |
| Development only | 130000–130007 | unit/synthetic only |
| Tuning | 131000–131007 | 4×12×8 = 384 |
| Independent confirmation | 133000–133031 | 6×32 = 192 |
| Bootstrap RNG only | 135000 | 10000 whole-seed resamples |

All seed ranges and the 136000+ RNG domains are fresh, including unused
reservations of previous studies. Do not reopen old studies or substitute
seeds. Run all 192 confirmation rows if tuning permits: slope, window, sgd,
adwin, oracle_nofallback, random_slope. There is no detector in this study
and no diagnostic screen is re-run. Do not stop measuring candidate
performance based on ablation outcomes.

Candidate must improve P by >=10% over EACH of window, sgd, adwin and
random_slope, with paired 95% upper candidate-minus-control delta < 0.
Against oracle_nofallback the candidate must PRESERVE P within the retention
bound (paired upper delta <= max(.002,.1*control mean)): the trend regime is
a drift addition, not an adaptation claim. For each of 14 R cells against
each of the five controls require paired upper delta <= max(.002,.1*control
mean), with the inherited repair: on the 8 stable/noise cells against
oracle_nofallback the bound becomes strict improvement (paired upper < 0)
EXCEPT where the control mean is zero, which passes as preservation. All
**75 comparisons** must pass for learning_positive; otherwise
learning_negative. Non-finite required trajectories fail; missing/malformed
evidence remains incomplete. Controls cannot be dropped because they are
strong or fail other diagnostics. Every final disposition closes this
registration with no automatic next experiment, mechanism change, default
change or agent integration. A positive reports the first full V3 positive
and justifies only a separately authorized broader benchmark, never
integration.

Report regime use rates (fast/slope/ADWIN prediction share per condition,
drift fixtures separately), estimator selections and slope magnitudes on the
ramp, request-count summaries per boundary provenance, and realized versus
expected random activity. Distinguish abrupt-target requests from
drift-boundary requests in every record. A failed result limits this finite
estimator family, not all forms of trend tracking.

## Evidence, implementation phases and refinement

Archive every policy/seed's learning metrics and actual update norms by
fixture; per-coordinate request indices with target/drift/random provenance,
event hit/latency against true target changes AND drift boundaries,
estimator states and regime (fast/slope/ADWIN) at each prediction, and
realized versus expected random activity. Always expose finite-seed counts
and expected versus realized schedule activity.

Phases: (1) register/refine; (2) implement/test and commit all scientific
sources; (3) tune all 384/freeze manifest; (4) confirm all 192; (5) reproduce
every reached row, manifest, selection and report; (6) publish a draft
codex/** PR, monitor all thirteen workflows at exact HEAD, mark ready and
merge when green and reviews resolved. Use separate v3_slope runtime/policy/
study/report/check modules plus a thirteenth workflow. Reuse frozen
retention/forgetting/ADWIN functions without monkeypatching module globals.
Preserve all earlier files except README/PLAN/V3 status pointers.

Before observations verify OLS/Holt parity on hand-worked traces (including
startup with fewer than W samples, exact ramp tracking, flat-line behavior,
tie handling); regime entry/exit on boundary sequences including back-to-back
boundaries and H interplay at drift_end; frozen dual parity outside the
slope regime against the retention oracle arm; all menus, common objective,
finite/tie selection; all 75 vetoes including the asymmetric primary rule,
the strict ablation cells and the both-perfect repair; missing/invalid/
non-finite records, changed sources, uncommitted manifests and forbidden
confirmation. Snapshot all transitive local code, report/check sources,
applicable protocols and pinned requirements. No source change after
observations except a diagnosed, explicitly reported instrument defect.
Registration SHA is immutable.

Reproduce all reached rows if eligible at rtol1e-11/atol1e-13; only execution
timing and regenerated input digests are exempt. Old drift+tolerance+
retention+discovery+forgetting+burst evidence must also reproduce unchanged,
and all twelve prior workflows remain intact. Statistical intervals are
descriptive; finite menus, small synthetic fixtures and granted schedules
cannot establish population guarantees or general neural-memory utility. No
new dependencies are needed.
