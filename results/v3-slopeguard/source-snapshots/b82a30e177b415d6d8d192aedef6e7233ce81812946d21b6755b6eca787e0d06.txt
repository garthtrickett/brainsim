# Registered V3 kink-guarded slope experiment

Protocol `v3-slopeguard-20260909-v1`. The operator authorized the fix the
benchmark report named: a kink guard on the frozen trend regime, forcing the
fast mean for J steps after every request before trend following begins.
Steep/shallow/noisy ramps plus unchanged abrupt fixtures decide whether
boundary blindness is curable without losing mid-ramp accuracy. No new
estimator, no detector arm, equal small tuning budgets, fresh confirmation,
and the adapted 75-comparison gate. Register before study observations.
Preserve all earlier protocols, scientific sources, evidence and fifteen CI
workflows. No dependency or agent/default change.

## Hypothesis and why this follows slopebench

The broader benchmark narrowed the slope win to a single mechanism boundary:
OLS-128 smears the ramp-onset kink through 128 fits, and on a shallow ramp
that transient dominates while the 4-sample fast window adapts immediately.
Trend buys mid-ramp accuracy at the price of boundary blindness. This
experiment pays the boundary in the cheaper currency: after any request,
predict the fast mean for J steps, then hand over to trend. If the handover
works, the shallow strict cell passes with steep/noisy/primary preserved; if
kink transients resist even explicit guarding, the boundary is structural to
local fitting and the mechanism stands narrowed as measured.

Falsifier, stated in advance: shallow still fails against no-fallback, or any
previously passing cell regresses. Either closes the registration with no
automatic follow-up.

## Learner semantics

Everything is frozen except J: OLS-128 estimator, K_fast=4/W_fast=32,
ADWIN2 delta=.1/clock 1, drift_start-gated trend regime. The guard rule: let
d be steps since the latest request (any kind); inside a drift segment,
predict the fast mean for d ≤ J and the trend estimate beyond it. Outside
drift segments behavior is the frozen dual policy exactly (fast owns d ≤ 32
there as before). J=0 reproduces the slope study bit-for-bit and anchors the
menu.

**Schedule ownership.** Granted true target times plus ramp boundaries,
exactly as in the drift and slope studies. No target values, noise labels,
ramp slopes or future samples; no requests on noise transitions. Any
positive authorizes only a separately authorized broader benchmark, never
agent integration.

**Arms.** guard (J menu on the enriched schedule; registered candidate);
reference (J=0, the slope-study policy exactly — diagnostic baseline);
random_guard (selected J on Bernoulli requests from t0, diagnostic timing
control); oracle_nofallback (fast base on the enriched schedule, diagnostic
mechanism control); window, SGD and ADWIN2 y-only controls on unchanged
menus, receiving no schedule of any kind.

## ADWIN baseline and scope

Unchanged from the forgetting study, including the bounded-input disclaimer
and the pre-data slow-implementation agreement.

## Fixed finite menus and objective

Four searched families, each **12 configurations × 8 paired seeds × all five
fixtures** (384 tuning rows):

- guard J in [0,48,64,96,128,192,256,384,512,1024,2048,6000], window, SGD and ADWIN2 on unchanged menus.
J=0 is the no-guard endpoint and must reproduce slope-study behavior
exactly — asserted in parity, not assumed. J=6000 is the always-fast
endpoint (reduces to no-fallback everywhere). Kink transients run O(W)
steps, so the menu jumps from identity to substantial guard rather than
sampling small J: every listed value is behaviorally distinct, and small
values would measure interpolation, not the fix. Order breaks exact
objective ties (inherited grids only for the trio).

The trained drift fixture is excluded by design: its result stands frozen,
and the guard only overrides trend with fast means near boundaries. This
study covers the benchmark shapes where the open cell lives. Stated, not
hidden.

Reuse the EXACT bench fixtures/metrics (core, mixed, steep, shallow, noisy)
and selection objective: P is the equal mean post-200 MSE over core
quiet/noisy switching and both mixed coordinates; R is the same 14 adapted
cells. Select minimum seed-mean (P+mean(R))/2 for every searched family.

Random-request probability is frozen from the SELECTED guard-candidate tuning
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
| Development only | 160000–160007 | unit/synthetic only |
| Tuning | 161000–161007 | 4×12×8 = 384 |
| Independent confirmation | 163000–163031 | 7×32 = 224 |
| Bootstrap RNG only | 165000 | 10000 whole-seed resamples |

All seed ranges and the 166000+ RNG domains are fresh. New-fixture RNG uses
SeedSequence([study_seed, 166000+fixture_ordinal, domain]) with ordinals
core=0, mixed=1, steep=2, shallow=3, noisy=4. Do not reopen old studies or
substitute seeds. Run all 224 confirmation rows if tuning permits: guard,
window, sgd, adwin, reference, random_guard, oracle_nofallback. Do not stop
measuring any arm based on another arm's outcome.

Candidate guard faces the adapted 75: primary ≥10% over
window/SGD/ADWIN/random with preservation against no-fallback, every
retention bound, strict improvement against no-fallback on the 7 adapted
stable cells with the both-perfect repair. All **75 comparisons** must pass
for learning_positive; otherwise learning_negative. Non-finite required
trajectories fail; missing/malformed evidence remains incomplete. Controls
cannot be dropped. Every final disposition closes this registration with no
automatic next experiment, mechanism change, default change or agent
integration.

Report regime shares (fast/guard-overridden/trend/ADWIN per fixture),
estimator slope magnitudes per ramp, and realized versus expected random
activity. A failed result keeps the mechanism narrowed as measured; name the
cells exactly.

## Evidence, implementation phases and refinement

Archive every policy/seed's learning metrics and actual update norms by
fixture; per-coordinate request indices with provenance, event hit/latency,
estimator states and regime at each prediction, and realized versus expected
random activity. Always expose finite-seed counts and expected versus
realized schedule activity.

Phases: (1) register/refine; (2) implement/test and commit all scientific
sources; (3) tune all 384/freeze manifest; (4) confirm all 224; (5) reproduce
every reached row, manifest, selection and report; (6) publish a draft
codex/** PR, monitor all sixteen workflows at exact HEAD, mark ready and
merge when green and reviews resolved. Use separate v3_slopeguard
runtime/policy/study/report/check modules plus a sixteenth workflow. Reuse
frozen slope/retention/forgetting/ADWIN/bench functions without
monkeypatching module globals. Preserve all earlier files except
README/PLAN/V3 status pointers.

Before observations verify guard-regime parity on hand-built boundary
sequences (J-boundary selection, fast-priority overlap, J=0 slope-study
identity, pre-request convention); frozen estimator parity; all menus,
common objective, finite/tie selection; all 75 vetoes on the adapted cells;
missing/invalid/non-finite records, changed sources, uncommitted manifests
and forbidden confirmation. Snapshot all transitive local code, report/check
sources, applicable protocols and pinned requirements. No source change after
observations except a diagnosed, explicitly reported instrument defect.
Registration SHA is immutable.

Reproduce all reached rows if eligible at rtol1e-11/atol1e-13; only execution
timing and regenerated input digests are exempt. All fifteen prior studies'
evidence must also reproduce unchanged, and all fifteen prior workflows
remain intact. Statistical intervals are descriptive; finite menus, synthetic
fixtures and granted schedules cannot establish population guarantees or
general neural-memory utility. No new dependencies are needed.
