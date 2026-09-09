# Slope broader benchmark closes learning-negative on one ramp

The registered candidate passed **74/75 independent comparisons** and closes
as **learning_negative** — on a single strict cell. Its primary post-switch
MSE was **0.079994**, versus **0.115912 for SGD**, **0.125080 for the tuned
fixed window**, **0.192259 for ADWIN2**, **0.191738 for random-schedule slope
fallback**, and **0.083458 for the matched no-fallback ablation** (preserved
within bounds). Every primary, every retention bound, and six of seven strict
cells pass.

The one failure is `oracle_nofallback/ramp_shallow`, strict:
**0.000960 vs 0.000259**, paired interval [0.000691, 0.000711], entirely
positive. On the shallow ramp — and only there — the trend regime loses to
its own fast-window base. Steep passes strictly (0.000143 vs 0.000498),
noisy passes strictly (0.003648 vs 0.007939), and the candidate beats SGD,
W=8 and ADWIN on the shallow ramp itself under preservation bounds. The
slope positive therefore narrows precisely: trend following generalizes to
steep and noisy ramps, but not to weak-signal ones.

All **288 tuning and 192 confirmation rows** were completed and finite. No
new default, broader benchmark, mechanism change or agent integration is
activated.

## What was implemented

The [registration](DESIGN-v3-slopebench.md) freezes the OLS-128 trend regime
and replays it against three ramps outside its experience — steep (4× the
trained slope), shallow (4× weaker), noisy (10× the training noise) — with
core/mixed fixtures riding along unchanged so primary stays comparable. The
trained drift fixture is not re-run. Controls are the unchanged y-only trio
(re-searched), the enriched no-fallback ablation, and enriched random
fallback (frozen p from 112 tuning requests / 432000). Every request record
carries target/drift/random provenance that never mixes.

No scientific source changed after tuning began.

## Equal-budget finite tuning

Three families, **12 configurations × 8 paired seeds × all five fixtures**
(288 rows). The trio selected W=8, lr=.128 and delta=.1/clock=1 — identical
for the eighth consecutive study.

## Independent performance

Six policies on the same **32 fresh confirmation seeds**. Lower is better.

| Policy | Primary MSE | Role |
| --- | ---: | --- |
| Slope on new ramps | **0.079994** | Registered candidate |
| Matched no-fallback | 0.083458 | Mechanism ablation |
| SGD | 0.115912 | Deployable control |
| Fixed window, W=8 | 0.125080 | Deployable control |
| Random slope | 0.191738 | Timing control |
| ADWIN2 | 0.192259 | Adaptive-window control |

Ramp excess MSE, candidate versus no-fallback ablation (strict cells):

| Ramp | Candidate | No-fallback | Outcome |
| --- | ---: | ---: | --- |
| steep | 0.000143 | 0.000498 | pass |
| shallow | 0.000960 | 0.000259 | **fail** |
| noisy | 0.003648 | 0.007939 | pass |

## Why the shallow ramp fails: kink-smearing

The OLS-128 window straddles the ramp onset: its first hundred-odd fits mix
the flat pre-ramp segment with the tilted post-onset samples, so the fitted
line carries kink bias long after the 4-sample fast window has adapted. On a
steep ramp the tilt signal dwarfs that bias within steps; on a noisy ramp
both arms are noise-dominated and the trend still wins on average; on a
shallow ramp the kink transient dominates because the signal is weak. Trend
following buys mid-ramp accuracy at the price of boundary blindness, and the
price exceeds the purchase exactly where the signal is weakest. That
tradeoff, not a bug, is the measured boundary of the mechanism — and it
suggests the shape of any successor: trend states need kink guards, not
bigger windows.

## Privilege caveat

Granted boundaries throughout; the ±2-step tolerance still binds; nothing
here is deployable. What generalizes, and what does not, is now mapped ramp
by ramp rather than claimed in general.

## Evidence, phases and changed files

| Phase | Evidence | Status |
| --- | --- | --- |
| Registration/refinement | branch commit | Before study observations |
| Implementation/checks | branch commits | Before tuning |
| Tuning / manifest freeze | 288 rows | Eligible; trio identical to seven predecessors |
| Confirmation | seeds 153000–153031, six policies | 192 rows; learning-negative |
| Reproduction/publication | All 480 reached rows; fifteen workflows | See validation below |

Protocol SHA-256:
`3e9c4039ddf08403fd26bcf4165dc4a3810a383a64d0c68ab74c6409414faa19`.
Development 150000–150007, tuning 151000–151007, confirmation 153000–153031,
bootstrap 155000 and the 156000+ RNG domains are separate and disjoint from
all previous studies. A pre-confirmation summary fix required regenerating
the not-yet-frozen evidence under final code; the superseded freeze remains
visible in history and no frozen evidence was edited.

New files: `v3_slopebench.py`, `v3_slopebench_policy.py`,
`study_v3_slopebench.py`, `report_v3_slopebench.py`,
`check_v3_slopebench.py`, `.github/workflows/v3-slopebench-checks.yml`, the
registration, this results file and `results/v3-slopebench/`. README and
PLAN/V3 status pointers report the outcome. Earlier scientific sources,
evidence, protocols, all fourteen previous workflows, dependencies and agent
defaults remain unchanged. No capability or registry row is promoted.

The [generated report](results/v3-slopebench/report.md) includes all 75
candidate comparisons with their improve/preserve/strict modes, per-fixture
absolute errors with ramp windows, regime shares and slope magnitudes, and
execution times.

## Validation and limits

All commands below passed locally, including reproduction of all 480 new rows.
Python commands use the project's existing `.venv`:

```sh
python check_v3_slopebench.py --evidence results/v3-slopebench --reproduce
python report_v3_slopebench.py --check
python check_evidence.py
git diff --check
```

Checks cover new-ramp fixture parity against hand-computed values, custom
ramp-window metrics, frozen candidate parity, causal prefixes, coordinate
isolation, privilege isolation of granted schedules, all 75 vetoes on the
adapted cells, per-request provenance accounting, immutable
sources/manifests/stages, missing/invalid/non-finite evidence, and
three-regime memory accounting. The parity suite caught three
pre-observation implementation bugs. Every reached row, manifest, selection,
probability, decision and scientific summary is reproduced at
rtol1e-11/atol1e-13, excluding only timing and regenerated input digests. CI
must pass all fifteen workflows before merge.

Intervals use 10000 whole-seed resamples (seed 155000). Small Gaussian
synthetic fixtures, three tested ramp shapes and granted boundaries cannot
establish population guarantees, global rankings, or neural-memory utility.
The authoritative outcome is the candidate's independent learning-negative
result on the shallow ramp.
