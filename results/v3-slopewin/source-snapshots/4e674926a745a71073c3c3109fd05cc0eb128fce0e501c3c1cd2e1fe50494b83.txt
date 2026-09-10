# Registered V3 adaptive-window slope experiment

Protocol `v3-slopewin-20260910-v1`. The operator authorized the fix the
benchmark report named: an estimator window that adapts to distance from the
last boundary — short at kinks where the fast window already wins, widening
mid-ramp where trend pays. Steep/shallow/noisy ramps plus unchanged abrupt
fixtures decide whether boundary blindness is curable inside local fitting.
No new estimator family, no detector arm, equal small tuning budgets, fresh
confirmation, and the adapted 75-comparison gate. Register before study
observations. Preserve all earlier protocols, scientific sources, evidence
and eighteen CI workflows. No dependency or agent/default change.

## Hypothesis and why this follows slopebench

The broader benchmark narrowed the slope win to kink-smearing: OLS-128 fits
straddling the ramp onset mix flat past with tilted present, and on a
shallow ramp that transient dominates while the 4-sample fast window adapts
immediately. The kink guard recovered two-thirds of the gap by handing
boundaries to the fast mean — but a handover is still a blind spot, not a
fit. This experiment fits through the kink instead: W(d) = W_near within S
steps of any request, W_far beyond it. If the shallow strict cell passes
with everything preserved, local fitting was never structurally blind, only
badly windowed. If it still fails, kink-blindness belongs to local fitting
itself, and the mechanism stands narrowed as measured.

Falsifier, stated in advance: shallow still fails against no-fallback, or any
previously passing cell regresses. Either closes the registration with no
automatic follow-up.

## Learner semantics

Everything is frozen except the window schedule: OLS estimator, K_fast=4/
W_fast=32, ADWIN2 delta=.1/clock 1, H=32, drift_start-gated trend regime. At
each step the estimator fits the most recent W(d) observations (causal,
strictly pre-update) where d counts steps since the latest request of any
kind: W_near for d ≤ S, W_far beyond. Outside the slope regime behavior is
the frozen dual policy exactly. The menu below pairs near/mid windows with
switch distances; S is measured in the same steps as H and the guard study.

**Schedule ownership.** Granted true target times plus ramp boundaries,
exactly as in the drift, slope and bench studies. No target values, noise
labels, ramp slopes or future samples; no requests on noise transitions. Any
positive authorizes only a separately authorized broader benchmark, never
agent integration.

**Arms.** win (window-schedule menu on the enriched schedule; registered
candidate); reference (OLS-128, the slope-study policy exactly — diagnostic
baseline); random_win (selected schedule on Bernoulli requests from t0,
diagnostic timing control); oracle_nofallback (fast base on the enriched
schedule, diagnostic mechanism control); window, SGD and ADWIN2 y-only
controls on unchanged menus, receiving no schedule of any kind.

## ADWIN baseline and scope

Unchanged from the forgetting study, including the bounded-input disclaimer
and the pre-data slow-implementation agreement.

## Fixed finite menus and objective

Four searched families, each **12 configurations × 8 paired seeds × all five
fixtures** (384 tuning rows): (W_near, W_far, S) in [{4,8} × {64,128,256} ×
{16,32}] in lexicographic order, window, SGD and ADWIN2 on unchanged menus.
W=128 with S≥6000 would reproduce slope-study behavior; the menu instead
spans genuine schedules from near-flat (W_near=8 throughout the transient)
to far-dominated. Every listed configuration is behaviorally distinct on
fixtures with boundaries. Order breaks exact objective ties (inherited grids
only for the trio).

The trained drift fixture is excluded by design: its result stands frozen,
and the window schedule only reshapes trend fits near boundaries. This study
covers the benchmark shapes where the open cell lives. Stated, not hidden.

Reuse the EXACT bench fixtures/metrics (core, mixed, steep, shallow, noisy)
and selection objective: P is the equal mean post-200 MSE over core
quiet/noisy switching and both mixed coordinates; R is the same 14 adapted
cells. Select minimum seed-mean (P+mean(R))/2 for every searched family.

Random-request probability is frozen from the SELECTED win-candidate tuning
requests, counted evaluator-side: pool N over S=6000*9*8, p=f/(1-16*f),
finite 0<=p<=1, opportunities from t0, 16-update suppression.

A configuration with any non-finite tuning trajectory/metric is ineligible,
with its failure retained. Finish all 384 rows. If any family lacks a
complete finite configuration, close tuning_inconclusive and forbid
confirmation. Otherwise freeze all selected configurations, random p, fixture
definitions, RNG domains, source identity and complete tuning evidence in a
committed manifest BEFORE independent confirmation.

## Partitions, confirmation and disposition

| Partition | Seeds | Rows |
| --- | --- | --- |
| Development only | 190000–190007 | unit/synthetic only |
| Tuning | 191000–191007 | 4×12×8 = 384 |
| Independent confirmation | 193000–193031 | 7×32 = 224 |
| Bootstrap RNG only | 195000 | 10000 whole-seed resamples |

All seed ranges and the 196000+ RNG domains are fresh, including unused
reservations of previous studies. Do not reopen old studies or substitute
seeds. Run all 224 confirmation rows if tuning permits: win, window, sgd,
adwin, reference, random_win, oracle_nofallback. Do not stop measuring any
arm based on another arm's outcome.

Candidate win faces the adapted 75: primary ≥10% over
window/SGD/ADWIN/random with preservation against no-fallback, every
retention bound, strict improvement against no-fallback on the 7 adapted
stable cells with the both-perfect repair. All **75 comparisons** must pass
for learning_positive; otherwise learning_negative. Non-finite required
trajectories fail; missing/malformed evidence remains incomplete. Controls
cannot be dropped. Every final disposition closes this registration with no
automatic next experiment, mechanism change, default change or agent
integration.

Report regime shares (fast/slope/ADWIN per fixture), mean in-regime window
per ramp, estimator slope magnitudes, and realized versus expected random
activity. A failed result keeps the mechanism narrowed as measured; name the
cells exactly.

## Evidence, implementation phases and refinement

Archive every policy/seed's learning metrics and actual update norms by
fixture; per-coordinate request indices with provenance, event hit/latency,
estimator states, window schedule and regime at each prediction, and
realized versus expected random activity. Always expose finite-seed counts
and expected versus realized schedule activity.

Phases: (1) register/refine; (2) implement/test and commit all scientific
sources; (3) tune all 384/freeze manifest; (4) confirm all 224; (5) reproduce
every reached row, manifest, selection and report; (6) publish a draft
codex/** PR, monitor all nineteen workflows at exact HEAD, mark ready and
merge when green and reviews resolved. Use separate v3_slopewin
runtime/policy/study/report/check modules plus a nineteenth workflow. Reuse
frozen slope/retention/forgetting/ADWIN/bench functions without
monkeypatching module globals. Preserve all earlier files except
README/PLAN/V3 status pointers.

Before observations verify window-schedule parity on hand-built boundary
sequences (near/far selection at S, pre-request convention, causal prefixes);
frozen OLS parity at fixed W against the slope kernels; all menus, common
objective, finite/tie selection; all 75 vetoes on the adapted cells;
missing/invalid/non-finite records, changed sources, uncommitted manifests
and forbidden confirmation. Snapshot all transitive local code, report/check
sources, applicable protocols and pinned requirements. No source change after
observations except a diagnosed, explicitly reported instrument defect.
Registration SHA is immutable.

Reproduce all reached rows if eligible at rtol1e-11/atol1e-13; only execution
timing and regenerated input digests are exempt. All eighteen prior studies'
evidence must also reproduce unchanged, and all eighteen prior workflows
remain intact. Statistical intervals are descriptive; finite menus, synthetic
fixtures and granted schedules cannot establish population guarantees or
general neural-memory utility. No new dependencies are needed.
