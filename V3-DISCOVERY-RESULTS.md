# Interference-as-discovery closes discovery-negative

The registered §11.1 candidate fails its own ground-truth falsifier and the
learning gate. Polarity-invariant discovery AUC\* is **0.626** for the
candidate and **0.626** for the shuffled-cue control (delta ≈ 0): the
discovered unit does not localize the hidden context. Learning is
**57/90 comparisons passed** — primary post-switch MSE **0.137288** versus
**0.114924 for SGD**, **0.123465 for the tuned fixed window**, and
**0.112036 for the matched no-conditioning control**. Conditioning on the
discovered unit adds nothing over random splits and loses to pooled
prediction. This experiment closes **discovery-negative** with no integration.

The privileged true-context oracle reaches primary MSE **0.047243**
(independently tuned) and **0.086099** (matched parameters), beating every
deployable control on the primary metric — but still fails its full criteria
(40/45 and 35/45), with stable/noise-condition failures against ADWIN. True
context would help adaptation enormously; the deployable discovery rule
cannot recover it. These diagnostics cannot override the candidate's
independent negative result.

All **480 tuning and 288 confirmation rows** were completed and finite.
No new default, broader benchmark, architecture growth or agent integration
is activated.

## What was implemented

The [registration](DESIGN-v3-discovery.md) tests V3 §11.1 on the existing
signal: y bytes are identical to the forgetting fixtures at equal seeds, so
the y-only controls stay comparable. The evaluator adds a hidden binary
context per coordinate (toggles at each `target_*` event, constant 0
otherwise) and a scalar cue `x = (2c−1)·0.5 + N(0,1)` available before each
prediction (single-sample AUC ≈ 0.76: learnable but not trivial).

The candidate keeps a pooled mean, two conditional means, an interval scale
`s` (agreement shrinks, conflict grows, pooled movement damped by
`1/(1+s)`), and cue weights trained online on the free label
`sign(y − pred)`. When `s ≥ TAU` it predicts from the conditional selected
by the cue; otherwise from the pooled mean. Polarity is arbitrary by
construction, so the gate uses polarity-invariant AUC\* = max(AUC, 1−AUC);
the registration was refined to AUC\* before implementation, with rationale
recorded, before any study observation.

Controls: y-only window/SGD/ADWIN2 (unchanged menus), random splits
(Bernoulli 0.5), shuffled cue (within-coordinate time permutation:
marginals preserved, cue–context correlation destroyed), and a matched
no-conditioning control (same state/updates, always predicts pooled). The
shuffled arm is the capacity control: if the candidate wins by extra
parameters alone, shuffled wins too.

## Equal-budget finite tuning

Five families each received **12 configurations × 8 paired seeds × all five
fixtures**, selected on the same objective as burst/forgetting (half primary
post-switch MSE, half mean of 14 retention metrics). Matched arms received
no additional search.

| Policy | Selected setting |
| --- | --- |
| Discovery | tau=0.5, alpha=0.01, cue_lr=0.01, lr=0.2 |
| Independently tuned oracle | tau=0.05, alpha=0.1, cue_lr=0.01, lr=0.05 |
| Fixed window | W=8 |
| SGD | lr=.128 |
| ADWIN2 | delta=.1, clock=1 |

All three y-only controls selected the identical settings as the forgetting
study (W=8, lr=.128, delta=.1/clock=1) — instrument stability across
registrations. Discover selections sit on menu endpoints (TAU high,
alpha/cue_lr low, lr high); these were explicitly reportable outcomes with
no automatic search extension.

## Independent performance

Each of nine policies ran on the same **32 fresh confirmation seeds**.
Primary MSE averages the four switching coordinates over 200 pre-update
predictions after each target change. Lower is better.

| Policy | Primary MSE | Role |
| --- | ---: | --- |
| Independently tuned oracle | **0.047243** | Privileged diagnostic |
| Matched oracle | 0.086099 | Privileged diagnostic |
| Matched no-conditioning | 0.112036 | Matched capacity control |
| SGD | 0.114924 | Deployable control |
| Fixed window, W=8 | 0.123465 | Deployable control |
| Random splits | 0.136749 | Timing/capacity control |
| Detector-controlled discovery | 0.137288 | Registered candidate |
| Shuffled cue | 0.138018 | Localisation control |
| ADWIN2 | 0.191803 | Adaptive-window control |

Candidate-minus-control paired 95% intervals (primary): SGD
**[0.020440, 0.024283]**, worse; fixed window **[0.011210, 0.016271]**,
worse; matched no-conditioning **[0.023165, 0.027384]**, worse; random
**[−0.002041, 0.003136]**, failing the required benefit; shuffled
**[−0.003169, 0.001702]**, failing the required benefit; ADWIN2 passes
alone. The candidate's 33 failures span primary and retention cells against
every control except ADWIN2.

## What the discovery gate shows

Mean polarity-invariant AUC\* over four switching coordinates, 32 seeds:

| Arm | Mean AUC\* | 95% interval |
| --- | ---: | --- |
| Discover | 0.625520 | [0.612679, 0.638624] |
| Shuffled | 0.626177 | [0.613013, 0.640123] |
| Delta | −0.000657 | [−0.009958, 0.008811] |

The gate requires candidate ≥ 0.65 (lower bound > 0.55), shuffled inside
[0.40, 0.60], and delta > 0.10 (lower > 0.05). All three cells fail. The
cue predictor learns *something* (0.63 > 0.5), but the identical shuffled
score proves it is not the hidden context — it is pull-sign dynamics that
exist regardless of cue (e.g. systematic post-switch pull directions while
means re-adapt, picked up through the evolving cue weights and bias). This
is exactly the failure V3 §12 named in advance: the contested set did not
localise the right variable, so the signal is noise and the idea dies in
this form. No MSE outcome can pass this gate, and none did.

## Evidence, phases and changed files

| Phase | Evidence | Status |
| --- | --- | --- |
| Registration/refinement | `7425958` / `30d0ac3` | Before study data |
| Implementation/checks | `3421d3b` | Before tuning |
| Tuning / manifest freeze | `ca5de7a` | 480 rows; before confirmation |
| Confirmation | seeds 93000–93031, nine policies | 288 rows; discovery-negative |
| Reproduction/publication | All 768 reached rows; nine workflows | See validation below |

Protocol SHA-256:
`48006f99b4e29475b265a883b73eff680da7bddcaa3adbedb34e15fda44d07cb`.
Development 90000–90007, tuning 91000–91007, confirmation 93000–93031 and
bootstrap 95000 are separate and disjoint from all previous studies. Thirty+
source snapshots include applicable protocols and every transitive local
runtime/report/check dependency. No scientific source changed after
observations began. Snapshots preserve identities after squash merge.

New files: `v3_discovery.py`, `v3_discovery_policy.py`,
`study_v3_discovery.py`, `report_v3_discovery.py`, `check_v3_discovery.py`,
`.github/workflows/v3-discovery-checks.yml`, the registration, this results
file and `results/v3-discovery/`. README and PLAN/V3 status pointers report
the outcome. Earlier scientific sources, protocols, evidence, all eight
previous workflows, dependencies and agent defaults remain unchanged. No
capability or registry row is promoted.

The [generated report](results/v3-discovery/report.md) includes all 90
candidate and both 45 oracle comparisons, the three discovery-gate cells,
memory and update-norm summaries and execution times. Raw records retain
cue/context/split provenance alongside scores, hats and interval scales.

## Validation and limits

All commands below passed locally, including reproduction of all 768 new
rows and the previous burst+forgetting evidence. Python commands use the
existing project `.venv`:

```sh
python check_v3_discovery.py --evidence results/v3-discovery --reproduce
python report_v3_discovery.py --check
python check_evidence.py
python check_v3_forgetting.py --evidence results/v3-forgetting --reproduce
python report_v3_forgetting.py --check
python check_v3_burst.py --evidence results/v3-burst --reproduce
python report_v3_burst.py --check
git diff --check
```

Checks cover hidden-context construction, cue/shuffle/split determinism and
isolation, hand-worked kernel parity (including TAU=0/always-conditional and
TAU=inf/never-conditional endpoints, tie-pull rule, frozen inactive memory,
logistic-step parity), AUC math, causal prefixes, coordinate isolation,
privilege rejection in deployable arms, every 90 vetoes, gate vetoes in both
directions (MSE cannot pass discovery), all 45 oracle cells, immutable
sources/manifests/stages, missing/invalid/non-finite evidence and memory
accounting. Every reached row, manifest, selection, decision and scientific
summary is reproduced at rtol1e-11/atol1e-13, excluding only timing and
regenerated input digests. CI must pass all nine workflows before merge.

Intervals use 10000 whole-seed resamples (seed 95000). Small Gaussian
supervised fixtures, finite parameter menus and privileged oracles cannot
establish population guarantees, global rankings, or neural-memory utility.
The authoritative outcome is the candidate's independent
discovery-negative result.
