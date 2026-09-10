# Adaptive-window slope closes learning-negative on the same ramp

The registered candidate passed **74/75 independent comparisons** and closes
as **learning_negative** — on the same single strict cell as the benchmark
and the guard studies. Selected schedule (W_near=8, W_far=128, S=16) brings
the shallow-ramp gap from 0.000960 to **0.000521** against no-fallback
0.000256, paired interval [0.000251, 0.000278] still entirely positive.
Against every other control on the shallow ramp — SGD, W=8, ADWIN — the
candidate passes under preservation bounds, as it does on every primary,
every retention bound, and both other strict ramp cells (steep 0.000148 vs
0.000506, noisy 0.004083 vs 0.007925).

Three fixes have now been measured against the kink-smearing boundary, and
they rank cleanly: guard-by-handover 0.000313, adaptive fitting 0.000521,
unmodified trend 0.000960 — all strictly worse than the plain fast window at
0.000256. Fitting through the kink, however adaptive, loses to not fitting
at all where the signal is weakest. The boundary belongs to local fitting
itself.

All **384 tuning and 224 confirmation rows** were completed and finite. No
new default, broader benchmark, mechanism change or agent integration is
activated.

## What was implemented

The [registration](DESIGN-v3-slopewin.md) freezes the OLS estimator family
and dual base and searches only the window schedule W(d): W_near within S
steps of any request, W_far beyond it, fit causally per step. Selected
(8, 128, 16). J=0-equivalent identity — constant-128 widths reproduce the
slope study bit-for-bit — is asserted in parity. Controls are the unchanged
y-only trio (re-searched: W=8, lr=.128, delta=.1/clock=1, identical for the
twelfth consecutive study), the fixed-window slope reference, Bernoulli
random-window fallback, and the enriched no-fallback ablation. Every request
record carries target/drift/random provenance that never mixes.

Tuning objectives across the twelve schedules were nearly flat
(0.052962–0.053551): as with estimators before, the selection among
schedules carries almost no information. The finding is the confirmation
gap, not the index.

## Independent performance

Seven policies on the same **32 fresh confirmation seeds**. Lower is better.

| Policy | Primary MSE | Role |
| --- | ---: | --- |
| Adaptive-window slope | **0.084815** | Registered candidate |
| Fixed-window slope reference | 0.084815 | Diagnostic baseline |
| Matched no-fallback | 0.088002 | Mechanism ablation |
| SGD | 0.119566 | Deployable control |
| Fixed window, W=8 | 0.127287 | Deployable control |
| Random window | 0.197774 | Timing control |
| ADWIN2 | 0.197919 | Adaptive-window control |

Candidate and reference primaries are bit-identical: the schedule acts only
inside drift segments. The sole failure:

| Cell | Candidate | Control | 95% interval |
| --- | ---: | ---: | --- |
| nofallback/ramp_shallow, strict | 0.000521 | 0.000256 | [0.000251, 0.000278] |

## Privilege caveat

Granted boundaries throughout; the ±2-step abrupt tolerance still binds;
nothing here is deployable. What narrows, for the third and final time, is
the mechanism boundary — and this study says it does not narrow to zero.

## Evidence, phases and changed files

| Phase | Evidence | Status |
| --- | --- | --- |
| Registration/refinement | branch commit | Before study observations |
| Implementation/checks | branch commits | Before tuning |
| Tuning / manifest freeze | 384 rows | Eligible; trio identical to eleven predecessors |
| Confirmation | seeds 193000–193031, seven policies | 224 rows; learning-negative |
| Reproduction/publication | All 608 reached rows; nineteen workflows | See validation below |

Protocol SHA-256:
`4e674926a745a71073c3c3109fd05cc0eb128fce0e501c3c1cd2e1fe50494b83`.
Development 190000–190007, tuning 191000–191007, confirmation 193000–193031,
bootstrap 195000 and the 196000+ RNG domains are separate and disjoint from
all previous studies.

New files: `v3_slopewin.py`, `v3_slopewin_policy.py`, `study_v3_slopewin.py`,
`report_v3_slopewin.py`, `check_v3_slopewin.py`,
`.github/workflows/v3-slopewin-checks.yml`, the registration, this results
file and `results/v3-slopewin/`. README and PLAN/V3 status pointers report
the outcome. Earlier scientific sources, evidence, protocols, all eighteen
previous workflows, dependencies and agent defaults remain unchanged. No
capability or registry row is promoted.

The [generated report](results/v3-slopewin/report.md) includes all 75
candidate comparisons with their improve/preserve/strict modes, per-fixture
absolute errors with window schedules, regime shares and slope magnitudes,
and execution times.

## Validation and limits

All commands below passed locally, including reproduction of all 608 new rows.
Python commands use the project's existing `.venv`:

```sh
python check_v3_slopewin.py --evidence results/v3-slopewin --reproduce
python report_v3_slopewin.py --check
python check_evidence.py
git diff --check
```

Checks cover adaptive-window parity against per-step numpy fits, fixed-width
kernel parity, window-schedule construction, J=0 slope-study identity,
frozen estimator parity, causal prefixes, coordinate isolation, privilege
isolation of granted schedules, all 75 vetoes on the adapted cells,
per-request provenance accounting, immutable sources/manifests/stages,
missing/invalid/non-finite evidence, and three-regime memory accounting. The
parity suite caught five pre-observation implementation bugs. Every reached
row, manifest, selection, probability, decision and scientific summary is
reproduced at rtol1e-11/atol1e-13, excluding only timing and regenerated
input digests. CI must pass all nineteen workflows before merge.

Intervals use 10000 whole-seed resamples (seed 195000). Small Gaussian
synthetic fixtures, finite schedule menus and granted boundaries cannot
establish population guarantees, global rankings, or neural-memory utility.
The authoritative outcome is the candidate's independent learning-negative
result on the shallow ramp.
