# Registered V3 separate-reference experiment

Protocol `v3-reference-20260909-v1`. The operator authorized the three-setup
experiment after the persistent detector passed passive observation but failed
six learning-coupled cells. Register before new study observations. Preserve all
earlier protocols, runtime sources, evidence and workflows unchanged.

## Questions and fixed treatments

1. How do ordinary learning, gate feedback and alarm calibration affect the same
   persistent detector? Does an absent alarm coincide with recovery of prediction?
2. Can that detector, observing a fixed reference while controlling another
   learner, improve independent prediction against the specified controls?

Use the EXACT persistent candidate from `v3_persistent.py` and
`DESIGN-v3-persistent.md`: non-overlapping recent/reference windows of 16/128
causal gradients, separate unbiased variances, epsilon 1e-8, four consecutive
same-sign standardized mean differences, minimum magnitude a, q=a²/(a²+16).
No signal redesign, parameter search, retrospective threshold adjustment or
extra study-seed selection. All learners receive observations only.

Three setups, each with one fixed configuration and equal calibration budget:

- **coupled:** reuse the preceding learning-coupled candidate exactly. Its
  gradient g_t=w_t-y_t feeds its detector, and q controls its own Adam updates.
- **watch_adam:** ordinary Adam with lr=.004, beta1=.9, beta2=.999, epsilon=1e-8,
  no modulation (gain=0). The same detector watches its pre-update gradients
  g_t=w_t-y_t but cannot affect the learner. This holds the base optimizer fixed
  relative to coupled while removing the modulation, not all model movement.
- **separate** (predeclared candidate): a reference predictor r=0 remains fixed
  and supplies g_ref=-y_t to the detector. Its q_t controls a separate Adam
  learner with lr=.004, beta1=.9, beta2=.999, epsilon=1e-8, gain=64. The learner
  uses its own gradient w_t-y_t and step lr*(1+64*q_t)*Adam_direction. Its updates
  cannot change reference gradients or detector state.

Coupled uses the same lr=.004/gain=64 and Adam constants. These settings are
transferred, not retuned or claimed optimal for the new policy. Fixed-observer
mode sets prediction=0 and disables learning in every setup; all three then
produce exactly the inherited passive signal. Active mode implements the three
setups above. The separate detector is identical in fixed and active modes BY
CONSTRUCTION; passing both is an integrity/fixture check, not independent
replication or a new detector discovery. The real advancement question is
independent learning performance.

A causal two-pass implementation is allowed: produce a full sequence of
pre-update ordinary-Adam gradients or fixed-reference gates, then run the
associated detector or controlled learner. Prefix-invariance tests must prove
that output at t cannot depend on later observations; no reverse-time pass,
future summary or evaluator metadata may enter the learner. This is a simple
separable supervised toy; evaluating reference gradients for a general neural
model could add substantial cost and is not implemented or justified here.

## Fixtures and seed partitions

Reuse every fixture and metric without changes from the persistent experiment:
6,000 observations, burn-in 1,000, core quiet/noisy stationary and switching
coordinates, noise_jump, drift, exactly_quiet, and both mixed coordinates with
simultaneous target/noise changes. Keep existing independent PCG64 domains and
seed-jittered event times. Targets, event indices and noise levels are evaluator
metadata. No model may inspect them.

| Partition | Seeds |
| --- | --- |
| Development only | 60000–60007 |
| Calibration | 61000–61015 |
| Detector and explanatory diagnostics | 63000–63031 |
| Conditional independent performance | 64000–64031 |
| Whole-seed bootstrap only | 65000 |

All ranges are fresh, including relative to previously reserved but unused
partitions. There is no tuning partition. Synthetic unit-test records may use
partition key names but may not sample their observations. Reused kernel tests
keep their original development fixtures.

## Calibration and freeze

For each of three setups and both modes, calibrate one threshold from stationary
quiet/noisy 100-observation block maxima on 16 core calibration seeds (50 blocks
per coordinate/seed), pooled equally. Use quantile .99, method='higher', strict >
for alarms. No per-condition thresholds. This is 48 calibration rows; each
contains both modes, maxima and all four core mean gates.

Freeze separate's four mean active calibration gates for the constant-gate
control. For every non-core fixture use their mean on all its coordinates.
Record all sources, configurations, partitions and calibrated values in a
committed manifest BEFORE diagnostic observations. Source-hash the report and
decision code before calibration. Require committed unchanged runtime sources
and manifest for confirmation. Any non-finite calibration closes as
calibration_inconclusive after all 48 rows; missing rows or unexpected errors
remain incomplete and must be diagnosed. No imputation or seed dropping.

## Diagnostic stage: detection and explanatory prediction records

Generate all 96 rows (3 setups × 32 seeds), each covering all five fixtures and
both modes. Candidate separate must pass ALL the inherited 24 detector cells:
for each mode, <=5% stationary block alarms separately quiet/noisy (1,600 blocks
each), >=80% detection within 100 observations for each quiet/noisy target
down/up, <=5% alarms separately on noise increase/decrease, and >=80% detection
for every mixed coordinate/direction (32 events each). No pooling. Record the
same cells for both controls, without changing which setup is the candidate.
Non-finite candidate trajectories, missing cells or invalid denominators cannot
pass. Other setup failures remain visible and cannot be silently excluded.

Unlike earlier registrations, this stage ALSO records explanatory prediction
metrics for every trajectory, irrespective of detector pass/fail. This change
is registered before data to resolve ambiguity about missing alarms; these
records cannot select settings, alter thresholds, replace the independent
performance partition or establish learning superiority.

For each fixture/mode/setup archive:

- original detector metrics and every event's hit, latency censored at 100,
  point/block counts and startup/settled q;
- inherited pre-update learning metrics, post-200 target-switch MSE, stationary
  and extra retention windows, update norms and recovery metrics;
- for each target event, q maximum in [event,event+100), signed prediction error
  at the event, MSE in the preceding 100 observations and following 20/100/200,
  recovery latency (ten consecutive absolute prediction errors <.2, searched
  for 1,000 observations, censored at 1,000), and recovered_within_100;
- the same alarm metrics using separate's FIXED calibrated threshold on every
  setup's unchanged gate sequence, as a predeclared common-threshold diagnostic.

Report per-condition counts of missed alarms, recovery within 100, and their
intersection, including the conditional recovered/missed fraction only when its
denominator is nonzero. Report mean post-100/post-200 MSE and q maximum, and
seed-level uncertainty. Report every common-threshold cell, including stationary
false alarms: a lower threshold cannot appear to repair detection while its
false positives are hidden. Common-threshold results NEVER decide advancement.
The native calibrated decision remains authoritative.

Comparing watch_adam with coupled diagnoses consequences of removing modulation;
it changes the learner trajectory and does not isolate every intermediate cause.
The common-threshold diagnostic isolates alarm-threshold choice on a fixed
recorded gate trajectory. Neither alone proves a general causal mechanism.
Separate's identical fixed/active gate sequence must be checked exactly.

If separate fails any native detector cell, close detector_negative, keep all
explanatory metrics and do not open independent performance. A pass opens only
the conditional stage below. Do not promote a control or reopen old experiments.

## Conditional independent performance

Run seven fixed policies on all 32 independent performance seeds and five
fixtures (224 rows): separate, coupled, watch_adam, tuned Adam, SGD, single
variance and constant-gate Adam. Tuned Adam uses lr=.032,beta2=.9999;
SGD lr=.035743040182210514; single variance lr=.016,gain=1,beta2=.999. These are
transferred comparator settings from the previous equal-budget search. Constant
uses separate's lr=.004,gain=64,beta2=.999 with frozen calibration mean q.
All policies have one setting; none receives additional tuning in this experiment.
A matched mean q is NOT a matched realized update norm; report actual norms.

Separate must improve the seed-level mean post-200 MSE, averaged equally across
the two core switching and two mixed coordinates, by at least 10% versus EACH
of the six controls; every paired 95% upper difference must be <0. Retention
requires paired upper delta <=max(.002,.1*control mean) for each of the four
core coordinates (post-MSE for switching, post-burn-in excess MSE for stationary),
three scalar extras, noise-increase/decrease and drift windows, and post-MSE /
stable-MSE separately for both mixed coordinates. Fifteen comparisons per control,
90 total; all must pass for positive. Otherwise learning_negative. No comparator
can be omitted based on its diagnostic behavior. Required non-finite trajectories
fail the stage; never replace them with finite scores.

Report absolute errors and update norms by policy/condition alongside all paired
contrasts. Detector and explanatory diagnostic data cannot tune this stage.
Settings are fixed finite policies, not a globally tuned optimizer ranking.
A positive result warrants only a separately registered agent experiment; any
negative/inconclusive outcome closes this experiment with no automatic expansion,
new detector, changed default or agent integration.

## Evidence, refinement and completion

Create new `v3_reference.py`, `v3_reference_policy.py`, `study_v3_reference.py`,
`report_v3_reference.py`, `check_v3_reference.py`, protocol/results documents and
a separate CI workflow. Reuse frozen functions directly; never mutate existing
module globals to substitute seeds/configurations. Store atomic per-seed evidence
under `results/v3-reference/`, with source snapshots of all transitive runtime
files, applicable protocols, report/decision files and pinned requirements.
Registration hash is immutable. Commit implementation before observations and
manifest before diagnostics; record these commit identities in the final report.

Phases: register; implement/refine/test; calibrate/freeze; diagnose; independently
confirm performance only if allowed; reproduce all reached evidence, report,
publish draft codex/** PR, monitor exact HEAD workflows, mark ready and merge
when green with all review conversations resolved. Preserve all five prior CI
workflows and their frozen study outcomes. No source change after observations
except a diagnosed and explicitly reported instrument defect; no retrospective
hypothesis change or weakened tests to obtain a pass.

Refinement/verification: exact coupled parity; watch_adam predictions/norms equal
unmodulated Adam; separate fixed/active q identity and independence from learner
rate/gain; independent scalar Adam recurrence for external q; zero-gain parity;
full observation prefix causality and coordinate isolation; unchanged fixture
semantics; explanatory event/recovery and conditional denominator checks; all 24
native/common-threshold cells; all 90 performance contrasts; exact row cohorts;
invalid/non-finite rejection; committed source/manifest and forbidden-stage gates.
Unit tests use development data only. CI regenerates EVERY reached scientific
row, thresholds, constants and decision at rtol 1e-11/atol 1e-13, excluding only
timing and regenerated scientific-input hashes. Recompute all report summaries.
Use 10,000 whole-seed bootstrap resamples with seed 65000. Point screens and
32-seed samples are not population guarantees; zero-event bootstrap intervals
cannot quantify unseen rare events. A negative scientific finding reproduces green.
