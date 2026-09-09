# Separate-reference detector: detection passes, learning advancement fails

The separate-reference setup passed **all 24 registered detector cells** and
therefore reached independent performance testing. It then passed **47/90 required
learning comparisons**. Its primary post-switch MSE was **0.304365**, compared with
**0.300031 for tuned Adam** and **0.294674 for SGD**. It did not earn the required
10% improvement against either and failed multiple retention checks.

This closes the registered experiment as **learning-negative**. The detector's
behavior is now independent of its learner, but this fixed update policy has
not earned a default or agent integration. All three stages completed, with
**368 reached scientific rows** archived and reproduced.

## What was tested

The previous study's persistent candidate passed passive observation and failed
six learning-coupled detector cells. This experiment kept that detector and its
16/128 windows, four-score persistence and q mapping unchanged, and compared:

| Setup | Detector observes | Learner |
| --- | --- | --- |
| coupled | Its own learner's pre-update gradients | Adam lr=.004, gain=64 |
| watch_adam | Ordinary Adam's pre-update gradients, without controlling it | Adam lr=.004, gain=0 |
| separate, the registered candidate | Gradients of a fixed zero reference | Separate Adam lr=.004, gain=64 |

All use beta1=.9/beta2=.999. Each setup has one fixed configuration and the same
16 calibration seeds. No new search or post-result threshold adjustment occurred.
The [protocol](DESIGN-v3-reference.md) fixes all equations and gates before data.
The underlying supervised fixtures, evaluator boundaries and metrics are unchanged.

The separate setup's passive and active gate sequences are identical **by
construction**. Its passing detector screen checks the new seeds and implementation;
it is not two independent replications or a new detector discovery. The new
scientific hurdle is whether using that signal helps independent learning.

## Native detector results

Thresholds come from the same pooled 99th percentile of stationary quiet/noisy
block maxima, with strict > for alarms. Each target/noise-direction cell has 32
events; each stationary cell has 1,600 blocks. Required detection is >=80% within
100 observations, with <=5% false alarms in each condition.

| Setup | Fixed threshold | Active threshold | Passing native cells |
| --- | ---: | ---: | ---: |
| coupled | 0.469023 | 0.813103 | 18/24 |
| watch_adam | 0.469023 | 0.456573 | 23/24 |
| separate | 0.469023 | 0.469023 | **24/24** |

Separate detects **32/32** in every quiet/noisy target direction and every
simultaneous target/noise-change cell. It has **1/32** noise-increase alarms,
**0/32** noise-decrease alarms, and **13/1600 quiet / 15/1600 noisy** stationary
alarm blocks. Fixed and active counts match exactly.

Coupled again fails six active target-change cells: noisy target down/up 0/32
each, and mixed cells 1/32, 23/32, 21/32, 0/32. Watch_adam detects every target
change but has 2/32 active noise-increase alarms (6.25%), failing that one cell.
Control failures do not change the predeclared candidate or its advancement gate.

## What the diagnostic prediction records clarify

This new registration explicitly recorded prediction error alongside alarms,
regardless of detector outcome. These diagnostic records are explanatory, not
independent learning confirmation and not a basis for choosing settings.

| Noisy core event, active mode | Alarms | Recovered within 100 observations |
| --- | ---: | ---: |
| coupled, target down | 0/32 | **29/32** |
| coupled, target up | 0/32 | **24/32** |
| watch_adam, target down | 32/32 | 0/32 |
| watch_adam, target up | 32/32 | 0/32 |
| separate, target down | 32/32 | 24/32 |
| separate, target up | 32/32 | 28/32 |

Recovery requires ten consecutive predictions with absolute error <.2, all
within the first 100 observations. Thus 29/32 and 24/32 of coupled's missed
alarms coincide with timely prediction recovery. **A missed alarm did not mean
that learning failed.** Conversely, watch_adam's alarms did not establish rapid
adaptation at its small unmodulated learning rate.

The predeclared common-threshold diagnostic scores each unchanged q sequence
at 0.469023. Coupled then detects 32/32 noisy downward and 31/32 upward changes,
but raises alarms in **443/1600 quiet stationary blocks (27.6875%)** and **6/32
noise-increase windows (18.75%)**. Lowering its threshold would not repair the
full detector criterion. These alternate cells never controlled advancement.

This separates threshold effects on recorded signals from prediction recovery,
but does not isolate every cause of the changed gradient statistics. Removing
modulation also changes the learner trajectory. A causal explanation of all
interactions would require further controlled tests; no new test is activated here.

## Independent performance

After committing the complete passing detector evidence, all seven fixed policies
were run on **32 fresh performance seeds**, across all five fixtures. The primary
metric is seed-level post-200 MSE averaged equally over the two core switching
and two mixed coordinates. Lower is better.

| Policy | Primary post-switch MSE | Separate's reduction versus this policy | Required improvement passes? |
| --- | ---: | ---: | --- |
| Separate reference | 0.304365 | — | — |
| Tuned Adam | 0.300031 | -1.44% | **No** |
| SGD | 0.294674 | -3.29% | **No** |
| Coupled persistent gate | 0.350430 | 13.15% | Yes |
| Single variance | 0.379332 | 19.76% | Yes |
| Constant mean-q boost | 0.479283 | 36.50% | Yes |
| Unmodulated matched Adam, watch_adam | 1.669829 | 81.77% | Yes |

The separate-minus-Adam paired 95% interval is **[-0.002513, 0.011755]**;
separate-minus-SGD is **[0.002494, 0.017412]**. The required 10% benefit is absent.
The mean improvement over the coupled policy also does not hold in every
condition: noisy core post-MSE regresses relative to that control.

There are **43 failed comparisons**: two primary improvement checks and 41
retention/non-regression checks. Examples from the independent partition:

- Noisy stationary MSE: separate **0.022847**, tuned Adam **0.015314**, constant
  boost **0.005461**; separate fails the retention bounds against both.
- Quiet core post-switch MSE: separate **0.252896**, tuned Adam **0.130679**;
  separate fails the per-condition non-regression bound.
- Noise-increase-window MSE: separate **0.066437**, SGD **0.019015**;
  separate fails the bound on this unchanged-target condition.

The [generated report](results/v3-reference/report.md) includes all 90 contrasts,
absolute per-condition errors and update norms for every policy, all native and
common-threshold cells, diagnostic recovery/miss intersections, and uncertainty.
Every required comparison counts; the stronger selected successes do not erase
other failures. Mean-q matching does not match realized update magnitudes.

The alarm threshold only classifies detections. The learner uses the continuous
multiplier **1+64*q**, including q below the alarm threshold. Passing a detector
screen therefore does not guarantee useful update magnitudes or retention.
This experiment demonstrates that distinction, without proving a unique cause
for every regression or ruling out all separate-reference designs.

## Evidence and provenance

| Stage | Seeds | Complete rows | Result |
| --- | --- | ---: | --- |
| Calibration | 61000–61015 | 48 | Finite; manifest frozen |
| Detector/explanatory diagnostics | 63000–63031 | 96 | Separate passes native criteria |
| Independent performance | 64000–64031 | 224 | Learning-negative |

Development fixtures use only 60000–60007; bootstrap seed 65000 is separate.
All 368 rows have source/protocol identity and snapshots of every transitive
runtime dependency, report/decision code, applicable protocols and requirements.
No runtime or report source changed after observations.

- Protocol registration: `8c72ef5e46e14fd22d04d84486176535f82b77c0`.
- Implementation committed before observations: `23eb048`.
- Manifest committed before diagnostics: `90c70ed`.
- Passing detector evidence committed before performance: `03a00e3`.
- Protocol SHA-256: `0d85fa18f4c636e4e93cb7f6d9cc5ef763fac8a7c2e0ccc0ee03ede28cef8341`.

Commit history records the ordering; snapshots remain in the final tree after
squash/branch cleanup. Older experiments retain their original outcomes and
unused partitions. Nothing was retrospectively reopened.

New files are `v3_reference.py`, `v3_reference_policy.py`, `study_v3_reference.py`,
`report_v3_reference.py`, `check_v3_reference.py`, the protocol, this report,
evidence and a separate workflow. Earlier scientific code, evidence, protocols
and all five previous workflows are unchanged; roadmap pointers report the new
outcome. No dependencies, agent behavior or defaults changed.

## Validation and scope limits

All local validation commands passed (Python commands used the project `.venv`):

```sh
python check_v3_reference.py --evidence results/v3-reference --reproduce
python report_v3_reference.py --check
python check_evidence.py
python check_v3_persistent.py --evidence results/v3-persistent --reproduce
python report_v3_persistent.py --check
git diff --check
```

Tests verify exact coupled parity and ordinary-Adam prediction/norm parity,
independent scalar Adam equations for external q, zero-gain parity, prefix
causality, coordinate isolation, separate-gate independence from learner settings,
recovery boundaries, explanatory intersections/denominators, all 24 native
vetoes, common-threshold non-authority, all 90 performance contrasts, exact row
cohorts, invalid/non-finite rejection, and immutable source/manifest/stage gates.
CI regenerates every reached numerical row and recomputes all thresholds,
constants, decisions and report summaries at rtol 1e-11 / atol 1e-13, excluding
only timing and regenerated scientific-input hashes. All six workflows must pass,
including the five earlier-study/baseline workflows.

Intervals resample whole seeds 10,000 times. Point screens and zero/one-rate
bootstrap intervals are not population guarantees. These are small separable
supervised fixtures with fixed transferred settings, not a globally tuned
optimizer comparison. A general neural model may require costly reference-gradient
evaluations; this toy establishes neither that mechanism nor an agent capability.
The registered experiment is closed as learning-negative with no automatic follow-up.
