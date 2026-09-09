# Registered V3 gain follow-up

Protocol: `v3-gain-followup-20260909-v1`. New experiment authorized by the
operator after slice1 closed as tuning-inconclusive. Register before any new
tuning, calibration or confirmation. Preserve all earlier protocols, code and
archived results byte-for-byte.

## Questions and scope

1. Does one wider, joint gain/rate search bracket a useful configuration?
2. Does the frozen mean-disagreement detector distinguish target changes from
   noise, including in its own learning trajectory?
3. Only if tuning is adequate AND detection passes: does it improve independent
   prediction performance against the registered controls without regressions?

The algorithm does not change: per-coordinate fast/slow centered EMA means and
variances, rates .1/.01; q=(mean_fast-mean_slow)^2 divided by that squared
 difference plus both variances plus 1e-8; Adam step multiplier 1+gain*q, with
beta1=.9 and beta2=.999 for gated arms. Base learning remains present at q=0.
Reuse the frozen slice1 update kernel and fixture/metric functions directly.
This is a bounded follow-up, not a v2 rewrite, agent integration or novelty claim.

The exact fixture equations, observation boundary, metrics and 16 detector cells
are inherited from `DESIGN-v3-slice1.md` (registration publication
`70f0449db3ecd7288773f8dcbf8547283ff1c7f6`). This document supersedes ONLY the
budgets, seeds, search ranges, stage dependency and evidence layout listed below.
All detector/performance acceptance thresholds remain unchanged.

## One search, fixed in advance

Each of SGD, Adam, single variance, historical dual variance and mean-disagreement
candidate gets exactly 48 configurations and 16 tuning seeds. Every trial uses
the same 6,000-observation four-coordinate core fixture and the same observations
across arms for a seed. No per-coordinate or per-condition tuning.

- Gated arms: rates .00025,.001,.004,.016,.064,.256 crossed with gains
  0,1,8,32,64,128,256,1024. This retains the previous winning configurations
  while testing intermediate and larger gains with smaller rates.
- Adam: rates .00025,.0005,.001,.002,.004,.008,.016,.032,.048,.064,.128,.256
  crossed with beta2 .9,.99,.999,.9999.
- SGD: exactly `np.geomspace(.0001, 1., 48)`.

Order is ascending rate, then the listed gain/beta2. Minimum mean post-burn-in
excess MSE across all four coordinates and all 16 seeds wins; grid-order tie
break. Any non-finite seed makes its configuration ineligible. Missing data or
unexpected implementation errors stop the run for diagnosis. No silent deletion
of seeds or replacement of failed scores. Finish all 3,840 tuning trajectories
(92,160,000 coordinate updates) before selection.

Record base rate and base_rate*gain for every selected gated arm: increasing
 gain while reducing the base rate can preserve the added step amplitude.
A boundary winner is not evidence that an unbounded gain would help indefinitely.

Search flags remain: a selected rate at either endpoint for SGD/Adam/single/
candidate, or selected gain=1024 for single/candidate, makes the SEARCH
inconclusive. Historical-dual boundaries are descriptive. Adam beta2 endpoints
are disclosed but permitted. A zero-gain candidate is a tuning-only negative.
No second expansion or data-dependent search is allowed inside this experiment.

## Independent detector question despite a search limit

This is the explicit difference from the previous slice's dependency order.
If every arm has a valid selected configuration, candidate gain>0, and calibration
is finite, freeze those settings and TEST DETECTION even when the wider search
still has boundary flags. Preserve and report the search-inconclusive status.
The fixed-observer gate does not depend on optimizer rate/gain, and the
closed-loop test evaluates one specified finite policy, not a global optimum.

This does NOT waive any detector test, resolve an inadequate search, or license
performance confirmation. A detector failure stops the follow-up; a detector
pass with boundary flags closes as search-inconclusive. Performance is forbidden
unless the search has no disqualifying flags AND all detector cells pass.
This separation is registered before seeing either new tuning or detector data.

If any arm has no valid configuration, or candidate gain=0, close at tuning.
If selected calibration becomes non-finite, record all calibration rows and
close as calibration-inconclusive; do not invent a threshold or resample.
Unexpected instrument errors remain incomplete work until diagnosed.

## Seeds and calibration

Use fresh disjoint ranges, never prior-study tuning or confirmation observations:

| Purpose | Seeds |
| --- | --- |
| Development/unit fixtures | 40000–40007 |
| Calibration | 41000–41015 |
| Tuning | 42000–42015 |
| Independent detector | 43000–43031 |
| Independent performance, conditional | 44000–44031 |

Keep the original fixture's independent PCG64 domains, inclusive schedule ranges,
core coordinate order and extra noise-jump/drift/exactly-quiet fixtures. Seed
45000 is used only for 10,000-resample seed-level bootstrap summaries. Unit tests
may construct synthetic result records using study key names, but must not
sample study observations. Tests of the reused code keep their original
non-confirmation development fixtures; no new search may use those fixtures.

For each of three gated arms and both fixed/closed observer modes, calibrate ONE
threshold on 100-observation stationary-block maxima pooled equally from quiet
and noisy coordinates over 16 calibration seeds; use the 99th percentile with
`method='higher'`, and strict > for an alarm. No noise-stratum-specific test
thresholds. Record all per-seed maxima and mean gates.

Freeze the candidate's per-coordinate mean closed-loop calibration gates for
the constant-gate Adam ablation. That arm uses the selected candidate's rate,
beta2 and gain, with those fixed q values. Scalar extra fixtures use their mean.
It receives no additional hyperparameter search. A mean multiplier is not a
matched realized update norm; record actual update norms separately.

Commit the manifest (seeds, source/protocol hashes, grid scores, selected settings,
search flags, thresholds and constants) before detector observations are generated.
Reject confirmation under an uncommitted or changed manifest. No CLI bypass.

## Unchanged confirmation gates

Detector: all 16 candidate cells must pass, separately for fixed and closed-loop
modes. At least 80% detection within 100 observations in EACH noise regime and
switch direction; at most 5% of stationary 100-observation blocks contain alarms
in EACH noise regime; at most 5% of noise-increase windows and at most 5% of
noise-decrease windows contain alarms. There are 32 events per direction and
1,600 stationary blocks per regime/mode. Do not pool directional failures away.
Archive every event, latency (censored at 100), point/block counts, startup and
settled gate activity, and all controls' descriptive diagnostics. Missing cells,
wrong denominators and non-finite values cannot pass. Point screens are not
population-wide guarantees; give seed-cluster intervals and counts.

Performance, only after BOTH prerequisites pass: all six arms, 32 independent
seeds, core and all three extra fixtures. Candidate must reduce the primary
200-observation post-switch excess MSE by at least 10% versus EACH of SGD, Adam,
single and constant-gate Adam, with each paired 95% upper difference below zero.
Per-noise post-switch and all stationary/extra retention windows must satisfy
upper difference <= max(.002, .1*control MSE), exactly as the original protocol.
Retain the 44 required comparisons; adaptation latency is secondary. Retain
all pre-update scoring, drift/noise window definitions and failed trajectories.
Do not tune using detector observations or substitute them for performance seeds.

## Evidence, validation and closure

Use new `v3_gain_policy.py`, `study_v3_gain.py`, `check_v3_gain.py` and
`report_v3_gain.py`. Reuse pure simulation/metric functions from the frozen old
modules; never mutate their global seed/grid settings. Capture all transitive
runtime source files and this protocol in each envelope. Record the registration
commit and immutable protocol SHA-256; source snapshots remain authoritative
when historical branches are eventually removed.

Checkpoint tuning in FIVE per-arm files (768 rows each) under
`results/v3-gain-followup/`; this avoids rewriting all 3,840 rows after each seed.
Calibration, detector and conditional performance have respectively 48, 96 and
192 rows. Source-hashed atomic checkpoints reject changed-source resume.
Report/decision sources are fingerprinted before confirmation.

Statuses distinguish search-inconclusive, detector-negative, calibration-
inconclusive, learning-negative, positive and genuinely incomplete stages.
A boundary flag remains visible even if the detector fails too. Check complete
expected key sets and each row's manifest identity; reject forbidden later-stage
files. CI reproduces EVERY reached scientific row and recomputes selections,
calibration and all decision cells; tolerance rtol 1e-11/atol 1e-13, excluding
only elapsed time and regenerated scientific-input hashes. Preserve all existing
V1, V3 and slice1 checks and exact frozen scores. Scientific failure must not
make reproducibility CI fail.

Publish one complete follow-up PR under `codex/`, with registration committed
before runs and the selected manifest committed before confirmation. Merge only
after the exact published commit's workflows pass and reviews are resolved.
A positive result only warrants a separately registered agent experiment.
Any negative/inconclusive result closes this follow-up without another search,
retuning, enabling a default, or automatically proceeding to another v3 idea.
