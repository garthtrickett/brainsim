# Observable-gated slope closes learning-negative

The registered candidate passed **41/45 independent comparisons** and closes
as **learning_negative**. Its primary post-switch MSE was **0.108994**,
versus **0.118972 for SGD** (paired interval entirely negative, but only an
8.4% mean improvement against the required 10%), **0.127588 for the tuned
fixed window** and **0.196737 for ADWIN2**. The four failures: the primary
10% rule and noisy switching against SGD, and two noise-jump retention cells
against ADWIN — noise-increase 0.050165 vs 0.003083 first among them.

The tuning menu had already delivered the verdict in miniature: Hs=16 and
Hs=32 tie at 0.073513 (both degenerate to no-slope, fast winning every
overlap), and every longer horizon climbs monotonically to a 0.134–0.135
plateau. Engaging the slope regime on observed alarms strictly hurts; the
selected endpoint is the configuration that engages it least. Confirmation
bears that out rather than overturning it.

All **384 tuning and 224 confirmation rows** were completed and finite. No
new default, broader benchmark, mechanism change or agent integration is
activated. The deployable slope line closes with the tolerance line: trend
following works under granted timing and fails under observed timing, in both
cases on stability destroyed by false alarms.

## What was implemented

The [registration](DESIGN-v3-slopetime.md) freezes the OLS-128 estimator and
dual base and searches only the slope horizon Hs: after an observed ADWIN
alarm the policy predicts from the trend while steps-since-alarm ≤ Hs, with
the fast mean winning the first 32 steps deliberately. Alarms come from the
standalone control run at the concurrently selected config (delta=.1,
clock=1 — selected for the eighth consecutive study). Diagnostics are the
granted enriched-boundary reference, Bernoulli random-schedule slope, and the
fast base on observed alarms. Every record carries observed/granted/random
provenance that never mixes.

No scientific source changed after tuning began.

## Equal-budget finite tuning

Four families, **12 configurations × 8 paired seeds × all five fixtures**
(384 rows). Horizon objectives: 16 → 0.073513, 32 → 0.073513, 64 → 0.103334,
128 → 0.132578, then 0.134–0.135 through 6000. The trio selected W=8,
lr=.128, delta=.1/clock=1 yet again.

## Independent performance

Seven policies on the same **32 fresh confirmation seeds**. Lower is better.

| Policy | Primary MSE | Role |
| --- | ---: | --- |
| Slope on observed alarms, Hs=16 | **0.108994** | Registered candidate |
| Fast base on observed alarms | 0.103576 | Mechanism control |
| SGD | 0.118972 | Deployable control |
| Fixed window, W=8 | 0.127588 | Deployable control |
| Random slope | 0.195218 | Timing control |
| ADWIN2 | 0.196737 | Adaptive-window control |
| Granted-boundary reference | 0.084769 | Diagnostic baseline |

The granted reference replicates its predecessors on fresh seeds (41/45,
drift only). The fast base on the same observed alarms reaches 39/45 with
the identical noise-retention failure shape — the damage is in the schedule,
not the trend estimator. Random scheduling is destroyed (25/45).

## Privilege caveat

The only slope result that passes anything is the granted one. Observable
timing fails it on false alarms, exactly as the tolerance number said it
would. Nothing here advances a deployable policy.

## Evidence, phases and changed files

| Phase | Evidence | Status |
| --- | --- | --- |
| Registration/refinement | branch commit | Before study observations |
| Implementation/checks | branch commits | Before tuning |
| Tuning / manifest freeze | 384 rows | Eligible; trio identical to seven predecessors |
| Confirmation | seeds 143000–143031, seven policies | 224 rows; learning-negative |
| Reproduction/publication | All 608 reached rows; fourteen workflows | See validation below |

Protocol SHA-256:
`6d2eb7366e12f1fadd1f3c979e5398e022ad0744a169bc61839f6c33b4e84d6d`.
Development 140000–140007, tuning 141000–141007, confirmation 143000–143031,
bootstrap 145000 and the 146000+ RNG domains are separate and disjoint from
all previous studies. Source snapshots cover all transitive local
runtime/report/check dependencies.

New files: `v3_slopetime.py`, `v3_slopetime_policy.py`,
`study_v3_slopetime.py`, `report_v3_slopetime.py`, `check_v3_slopetime.py`,
`.github/workflows/v3-slopetime-checks.yml`, the registration, this results
file and `results/v3-slopetime/`. README and PLAN/V3 status pointers report
the outcome. Earlier scientific sources, evidence, protocols, all thirteen
previous workflows, dependencies and agent defaults remain unchanged. No
capability or registry row is promoted.

The [generated report](results/v3-slopetime/report.md) includes all 45
advancement comparisons, per-level diagnostic tables, per-fixture absolute
errors with regime shares and slope magnitudes, and execution times.

## Validation and limits

All commands below passed locally, including reproduction of all 608 new rows.
Python commands use the project's existing `.venv`:

```sh
python check_v3_slopetime.py --evidence results/v3-slopetime --reproduce
python report_v3_slopetime.py --check
python check_evidence.py
git diff --check
```

Checks cover horizon-regime entry/exit with fast priority, frozen estimator
parity, alarm provenance from the selected control config, causal prefixes,
coordinate isolation, privilege isolation of granted versus observed
schedules, all 45 vetoes, per-arm provenance accounting, immutable
sources/manifests/stages, missing/invalid/non-finite evidence, and
three-regime memory accounting. The parity suite caught four
pre-observation implementation bugs. Every reached row, manifest, selection,
probability, decision and scientific summary is reproduced at
rtol1e-11/atol1e-13, excluding only timing and regenerated input digests. CI
must pass all fourteen workflows before merge.

Intervals use 10000 whole-seed resamples (seed 145000). Small Gaussian
supervised fixtures, finite horizon menus and observed alarms cannot
establish population guarantees, global rankings, or neural-memory utility.
The authoritative outcome is the candidate's independent learning-negative
result.
