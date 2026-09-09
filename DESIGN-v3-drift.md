# Registered V3 drift-boundary schedule experiment

Protocol `v3-drift-20260909-v1`. The operator authorized a schedule-ontology
test on the frozen retention candidate: the same fast-window/ADWIN2 fallback
at its selected configuration, with drift-start/end times added to the granted
schedule. No new mechanism, no detector arm, equal small tuning budgets for
the y-only controls, fresh confirmation, and the inherited 75-comparison
gate with one repaired veto. Register before study observations. Preserve all
earlier protocols, scientific sources, evidence and eleven CI workflows. No
dependency or agent/default change.

## Hypothesis and why this follows tolerance

The retention study closed learning-negative on six drift cells with the
candidate reducing to ADWIN2 exactly on drift fixtures — by construction, the
schedule grants abrupt-target times only. That reading is ambiguous between a
mechanism gap (no slope state) and an ontology gap (the evaluator never marks
the ramp), and the retention report stated it more confidently than the
evidence supports. The tolerance study then priced abrupt timing (±2 steps
alive, dead by ±8) without touching drift. This experiment separates the two
readings for the price of a schedule change: grant the drift boundaries too,
and see whether the frozen candidate passes drift or still fails it.

Falsifier, stated in advance: if the enriched schedule still fails the drift
cells against the fast trackers, the wall is the mechanism — a slope state is
then motivated by evidence, not intuition. If drift passes, no new state was
ever needed and the slope-state design evaporates. Either outcome closes this
registration with no automatic follow-up.

## Learner semantics

The learner is the frozen retention policy at its selected configuration,
unchanged: fast window K_fast=4, W_fast=32; ADWIN2 slow state at delta=.1,
clock 1, five buckets per size, minimum subwindow 5, grace 10; fallback
horizon H=32. Only the granted schedule is enriched.

**Schedule ownership.** The evaluator supplies requests at true abrupt target
changes AND at drift-start/drift-end indices, after the current observation
arrives and its pre-update prediction has been scored. Requesting arms receive
no true target value, noise level, ramp slope or future samples, and no
requests on noise transitions. Keeping K_fast=4 at any boundary can retain
old-regime samples; perfect timing is not perfect segmentation or a
mathematical performance upper bound. The granted schedule is the
experiment's premise, not a deployable claim: any positive authorizes only a
separately authorized broader benchmark with rediscovered timing, never agent
integration. Random-request arms receive no true indices. Window, SGD and
ADWIN receive no schedule of any kind.

**Arms.** retain_drift (frozen candidate on the enriched schedule);
oracle_nofallback (forgetting learner K=4, W=32 on the enriched schedule, the
mechanism ablation); random_drift (frozen candidate config on Bernoulli
requests from t0 with 16-update suppression, frozen expected frequency from
the enriched tuning requests); window, SGD and ADWIN2 y-only controls on
their unchanged menus. Pre-stated expectation, neutrally: two extra fast
windows per drift run may re-aim tracking onto the ramp, or may plant stale
fast means on it. Measured, not assumed.

## ADWIN baseline and scope

The paper-based ADWIN2 implementation, Eq.(3.1) threshold, bucket compression
and bounded-input disclaimer are unchanged from the forgetting study. A
separate slow implementation using explicit bucket contents must agree before
study data. Established prior art, not a new proposed detector.

## Fixed finite menus, objective, and one repaired veto

Three searched families, each **12 configurations × 8 paired seeds × all five
fixtures** (288 tuning rows): window, SGD and ADWIN2 on their unchanged
menus. The candidate configuration is frozen from the retention manifest; the
enriched-schedule and random arms receive no search. Order below breaks exact
objective ties (inherited grids only; nothing new is searched).

Reuse the EXACT nine-coordinate fixtures/metrics and selection objective of
the burst/forgetting/discovery/retention registrations: P is the equal mean
post-200 MSE over core quiet/noisy switching and both mixed coordinates; R
comprises the same 14 cells. Select minimum seed-mean (P+mean(R))/2 for every
searched family.

The advancement gate is the retention 75-comparison structure — primary ≥10%
improvement over window/SGD/ADWIN/random with preservation against
no-fallback, every retention bound, and strict improvement on the 8
stable/noise cells against no-fallback — with one prospective repair,
recorded here before any observation: the strict requirement applies only
where the control mean exceeds zero. The retention study's `exactly_quiet`
cell failed on 0.000000 vs 0.000000, an unsatisfiable demand on a perfect
tie; re-registering that veto knowingly would repeat a documented defect. A
both-perfect cell passes as preservation instead. This is a rule correction
with retained rationale, not a dropped control.

Random-request probability is frozen from the SELECTED enriched-candidate
tuning requests only: pool counts N over S=6000*9*8, f=N/S, p=f/(1-16*f),
p=0 if N=0, finite 0<=p<=1, no clipping, opportunities from t0. Expected
pooled frequency is matched, not confirmation counts or memory age.

A configuration with any non-finite tuning trajectory/metric is ineligible,
with its failure retained. Finish all 288 rows. If any family lacks a
complete finite configuration, close tuning_inconclusive and forbid
confirmation. Otherwise freeze all selected configurations, random p, the
enriched schedule definition, RNG domains, source identity and complete
tuning evidence in a committed manifest BEFORE independent confirmation.

## Partitions, confirmation and disposition

| Partition | Seeds | Rows |
| --- | --- | --- |
| Development only | 120000–120007 | unit/synthetic only |
| Tuning | 121000–121007 | 3×12×8 = 288 |
| Independent confirmation | 123000–123031 | 6×32 = 192 |
| Bootstrap RNG only | 125000 | 10000 whole-seed resamples |

All seed ranges and the 126000+ RNG domains are fresh, including unused
reservations of previous studies. Do not reopen old studies or substitute
seeds. Run all 192 confirmation rows if tuning permits: retain_drift,
window, sgd, adwin, oracle_nofallback, random_drift. There is no detector in
this study and no diagnostic screen is re-run. Do not stop measuring
candidate performance based on ablation outcomes.

All **75 comparisons** must pass for learning_positive; otherwise
learning_negative, with the repaired veto above. Non-finite required
trajectories fail; missing/malformed evidence remains incomplete. Controls
cannot be dropped because they are strong or fail other diagnostics. Every
final disposition closes this registration with no automatic slope-state
build, detector change, default change or agent integration. A positive
retires the slope-state design; a drift failure motivates it — either way, by
a NEW registration, never by this one.

Report regime use rates (fast vs ADWIN prediction share per condition, drift
fixtures separately), request-count summaries per schedule family, and
realized versus expected random activity. Distinguish abrupt-target requests
from drift-boundary requests in every record: the two provenances must never
mix. A failed result limits this finite enriched-schedule test, not all forms
of drift tracking.

## Evidence, implementation phases and refinement

Archive every policy/seed's learning metrics and actual update norms by
fixture; per-coordinate request indices with boundary provenance
(target/drift), event hit/latency against true target changes AND drift
boundaries, fast/ADWIN widths and regime at each prediction, and realized
versus expected random activity. Always expose finite-seed counts and
expected versus realized schedule activity.

Phases: (1) register/refine; (2) implement/test and commit all scientific
sources; (3) tune all 288/freeze manifest; (4) confirm all 192; (5) reproduce
every reached row, manifest, selection and report; (6) publish a draft
codex/** PR, monitor all twelve workflows at exact HEAD, mark ready and merge
when green and reviews resolved. Use separate v3_drift runtime/policy/
study/report/check modules plus a twelfth workflow. Reuse frozen
retention/forgetting/ADWIN functions without monkeypatching module globals.
Preserve all earlier files except README/PLAN/V3 status pointers.

Before observations verify schedule-construction parity (drift-boundary
extraction against fixture events, target/drift provenance separation, random
RNG independence and domain separation, prefix and coordinate causality, no
true-index access in the random arm, no schedule access in window/sgd/adwin);
frozen candidate parity against the retention oracle arm on abrupt-only
schedules; all menus, common objective, finite/tie selection; all 75 vetoes
including the repaired both-perfect rule; missing/invalid/non-finite records,
changed sources, uncommitted manifests and forbidden confirmation. Snapshot
all transitive local code, report/check sources, applicable protocols and
pinned requirements. No source change after observations except a diagnosed,
explicitly reported instrument defect. Registration SHA is immutable.

Reproduce all reached rows if eligible at rtol1e-11/atol1e-13; only execution
timing and regenerated input digests are exempt. Old tolerance+retention+
discovery+forgetting+burst evidence must also reproduce unchanged, and all
eleven prior workflows remain intact. Statistical intervals are descriptive;
finite menus, small synthetic fixtures and granted schedules cannot establish
population guarantees or general neural-memory utility. No new dependencies
are needed.
