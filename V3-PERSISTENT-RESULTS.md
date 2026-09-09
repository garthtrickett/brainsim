# Persistent mean-change detector: observer passes, learning loop fails

The registered candidate passed **all 12 fixed-observer detector checks**, including
all tested target changes and simultaneous target/noise changes, with **0/32 alarms
on noise increases and 0/32 on noise decreases**. This addresses the preceding
experiment's observed failure in passive observation on the new confirmation data.

During its own learning trajectory it passed only **6/12 checks**. It detected
just **1/32 noisy target-down events and 1/32 noisy target-up events**, and failed
all four simultaneous target/noise-change cells. Overall **18/24** candidate cells
pass. The registered all-cells rule therefore closes this experiment as
**detector-negative**. Independent performance remains unrun; no defaults change.

## What changed and why

The previous mean-disagreement signal detected target changes but also reacted
to noise increases. This experiment tested one fixed candidate that compares
16 recent gradients with 128 earlier, non-overlapping gradients, estimates their
variances separately, and requires four consecutive standardized differences
with the same sign. The minimum magnitude over those four scores drives a fixed
bounded gate. Four overlapping scores are correlated; they are not four
independent statistical tests.

The [registered protocol](DESIGN-v3-persistent.md) includes the exact equations,
seed partitions and decision rules. The controls are the unchanged current gate,
a persistence-only version of it, and a two-sided CUSUM with moving reference and
scale estimates. The CUSUM recurrence follows the [NIST handbook](https://www.itl.nist.gov/div898/handbook/pmc/section3/pmc323.htm);
our moving estimates and empirical calibration are explicit adaptations, with
no claim to textbook known-parameter guarantees. This is not a reproduction of
the previously linked likelihood-ratio research paper or a novelty claim.

Every detector uses one fixed configuration, Adam lr=.004 and gain=64 transferred
from the completed gain search, and the same 16 calibration seeds. No method
receives an additional search. These settings are not claimed optimal for the
new gate scales. One threshold per arm/mode is calibrated on stationary quiet
and noisy block maxima, pooled equally. Thresholds and sources were committed
before any independent detector observations.

The added two-coordinate mixed fixture covers every combination of target
up/down and noise increase/decrease. A blanket veto of noise changes cannot pass
these checks. The learner receives observations only; targets, event times,
noise regimes and future observations remain evaluator-owned.

## Independent candidate findings

Each event cell contains 32 fresh seeds; stationary cells contain 1,600 blocks.
Detection must be >=80% in each direction/condition within 100 observations.
False alarms must be <=5%. Fixed means the observer's prediction remains zero;
closed means the gate controls its own Adam updates.

| Condition | Fixed observer | Closed learning loop | Required |
| --- | ---: | ---: | --- |
| Quiet stationary alarm blocks | 8/1600 (0.5%) | 21/1600 (1.3125%) | <=5% |
| Noisy stationary alarm blocks | 14/1600 (0.875%) | 0/1600 | <=5% |
| Quiet target-down detection | 32/32 | 30/32 (93.75%) | >=80% |
| Quiet target-up detection | 32/32 | 30/32 (93.75%) | >=80% |
| Noisy target-down detection | 32/32 | **1/32 (3.125%)** | >=80% |
| Noisy target-up detection | 32/32 | **1/32 (3.125%)** | >=80% |
| Noise-increase alarms | 0/32 | 0/32 | <=5% |
| Noise-decrease alarms | 0/32 | 0/32 | <=5% |
| Target down + noise increase | 32/32 | **1/32 (3.125%)** | >=80% |
| Target up + noise decrease | 32/32 | **16/32 (50%)** | >=80% |
| Target down + noise decrease | 32/32 | **22/32 (68.75%)** | >=80% |
| Target up + noise increase | 32/32 | **0/32** | >=80% |

The candidate's calibrated threshold is **0.468224** in fixed-observer mode and
**0.816180** during learning. This measured difference accompanies the change in
detection behavior. The experiment does not isolate whether the cause is the
transferred update strength, endogenous movement of gradients, gate mapping,
calibration distribution, or their interaction. It would be incorrect to turn
this association into a confirmed mechanism.

A missed alarm also does not prove poor prediction or slow adaptation: those
learning outcomes were deliberately reserved for an independent performance
partition and were not evaluated after the detector failure.

## Controls and limits on interpretation

| Detector | Passing cells | Noise-increase alarms: fixed / closed | Disposition |
| --- | ---: | ---: | --- |
| Current mean disagreement | 22/24 | 5/32 / 5/32 | Fails both noise-increase cells |
| Persistence only | 22/24 | 4/32 / 4/32 | Fails both noise-increase cells |
| Candidate | 18/24 | 0/32 / 0/32 | Fails six closed-loop target-change cells |
| CUSUM reference | 22/24 | 9/32 / 8/32 | Fails both noise-increase cells |

All controls detect every tested target switch, including mixed changes, and pass
the other stationary/noise-decrease cells. None satisfies the entire detector
screen; no control is promoted to the candidate after seeing results. Pass counts
are descriptive and are not a new ranking or selection criterion.

[The generated report](results/v3-persistent/report.md) retains all 96 arm/cell
results, censored latencies, seed-bootstrap intervals, and startup/settled gate
activity for all conditions. Raw per-event records are in the archive. Bootstrap
intervals use 10,000 whole-seed resamples, seed 55000. Zero observed alarms and
32/32 successes do not prove population probabilities of zero or one; degenerate
bootstrap intervals at those boundaries cannot quantify unseen rare events.

This is evidence for a passive detector on a small synthetic fixture, and a
negative result for its specified learning-coupled policy. It neither rejects
all V3 ideas nor establishes an effective learning rule, optimizer-wide advantage,
representation-interference solution, or agent capability.

## Evidence, provenance and validation

| Stage | Rows | Disposition |
| --- | ---: | --- |
| Calibration | 64 | Complete, finite; immutable manifest frozen |
| Independent detector | 128 | Complete; candidate detector-negative |
| Independent performance | 0 of conditional 256 | Not run: detector prerequisite failed |

All **192 reached scientific rows** are archived with snapshots of every runtime
source, report and decision code, applicable protocols and pinned requirements.
Seeds 51000–51015 calibrate; seeds 53000–53031 confirm. Reserved performance seeds
54000–54031 remain unsampled. Development tests use 50000–50007 and synthetic
records, including exercise of the conditional performance code without drawing
performance observations.

- Registration commit: `fc78d253bd3101b5a8d804f111cf89fe1a423f79`.
- Implementation committed before observations: `c0e225e`.
- Manifest committed before confirmation: `2af02b0`.
- Protocol SHA-256: `6c64064ce2aa347379b55bf21218ffbecd4ffb3a23d7c7fd946802d9e7962daa`.

These commits record ordering in PR history; source snapshots remain in the
merged tree after squash/branch cleanup. Runtime and report sources did not
change after observations. Additional development-only tests cover conditional
constant-gate semantics and source-mismatch rejection.

New files: `v3_persistent.py`, `v3_persistent_policy.py`,
`study_v3_persistent.py`, `report_v3_persistent.py`, `check_v3_persistent.py`,
a dedicated CI workflow, this report and the registered protocol. Existing
protocols, scientific runtime code, evidence and all four prior workflows remain
byte-for-byte unchanged. README and roadmap pointers identify the latest outcome.

All commands below passed locally in the existing pinned environment. All 192
new rows and the previous follow-up's 3,984 rows reproduced with unchanged
scientific outcomes:

```sh
python check_v3_persistent.py --evidence results/v3-persistent --reproduce
python report_v3_persistent.py --check
python check_evidence.py
python check_v3_gain.py --evidence results/v3-gain-followup --reproduce
python report_v3_gain.py --check
git diff --check
```

Unit checks independently calculate the window/EMA/CUSUM equations, verify exact
current-gate parity, causality, coordinate isolation, mixed fixture construction,
arithmetic failure handling, all 24 detector vetoes, 105 conditional performance
comparisons, immutable manifest/source checks and forbidden-stage enforcement.
Reproduction regenerates every reached numerical row, threshold, constant and
decision at rtol 1e-11 / atol 1e-13, excluding only timing and regenerated
scientific-input hashes. Scientific failure must reproduce with green checks.
The five GitHub workflows also validate all previous studies and frozen V1 scores.

The experiment is closed at its registered negative stop. No performance
confirmation, retuning, new detector, or agent integration automatically follows.
