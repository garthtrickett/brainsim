# Kink-guarded slope closes learning-negative on the same ramp

The registered candidate passed **74/75 independent comparisons** and closes
as **learning_negative** — on the same single strict cell as the benchmark.
Selected guard J=96 narrows the shallow-ramp gap threefold (0.000960 to
**0.000313** vs no-fallback 0.000264, paired interval [0.000042, 0.000055]
still entirely positive) but does not close it. Everything else passes:
primary 0.080223 against every control, all retention bounds, all six other
strict cells.

All **384 tuning and 224 confirmation rows** were completed and finite. No
new default, broader benchmark, mechanism change or agent integration is
activated. The kink-guard hypothesis is now measured rather than open: fast
means at boundaries recover most of the transient, and the residue is small,
positive, and stable across guard horizons — a boundary this local fitting
family cannot fully erase.

## What was implemented

The [registration](DESIGN-v3-slopeguard.md) freezes OLS-128, the dual base
and drift_start-gated trend regime, and searches only the guard horizon J:
in-segment steps within J of any request predict the fast mean, trend beyond
it. J=0 reproduces the slope study bit-for-bit (asserted in parity); J=6000
is always-fast. Controls are the unchanged y-only trio (re-searched: W=8,
lr=.128, delta=.1/clock=1, identical for the ninth consecutive study), the
granted J=0 reference, Bernoulli random-guard fallback (frozen p from the
selected guard's tuning requests), and the enriched no-fallback ablation.
Every request record carries target/drift/random provenance that never mixes.

Tuning selected **J=96** with objectives nearly flat (0.050560–0.050703
across the menu; J=0 at 0.050612). As with the estimator menu before it, the
selection among horizons carries little information — the finding is the
confirmation gap, not the index.

## Independent performance

Seven policies on the same **32 fresh confirmation seeds**. Lower is better.

| Policy | Primary MSE | Role |
| --- | ---: | --- |
| Kink-guarded slope, J=96 | **0.080223** | Registered candidate |
| Granted reference (J=0) | 0.080223 | Diagnostic baseline |
| Matched no-fallback | 0.082834 | Mechanism ablation |
| SGD | 0.116707 | Deployable control |
| Fixed window, W=8 | 0.125129 | Deployable control |
| Random guard | 0.193052 | Timing control |
| ADWIN2 | 0.193361 | Adaptive-window control |

Candidate and reference primaries are bit-identical (0.080223): the guard
acts only inside drift segments, so switching metrics cannot move. The sole
failure:

| Cell | Candidate | Control | 95% interval |
| --- | ---: | ---: | --- |
| nofallback/ramp_shallow, strict | 0.000313 | 0.000264 | [0.000042, 0.000055] |

Against every other control on the shallow ramp — including SGD and W=8 —
the candidate passes under preservation bounds. Only its own fast-window
base, on the weakest-signal ramp, still beats it.

## Privilege caveat

Granted boundaries throughout; the ±2-step tolerance still binds; nothing
here is deployable. What narrows, precisely quantified, is the mechanism
boundary: kink-guarding recovers two-thirds of the shallow transient, and
the remaining third belongs to local fitting itself.

## Evidence, phases and changed files

| Phase | Evidence | Status |
| --- | --- | --- |
| Registration/refinement | branch commit | Before study observations |
| Implementation/checks | branch commits | Before tuning |
| Tuning / manifest freeze | 384 rows | Eligible; trio identical to eight predecessors |
| Confirmation | seeds 163000–163031, seven policies | 224 rows; learning-negative |
| Reproduction/publication | All 608 reached rows; sixteen workflows | See validation below |

Protocol SHA-256:
`b82a30e177b415d6d8d192aedef6e7233ce81812946d21b6755b6eca787e0d06`.
Development 160000–160007, tuning 161000–161007, confirmation 163000–163031,
bootstrap 165000 and the 166000+ RNG domains are separate and disjoint from
all previous studies.

New files: `v3_slopeguard.py`, `v3_slopeguard_policy.py`,
`study_v3_slopeguard.py`, `report_v3_slopeguard.py`,
`check_v3_slopeguard.py`, `.github/workflows/v3-slopeguard-checks.yml`, the
registration, this results file and `results/v3-slopeguard/`. README and
PLAN/V3 status pointers report the outcome. Earlier scientific sources,
evidence, protocols, all fifteen previous workflows, dependencies and agent
defaults remain unchanged. No capability or registry row is promoted.

The [generated report](results/v3-slopeguard/report.md) includes all 75
candidate comparisons with their improve/preserve/strict modes, per-fixture
absolute errors with four-regime shares and slope magnitudes, and execution
times.

## Validation and limits

All commands below passed locally, including reproduction of all 608 new rows.
Python commands use the project's existing `.venv`:

```sh
python check_v3_slopeguard.py --evidence results/v3-slopeguard --reproduce
python report_v3_slopeguard.py --check
python check_evidence.py
git diff --check
```

Checks cover guard-regime entry/exit with fast priority, J=0 slope-study
identity, frozen estimator parity, causal prefixes, coordinate isolation,
privilege isolation of granted schedules, all 75 vetoes on the adapted
cells, per-request provenance accounting, immutable sources/manifests/
stages, missing/invalid/non-finite evidence, and four-regime memory
accounting. The parity suite caught three pre-observation implementation
bugs. Every reached row, manifest, selection, probability, decision and
scientific summary is reproduced at rtol1e-11/atol1e-13, excluding only
timing and regenerated input digests. CI must pass all sixteen workflows
before merge.

Intervals use 10000 whole-seed resamples (seed 165000). Small Gaussian
synthetic fixtures, finite horizon menus and granted boundaries cannot
establish population guarantees, global rankings, or neural-memory utility.
The authoritative outcome is the candidate's independent learning-negative
result on the shallow ramp.
