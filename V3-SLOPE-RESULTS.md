# Slope state closes the first full V3 positive

The registered candidate passed **75/75 independent comparisons** and closes
as **learning_positive** — the first full positive in the V3 chain. Its
primary post-switch MSE was **0.079480**, versus **0.117088 for SGD**,
**0.125866 for the tuned fixed window**, **0.192391 for ADWIN2**,
**0.192386 for random-schedule slope fallback**, and **0.083258 for the
matched no-fallback ablation** (preserved within bounds). Every primary,
every retention bound, and every strict ablation cell passes.

The six drift cells that closed the retention and drift-boundary studies now
pass — and not marginally: candidate drift-window MSE **0.000091** versus
**0.000193 for SGD** and **0.000320 for W=8**; drift-fixture MSE **0.000088**
versus **0.000227** and **0.000328**. This is the first V3 policy to beat the
fast exponential tracker on a ramp, rather than merely approaching it.

All **384 tuning and 192 confirmation rows** were completed and finite. The
positive justifies only a separately authorized broader benchmark, never
agent integration — the schedule remains granted, and the tolerance number
(±2 steps alive, dead by ±8) still binds any deployable claim.

## What was implemented

The [registration](DESIGN-v3-slope.md) adds a third regime to the frozen
retention policy at its selected configuration: on a granted drift_start
request the policy predicts from a trend estimator (selected: OLS over the
most recent 128 observations); on drift_end or any abrupt-target request it
exits to ordinary fast/ADWIN behavior. Fast window and ADWIN update every
step regardless of regime. Controls are the unchanged y-only trio
(re-searched), the enriched no-fallback ablation, and enriched random-schedule
slope fallback (frozen p from 80 tuning requests / 432000). Every request
record carries target/drift/random provenance that never mixes.

No scientific source changed after tuning began.

## Equal-budget finite tuning

Four families, **12 configurations × 8 paired seeds × all five fixtures**
(384 rows). The estimator family alone was searched; the dual base stayed
frozen.

| Policy | Selected setting |
| --- | --- |
| Slope estimator | OLS, W=128 |
| Fixed window | W=8 |
| SGD | lr=.128 |
| ADWIN2 | delta=.1, clock=1 |

The trio selected identically for the seventh consecutive study. Estimator
objectives were nearly flat across all twelve configurations (0.055843–
0.055983): the tuning objective barely distinguishes trend estimators,
because drift is 2 of its 15 cells. OLS-128 won by a hair; the selection
among estimators carries almost no information, and the result must not be
read as establishing OLS-128 over its rivals. What matters is that the
regime, not the estimator, does the work — every tested estimator would
likely have passed, given how decisively the drift cells fall.

Random-request probability was frozen at **0.00018573551263001485**, from
**80 enriched tuning requests / 432000 coordinate-updates** with 16-update
suppression, opportunities from t0.

## Independent performance

Six policies on the same **32 fresh confirmation seeds**. Lower is better.

| Policy | Primary MSE | Role |
| --- | ---: | --- |
| Slope-regime retention | **0.079480** | Registered candidate |
| Matched no-fallback | 0.083258 | Mechanism ablation |
| SGD | 0.117088 | Deployable control |
| Fixed window, W=8 | 0.125866 | Deployable control |
| Random slope fallback | 0.192386 | Timing control |
| ADWIN2 | 0.192391 | Adaptive-window control |

The drift cells, with paired 95% intervals:

| Cell | Candidate | Control | Interval |
| --- | ---: | ---: | --- |
| sgd/drift | 0.000091 | 0.000193 | [-0.000110, -0.000096] |
| sgd/drift/drift | 0.000088 | 0.000227 | [-0.000147, -0.000131] |
| window/drift | 0.000091 | 0.000320 | [-0.000237, -0.000221] |
| window/drift/drift | 0.000088 | 0.000328 | [-0.000249, -0.000231] |

## The regime fires only where it should, and measures the ramp

Post-burn slope-regime share: drift fixture **0.4083** (≈2000-step ramp /
5000 post-burn steps, exactly as constructed), **0.0000 everywhere else**
across all 32 seeds. Mean estimated slope on the ramp: **-0.000955** against
the true **-0.001001** — noise and edge effects account for the gap. The
third regime engages precisely on ramps, nowhere else, and reports the ramp
it sees. The repaired `exactly_quiet` veto passes as preservation on its
0-vs-0 tie with mode recorded.

## Privilege caveat

Drift boundaries are granted ground truth; the ±2-step tolerance still
binds; nothing here is deployable. What changed is the mechanism verdict:
ramps yield to local trend following with granted timing. Whether trend
states survive rediscovered timing is a new registration's question.

## Evidence, phases and changed files

| Phase | Evidence | Status |
| --- | --- | --- |
| Registration/refinement | branch commit | Before study observations |
| Implementation/checks | branch commits | Before tuning; one dual-memory fix pre-confirmation |
| Tuning / manifest freeze | 384 rows | Eligible; trio identical to six predecessors |
| Confirmation | seeds 133000–133031, six policies | 192 rows; learning_positive |
| Reproduction/publication | All 576 reached rows; thirteen workflows | See validation below |

Protocol SHA-256:
`c089f89083e200ef4142d4330c8fc01309767820f9331feea2c37433d088fe3f`.
Development 130000–130007, tuning 131000–131007, confirmation 133000–133031,
bootstrap 135000 and the 136000+ RNG domains are separate and disjoint from
all previous studies. A pre-confirmation memory-record fix required
regenerating the not-yet-frozen evidence under final code; the superseded
freeze remains visible in history and no frozen evidence was edited.

New files: `v3_slope.py`, `v3_slope_policy.py`, `study_v3_slope.py`,
`report_v3_slope.py`, `check_v3_slope.py`,
`.github/workflows/v3-slope-checks.yml`, the registration, this results file
and `results/v3-slope/`. README and PLAN/V3 status pointers report the
outcome. Earlier scientific sources, evidence, protocols, all twelve previous
workflows, dependencies and agent defaults remain unchanged. No capability or
registry row is promoted.

The [generated report](results/v3-slope/report.md) includes all 75 candidate
comparisons with their improve/preserve/strict modes, per-fixture absolute
errors, dual-state memory with boundary provenance, regime shares and slope
magnitudes, and execution times.

## Validation and limits

All commands below passed locally, including reproduction of all 576 new rows.
Python commands use the project's existing `.venv`:

```sh
python check_v3_slope.py --evidence results/v3-slope --reproduce
python report_v3_slope.py --check
python check_evidence.py
git diff --check
```

Checks cover OLS/Holt parity against independent fits, regime entry/exit
including tie behavior, frozen dual parity outside the slope regime, causal
prefixes, coordinate isolation, privilege isolation of granted schedules, all
75 vetoes including the repaired both-perfect rule (pinned by an explicit
passing test), immutable sources/manifests/stages, missing/invalid/
non-finite evidence, and three-regime memory accounting. The parity suite
caught three pre-observation implementation bugs. Every reached row,
manifest, selection, probability, decision and scientific summary is
reproduced at rtol1e-11/atol1e-13, excluding only timing and regenerated
input digests. CI must pass all thirteen workflows before merge.

Intervals use 10000 whole-seed resamples (seed 135000). Small Gaussian
supervised fixtures, finite estimator menus and granted boundaries cannot
establish population guarantees, global rankings, or neural-memory utility.
The authoritative outcome is the candidate's independent learning-positive
result — the first in the V3 chain.
