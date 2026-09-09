# Bounded gain follow-up: search resolved, detector rejected

The wider search selected **learning rate .004 and gain 64** again, now inside
its registered range. The previous search-limit concern is resolved for this
bounded grid. Independent testing then found a specific failure: the gate
responds to increases in noise even when the target does not change.

It caught every tested target switch, but noise-increase alarms occurred in
**8/32 fixed-observer trials (25%)** and **11/32 learning trials (34.375%)**.
Both exceed the registered 5% maximum. Fourteen of the sixteen detector cells
pass; these two failures close the experiment as **detector-negative**.
Independent performance testing was not opened. No brainsim default changes.

## What this establishes

The candidate is sensitive to target changes, including under the tested high
noise. It does not meet the stronger claim that it distinguishes those changes
from an increase in noise. Low alarm rates under *constant* noise did not imply
low alarm rates during a noise transition.

This rejects this specified mean-disagreement signal/policy on these fixtures.
It does not reject all of V3, establish a general impossibility, or establish
whether the candidate would improve independent prediction performance. Tuning
scores cannot answer that last question, and the constant-gate performance
comparison remains unrun. No retuning or second expansion follows this result.

## Registered search and confirmation

[The new protocol](DESIGN-v3-gain-followup.md) was committed before observations.
It preserves the slice1 kernel, fixtures and metrics, increases each method's
budget to 48 configurations × 16 fresh tuning seeds, and jointly searches base
rate and gain. Gated gains extend through 128, 256 and 1024. All five methods
complete the same 3,840 total tuning trajectories: 92,160,000 coordinate updates.

| Method | Selected configuration | Base rate × gain | Tuning excess MSE |
| --- | --- | ---: | ---: |
| SGD | lr=0.03574304018 | — | 0.02050238 |
| Adam | lr=.032, beta2=.9999 | — | 0.01906885 |
| Single variance | lr=.016, gain=1 | .016 | 0.01934858 |
| Historical dual variance | lr=.016, gain=8 | .128 | 0.01877149 |
| Mean disagreement | lr=.004, gain=64 | .256 | 0.01230101 |

All selected rates and gated gains are interior; no disqualifying search flag
remains. Adam's beta2 endpoint is disclosed and explicitly permitted. The
candidate has the lowest selected tuning score, which is not a held-out result
or proof that this grid finds a global optimum.

Sixteen separate calibration seeds fix thresholds for each gated method in
fixed-observer and learning modes, using pooled stationary-block maxima. They
also fix the candidate's constant-gate ablation values. The complete manifest
and report-source fingerprint were committed before the 32 detector seeds were
sampled. No threshold is adjusted after seeing confirmation.

The protocol separately permits detection at a frozen finite policy if a wider
search still hits its boundary; performance still requires adequate search and
passing detection. This distinction was registered before data and did not need
to be exercised here: search was eligible.

| Candidate detector condition | Fixed observer | During learning | Required |
| --- | ---: | ---: | --- |
| Quiet stationary blocks with alarms | 18/1600 (1.125%) | 2/1600 (0.125%) | ≤5% |
| Noisy stationary blocks with alarms | 17/1600 (1.0625%) | 35/1600 (2.1875%) | ≤5% |
| Quiet target-down / target-up detections | 32/32 each | 32/32 each | ≥80% each |
| Noisy target-down / target-up detections | 32/32 each | 32/32 each | ≥80% each |
| Noise-increase windows with alarms | **8/32 (25%)** | **11/32 (34.375%)** | ≤5% |
| Noise-decrease windows with alarms | 0/32 | 0/32 | ≤5% |

Noise-increase seed-bootstrap 95% intervals are [12.5%, 40.625%] for the fixed
observer and [18.75%, 50%] during learning. The intervals resample whole seeds;
they are not independent-event intervals. Point-screen thresholds and 32-seed
samples do not establish population-wide guarantees, even for cells with 32/32
successes. Complete cells, censored latencies, startup/settled gate activity and
all controls' descriptive diagnostics are in the [generated report](results/v3-gain-followup/report.md).

## Evidence and implementation

| Stage | Complete rows | Disposition |
| --- | ---: | --- |
| Tuning | 3,840, five files of 768 | Eligible |
| Calibration | 48 | Finite; thresholds and constants frozen |
| Independent detector | 96 | Negative; all registered cells evaluated |
| Independent performance | 0 | Not run: detector prerequisite failed |

There are **3,984 reached scientific rows**. All use fresh seed partitions from
[the protocol](DESIGN-v3-gain-followup.md). Every raw event and failed criterion
is retained. Earlier V1, V3 and slice1 protocols, runtime sources and evidence
remain byte-for-byte unchanged.

New files are `v3_gain_policy.py` (grids and decisions), `study_v3_gain.py`
(staging and evidence), `report_v3_gain.py` (derived report), `check_v3_gain.py`
(policy checks and complete reproduction), and a separate GitHub workflow.
The runner directly reuses immutable slice1 simulation functions. Tuning is
checkpointed per method to avoid rewriting all 3,840 rows after every trial.
Source snapshots include transitive runtime files, both applicable protocols,
requirements and the report. Confirmation rejects an uncommitted/changed
manifest or a changed report fingerprint. Later-stage evidence is forbidden
after failed prerequisites.

Provenance in the PR history:

- Protocol registration: `c2dd7e6a4d4dd847ffc52c4d32958923c0d7a5cb`.
- Runtime implementation committed before tuning: `44af355`.
- Complete manifest/calibration committed before detection: `a0df1cf`.
- Registered protocol SHA-256: `a249ab4cda7a7810d26d78885ed073f557726040b28973fbb965b997142177bb`.
- Scientific manifest identity: `3deab2c81c2a194d8bedf779d90617b96df333d55562b1c5336ef41ade3d915b`.

Source snapshots and hashes remain available after branch cleanup. A squash
merge's final tree does not itself encode the earlier runtime ordering; the
registration, implementation and frozen-manifest commits record it.

## Validation and remaining limits

All commands below passed locally using the existing pinned Python environment.
All 56 V1 reference scores matched exactly; the original V3 and slice1 evidence
reproduced without changing their outcomes:

```sh
python check_v3_gain.py --evidence results/v3-gain-followup --reproduce
python report_v3_gain.py --check
python check_evidence.py
python check_v1.py
python check_reference.py --out /tmp/brainsim-gain-reference.json
python check_v3_gate.py --evidence results/v3 --reproduce
python report_v3_gate.py --check
python check_v3_slice1.py --evidence results/v3-slice1 --reproduce
python report_v3_slice1.py --check
git diff --check
```

Reproduction checks every reached numerical row at rtol 1e-11 / atol 1e-13,
then recomputes selected settings, calibrated thresholds, constants and every
detector decision. Only elapsed time and regenerated scientific-input hashes
are excluded. Policy tests use synthetic records and cover all sixteen detector
cells, all forty-four conditional performance comparisons, missing data,
non-finite trajectories and forbidden stages. No reserved performance
observations are generated by those tests.

The existing three GitHub workflows remain intact; the added workflow reproduces
this follow-up and checks its generated report. Scientific failure is the
archived finding, not a reason to weaken the checks.

The task is still a small, separable supervised fixture. Representation
interference, agent behavior, learning gains and the wider V3 program are not
settled by this test. Further work requires a separately specified hypothesis
and fresh evidence, rather than tuning against these detector outcomes.
