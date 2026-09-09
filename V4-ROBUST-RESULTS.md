# Robustness under frozen lies closes learning-negative on stability

The registered candidate passed **40/45 independent comparisons** and closes
as **learning_negative**. Its primary post-switch MSE was **0.103128**,
versus **0.115491 for SGD**, **0.123616 for the tuned fixed window** and
**0.191598 for ADWIN2** — adaptation under lies holds on every switching
cell against every control. All five failures are stable/noise cells against
ADWIN: stationary noisy 0.069985 vs 0.001029, noise_jump 0.027726 vs
0.000717, noise-increase 0.066762 vs 0.002346, both mixed stable cells.
False alarms tax stability exactly as predicted; nothing else fails.

The ADWIN-gated diagnostic is worse (29/45): real alarms plus graded response
double the noise-increase damage (0.125591). Timing-robust response does not
rescue mistimed schedules — it only makes adaptation survive them.

All **384 tuning and 160 confirmation rows** were completed and finite. No
new default, broader benchmark, mechanism change or agent integration is
activated.

## What was implemented

The [registration](DESIGN-v4-robust.md) freezes the lie profile (delay
uniform [0,8], miss 0.1, false Bernoulli 0.001/step — every rate traceable to
frozen retention evidence) and searches graded SGD: base rate 0.128
multiplied by (1+G·s_t) with s_t counting alarms in the trailing W_s steps,
G in [1,2,4,8] × W_s in [8,32,128]. The ADWIN-gated arm runs the selected
config on observed control alarms as a diagnostic operating point. Controls
are the unchanged y-only trio, re-searched for the eleventh consecutive
identical selection (W=8, lr=.128, delta=.1/clock=1).

Tuning selected **gain=2, window=8**; the high-gain/long-window corner
explodes (objective 7e37 at gain 8/W 128 — unbounded graded response
diverges on false alarms, measured rather than argued).

## Independent performance

Five policies on the same **32 fresh confirmation seeds**. Lower is better.

| Policy | Primary MSE | Role |
| --- | ---: | --- |
| Graded response, G=2/W=8 | **0.103128** | Registered candidate |
| SGD | 0.115491 | Deployable control |
| Fixed window, W=8 | 0.123616 | Deployable control |
| ADWIN-gated graded | 0.133386 | Diagnostic operating point |
| ADWIN2 | 0.191598 | Adaptive-window control |

## Reading

The falsifier as stated closes this experiment negative: no graded design
beats the fast trackers *while preserving stability*. But the shape of the
negative is new in the program's history — every prior V3 failure lost
adaptation, retention, or both; this one holds adaptation everywhere and
loses only stability, only to false alarms. Graded response is necessary and
insufficient: it buys exactly what binary bursting could not (adaptation
under mistimed schedules) and pays exactly where every alarm-driven policy
has paid (stable accuracy under false alarms). The missing piece is alarm
*selectivity*, not response shape — a detector question the program has
twice closed, now reframed by a learner that could actually use one.

## Privilege caveat

The lie profile is synthetic and evaluator-built; the ADWIN-gated arm is the
only observable-derived schedule and it fails broadly. Nothing here is
deployable. What is established is the response shape's half of the
bargain, with the numbers to show which half is missing.

## Evidence, phases and changed files

| Phase | Evidence | Status |
| --- | --- | --- |
| Registration/refinement | branch commit | Before study observations |
| Implementation/checks | branch commits | Before tuning |
| Tuning / manifest freeze | 384 rows | Eligible; trio identical to ten predecessors |
| Confirmation | seeds 183000–183031, five policies | 160 rows; learning-negative |
| Reproduction/publication | All 544 reached rows; eighteen workflows | See validation below |

Protocol SHA-256:
`a05b07315d2c72a52f6c16c0e1160e9708ae153c4260a58b739dd1711044b167`.
Development 180000–180007, tuning 181000–181007, confirmation 183000–183031,
bootstrap 185000 and the 186000+ lie RNG domains are separate and disjoint
from all previous studies.

New files: `v4_robust.py`, `v4_robust_policy.py`, `study_v4_robust.py`,
`report_v4_robust.py`, `check_v4_robust.py`,
`.github/workflows/v4-robust-checks.yml`, the registration, this results
file and `results/v4-robust/`. README and PLAN/V3 status pointers report the
outcome. Earlier scientific sources, evidence, protocols, all seventeen
previous workflows, dependencies and agent defaults remain unchanged. No
capability or registry row is promoted.

The [generated report](results/v4-robust/report.md) includes all 45
comparisons for both graded subjects, per-fixture absolute errors with lie
activity, and execution times.

## Validation and limits

All commands below passed locally, including reproduction of all 544 new rows.
Python commands use the project's existing `.venv`:

```sh
python check_v4_robust.py --evidence results/v4-robust --reproduce
python report_v4_robust.py --check
python check_evidence.py
git diff --check
```

Checks cover graded-gain equations on hand-worked traces, the frozen lie
profile (bounds, rates, independence, determinism, domain separation),
causal prefixes, coordinate isolation, privilege isolation of lie schedules,
all 45 vetoes for both subjects, per-alarm provenance accounting, immutable
sources/manifests/stages, missing/invalid/non-finite evidence, and graded
memory accounting. The parity suite caught six pre-observation
implementation bugs. Every reached row, manifest, selection, schedule,
decision and scientific summary is reproduced at rtol1e-11/atol1e-13,
excluding only timing and regenerated input digests. CI must pass all
eighteen workflows before merge.

Intervals use 10000 whole-seed resamples (seed 185000). Small Gaussian
synthetic fixtures, one frozen lie profile and graded SGD cannot establish
population guarantees, global rankings, or neural-memory utility. The
authoritative outcome is the candidate's independent learning-negative
result on stability.
