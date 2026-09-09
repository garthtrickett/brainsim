# Registered V3 persistent mean-change experiment

Protocol `v3-persistent-20260909-v1`. Register before any study observations.
The operator authorized the next bounded detector experiment after the gain
follow-up failed noise-increase controls. Preserve all earlier registered
protocols, runtime sources and evidence unchanged.

## Hypothesis and fixed designs

A mean comparison with separate estimates of recent and reference noise, followed
by directional persistence, may distinguish changed targets from changed noise.
This is a hypothesis, not an established property or a novelty claim. The earlier
confirmation outcomes motivate it; they are not reused for tuning or selection.

Four detector arms each have ONE configuration. No grid search, best-seed
selection, threshold rescue or automatic follow-up expansion is permitted.
The learner receives observations only. Its gradient is g_t=w_t-y_t; predictions
are scored before that observation updates the learner. Fixed observer means
w=0 forever. Closed-loop means the gate drives its own Adam trajectory.
All four use Adam beta1=.9, beta2=.999, epsilon=1e-8, lr=.004, gain=64:
update = lr*(1+64*q_t)*bias_corrected_Adam_direction. These rate/gain values are
transferred from the completed search; they are not claimed optimal for new gates.

1. **current:** the unchanged mean-disagreement gate from slice1: centered
   fast/slow EMA mean/variance at .1/.01, initialized first g/zero variance;
   q=d²/(d²+s_fast+s_slow+1e-8), d=mean_fast-mean_slow.
2. **persistence:** compute current's signed score sign(d)*sqrt(q). If the last
   FOUR signed scores have one strict common sign, let a be their minimum
   absolute magnitude; otherwise a=0. Output q=a². Startup before four scores
   outputs zero. This isolates persistence without a new noise statistic.
3. **candidate:** at t>=143, compare the most recent 16 gradients (including t)
   with the immediately preceding, non-overlapping 128 gradients. Use sample
   means m_r,m_b and unbiased sample variances v_r,v_b separately. Compute
   z=(m_r-m_b)/sqrt(v_r/16+v_b/128+1e-8). Apply the same four-score directional
   minimum to z, giving a; output q=a²/(a²+16). Before sufficient history the
   signed score and q are zero. This is a Welch-style standardized mean
   difference with a persistence filter. Overlapping time windows are correlated:
   z is NOT interpreted as a p-value, and four scores are NOT four independent
   observations. The q mapping is fixed before data and retains a base Adam step.
4. **cusum:** use the same 16/128 windows, then standardized innovation
   u=(g_t-m_b)/sqrt(max(v_r,v_b)+1e-8). From zero states accumulate
   C_plus=max(0,C_plus+u-.5), C_minus=max(0,C_minus-u-.5).
   With C=max(C_plus,C_minus), q=C/(C+16). Before t=143 output zero and leave
   states zero. No alarm-triggered reset: the recurrence's return to zero is the
   only reset, so threshold calibration cannot alter the trajectory.

CUSUM is the established sequential-test reference, with our explicit moving
reference and scale adaptation. The recurrence follows the tabular two-sided
CUSUM in the [NIST handbook](https://www.itl.nist.gov/div898/handbook/pmc/section3/pmc323.htm)
and [Page (1954)](https://doi.org/10.1093/biomet/41.1-2.100).
The moving estimates and empirical calibration here do not inherit textbook
known-parameter false-alarm guarantees. The earlier suggested
[likelihood-ratio paper](https://arxiv.org/abs/1802.07696) is background, not an
implementation we claim to reproduce. CUSUM provides a simpler auditable control.

Windows consume only past/current gradients and never known noise levels,
targets, event indices, fixture names or future observations. Compute window
variances by centered sums; non-finite arithmetic is a recorded failed trajectory,
not clipped or replaced evidence. No new dependencies.

## Fixtures and partitions

Reuse slice1's 6,000-observation core, noise_jump, drift and exactly_quiet
fixtures, BURN=1000, 100-observation alarm windows, pre-update learning metrics,
independent PCG64 noise domains and seed-jittered switch times in [1800,2200]
and [3800,4200]. Preserve the exact inherited definitions in
`DESIGN-v3-slice1.md` and `v3_slice1_streams.py`.

Add `mixed`, two coordinates with target +1, then -1 between the same switch
times, then +1. Coordinate `increase_first` has sigma .05, then 1, then .05;
coordinate `decrease_first` has sigma 1, then .05, then 1. Use new independent
noise domains 21 and 22. Both directions are therefore tested during noise
increases and decreases, with no event metadata available to the learner.
Evaluate each of the four coordinate/direction combinations separately.

| Purpose | Seeds |
| --- | --- |
| Development fixtures only | 50000–50007 |
| Calibration | 51000–51015 |
| Independent detector confirmation | 53000–53031 |
| Conditional independent performance | 54000–54031 |
| Whole-seed bootstrap only | 55000 |

No tuning partition exists. Unit tests may use synthetic records with these key
names but cannot sample calibration/confirmation observations. Reused unit tests
retain their original development fixtures. All new observation seeds are disjoint
from every previous study, including its unused partitions.

## Calibration and immutable manifest

For every arm and each mode, pool stationary quiet/noisy 100-step block maxima
from the core across 16 calibration seeds, 50 blocks per coordinate per seed.
One threshold per arm/mode is the 99th percentile with method='higher'. Alarms
use strict >. No fixture-specific or noise-specific thresholds. Calibration has
64 rows (one arm/seed row contains both modes). Record maxima and mean gates.
Freeze per-coordinate mean closed-loop candidate gates for constant-gate Adam.
For every non-core fixture, fill its coordinates with the average core constant.

Commit the complete source-hashed manifest, thresholds, constants, fixed
configurations and seed lists BEFORE any detector confirmation observations.
Fingerprint report and decision code before calibration. Confirmation rejects
changed/uncommitted sources or manifest. Non-finite calibration closes as
calibration_inconclusive after all 64 rows; missing data/errors remain incomplete.

## Detector decision and controls

Run every arm on every fixture in both modes for all 32 fresh detector seeds:
128 complete rows. Archive raw per-event hits and latencies (censored at 100),
point/block counts, startup/settled gate means and all arms' conditions.

The candidate must pass ALL 24 cells. The original sixteen are unchanged:
for each mode, <=5% stationary alarm blocks separately quiet/noisy (1,600 each),
>=80% detection within 100 observations for each quiet/noisy target down/up
(32 each), and <=5% alarms for each noise increase/decrease (32 each).
The additional eight require >=80% detection separately for every mixed
coordinate/direction and mode (32 each). Do not pool failures across directions,
noise regimes or modes. Exactly quiet and drift remain descriptive conditions.

Report the same 24 cells for each control without promoting a control to the
candidate after seeing data. Give counts and 95% intervals from 10,000 whole-seed
bootstrap resamples (seed 55000), plus censored mean latencies and their intervals.
These point screens are not population-wide guarantees or independent-event
intervals. Passing does not establish superiority to controls.

A candidate failure closes as detector_negative; performance remains forbidden.
A pass opens the predeclared performance stage below. No changes after observing
confirmation, and no further detector design is automatically activated.

## Conditional performance

Only if all 24 candidate cells pass: run eight fixed policies on 32 independent
performance seeds, all five fixtures (256 rows): current, persistence, candidate,
cusum, SGD, Adam, single variance, constant-gate Adam. No hyperparameter search
for any arm in this experiment. SGD lr=.035743040182210514; Adam lr=.032,
beta2=.9999; single variance lr=.016,gain=1. These are strong transferred
comparators from the previous equal-budget search. Constant uses candidate Adam
settings and frozen mean q. Report actual update norms, not a claim of matched
realized step sizes. Detector thresholds classify alarms but do not change q.

The candidate must improve mean 200-step post-switch MSE averaged equally over
the two core switching coordinates AND two mixed coordinates by >=10% versus
EACH of the seven controls, with paired 95% upper delta <0. Retention requires
upper paired delta <=max(.002,.1*control mean) for each core coordinate (post-MSE
for switching, post-burn-in MSE for stationary), three scalar extra fixtures,
noise-increase/decrease windows, drift window, and post-MSE/stable-MSE separately
for each mixed coordinate. That is 15 comparisons/control, 105 required cells.
All must pass for positive; otherwise learning_negative. Resource cost and
adaptation latency are descriptive, no result-based selection or acceptance rule.

Fixed transferred settings limit the conclusion to these policies, not an
optimizer-wide ranking or globally optimal tuning. A positive result warrants
only a separately registered agent experiment; no agent integration/default change
is part of this work. Any negative/inconclusive disposition closes this experiment.

## Implementation, refinement and validation

Implement new `v3_persistent.py` (observations-only kernel and mixed fixture),
`v3_persistent_policy.py`, `study_v3_persistent.py`, `report_v3_persistent.py`,
`check_v3_persistent.py`, and a separate CI workflow. Reuse frozen Adam/variance
steps, fixture/metric helpers and source-hashed atomic evidence. Preserve old
runtime files and workflows byte-for-byte. Store evidence under
`results/v3-persistent/`, one file per reached stage, snapshots of every runtime
source, both applicable protocols and requirements. Registration hash is
immutable; record registration, implementation and manifest commit identities.

Phases: (1) register; (2) implement and validate equations/causality/decisions;
(3) calibrate and commit manifest; (4) confirm detection; (5) performance only if
allowed; (6) reproduce every reached row, report, publish draft PR, monitor exact
HEAD workflows, mark ready and merge when all green/review threads resolved.
No source changes after observations except diagnosed instrument defects, which
must be reported explicitly rather than retroactively changing the hypothesis.

Pre-data refinement checks: directional minimum is a real persistence ablation;
separate variances avoid assuming equal noise across windows; mixed fixtures
prevent a blanket noise veto; controls cannot inspect targets; all false alarms
and missed switches remain visible; closed-loop testing includes feedback from
new q scales; calibration never selects a winner; conditional performance checks
all fixed controls and retention conditions.

Tests: independently calculated window/EMA/CUSUM equations; four-score sign
logic; startup; observation causality and coordinate isolation; original-gate
parity; exact event/noise generation; threshold boundaries; all 24/105 decision
cells and missing/invalid/non-finite rejection; manifest/source and forbidden-stage
enforcement. Reproduction regenerates EVERY reached row and recomputes manifest,
thresholds and decisions at rtol 1e-11/atol 1e-13, excluding only timing and
regenerated scientific-input hashes. Scientific negatives must reproduce green.
Preserve all four existing CI workflows and run relevant old checks locally.
