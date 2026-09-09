# Slice1 closure: promising tuning result, inconclusive experiment

The registered mean-disagreement successor reached the search limit. Its selected
configuration uses gain **64**, the highest searched value. The plan explicitly
requires a tuning-inconclusive stop in that case. All 1,920 registered tuning
trajectories completed; calibration and both confirmation partitions were not
opened. This closes the bounded slice without changing any brainsim default.

This is not a second confirmed failure of the original variance hypothesis, and
it is not a confirmed success for the successor. It is an incomplete basis for
judging the successor's scientific claims, with an explicit, predeclared reason.

## Result and rationale

The first experiment showed that the centered-variance gate could beat Adam while
losing to the simpler single-timescale control and missing noisy switches. Slice1
therefore tested a different proposed signal: normalized disagreement between
fast and slow mean gradients. Its fixed .1/.01 EMA rates and update multiplier
were registered before the new search. The original experiment remains intact.

All arms used one shared configuration across four simultaneous, independent
coordinates: stationary quiet/noisy and switching quiet/noisy. Each arm received
24 configurations and 16 tuning seeds, 6,000 observations per trajectory.
Selection minimized mean post-burn-in excess MSE, using identical observations
across arms. This is 1,920 trajectories and 46,080,000 coordinate updates.

| Arm | Selected configuration | Tuning excess MSE |
| --- | --- | ---: |
| SGD | lr=0.04061586 | 0.01983428 |
| Adam | lr=.016, beta2=.9999 | 0.02167431 |
| Single variance | lr=.016, gain=1 | 0.01859112 |
| Historical dual variance | lr=.016, gain=8 | 0.01756072 |
| New mean disagreement | lr=.004, gain=64 | 0.01188590 |

The candidate leads these tuning scores. However, the winning candidate is at
the gain boundary. The registered rule does not distinguish a candidate boundary
from a comparator boundary: either blocks advancement. Adam's beta2 endpoint is
also disclosed, but that endpoint is explicitly permitted by the protocol.

Extending the grid now, running confirmation anyway, or presenting the selected
tuning scores as held-out evidence would change the accepted experiment. None
was done. The result does not establish detection reliability, retention,
independent learning gains, or an advantage over the constant-gate ablation.
That ablation depends on calibration and was therefore not constructed from data.

## Phase dispositions

| Phase | Disposition |
| --- | --- |
| 0: baseline and registration | DONE; original study reproduced; successor protocol published in PR #4 |
| 1: causal instrument | DONE; streams, scoring and event tests published in PR #5 |
| 2: candidate and controls | DONE; registered updates and causal/invariance tests published in PR #6 |
| 3: tuning and calibration | Tuning DONE; registered search screen INCONCLUSIVE; calibration not run; evidence published in PR #7 |
| 4: detector confirmation | NOT RUN: tuning prerequisite failed |
| 5: performance confirmation | NOT RUN: tuning prerequisite failed |
| 6: closure | Evidence reproduced, stop enforced, report and status published |

A not-run prerequisite is an intentional disposition, not a fabricated pass.
No detector or performance conclusion is inferred from tuning. The reserved
confirmation partitions remain unused; any follow-up needs a new registration
and must explicitly allocate untouched confirmation data.

## What was implemented

- `v3_slice1_streams.py`: evaluator-owned targets/events, independent RNG domains,
  pre-update scores, directional noise-change metrics and censored recovery.
- `v3_slice1_learning.py`: SGD, Adam, single/historical gates, the mean-disagreement
  candidate and the constant-gate update path. Learners accept observations only.
- `v3_slice1_decisions.py`: exact budgets, selection, complete-cell gates, paired
  statistics and early-stop classifications.
- `study_v3_slice1.py`: staged runner, atomic checkpoints, immutable registration
  checks, committed-manifest enforcement and blocked dependent stages.
- `check_v3_slice1.py`: instrument/update tests, constructed decision-edge tests,
  archive checks and full reached-stage reproduction.
- `report_v3_slice1.py`: recomputed decision, source-fingerprinted report and
  explicit distinction between absent, pending and forbidden evidence.
- `DESIGN-v3-slice1.md`, `results/v3-slice1/`, the slice1 workflow and status docs.

The diagnostic/performance command paths have scientific unit and prerequisite
checks; they were not exercised on reserved confirmation data. Their existence
is not evidence that those scientific phases ran.

Registration publication: `70f0449db3ecd7288773f8dcbf8547283ff1c7f6`.
Runner/decision implementation committed before tuning: `264d9eb`.
Complete tuning and manifest frozen in original PR history: `f6a08a3`.
Original commits may be squash-merged; exact source snapshots and protocol
provenance are preserved in every tuning evidence envelope.

## Validation and reproducibility

These commands passed locally:

```sh
.venv/bin/python check_v3_gate.py --evidence results/v3 --reproduce
.venv/bin/python report_v3_gate.py --check
.venv/bin/python check_v3_slice1.py
.venv/bin/python study_v3_slice1.py prepare
.venv/bin/python report_v3_slice1.py
.venv/bin/python check_v3_slice1.py --evidence results/v3-slice1 --reproduce
.venv/bin/python report_v3_slice1.py --check
.venv/bin/python check_evidence.py
.venv/bin/python check_v1.py
git diff --check
```

Reproduction reruns all 1,920 tuning trajectories, compares every scientific
field with rtol 1e-11/atol 1e-13, and independently recomputes the selected
configurations and stop decision. Only elapsed time is excluded. Verification
rejects changed source/protocol hashes, missing rows, stale reports and forbidden
later-stage files. Constructed tests exercise scientific pass/fail boundaries,
zero-gain rejection, malformed metrics and confirmation prerequisites without
sampling study confirmation streams.

GitHub `V3 slice1 validation` enforces full reached-stage reproduction; existing
`V3 validation` preserves the original 552-row study, and `V1 validation` retains
all 56 frozen reference scores. Publication requires all three workflows green
on the exact PR commit. Passing CI validates implementation and reproducibility;
it does not convert this inconclusive experiment into a scientific success.

Full tuning objectives, selected configurations, source hashes and seed lists
are in [the frozen manifest](results/v3-slice1/manifest.json). The generated
[report](results/v3-slice1/report.md) and [decision summary](results/v3-slice1/summary.json)
are derived from the complete archive.

## Remaining uncertainty and next boundary

It remains unknown whether the candidate distinguishes noisy changes reliably,
retains stationary performance, or beats simple controls on independent data.
Only the bounded tuning behavior has been measured. The four-coordinate problem
is separable and does not test representation interference or brainsim behavior.
The implementation also has no optimized memory-cost claim: the reference kernel
allocates seven width-sized state arrays for every arm.

A further investigation would need a new, predeclared search policy addressing
the gain-boundary result and independently reserved confirmation. It is outside
this slice. No automatic range extension, agent integration, v2 rewrite, or later
v3 queue item follows this closure.
