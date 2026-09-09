# V3 first experiment: registered protocol

Registered before study execution on 2026-09-09. Scope: V3 §9's standalone
supervised optimizer test. No brainsim default, task API, or v2 change.

## Predictions and decision

The two-timescale gate should detect abrupt target changes, keep stationary
false alarms rare, and improve adaptation compared with equally tuned Adam,
constant-rate SGD, and a single-timescale gate. Stable noise is expected to
produce a positive mean rectified gate, not zero. A noise-level increase may
also trigger the gate; this is an explicit specificity challenge, not evidence
of a changed optimum. Smooth drift checks response to ordinary mean movement.

Advancement requires BOTH:

1. Fixed-observer detection: at least 80% of target switches detected within
   100 observations in EACH noise regime; at most 5% of stationary 100-step
   blocks contain an alarm in EACH noise regime, on confirmation seeds.
2. Learning: at least 10% lower post-switch excess MSE than EACH of Adam, SGD,
   and the single-timescale arm, with paired bootstrap 95% intervals for the
   treatment-minus-control difference entirely below zero. On EACH stationary
   condition, the upper interval endpoint against EACH comparator must be no
   larger than max(0.002, 10% of that comparator's MSE).

All are conjunctions, with no best-condition selection. Failure stops integration
of this specified hypothesis. Passing licenses a noisy-volatile task experiment,
not a shipped optimizer or claims about brainsim/general optimization. Even a
pass cannot establish epistemic/aleatoric separation if noise increases trigger
alarms. Do not silently retune after confirmation. Report nulls and all arms.

## Streams and observation boundary

Each independent stream has 6,000 observations, scalar prediction w (initially
zero), target theta initially +1, and y = theta + sigma*z, z standard normal.
Online objective is (w-y)^2/2; gradient g=w-y. Score predictions BEFORE updates.
Updates receive y only, never theta, switch times, noise level, or task labels.
Four learning conditions: stationary/alternating target crossed with sigma
0.05/1.0. Alternating theta changes sign at indices 2,000 and 4,000.
The first 1,000 samples are a burn-in; no learner resets at switches.

Separately, a fixed observer w=0 receives the same g=-y streams, so its detector
is not confounded by optimizer motion. Two further diagnostic conditions are
smooth drift (theta moves linearly +1 to -1 during [2000,4000), sigma .05) and
noise jump (theta stays +1; sigma .05, then 1 during [2000,4000), then .05).
Fixed-observer results cannot establish closed-loop optimizer detection.
The stationary learning streams start away from their optimum and thus also
expose gate transients caused by learning itself; report initial gate activity
separately from activity after burn-in.

## Exact statistics and updates

Adam follows Kingma and Ba Algorithm 1: m=.9*m+.1*g,
v=beta2*v+(1-beta2)*g*g, zero initialized, both bias corrected at step t (1-based),
and w -= lr*m_hat/(sqrt(v_hat)+1e-8). v is a RAW SECOND MOMENT, not variance.

Additional centered, exponentially weighted population variance estimates use
rates a_fast=.1 and a_slow=.01. Initialize mean to the first g and variance to
zero; on later g use d=g-mean, mean += a*d,
s=(1-a)*(s+a*d*d). This is the stable recurrence for weighted centered variance,
not an unbiased estimate of a stationary population variance. No bias correction.

Dual gate q=max(0,s_fast-s_slow)/(s_fast+s_slow+1e-8).
Single gate q=s_fast/(s_fast+1). The constant 1 is the declared unit-scale
reference; this control is intentionally not scale invariant. Both multiply
Adam's update by 1+gain*q, leaving learning possible at q=0, with beta2=.999.
There is no threshold or known-switch input in either optimizer. Fixed SGD is
w -= lr*g. All arms consume exactly one gradient and one update per sample.
Report per-arm elapsed time and persistent scalar state; extra gate arithmetic
is a cost, not equal wall-clock compute. No arm gets extra samples or updates.

## Tuning, calibration, and independent confirmation

Disjoint seeds: calibration 0..7, tuning 1000..1007, confirmation 2000..2031.
Generate common noise per seed and use it across every condition and arm.
Each arm gets exactly 12 configurations, 8 tuning seeds, 4 conditions, and
6,000 samples per condition. Select the lowest average excess MSE over all four
conditions after burn-in; deterministic grid-order tie break. No per-task tuning.

- SGD rates: .001,.002,.004,.008,.016,.032,.064,.128,.256,.512,.768,1.
- Adam: rates .004,.016,.064,.256 crossed with beta2 .9,.99,.999.
- Single and dual: rates .004,.016,.064,.256 crossed with gain 1,4,16.

The gate timescales are fixed, not searched. Baselines use their 12 trials for
rate/moment tuning; gated arms spend trials on rate/gain tuning. This matches
trial and sample budgets, not an exhaustive or universally fair search. An edge
winner must be disclosed as a search-range limitation; do not extend its range
using confirmation results.

For each gate and each stationary noise regime, calibrate an alarm threshold as
the 99th percentile (`method='higher'`) of maxima in non-overlapping 100-sample
blocks after burn-in, pooled across calibration seeds (400 blocks). Alarms are
strictly above threshold. Freeze calibration and selected configurations to a
JSON file and commit it BEFORE any confirmation runs. Noise-specific thresholds
are a diagnostic instrument with known noise strata, not a deployable detector.
Use the noisy threshold for the extra noise-jump diagnostic; use the quiet
threshold for smooth drift. Blocks are correlated; seed is the inference unit.

## Measurements and evidence

For each arm/seed/condition record excess MSE (w-theta)^2 and observed prediction
MSE (w-y)^2 after burn-in; post-switch excess MSE over the first 200 predictions
following each true switch; stationary-region MSE excluding those windows;
adaptation latency as first start of 10 consecutive predictions within .2 of
new theta, censored at 1,000 samples if absent, plus success fraction. Report
mean gate before and after burn-in and elapsed time. Both true switch windows
are included, regardless of detection or adaptation success.

Fixed-observer diagnostics record mean gate, point alarm rate, stationary block
alarm rate, true-switch detection fraction and censored first-alarm latency
(100 if absent); also the descriptive response at drift/noise-change boundaries.
Do not label drift/noise-change alarms successful target-switch detections.

Compare paired seed averages, averaging the two switch/noise regimes per seed
for the primary learning endpoint. Use 10,000 paired-seed bootstrap resamples,
fixed RNG seed 20260909, percentile 95% intervals. Report each condition too.
Confidence intervals do not account for the full optimizer-design search or
justify generalization beyond these synthetic streams.

Checkpoint completed rows atomically, archive source hashes and exact sources,
and retain the registration, frozen selection, tuning, calibration, and complete
confirmation evidence. Tests check hand-computable Adam/variance updates, causal
prediction order, zero-gain equivalence, no future/target leakage, disjoint seeds,
block/detection/censoring semantics, selected grid minima and archived evidence.
CI reproduces the bounded v3 study in addition to existing v1 gates.

## Interpretation and related work

This experiment tests one centered-variance implementation of V3's underspecified
s_fast/s_slow, not all second-moment variants or possible timescales.
The Kalman analogy remains unproven. Adam estimates first and raw second moments
([Kingma and Ba](https://arxiv.org/abs/1412.6980)); using a gradient-prediction
residual in adaptive optimization already has precedent
([AdaBelief, Zhuang et al.](https://arxiv.org/abs/2010.07468)). These sources do not
establish novelty of this particular gate or an advantage over modern optimizers.
No such novelty or general advantage claim is made; this is a bounded falsifier.
