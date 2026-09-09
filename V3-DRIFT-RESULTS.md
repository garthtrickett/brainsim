# Drift-boundary schedule closes learning-negative on drift again

The registered candidate passed **69/75 independent comparisons** and closes
as **learning_negative**. Its primary post-switch MSE was **0.083613**,
versus **0.118311 for SGD**, **0.126196 for the tuned fixed window**,
**0.199363 for ADWIN2**, **0.199235 for random-schedule drift fallback**,
and **0.085909 for the matched no-fallback ablation** (preserved within
bounds). All five primary comparisons pass, as does every stable and noise
cell — including the repaired `exactly_quiet` veto, which passes as
preservation on a 0-vs-0 tie exactly as specified.

The six failures are the same six drift cells that closed the retention
study, at essentially unchanged values (drift-window 0.003115 vs 0.003148
before; drift-fixture 0.007974 vs 0.007562). Granting drift-start/end times
changed nothing about drift. The wall is the mechanism, not the schedule
ontology — and that distinction, not the gate outcome, is this experiment's
product.

All **288 tuning and 192 confirmation rows** were completed and finite. No
new default, broader benchmark, slope-state build or agent integration is
activated. A slope state is now motivated by evidence, by a new registration,
never by this one.

## What was implemented

The [registration](DESIGN-v3-drift.md) freezes the retention candidate
(K_fast=4, W_fast=32, ADWIN2 delta=.1, drift-blind clock 1, H=32) and enriches
only its granted schedule: true abrupt-target times plus drift-start/end
indices. No new state, no detector, no search on the candidate. Controls are
the unchanged y-only trio (re-searched), the enriched no-fallback ablation,
and enriched random-schedule fallback (frozen p=0.00018573551263001485 from
80 tuning requests / 432000 coordinate-updates, opportunities from t0).
Every request record carries target/drift/random provenance that never mixes.

The registration carries one prospective rule repair, recorded before any
observation: the strict stable/noise requirement applies only where the
control mean exceeds zero, so a both-perfect cell passes as preservation. No
scientific source changed after tuning began.

## Equal-budget finite tuning

Three families, **12 configurations × 8 paired seeds × all five fixtures**
(288 rows), same objective as every predecessor. The trio selected W=8,
lr=.128 and delta=.1/clock=1 — identical for the sixth consecutive study.

## Independent performance

Six policies on the same **32 fresh confirmation seeds**. Primary MSE as
defined in every predecessor study. Lower is better.

| Policy | Primary MSE | Role |
| --- | ---: | --- |
| Drift-boundary retention | **0.083613** | Registered candidate |
| Matched no-fallback | 0.085909 | Mechanism ablation |
| SGD | 0.118311 | Deployable control |
| Fixed window, W=8 | 0.126196 | Deployable control |
| Random drift fallback | 0.199235 | Timing control |
| ADWIN2 | 0.199363 | Adaptive-window control |

Candidate-minus-control paired 95% intervals (primary) all pass, including
preservation against no-fallback. The six failures:

| Cell | Candidate | Control | 95% interval |
| --- | ---: | ---: | --- |
| sgd/drift | 0.003115 | 0.000196 | [0.002891, 0.002947] |
| sgd/drift/drift | 0.007974 | 0.000237 | [0.007525, 0.007944] |
| window/drift | 0.003115 | 0.000319 | [0.002765, 0.002825] |
| window/drift/drift | 0.007974 | 0.000334 | [0.007426, 0.007851] |
| nofallback/drift | 0.003115 | 0.000191 | [0.002897, 0.002950] |
| nofallback/drift/drift | 0.007974 | 0.000375 | [0.007401, 0.007794] |

## The treatment was delivered; the wall did not move

Post-burn fast-regime share of the candidate: drift fixture **0.0128**
exactly (2 boundary requests × 32 steps, no more, no less), core 0.0064,
mixed 0.0128, zero elsewhere. The enriched schedule engaged precisely as
specified — two fast windows opened on every ramp — and drift MSE is
unchanged from the schedule-blind baseline to four significant figures.
Perfect drift timing buys nothing here because neither state estimates slope:
the fast window averages a tilted recent past, ADWIN averages a longer
tilted past, and 32 post-boundary observations of either cannot track a ramp
either component was never built to see. That is now measured, not asserted.

## The repaired veto behaved as designed

`oracle_nofallback/exactly_quiet` reads 0.000000 vs 0.000000 and passes with
mode recorded as preservation — the rule firing exactly as re-specified, on
a tie it was built to survive rather than a regression it was built to catch.
Had the unrepaired rule been re-registered, this cell would have failed
again on identical values; the repair changed one cell's disposition and
nothing else, and the experiment still closes on drift independently of it.

## Privilege caveat

The enriched schedule is granted, not recovered: drift boundaries are
evaluator-owned ground truth no deployable arm could read. Nothing here
advances a deployable policy. What advances is the diagnostic conclusion —
the next mechanism, if any, must estimate change-within-regime, and that
design belongs to a new registration.

## Evidence, phases and changed files

| Phase | Evidence | Status |
| --- | --- | --- |
| Registration/refinement | branch commit | Before study observations; repaired veto reviewed in |
| Implementation/checks | branch commits | Before tuning |
| Tuning / manifest freeze | 288 rows | Eligible; trio identical to five predecessors |
| Confirmation | seeds 123000–123031, six policies | 192 rows; learning-negative |
| Reproduction/publication | All 480 reached rows; twelve workflows | See validation below |

Protocol SHA-256:
`62a8eb8470e934430cfbcc9ee21fc3cad3c10853774ea795c4f38bcddcc713bb`.
Development 120000–120007, tuning 121000–121007, confirmation 123000–123031,
bootstrap 125000 and the 126000+ RNG domains are separate and disjoint from
all previous studies. Source snapshots cover all transitive local
runtime/report/check dependencies. Snapshots preserve provenance after squash
merge.

New files: `v3_drift.py`, `v3_drift_policy.py`, `study_v3_drift.py`,
`report_v3_drift.py`, `check_v3_drift.py`,
`.github/workflows/v3-drift-checks.yml`, the registration, this results file
and `results/v3-drift/`. README and PLAN/V3 status pointers report the
outcome. Earlier scientific sources, evidence, protocols, all eleven previous
workflows, dependencies and agent defaults remain unchanged. No capability or
registry row is promoted.

The [generated report](results/v3-drift/report.md) includes all 75 candidate
comparisons with their improve/preserve/strict modes, per-fixture absolute
errors, dual-state memory with boundary provenance and regime shares, and
execution times. Raw records retain request indices with target/drift/random
provenance at each prediction.

## Validation and limits

All commands below passed locally, including reproduction of all 480 new rows.
Python commands use the project's existing `.venv`:

```sh
python check_v3_drift.py --evidence results/v3-drift --reproduce
python report_v3_drift.py --check
python check_evidence.py
git diff --check
```

Checks cover enriched-schedule extraction and provenance tagging, frozen
dual-state parity, causal prefixes, coordinate isolation, privilege isolation
of granted schedules, all 75 vetoes including the repaired both-perfect rule
(pinned by an explicit passing test), immutable sources/manifests/stages,
missing/invalid/non-finite evidence, and dual memory accounting. The parity
suite caught two pre-observation implementation bugs. Every reached row,
manifest, selection, probability, decision and scientific summary is
reproduced at rtol1e-11/atol1e-13, excluding only timing and regenerated
input digests. CI must pass all twelve workflows before merge.

Intervals use 10000 whole-seed resamples (seed 125000). Small Gaussian
supervised fixtures, finite schedule menus and granted boundaries cannot
establish population guarantees, global rankings, or neural-memory utility.
The authoritative outcome is the candidate's independent learning-negative
result on drift, and the diagnostic conclusion that timing does not explain
it.
