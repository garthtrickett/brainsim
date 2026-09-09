# Bounded bursts fail independent learning advancement

The registered burst candidate passed **46/60 independent learning comparisons**
and closes as **learning-negative**. Primary post-switch MSE was **0.261323**,
compared with **0.194492 for equally searched Adam** and **0.119910 for SGD**.
Even the independently tuned perfect-timing oracle had MSE **0.146911** and
failed the full criteria against SGD. This finite burst family has not earned
advancement or integration.

The fixed detector passed all **12 diagnostic cells**, and actual burst starts
caught every abrupt target change within 100 observations. The remaining gap
cannot be attributed solely to failing to trigger on changes. Oracle scheduling
improves this controller's results, but is privileged and changes more than
latency alone. No result here rules out every possible burst design or all V3.

## What changed and why

The preceding separate-reference study passed detection but failed learning with
continuous lr*(1+64*q) updates. Its positive modulation below the alarm threshold
suggested a possible retention problem, without proving that explanation.
This experiment keeps its detector AND calibrated threshold fixed, and replaces
continuous modulation with a bounded response to an alarm.

The candidate uses ordinary Adam at its base rate between alarms. On strict
q>0.4690234346011377 it raises the rate by a fixed factor for exactly D updates,
including the trigger update. A sustained alarm cannot extend a burst. Afterward,
16 consecutive quiet observations are required before another alarm can trigger.
This caps the learning rate, not realized Adam update magnitudes. It neither
resets optimizer state nor reads target/event metadata.

The [registration](DESIGN-v3-burst.md) was committed before observations. Its
refinement fixed startup and off-by-one semantics, post-burst rearming, oracle
ownership, frequency matching, all required comparisons and immutable stage gates.
Source-closure checking added a transitive reporting dependency before the
implementation freeze. No scientific source changed after tuning began.

## Equal finite-menu tuning

Each of five searched families received **12 configurations ×8 paired tuning
seeds ×all five fixtures**. Selection minimized the equal-weight mean of the
primary post-switch metric and the mean of 14 retention metrics. This was a
finite-menu comparison, not a claim of globally optimal settings.

| Policy | Selected configuration |
| --- | --- |
| Detected burst | lr=.032, factor=2, duration=16, beta2=.999 |
| Independently tuned oracle | lr=.032, factor=8, duration=16, beta2=.999 |
| Continuous reference modulation | lr=.032, gain=8, beta2=.999 |
| Adam | lr=.128, beta2=.999 |
| SGD | lr=.128 |
| Matched oracle | Exact detected-burst configuration |
| Random bursts | Exact detected-burst configuration |

Oracle_matched and random are ablations of the selected candidate, so they have
no independent parameter search. The independently searched oracle receives the
same budget as each searched family. It triggers only on true abrupt target-change
times, never noise transitions or drift, and receives no new target value.

Several selections lie on menu endpoints, including the candidate's base rate
and Adam's rate. The protocol explicitly fixes finite menus without automatic
extension. These outcomes cannot establish an optimum outside the tested choices.
The new tuning objective and comparator settings differ from the previous study;
compare policies within this fresh experiment, not raw means across studies.

Random trigger probability was frozen at **0.0004011424151655854**, derived from
**167 detected starts /421,488 tuning coordinate-updates**, with burst duration
and cooldown accounted for. This matches expected pooled frequency, not exact
confirmation counts, per-condition duty cycles or realized movement.

## Independent confirmation

All seven fixed policies ran on **32 fresh seeds**, across the unchanged core,
noise_jump, drift, exactly_quiet and mixed fixtures. All **224 confirmation rows**
were finite. Primary MSE averages equally over the four core/mixed switching
coordinates, using pre-update predictions over 200 observations after each switch.

| Policy | Primary MSE | Role |
| --- | ---: | --- |
| SGD | **0.119910** | Deployable control |
| Independently tuned oracle | 0.146911 | Privileged diagnostic |
| Adam | 0.194492 | Deployable control |
| Matched oracle | 0.218205 | Privileged diagnostic |
| Detected burst | 0.261323 | Registered candidate |
| Continuous reference modulation | 0.277312 | Deployable control |
| Random bursts | 0.297185 | Matched timing control |

The candidate's paired 95% difference intervals are:

- versus Adam: **[0.062226, 0.071490]**, worse;
- versus SGD: **[0.137831, 0.145210]**, worse;
- versus continuous: **[-0.020962, -0.010850]**, lower error, but only a **5.77%**
  mean reduction, below the required 10%;
- versus random: **[-0.038527, -0.032953]**, a **12.07%** mean reduction, passing
  that primary comparison.

Of 60 required candidate comparisons, **14 fail: three primary and 11 retention /
per-condition checks**. For example, noisy switching MSE is **0.338489** versus
**0.151504 for SGD**, and quiet switching MSE is **0.158330** versus **0.134337
for random bursts**. Candidate performance during the noise-decrease window also
fails the uncertainty-aware non-regression bound against SGD. Selected aggregate
wins do not override these failures.

## What the timing controls resolve

The independently tuned oracle passes **25/30** checks against Adam and SGD.
It passes all 15 against Adam, including its primary improvement, but fails
five against SGD: primary, noisy switching, both mixed post-switch cells and the
noise-decrease window. Its primary difference versus SGD has paired 95% interval
**[0.021134, 0.033082]**. Perfect trigger timing plus the selected stronger burst
still does not establish the required advantage over the simpler control.

The matched oracle passes **20/30** checks. Its primary MSE falls from candidate
**0.261323 to 0.218205** with parameters held fixed, but still exceeds both Adam
and SGD. This diagnoses consequences of replacing detector-driven scheduling
with true-change scheduling; it does not isolate delay from removing false or
repeated bursts. Oracle timing is not a mathematical performance upper bound.

The raw detector catches **32/32** in each of eight abrupt target cells, with
mean detection delays of **10.03–12.84 observations**. Actual burst-start hit
counts and first-start latencies match those raw detections in these cells.
It raises alarms in **13/1600 quiet** and **8/1600 noisy** stationary blocks,
and **0/32** of either noise-transition window. All 12 diagnostic cells pass;
these counts were not used to override learning outcomes.

Across all confirmation coordinates there are **729 candidate starts**, **661
random starts**, and **256 starts in each oracle arm**. Random bursts distribute
activity differently: for example, 79 starts on the stationary noisy core versus
10 for the detector, and 70 on noisy switching versus 96 for the detector.
The expected-frequency control therefore does not isolate timing at an exactly
matched realized burst count. The generated report exposes every condition's
counts, duty cycle, event latencies, errors and actual update norms.

The useful finding is limited: the observed schedule beats its random control on
the aggregate primary metric, and true-change scheduling improves the burst
controller further, but neither tested burst policy clears the strong controls
and all retention requirements. This closes the finite-menu experiment; it does
not activate another search, a broader benchmark or agent integration.

## Evidence and implementation

| Phase | Evidence | Status |
| --- | --- | --- |
| Registration | `1c45603b7c7e7ad3d44c4a3ba822d95b7bac05c5` | Before study observations |
| Implementation and refinement | `0a40c0ac0677f6ef1b6e54cd02dfc998a3a8dc82` | Before tuning |
| Tuning / manifest freeze | `f6ee9f4aa04757a155b7934e732ca249817255da` | 480 complete rows; before confirmation |
| Confirmation | seeds 73000–73031, all seven policies | 224 complete rows; learning-negative |
| Reproduction / publication | All 704 reached rows and all seven workflows | See validation below |

Protocol SHA-256:
`ef249ae9dcf9afe8822ee2c0f188f2e780596450b7fcc6881028191b3e8a4d5c`.
Development seeds 70000–70007, tuning 71000–71007, confirmation 73000–73031 and
bootstrap 75000 are separate. Source snapshots cover 23 files, including applicable
protocols, transitive runtime/report/check dependencies and the inherited
threshold manifest. Snapshots preserve provenance after squash merge.

New files: `v3_burst.py`, `v3_burst_policy.py`, `study_v3_burst.py`,
`report_v3_burst.py`, `check_v3_burst.py`, `.github/workflows/v3-burst-checks.yml`,
this report, the registration and `results/v3-burst/`. README and the PLAN/V3
status pointers record this outcome. Earlier scientific sources, evidence,
protocols, all six previous workflows, dependencies and agent defaults are intact.
No capability registry row or agent feature is promoted.

The [generated report](results/v3-burst/report.md) contains all 60 candidate and
all 60 oracle contrasts, all 12 raw detector cells, full condition metrics, activity
and measured row execution time. The [summary](results/v3-burst/summary.json) also
includes uncertainty. Raw evidence retains every tuning score and candidate
prediction-error/recovery record alongside its alarms.

## Validation and limits

All listed local validation commands passed, including reproduction of all 704
new rows and all 368 prior reference rows. Python commands use the project's
existing `.venv`:

```sh
python check_v3_burst.py --evidence results/v3-burst --reproduce
python report_v3_burst.py --check
python check_evidence.py
python check_v3_reference.py --evidence results/v3-reference --reproduce
python report_v3_reference.py --check
git diff --check
```

Tests cover independent scalar Adam equations, inherited parity, exact burst /
cooldown/rearm semantics, causal prefixes, per-coordinate isolation, oracle
metadata boundaries, random RNG separation and frequency math, complete finite
selection, all 60 individual vetoes, oracle/diagnostic non-authority, invalid and
missing data, committed source/manifest requirements and forbidden confirmation.
Every reached row, selected setting, frequency, decision and scientific report
summary is reproduced at rtol1e-11/atol1e-13, excluding timings and regenerated
input digests. CI must pass all seven workflows before merge.

Intervals use 10,000 whole-seed resamples. The finite menus, 32 confirmation seeds
and separable supervised fixtures do not establish global optimizer rankings,
population false-alarm guarantees or reference-gradient scalability for a neural
network. The privileged oracle result is diagnostic; the candidate's independent
negative decision is the authoritative disposition.
