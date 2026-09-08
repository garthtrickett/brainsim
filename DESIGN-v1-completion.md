# Remaining v1 experiments

Predictions registered before corrected step 9 or later results. The operator
authorised completion of v1, followed by an assessment of v3 versus v2.

## Method

Keep `reference.json` frozen. Use paired seeds, calibrated random/oracle controls,
and record individual seed scores. Persist each finished condition atomically.
Compare all seven reference tasks before enabling any new default. A completed
experiment may reject a mechanism; a proposal without its required instrument is
explicitly deferred, never presented as validated. Report intervals and seed
agreement, not just the best of several means.

Long jobs use `work run ... -- systemd-run --user --scope ...` so they appear on
the work board and their computation survives a Paseo service restart. Every
job also checkpoints in the repository; logs and process/exit status determine
whether it finished. Monitor at least every five minutes.

## 9 — local competition

The inherited probe changed the winner budget: `max(1, 6//P)*P` equals 4 at
P=4 and 8 at P=8. Preserve that probe and its data in `superseded/`.
Use P=1,2,3,6, k=6, H=80. Pools have floor/ceil(H/P) units and k/P winners;
reject non-divisors instead of silently changing sparsity. Report realised
activity as well: thresholds and ties can make a nominal quota differ from firing.

The old 0.385 capacity score predates commit fc84358, which replaced the
compositional label `(shape+colour)%4` with `shape%4`. Keep the current task
unchanged and add an explicitly named legacy-label experimental condition.
Prediction: the legacy task remains harder; local pools will not robustly improve
both it and volatile-4. Enable no default unless a paired improvement has a
95% interval above zero and survives the regression suite. Six seeds for screening;
any promising result requires confirmation with additional independent seeds.

The accelerated kernel must first reproduce the plain implementation's reward
trajectories with pools on and off, and matching floating-point state within
roundoff. The existing check compared rewards only: that is trajectory equality,
not proof that every floating-point operation or internal state is bit-exact.

## 11 and 13b — representation and local learning

Recheck the compositional generalisation gates with evaluation weights frozen,
disjoint train/test pairs, and a measured test floor/ceiling. The current label
is shape identity; the old nonlinear additive label is a different question.
Prediction: the fixed encoder still generalises above chance. If it does, the
planned predictive-coding hierarchy and Forward-Forward encoder do not have the
registered representation gap; close their v1 investigations as deferred on this
instrument, without inventing a harder task solely to justify implementation.
This is a premise test, not evidence that either learning mechanism is ineffective.

Step 8 already tested a privileged scored-step policy gate. It does not establish
the value of general precision weighting or a hierarchy. Those require their own
valid experiment; v3's noise/change test is the specified next instrument.

For generative replay, first test whether a learned local forward model can
predict next observations and rewards on held-out transitions better than
state-only and unconditional predictors. Then compare extra model backups with
matched extra real replay updates on the lock, scoring external reward only.
Prediction: a model can fit observed transitions, but counterfactual planning is
limited by action coverage; do not claim planning from better reconstruction alone.

## 12 — curiosity

Test observation prediction error as intrinsic reward with the validated forward
model. Compare zero and small positive bonuses; score only task reward and report
time to first external reward and seeds that never find it. Keep the extrinsic
episode store uncontaminated by intrinsic bonuses. Prediction: curiosity may
improve discovery but can reduce final exploitation. A useful discovery effect
alone is not sufficient to change the default. Match task and agent seeds; keep
the calibrated 12,000-decision lock horizon.

## 13a — content-addressed replay

Bias selection of existing episodes by cosine similarity to the current hidden
state, preserving episode ordering, replay count and reward weighting. A shuffled
query control separates context matching from merely changing sampling weights.
Prediction: the single-path lock offers little benefit; do not interpret a null
as refuting content-addressed memory generally.

## 13c — synaptic failure

Compare motor-path transmission failure with no failure at fixed learning rules.
Include deterministic attenuation matched to each failure rate, so reduced drive
cannot masquerade as a stochastic regularisation effect. Use separate random
streams for the experimental masks. Prediction: high failure harms the working
credit-alignment mechanism; no across-task improvement. Test moderate (0.1) and
high (0.5) failure rates. Frozen defaults must consume no new random draws.

## 10 and v2/v3 boundary

The revised `V2.md` places embodiment with continuous time. It changes the reward
source, task interface and replay boundaries together, so it remains explicitly
deferred to that fork rather than being silently omitted from v1 closure.
Recurrence, event-driven execution, parallel neuromodulator loops and large-scale
hardware work are not required to close these v1 rule investigations.

After the v1 results, assess the already-specified standalone Adam versus
two-timescale gate experiment before committing to a v2 rewrite. This assessment
does not authorise claiming or implementing all of v3's speculative queue.

## Locked protocols for the remaining arms

Registered after the forward-model calibration and before the intervention runs:

- The observation model is action-conditioned normalised LMS, rate 0.2, evaluated
  before each online update. It predicts the public next observation, reward and
  termination. The calibration used eight paired task/agent seeds and the final
  2,000 transitions of a 12,000-decision run. This is sequential out-of-sample
  prediction, not a held-out state/action split.
- Curiosity uses 0, 0.1 or 0.5 times next-observation mean-squared prediction error
  as a bonus to the online policy only. Its critic, reward-rate adaptation and
  replay reward fields stay external. Six seed pairs, 12,000 lock decisions.
- Dyna compares no extra backup, one real one-step TD backup per decision, and
  one learned-model backup with the same rule and budget. A second local model
  predicts the next observed hidden trace, reward and termination; errors are
  logged separately from the observation calibration. Starts/actions are drawn
  from the last 512 actually observed transitions; unsupported state/action
  guesses are excluded. This tests model recomputation on supported experience,
  not open-ended counterfactual discovery. Nonterminal successor traces arrive at
  the next decision; terminal successor value is zero. Six paired lock seeds.
- Content retrieval uses cosine similarity of the current hidden trace to each
  episode's mean hidden trace, with a 0.05 positive floor, multiplied by existing
  reward weights. The shuffled control queries a randomly selected episode
  centroid. Replay counts, ordering and TD updates are unchanged. Six lock seeds.
- Transmission uses independent Bernoulli masks per motor synapse per tick, with
  failure probabilities 0.1 and 0.5. The attenuation controls multiply motor drive
  by 0.9 and 0.5 without masking. Six seeds on lock, volatile, XOR and nway-8.
- No arm can be enabled from these screening means alone. A promising arm must
  beat its appropriate control on additional independent seeds and clear the
  remaining reference tasks. Multiple candidates are not pooled into one claim.

Before any transmission result on the capacity task: also run the explicit
legacy additive-label 4x4 task, using the same six seeds and all five failure/
attenuation arms, saved separately in `v1-failure-capacity.json`. Step 13c's
original motivation mentions this capacity limit, so the four standard tasks
alone would not fully test its stated target. The original four-task screen is
retained unchanged, including all negative results.
