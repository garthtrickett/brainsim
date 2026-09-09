# Drift-timing tolerance: the win survives ±256, dies by ±1024

The registered tolerance point is **256**: drift-boundary jitter at ±32 and
±256 steps passes all 45 cells each, while ±1024 fails two. The unperturbed
reference passes all 45, replicating its predecessors on fresh seeds
(primary 0.085204). Dropped boundaries fail the same two cells. This
disposition authorizes nothing — the point lands squarely in the pre-stated
middle band (alive past ±128, short of ±512): report the curve, no automatic
follow-up.

All **288 tuning and 288 confirmation rows** were completed and finite.

## What was implemented

The [registration](DESIGN-v3-drifttol.md) freezes the OLS-128 slope policy
and moves only its drift boundaries: uniform jitter ±{32,256,1024} per
coordinate with clipping and order enforcement, plus per-boundary drops at
50%. Abrupt-target times stay granted and exact in every arm, isolating
boundary precision from the priced abrupt tolerance. The y-only trio was
re-searched (W=8, lr=.128, delta=.1/clock=1 — identical for the tenth
consecutive study); the slope configuration is frozen from its manifest.

No scientific source changed after tuning began.

## The tolerance curve

Primary post-switch MSE is bit-identical across reference and all perturbed
arms (0.085204): primaries average switching cells, which drift boundaries
never touch. The action is all on drift:

| Arm | Drift-window MSE | Drift-fixture MSE | Cells |
| --- | ---: | ---: | --- |
| reference | passing | passing | 45/45 |
| jitter_32 | passing | passing | 45/45 |
| jitter_256 | passing | passing | 45/45 |
| jitter_1024 | passing | 0.001969 vs 0.000229 SGD | 43/45 |
| drop_50 | passing | 0.002656 vs 0.000229 SGD | 43/45 |

Misplacing a boundary by up to 256 steps on a ~2000-step ramp costs nothing
measurable; at ±1024 the whole-fixture drift error climbs past the fast
trackers while the drift-window cells still pass — the regime still tracks
locally, but a quarter-ramp of misalignment poisons the average. Dropping
half the boundaries degrades identitically: the slope state is robust to
*where* the ramp is marked within hundreds of steps, and fragile only to
*missing* it or marking it a half-ramp away.

## Reading, per the pre-stated rules

Tolerance 256 sits between "dead within ±128" and "alive at/above ±512",
so the rules say: report the curve, authorize nothing. That is this
document. Two observations for whoever frames the next question: first, the
curve is far wider than abrupt tolerance (±2–8), as hypothesized — ramps
forgive what steps do not. Second, the binding constraint on any observed
drift alarm was never going to be precision (hundreds of steps suffice) but
selectivity: slopetime died on false alarms, and nothing here changes that.
A drift-selective alarm remains unbuilt and untested, but this study does not
authorize building it — the point fell short of the bar by design, not by
accident.

## Privilege caveat

Every schedule here is evaluator-built from true times. Nothing is
deployable and nothing advances.

## Evidence, phases and changed files

| Phase | Evidence | Status |
| --- | --- | --- |
| Registration/refinement | branch commit | Before study observations |
| Implementation/checks | branch commits | Before tuning |
| Tuning / manifest freeze | 288 rows | Eligible; trio identical to nine predecessors |
| Confirmation | seeds 173000–173031, nine policies | 288 rows; tolerance 256 |
| Reproduction/publication | All 576 reached rows; seventeen workflows | See validation below |

Protocol SHA-256:
`d5c1b929e8269d270d20c604ab548a90573a2a104e9954446791f2de986df2ad`.
Development 170000–170007, tuning 171000–171007, confirmation 173000–173031,
bootstrap 175000 and the 176000+ RNG domains are separate and disjoint from
all previous studies.

New files: `v3_drifttol.py`, `v3_drifttol_policy.py`, `study_v3_drifttol.py`,
`report_v3_drifttol.py`, `check_v3_drifttol.py`,
`.github/workflows/v3-drifttol-checks.yml`, the registration, this results
file and `results/v3-drifttol/`. README and PLAN/V3 status pointers report
the outcome. Earlier scientific sources, evidence, protocols, all sixteen
previous workflows, dependencies and agent defaults remain unchanged. No
capability or registry row is promoted.

The [generated report](results/v3-drifttol/report.md) includes per-level
pass tables, the tolerance point, the full 45-cell reference table,
per-fixture absolute errors with regime shares, and execution times.

## Validation and limits

All commands below passed locally, including reproduction of all 576 new rows.
Python commands use the project's existing `.venv`:

```sh
python check_v3_drifttol.py --evidence results/v3-drifttol --reproduce
python report_v3_drifttol.py --check
python check_evidence.py
git diff --check
```

Checks cover boundary-perturbation construction (uniform bounds, clipping,
order enforcement, collision merging, RNG independence and domain
separation), frozen candidate parity, causal prefixes, coordinate isolation,
privilege isolation of granted schedules, the per-level instrument and
tolerance-point logic, per-arm provenance accounting, immutable
sources/manifests/stages, missing/invalid/non-finite evidence, and dual
memory accounting. The parity suite caught two pre-observation
implementation bugs. Every reached row, manifest, selection, schedule,
decision and scientific summary is reproduced at rtol1e-11/atol1e-13,
excluding only timing and regenerated input digests. CI must pass all
seventeen workflows before merge.

Intervals use 10000 whole-seed resamples (seed 175000). Small Gaussian
synthetic fixtures, three jitter levels and granted true times cannot
establish population guarantees, global rankings, or neural-memory utility.
The authoritative outcome is the registered tolerance point of 256 with its
middle-band reading.
