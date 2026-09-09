# Registered V3 bounded burst-controller experiment

Protocol `v3-burst-20260909-v1`. The operator authorized short alarm-triggered
learning bursts, true-change-time and randomly timed controls, equal small tuning
budgets, fresh confirmation, and adaptation plus retention criteria. Register
before study observations. Preserve all older scientific code, evidence,
protocols and six workflows. No default change or agent integration is authorized.

## Question and fixed detector

Can the already tested separate-reference signal usefully TIME a bounded burst
of larger updates? The preceding continuous gain=64 policy passed detection but
failed independent learning. Below-threshold modulation is a possible explanation,
not an established cause. This experiment changes the controller and tunes a
small finite set; it cannot isolate every reason for the preceding failure.

Reuse exactly `v3_persistent.run(y, 'candidate', observer=True)[1]`: fixed zero
reference, recent16/previous128 nonoverlapping gradient windows, separate unbiased
variances, epsilon1e-8, four same-sign scores, q=a²/(a²+16). Freeze the preceding
reference calibration threshold **0.4690234346011377**, strict >. There is no new
detector calibration, search or threshold adjustment. The threshold's provenance
is `results/v3-reference/manifest.json` at master `8bc0ca0` and
`DESIGN-v3-reference.md`. First possible nonzero score is t146 (zero based).

Learners predict before observing y_t. After observing it, they use their own
gradient w_t-y_t and Adam's inherited direction (beta1=.9, epsilon1e-8, ordinary
bias corrections with global t+1). No moment/weight reset, norm clipping,
future observation, target value, noise label or event index enters a deployable
learner. A causal cached two-pass gate implementation is permitted, with prefix
and coordinate-isolation tests. Reference-gradient scalability remains untested.

## Controllers and oracle separation

**burst (candidate):** base rate lr, beta2=.999. Beginning at t146, an armed
controller starts on q>threshold. It uses rate lr*factor for exactly D updates,
including that update, and lr otherwise. Factor is 2 or 8; the maximum rate in
the grid is .256. A high q during a burst cannot extend it. After a burst ends,
16 consecutive observations with q<=threshold are required to rearm; observations
during a burst do not count. A subsequent high q may start the next burst.
Initially armed. The cap bounds learning RATE, not realized Adam update norms.
All state is per coordinate. A high signal held forever produces one burst.

**continuous:** same separate-reference q and inherited Adam direction; rate
lr*(1+gain*q) at every update, beta2=.999. Its grid includes the preceding
lr=.004,gain=64 policy. Tune it equally; do not keep a weak fixed comparator.

**adam**, **sgd:** ordinary inherited implementations, no burst or detector effect.

**oracle:** evaluator-only diagnostic. Supply a trigger on the first observation
of each true abrupt TARGET change, per coordinate, never noise changes or drift.
It uses the same burst engine/duration and no model-state reset. It cannot know
the new target value, change magnitude or future observations. Its 12 settings
are tuned independently with the same seeds, fixtures and objective as burst.
This privileged arm can never authorize advancement or count as deployable.

**oracle_matched:** same true-time triggers, but EXACT selected burst parameters.
This isolates trigger scheduling with parameters held fixed. Oracle timing is
not a mathematical performance upper bound: optimizer state and noise interact
with timing. A failed tuned oracle rules out an advantage only for this tested
finite family and objective, not all bursts or all V3 approaches.

**random:** selected burst's exact lr/factor/D/beta2, with observation-independent
Bernoulli trigger opportunities from t146. After each start, suppress triggers
for its D updates and 16 further updates; then resume opportunities. No q, target
or event metadata is supplied. Generate independent uniforms per coordinate with
PCG64 SeedSequence([study_seed, 76000+fixture_ordinal, coordinate]), using the
fixed fixture order below. Pre-generating uniforms is allowed and prefix invariant.

Freeze random frequency from SELECTED burst tuning rows only. Pool start counts N
and observed coordinate-time S=(6000-146)*9*8 across all five fixtures/eight seeds.
Let f=N/S and p=f/(1-f*(D+15)); p=0 if N=0. Require finite 0<=p<=1, no clipping.
The renewal process has long-run start rate f (mean inter-start spacing
D+16+(1-p)/p). This matches expected pooled frequency, NOT exact per-condition
counts, realized update norms or confirmation duty cycle. Report those differences;
no post-confirmation matching, shuffling or access to future candidate gates.
Oracle_matched and random are parameter-matched ablations, not separately searched
families. Giving them another search would break that controlled comparison.

## Fixed search and partitions

All five searched families have **12 configurations × 8 seeds × all 5 fixtures**.
Same observations and selection objective; cache the identical fixed q rather
than computing it once per setting. Report compute, not an assertion of identical
CPU costs. The configuration order below breaks exact objective ties.

- burst and oracle: lr in [.004,.016,.032], then factor in [2,8], then
  D in [16,64], Cartesian product, beta2=.999 (12 each).
- continuous: same three rates, then gain in [0,8,32,64], beta2=.999 (12).
- adam: lr in [.001,.004,.016,.032,.064,.128], then beta2 in [.999,.9999] (12).
- sgd: lr in [.0001,.0004,.001,.004,.008,.016,.035743040182210514,
  .064,.128,.256,.512,1] (12).

These are FINITE policy menus, not searches for global optima. Record endpoint
selections but do not expand a grid or declare a boundary failure after observing
results. Earlier experiments' boundary stops remain unchanged. A configuration
with a non-finite trajectory/metric on any tuning seed is ineligible; archive it
explicitly. If any searched family has no eligible configuration after ALL tuning
rows, close tuning_inconclusive and forbid confirmation. Otherwise select one
configuration per family and commit the complete tuning manifest before confirmation.

| Partition | Seeds | Complete rows |
| --- | --- | ---: |
| Development only | 70000–70007 | synthetic/unit, not study |
| Tuning | 71000–71007 | 5 families ×12 ×8 =480 |
| Independent confirmation | 73000–73031 | 7 policies ×32 =224 |
| Whole-seed bootstrap RNG | 75000 | 10,000 resamples |

All ranges are fresh, including previously reserved unused partitions. No study
seed substitution or retrospective partition reopening. Reuse exact 6000-step,
burn1000 fixtures and metrics from `v3_persistent.py` / `v3_slice1_streams.py`:
ordered core, noise_jump, drift, exactly_quiet, mixed. Nine coordinates total.
Tuning rows contain all five fixtures so the objective can include every regime.

Define primary P as the equal mean post-200 MSE across core switch_quiet,
switch_noisy, mixed increase_first and decrease_first. Define 14 retention cells
R: core quiet/noisy excess-MSE and switch_quiet/switch_noisy post-MSE; whole
noise_jump/drift/exactly_quiet excess-MSE; noise-increase/noise-decrease/drift
windows; mixed post-MSE and stable-MSE for each of its two coordinates.
Select the lowest seed-mean **(P + mean(R))/2**, uniformly for all five families.
This explicit adaptation/retention tradeoff is tuning only. Confirmation still
requires every individual registered comparison, not just this aggregate score.

## Confirmation and stopping rules

Once a finite manifest is committed, run ALL 224 confirmation rows. Do not gate
learning measurement on alarm counts or oracle results; earlier evidence showed
missed alarms can coexist with recovery. The raw fixed detector's 12 cells are
reported on candidate confirmation seeds: >=80% hit within100 in eight abrupt
target cells, <=5% noise-increase/decrease windows, <=5% stationary quiet/noisy
100-block alarms. Fixed/active signals are identical by construction and are
not duplicated as independent evidence. These are diagnostic screens, not a
substitute for the learning criteria below. Report actual burst start hits and
latencies alongside raw-q alarms to expose rearming delays and suppressed alarms.

Candidate burst must improve P by >=10% over EACH of adam, sgd, continuous and
random, with paired whole-seed 95% upper candidate-minus-control difference <0.
For each of the 14 R cells against EACH of those controls require paired upper
difference <=max(.002,.1*control mean). All **60 comparisons** must pass for
learning_positive; otherwise learning_negative. Any non-finite required policy
trajectory fails; missing/invalid records remain incomplete and require diagnosis.
No oracle comparison can repair a candidate failure. Oracle and oracle_matched
are each evaluated against adam and sgd using the same 30 primary/retention
criteria, reported separately as oracle_pass/oracle_negative. Report ALL metrics
and paired contrasts, including perfect-time failures or contradictory outcomes.

Interpretation: an oracle advantage with a detected-policy failure motivates
inspection of timing errors and controller state; it does not uniquely establish
detection delay as the cause. A random-policy tie fails to establish timing value.
A candidate pass permits only a separately authorized broader supervised benchmark,
not agent integration. Any outcome closes this registration: no automatic search
extension, detector change, policy replacement or next experiment.

Archive per-policy/seed learning metrics and actual update norms for every fixture;
per-coordinate burst start times, active-update counts, duty cycle and event
start-hit/latencies; candidate raw-q detector cells and explanatory event errors /
recovery using the frozen previous evaluator. Oracle markers are conspicuous.
Do not equate a rate cap with a norm cap or frequency matching with equal movement.

## Implementation phases and refinement gates

1. Register this protocol and record its immutable SHA and commit before data.
2. Implement new runtime, policy, runner, report and check modules; reuse frozen
   kernels/evaluators without editing them. Commit all source before tuning.
3. Run all480 tuning rows, compute selections and random p, archive/commit manifest.
4. Run all224 independent confirmation rows only if eligible. Freeze outcomes.
5. Reproduce EVERY reached row, manifest, decision and report locally and in a new
   seventh CI workflow. Publish one draft codex/** PR; monitor exact HEAD across
   all seven workflows; mark ready and merge when green and reviews resolved.

Refinement before observations must check: exact D updates including trigger;
16 quiet observations AFTER a burst before rearm; no extension on high q; strict
threshold and startup; ordinary Adam parity with no bursts, factor1, and continuous
gain0; independent scalar update equations and per-coordinate state; prefix
causality and coordinate isolation; oracle only target indices/evaluator ownership;
random RNG domain independence, cooldown, prefix and frequency formula; all12 grids,
seed separation, shared tuning objective, deterministic tie and finite selection;
all60 required vetoes, oracle non-authority, diagnostics non-authority; missing /
non-finite rows, changed sources, uncommitted manifest and forbidden confirmation;
full source snapshot and numerical evidence reproduction.

Source snapshots include this registration, applicable previous protocols, every
transitive runtime dependency, report/decision/check sources and requirements.
No runtime, evaluation or reporting source changes after observations except a
diagnosed instrument defect, explicitly reported before any correction. Report
endpoint selections and remaining uncertainties. Preserve every earlier result.
Reproduction tolerance rtol1e-11/atol1e-13 excludes only timings and regenerated
input digests, not scientific metrics or decisions. Whole-seed bootstrap intervals
are descriptive and do not guarantee unseen rare-event rates or global superiority.
