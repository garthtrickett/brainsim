# Registered protocol: V3 slice 1 mean-disagreement successor

Protocol ID: `v3-slice1-mean-20260909-v1`. Registered before successor calibration,
tuning, or confirmation. The operator activated the refined plan on 2026-09-09.
The accepted plan is commit `b05a41d6a898a2f87a9161d5f45aa94eb85c619d`.
The registration publication commit will be recorded in the instrument and every
evidence envelope after Phase 0 merges, so no self-referential commit hash is
needed in this document. This protocol is immutable once published.

## Outcome and boundary

Answer one question: **can a causal signal of a changed mean gradient improve
adaptation without chasing observation noise, beyond a simpler learning rule?**

The first centered-variance candidate is closed: 43.9% lower post-switch error
than Adam, but 7.5% worse than its single-timescale control, 25% noisy-switch
detection, and worse stationary-noise retention. Keep that result intact; see
[V3-RESULTS.md](V3-RESULTS.md) and [the registration](DESIGN-v3-gate.md).

The proposed successor measures normalized disagreement between two running MEANS.
It is a new hypothesis motivated by the result, not a renamed successful version
of the variance experiment. No empirical benefit is assumed.

This slice ends with a reproducible standalone result and an integration decision.
It does not implement a brainsim gate, replace ADAPTIVE, change
replay/exploration, start v2, or build V3 §§10–11. A positive result is only a
prerequisite for a separately registered noisy-volatile agent experiment.

## Phases at a glance

| Phase | Deliverable | Exit gate | On failure |
| --- | --- | --- | --- |
| 0. Establish the baseline | Failure diagnosis and frozen successor protocol | Exact hypothesis, budgets and criteria committed | Resolve specification defects before experiments |
| 1. Build the instrument | Causal streams, metrics and seed manifest | Hand-checkable measurement tests pass | Fix the instrument, preserve failed checks |
| 2. Implement one successor | Mean-disagreement gate and controls | Update, causality and equivalence checks pass | Fix implementation; no formula search |
| 3. Calibrate and tune | One frozen configuration per arm and global alarm thresholds | Complete equal budgets; no unresolved search-boundary ambiguity | Close as inconclusive if tuning is inadequate |
| 4. Confirm detection | Fresh fixed-observer and closed-loop diagnostic evidence | Noise, change and false-alarm criteria all pass | Stop before performance confirmation |
| 5. Confirm learning | Independent paired performance evidence | Improvement, retention and attribution criteria all pass | Stop before agent integration |
| 6. Close and publish | Report, source archive, CI reproduction and disposition | Evidence complete; published checks green | Fix reproduction defects, not acceptance thresholds |

Each phase depends on the previous one. Evidence of failure advances to Phase 6,
not to the next capability phase. Phase completion is tracked outside this immutable registration.

## Phase 0 — preserve the result and register the successor

1. Verify the existing archived experiment and generated report using
   `python check_v3_gate.py --evidence results/v3 --reproduce` and
   `python report_v3_gate.py --check`. Do not edit
   `v3_gate.py`, `study_v3_gate.py`, `DESIGN-v3-gate.md`, or `results/v3/` to make
   the successor fit. Those files are the original experiment's reproduction.
2. Write `DESIGN-v3-slice1.md` with the equations, update order, seed manifest,
   stream definitions, exact grids, scoring windows and decision code below.
3. Explain the failure mechanism as a hypothesis, distinguishing observation
   from inference: variance excess responded to noise increases and missed noisy
   mean switches; this does not prove why every learning trajectory improved.
4. Commit the protocol before calibration or tuning. Record its commit and source
   hash in every new evidence file. Use a dedicated `codex/v3-slice1-*` worktree.

**Analytical check before implementation:** a raw-second-moment substitution is
not the proposed repair. For a fixed observer, symmetric targets +1 and -1 with
symmetric zero-mean noise have the same squared observation distribution. Squaring
discards that sign information. This simple counterexample belongs in the
instrument tests; no benchmark run is needed to establish it. It does not say
gradients in a moving optimizer never change magnitude.

Exit: no unspecified candidate formula, tuning budget or acceptance criterion. Any
change after confirmation begins creates a new experiment, never an amended pass
for this one. Literature/novelty claims are outside the acceptance criteria.

## Phase 1 — build a task whose labels cannot leak

Add `v3_slice1_streams.py` and instrument checks in `check_v3_slice1.py`. Expose
observations to learners and keep targets, noise labels and event times in an
evaluator-owned record. The learning interface accepts observations only.

Core learning fixture: 6,000 observations of a four-dimensional separable
quadratic, loss `sum((w-y)^2)/2`, with one shared optimizer configuration and
per-coordinate state. Coordinates combine stationary quiet, stationary noisy,
switching quiet and switching noisy targets in the SAME run. Noise standard
deviations are .05 and 1; initial target is +1 and initial prediction is zero.
Switching targets change sign twice. Draw event indices from inclusive ranges
[1800,2200] and [3800,4200] using an independent schedule RNG. No event or known
noise level enters the optimizer; no reset occurs at an event.

Use independent coordinate noise streams, but identical underlying observations
across competing arms for each seed. Separate schedule and observation RNGs, so
adding a metric or changing a learner's random draws cannot alter the environment.
Score the prediction before consuming the current observation. Burn-in is 1,000
samples. This fixture tests coexistence with shared tuning; its separable
coordinates do not test representation interference or brainsim learning.

Additional diagnostic/retention streams, all 6,000 observations:

- Noise-only change: constant target, sigma .05 → 1 → .05 at the two event times.
  Score the increase and decrease separately; do not average away a bad direction.
- Smooth mean drift: theta moves +1 → -1 between the two event times, sigma .05.
  Score prediction quality; do not treat drift as an abrupt-switch detection.
- Exactly quiet: constant target, sigma 0, to expose epsilon and startup behavior.

For each diagnostic use a fixed observer `w=0` and an actual learning trajectory.
The latter tests whether the detector mistakes its own optimizer's progress for an
external change. Log startup separately; normal detector scoring begins after
burn-in. The known-initialization transient is not a hidden target switch.

Exit tests: event boundaries and pre-update scoring; noise-up/down labels;
independent RNG streams; shared samples across arms; constant-target invariants;
future-suffix changes cannot affect earlier predictions; evaluator metadata is
absent from update arguments. Unit-test fixtures never use confirmation seeds.

## Phase 2 — implement one exact successor and preserve simple controls

Add `v3_slice1_learning.py`; reuse only stable helpers whose source hashes are
recorded. Avoid a framework refactor of the original experiment.

For each coordinate, compute gradient `g = w - y`. Initialize each running mean to
the first gradient and each centered variance to zero. Thereafter update both
pairs using the existing centered EMA recurrence, with rates .1 and .01:

```text
d = g - mean
mean = mean + a*d
variance = (1-a)*(variance + a*d*d)

D = (mean_fast - mean_slow)^2
N = variance_fast + variance_slow
q = D / (D + N + 1e-8)
```

Compute q after observing the current gradient, then apply it to the same update.
This is a bounded heuristic statistic, not a calibrated probability, unbiased
variance estimator, or derived Kalman gain. Stable noise can still give positive
q; whether normalization handles a noise increase is an empirical question.

Use bias-corrected Adam with beta1=.9, beta2=.999 and denominator epsilon 1e-8;
scale its step by `lr * (1 + gain*q)`. Base learning remains possible at q=0. No
hard alarm threshold enters this optimizer; alarms evaluate its signal.

Control gate formulas retain the old rates .1/.01: single uses
`q = variance_fast / (variance_fast + 1)`; historical dual uses
`q = max(0, variance_fast - variance_slow) /
(variance_fast + variance_slow + 1e-8)`. Both use the same base Adam update and
gain convention as the candidate.

Primary arms: constant-rate SGD, Adam, the existing single-variance modulation,
and the new mean-disagreement modulation. Rerun the old centered-variance dual arm
as a historical comparator, with the same tuning budget, but do not require
beating it as a substitute for beating the stronger single control.

Tests: independent hand-calculated Adam steps and weighted-variance identities;
zero-gain equality to Adam; equal means give q=0; q stays in [0,1]; sign reversal
of an entire input sequence preserves q; constant offsets to a fixed gradient
sequence preserve the mean-disagreement statistic; finite behavior at zero noise;
no shared state between coordinates or arms. Do not add clipping to conceal
instability: non-finite trajectories fail that configuration and stay in evidence.

Exit: one implemented candidate matches the registered formula. A failing test
permits an implementation correction, not choosing a different statistic.

## Phase 3 — bounded tuning and calibration, then freeze

Add `study_v3_slice1.py` with explicit `prepare`, `diagnostics`, `performance` and
`report` stages. Before confirmation, the command must check that the manifest is
committed and that the protocol and learning/stream source hashes match.
`performance` also requires a complete passing diagnostic decision with matching
hashes; a command-line flag must not bypass that prerequisite. Store outputs under
`results/v3-slice1/`, never `results/v3/`.

Reserve new seed ranges, checked against prior evidence before running:

| Use | Seeds | May influence selection? |
| --- | --- | --- |
| Development/instrument smoke tests | 30000–30007 | Code correctness only; no grid search |
| Calibration | 31000–31015 | Alarm thresholds and derived constant-gate ablation only |
| Tuning | 32000–32015 | Optimizer configuration only |
| Detector confirmation | 33000–33031 | No |
| Performance confirmation | 34000–34031 | No |

Use 24 configurations per primary/historical arm, 16 tuning seeds, and the same
core fixture for every trial. Rate set for Adam and gated arms:
`.001,.004,.016,.064,.256,1`. Adam crosses those rates with beta2
`.9,.99,.999,.9999`; each gated arm crosses them with gain `0,1,8,64` and keeps
beta2=.999. SGD gets 24 geometrically spaced rates from .0001 through 1 inclusive.
This is 1,920 tuning trajectories (46,080,000 coordinate updates) across the
five tuned arms. Calibration and each confirmation partition are bounded by the
seed tables; no extra exploratory sweep is part of this slice. Fixed gate
timescales are not tuned. A zero-gain winner means the modulation has
not earned use. This is a deliberately bounded search, not optimal tuning.

Select each arm by minimum mean post-burn-in excess MSE over all four core
coordinates and all tuning seeds, with grid-order tie breaking. Select before
looking at confirmation. Record every failed/non-finite configuration as such;
never silently drop seeds or substitute a finite score. A configuration with any
failed seed is ineligible for selection; rank only configurations with all 16
complete finite seed results. If an arm has no eligible configuration, close as
inconclusive. Unexpected runtime/instrument errors stop the phase for diagnosis
rather than being counted as optimizer divergence. Calibration comes after this
selection when it needs closed-loop trajectories.

No adaptive grid extension inside this slice. If a selected learning rate is at
either edge, or a selected nonzero gated gain is 64, close as tuning-inconclusive
before confirmation. A zero-gain candidate closes as no modulation benefit. Adam
beta2 endpoints are declared finite choices and must be disclosed, but do not
independently block confirmation. The boundary rules apply to the candidate and
required primary comparators (SGD, Adam, single). Historical-dual boundary winners
are disclosed but do not block a decision, because that arm is not an advancement
comparator. A zero-gain single-control winner is valid. Candidate screening at
this phase is explicitly labelled tuning-only; it is not an independently
confirmed negative.

For each selected gated arm and observer mode (fixed or closed-loop), derive ONE
threshold from calibration maxima over non-overlapping 100-sample blocks after
burn-in, pooled equally from stationary quiet and stationary noisy coordinates.
Use the 99th percentile, `method='higher'`, and alarm only strictly above it. No
threshold is chosen using the test condition's noise label. The two observer modes
have separate thresholds because their signal distributions differ.

Add one derived ablation, **constant-gate Adam**, to distinguish varying
modulation from a higher average rate. Replay the selected candidate on the 16
calibration seeds' CORE fixtures; average q after burn-in separately for each
coordinate. Freeze those four constants. The ablation uses the candidate's
selected Adam settings and gain, replacing current q with that coordinate's frozen
mean. For scalar extra streams use the mean of the four constants. No additional
hyperparameter search or test data is used. This is a derived ablation, not a
fifth independently tuned primary optimizer. It preserves a calibration mean
multiplier, not exact confirmation update norms; report both. Calibration
threshold estimates still use only the stationary coordinates.

Freeze a manifest containing all configurations, thresholds, constant gates, exact
seed lists, source/protocol hashes and tuning selection scores. Confirmation
refuses a missing or mismatched manifest. A changed formula or source uses a new
evidence directory and new confirmation allocation. Commit the manifest before
Phase 4.

## Phase 4 — confirm that the signal distinguishes the declared conditions

Run detector confirmation once on seeds 33000–33031, with the frozen candidate and
all diagnostic controls. No performance confirmation seeds may be opened yet.
Write a complete `diagnostic-decision.json`, including each required cell and its
denominator; a missing cell is incomplete evidence, never an implicit pass.

Candidate must meet ALL of these, separately in fixed and closed-loop modes:

- At least 80% of true target switches detected within 100 observations in each
  noise regime and each switch direction.
- At most 5% of stationary 100-observation blocks contain an alarm in each noise
  regime; do not pool quiet and noisy results to mask a failure.
- At most 5% of noise-increase windows and at most 5% of noise-decrease windows
  contain an alarm in their first 100 observations, with the target unchanged.

Report point alarms, block alarms, event hit rates, first-alarm latencies
(censored at 100), mean gate, startup activity and seed-level uncertainty. Use
10,000 seed-cluster bootstrap resamples, RNG seed 35000, for descriptive 95%
intervals; resample whole seeds with all their events and blocks intact. Exactly
quiet and smooth drift are descriptive detector stress tests, not post-hoc
substitutes for the declared event tests. Preserve per-event records. The
hit/false-alarm thresholds above are point-estimate screens; 32 seeds cannot
establish a population-wide false-alarm guarantee. Show intervals and counts.

Exit: every required detector cell passes. Otherwise close with a detector null;
do not run Phase 5 merely because the gate might beat Adam anyway.

## Phase 5 — independently confirm learning and the value of timing

Only after Phase 4 passes, run seeds 34000–34031 once. Use the selected primary
and historical arms, plus constant-gate Adam, on core and additional retention
streams. Make no selection from these results. Record prediction MSE, excess MSE,
stable-region error, post-switch error, adaptation latency and success, gate
activity, update norms, active state size and wall time measured with a
high-resolution timer after JIT warmup. One observation/gradient/update per
coordinate; report arithmetic costs separately from sample budgets.

Primary post-switch score: mean excess MSE over the first 200 predictions after
each target switch, averaged within seed across the two switching coordinates.
Adaptation: first start of 10 consecutive predictions within .2 of the target,
censored at 1,000 observations; include failures in the latency mean.

Using 10,000 paired-seed bootstrap resamples (RNG seed 35000), require:

1. At least 10% lower primary post-switch error than EACH of SGD, Adam, single
   and constant-gate Adam;
   each 95% interval for candidate-minus-control must be wholly below zero.
2. On EACH noise regime separately, no post-switch regression against each of
   those four comparators: upper difference
   interval at most max(.002, 10% of the comparator's mean error).
3. On EACH stationary coordinate and each additional retention stream, the same
   non-inferiority allowance against EACH of those four comparators. Score noise-up and
   noise-down over the first 200 predictions after each event separately, score
   drift from the first event index inclusive to the second exclusive, and score
   exactly quiet after burn-in. Also score post-burn-in MSE for each full extra
   stream, so a transient-only improvement cannot hide lasting damage.

All are conjunctions; no choice of the best task or comparator. The single control
is mandatory even if Adam loses substantially. Adaptation latency is secondary,
not a replacement endpoint when MSE fails.

Exit: every registered learning and retention comparison passes. Otherwise close
as a learning null. The constant-gate comparison tests whether variation helps
beyond its calibrated average multiplier. It does not prove that every benefit is
due to correct change detection or to matched cumulative plasticity. Those
stronger claims remain outside this slice.

## Phase 6 — close the slice, including negative outcomes

Add `report_v3_slice1.py`, final `V3-SLICE-1-RESULTS.md`, and a bounded CI
workflow. Archive the protocol, sources, manifest, completed seeds, failed
configurations, full metrics, generated contrasts and the machine-readable
decision. Distinguish `not run: prerequisite failed` from missing or incomplete
evidence. CI must not require a scientific pass; it must require an honest,
reproducible decision. A selected configuration that becomes non-finite on
confirmation fails its scientific gate; an implementation/instrument error is an
inconclusive experiment until diagnosed. Neither licenses editing completed
confirmation data.

Before the first `prepare`, implement an expected-row manifest and a test for each
possible early-stop disposition. Store rows atomically through `Evidence` with
source snapshots; reject resume under changed hashes. Reproduction compares every
scientific field of reached phases (rtol 1e-11, atol 1e-13), excluding only
timing, and independently recomputes configuration selection and decision cells.
Report code is separately hashed and tested at threshold boundaries; a missing/NaN
metric must never turn into a pass. Do not create a guard that only checks row
counts.

Planned entry points (to be implemented, not commands available today):

```sh
python check_v3_slice1.py
python study_v3_slice1.py prepare
# Commit the frozen manifest; command verifies that boundary.
python study_v3_slice1.py diagnostics
# Run only if the diagnostic decision passes; command enforces that boundary.
python study_v3_slice1.py performance
python report_v3_slice1.py
python check_v3_slice1.py --evidence results/v3-slice1 --reproduce
python report_v3_slice1.py --check
```

The `report` command in the study runner delegates to the report module; it must
not implement another scoring path. Reproduction uses the committed manifest as a
read-only reference and writes temporary evidence; it never reopens selection or
needs to commit its regenerated files.

Local validation starts with instrument/update tests, then complete reproduction
of the reached phases and a check that generated reports are current. Run the
existing v1 integration and evidence checks. GitHub retains existing V1 and V3
workflows, including all 56 frozen scores and all 552 original-study rows. Publish
each complete phase through a codex branch/PR, monitor the exact commit, fix
implementation/CI defects, and merge only after checks pass. Do not rewrite the
protocol or weaken gates to obtain a pass. A split confirmation phase may publish
evidence and decision together; do not publish selectively favorable rows.

Completion has exactly three dispositions:

- **Negative:** a scientific gate failed; stop this successor before integration.
- **Inconclusive:** instrument/search/evidence limits prevent the declared decision;
  state the limit and require a new protocol to investigate further.
- **Positive:** all gates passed; recommend a separately registered T1 experiment.
  This does not enable the candidate or establish a general optimizer advantage.

The conditional T1 handoff must define payoffs for EVERY action, including p=.5
for every action in an unlearnable state; include stable and switching states,
measured random/oracle baselines, hidden switch labels, separate learning-rate and
exploration interventions, matched simpler controls, fresh seeds, and v1
regression checks. Its implementation and acceptance thresholds belong to that
next slice, not this one.


## Operational definitions fixed before implementation

- Stream RNGs use NumPy PCG64 via `default_rng(SeedSequence([seed, domain]))`.
  Domain 0 generates the two shared event indices using inclusive endpoints;
  domains 1..4 generate the four core coordinate noises independently. Extra
  fixtures use domains 11 (noise jump), 12 (drift) and 13 (exactly quiet).
  All fixtures use the same schedule for a seed. Each extra fixture is scalar.
- Coordinate order is `quiet`, `noisy`, `switch_quiet`, `switch_noisy`.
  Target is -1 from the first event inclusive to the second exclusive in the
  switching coordinates. Drift uses equally spaced values +1 to -1 with the
  endpoint excluded over that interval, and stays -1 afterwards.
- Every stationary block starts at burn-in + 100*k. Event windows include the
  event observation and exclude event + window_length. Full-stream metrics start
  at burn-in. Stable-region error excludes each true target switch's first 200
  predictions. Noise changes are not target switches.
- Gate means and gate multipliers are measured per coordinate. Update norm is
  the Euclidean norm across that observation's coordinate updates; retain its
  mean and sum. Timings are high-resolution seconds, separate from science;
  the inherited Evidence envelope's rounded `seconds` field is also retained.
- Configuration order is ascending rate, then listed beta2/gain. Arm order is
  `sgd`, `adam`, `single`, `historical`, `candidate`; the derived `constant`
  ablation is never included in hyperparameter selection. SGD uses exactly
  `np.geomspace(.0001, 1., 24)`; there is no rounding of generated rates.
- Finish all 1,920 tuning rows before applying the screening rule. First classify
  absent valid configurations or required rate/gain boundary winners as
  tuning-inconclusive; only if none exist classify candidate gain=0 as a
  tuning-only negative. Do not call it independent confirmation. An ineligible
  configuration has an explicit failure record, never NaN/Infinity in JSON.
- Calibration is reached only if that tuning screen passes. Its expected rows
  are 16 seeds for each of the three gated arms. Each row records both observer
  modes' core statistics and block maxima. Candidate rows also provide the
  per-coordinate gate means for the constant ablation. All 48 rows are required.
- Detector confirmation has 32 seeds for each of the three gated arms, each row
  containing fixed and closed-loop results on core plus all three extra fixtures.
  Learning scores from those closed-loop runs cannot be used for retuning or as
  Phase 5 evidence. Phase 5, if reached, has 32 seeds for each of six arms,
  with core plus the three extra fixtures in every row.
- Required detector cells: 4 true-switch cells, 2 stationary block cells and
  2 noise-change cells per observer mode; 16 candidate cells total. Each switch
  direction and noise-change direction has denominator 32; stationary blocks
  have denominator 32*50. Compute each seed's fraction before seed resampling.
  Descriptive bootstrap intervals use 10,000 resamples and seed 35000.
- Decision code must reject missing, wrong-denominator or non-finite required
  metrics. Point screening comparisons are inclusive (>=.80, <=.05). Performance
  improvement is <=.90 times each control and bootstrap upper difference <0;
  retention comparisons use <= the specified allowance. Resample paired seeds,
  never individual events/coordinates as independent samples.
- Evidence lives only under `results/v3-slice1/` (or isolated reproduction temp
  directories). All learning/stream/metric/decision/runner source hashes plus
  this protocol are captured before the first prepare. Reports have a separate
  source fingerprint. Expected keys and reached-stage disposition are checked,
  not inferred from whichever rows happen to exist.
- A tuning stop produces a committed screening manifest and closure report;
  calibration, detector and performance files are explicitly NOT EXPECTED.
  A detector stop requires all calibration and detector rows and a matching
  decision; only performance is not expected. Positive/learning-negative closure
  requires all four stages. Unexpected files from a forbidden later stage fail
  closure validation. An interrupted incomplete run is not a closed experiment.
- Automated reproduction reads the committed manifest as the reference. It may
  regenerate reached rows in temporary storage and recalculate decisions, but
  has no option to execute a stage absent from the frozen reached-stage record.
  Reports must display every observed failure and each not-run prerequisite.

## Baseline verification and diagnosis

The unchanged first study is reproduced before publication with
`python check_v3_gate.py --evidence results/v3 --reproduce` and its generated
report checked with `python report_v3_gate.py --check`. The measured misses and
noise responses motivate the successor. The inference that mean disagreement
will separate these cases remains untested. Shared samples, a constant-gate
ablation, per-direction noise tests, and independent confirmation are intended
to expose rather than assume that benefit.
