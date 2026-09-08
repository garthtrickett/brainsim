# Remaining v1 investigations

**All bounded remaining-v1 investigations are closed. No experimental feature
earned a new default.** Embodiment/continuous time, the untested hierarchy and
Forward-Forward mechanisms remain explicitly deferred, not claimed implemented.
The next-step decision is in `V3-NEXT.md`.

Protocol: `DESIGN-v1-completion.md`. Raw evidence is checkpointed per seed in
`results/v1-*.json`, including source hashes and parameters. `reference.json` is
unchanged. The new studies vary task and agent seeds together; the frozen table
fixes the task at seed zero. Their means should not be compared as though they
were the same experiment.

## Step 9: local pools — closed, keep the default

The inherited probe did not hold sparsity constant: P=4 and P=8 changed the
nominal six winners into four and eight. Its code and data are retained under
`superseded/step9_sparsity_confound/`. The corrected experiment uses P=1,2,3,6,
H=80, k=6; balanced pools differ by at most one unit in size. Each configuration's
separate 100-tick activity probe observed six winners. Both kernels reject
non-divisors of k; tied values and membrane thresholds remain part of the
original threshold-based winner semantics.

The capacity discrepancy was a changed task, not a newly acquired capacity.
Commit fc84358 changed labels from `(shape+colour)%4` to `shape%4` while the
roadmap retained the old capacity numbers. On six paired seeds the global pool
scores **0.363** on the explicitly restored additive-label task and **0.964** on
the current shape-label task. No task definition in the frozen suite was changed.

No pooled setting has a positive paired interval on either capacity task.
P=3 raises volatile's mean by 0.030, but its interval includes zero and XOR drops
in all six seeds. P=6 reduces volatile by 0.069. P=2 reduces nway-8 by 0.008.
These data do not justify enabling local pools. The implementation remains an
opt-in instrument, with defaults unchanged. They also do not prove that local
competition would fail at larger scales or with learned routing.

## Steps 6, 11 hierarchy, and 13b: representation gate — closed, defer the mechanisms

Eight seeds, 4,000 training decisions on 12 shape/colour pairs, then 1,000
evaluation decisions on four disjoint pairs. Evaluation disables every weight
writer and asserts exact equality of encoder, policy, memory, value, eligibility
baseline and threshold parameters before and after testing.

Seen accuracy is **0.966**; unseen accuracy is **0.751**, against a measured
**0.257** floor and **1.000** ceiling. Every seed beats its test floor. The paired
unseen-minus-floor difference is 0.494, bootstrap interval [0.398, 0.576].

The registered gate required the fixed encoder to be at chance on unseen pairs.
It fails. Therefore this task does not justify a learned predictive-coding
hierarchy or Forward-Forward encoder under the plan's stated gate. Neither
mechanism was implemented or experimentally refuted. There is still headroom;
the evidence establishes generalisation above chance, not an optimal encoder.

The precision-weighting thread also remains distinct: step 8 tested privileged
scored-step gating on a particular T-maze. That does not bound arbitrary learning
rules or every possible gate. A noisy-versus-changing environment is needed for
the v3 precision hypothesis, and the frozen suite has deterministic task rewards.

## Step 11: forward-model gate

An action-conditioned local predictor learns next observations, reward and
termination online. Every error is scored before that transition updates the
predictor; the final 2,000 transitions of eight 12,000-decision lock runs are
reported. The agent sees only public observations/actions/outcomes, never state
identity or `correct()`.

Next-observation MSE is **0.00000285**, versus **0.0525** for a state-only
predictor. This passes the action-dependence gate. It is sequential prediction
on recurrent states, not generalisation to unseen state/action pairs, and does
not by itself demonstrate planning. The intervention experiments follow it.

## Step 11: model-generated backups — closed, keep default off

Six paired lock seeds, 12,000 decisions. Baseline **551.7** rewards; additional
real-transition backups **596.2**; model-generated backups **580.0**. Both
intervention arms perform exactly **11,999** extra one-step backups per run.
The model-versus-real difference is -16.2 rewards, interval [-37.7, 1.8], with
the model winning only two seeds. The gain over baseline does not establish a
benefit from imagination: extra real updates explain at least as much.

The hidden-state forward model is separate from the observation predictor above;
its pre-update next-trace, reward and termination errors are logged in the Dyna
evidence. It samples starts/actions from observed transitions and recomputes
their successors, so it does not test discovery of never-observed actions. The
first reward is unchanged in every seed. No generative replay is enabled.

## Step 12: curiosity — closed, keep default off

The next-observation predictor supplies bonuses only to the online policy. The
recorded task scores, value targets, reward-rate controller and episodic reward
fields remain extrinsic; isolation is covered by the focused gate.

Six lock seeds: baseline **551.7**, bonus coefficient 0.1 **541.3**, coefficient
0.5 **558.8**. Their paired differences are -10.3 [-146.7, 102.3] and +7.2
[-157.3, 201.3]. Time to first reward sometimes improves dramatically and sometimes
worsens. All seeds eventually find reward. Early external reward averages also
do not improve (119.5/131.5 versus 133.0 in the first 4,000 decisions).
The evidence does not establish a reliable discovery or total-reward gain.
This null is specific to the predictor, bonus, horizon and task tested.

## Step 13a: content-addressed replay — closed, keep default off

Six lock seeds: existing reward-weighted retrieval **551.7**, context query
**535.5**, shuffled query **539.8**. Context-minus-shuffled is -4.3 rewards,
interval [-21.2, 10.7], three wins out of six. This retrieval change has no
demonstrated value on a lock with one rewarded path. It is not a general
refutation of content-addressed memory. Counts and the existing reverse-TD
implementation are shared across arms.

## Step 13c: synaptic failure — closed, keep default off

Six seed pairs on five tasks, with separate matched-attenuation controls. The
additive-label capacity task scores 0.363 without intervention, 0.378/0.380 at
10%/50% failure and 0.360/0.390 under corresponding attenuation. No capacity
contrast has a paired interval above zero, including stochastic-versus-
attenuation comparisons.

The one positive screening interval against baseline is the small nway-8 gain
at 10% failure: 0.9805→0.9850. Its attenuation control scores 0.9882, and the
stochastic-versus-attenuation interval includes zero. It therefore does not
establish a benefit from synaptic randomness. At 50% failure XOR falls in every
seed, 0.893→0.849, and is also worse than matched attenuation in every seed.
Lock and volatile differences are inconclusive, with broad intervals.

Neither failure rate meets the preregistered promotion gate. No independent
confirmation or new-default validation is warranted for these arms. This does
not rule out other rates or architectures; it rules out enabling the tested
mechanism from these results.

## Validation and reproducibility

- `.venv/bin/python check_v1.py`: pool winner quotas, invalid configurations,
  plain/accelerated trajectory and state parity, phase-structured memory,
  transmission parity, zero-arm equivalence, intrinsic/external reward isolation,
  and action-conditioned predictor checks pass.
- `.venv/bin/python check_reference.py`: all 56 frozen per-seed scores matched
  exactly after the pool correction. Final integration is checked separately.
- `.venv/bin/python study_pools.py`: 120 experimental runs plus controls complete.
- `.venv/bin/python study_representation.py`: eight frozen evaluation runs complete.
- `.venv/bin/python study_model.py`: eight online prediction calibrations complete.
- `.venv/bin/python study_learning.py dyna`: 18 runs plus controls complete.
- `.venv/bin/python study_learning.py curiosity`: 18 runs plus controls complete.
- `.venv/bin/python study_learning.py replay`: 18 runs plus controls complete.
- `.venv/bin/python study_learning.py failure`: 120 runs plus controls complete.
- `.venv/bin/python study_learning.py failure --tasks legacy-additive-4x4 --out results/v1-failure-capacity.json`:
  30 runs plus controls complete.
- `.venv/bin/python check_reference.py --out results/v1-reference-final.json`:
  final integration reproduces all **56/56** frozen scores exactly.
- `.venv/bin/python check_evidence.py`: all **530** evidence rows present, finite,
  and backed by verified source snapshots.
- `.venv/bin/python summarise_v1.py`: produces `results/v1-contrasts.md` from raw
  paired scores. It does not automatically declare a mechanism successful.
- `git diff --check`: pass.

All study processes finished with exit code zero. There are **340 study runs**
in addition to controls and two full reference checks. Six-seed bootstrap
intervals are exploratory, unadjusted for multiple comparisons, and can miss
small effects. No mechanism is promoted on a selected small-sample mean.

The frozen baseline was not rewritten. Source digests refer to files as they
were loaded for each run; their exact contents are archived under
`results/source-snapshots/<sha256>.txt`, including intermediate versions. This
avoids confusing later documentation or integration edits with the code used to
produce a number. Dependencies are pinned in `requirements.txt`.

Changes are in the two simulation implementations, opt-in research agents and
transition model, study/check scripts, source/evidence archives, and the roadmap
documents. There is no capability registry in this repository. No Gust compiler,
stdlib, runtime, or roadmap file was changed.

The `V1 validation` GitHub workflow runs source/evidence integrity checks,
execution/parity gates and all frozen reference scores on the published commit.

The old port gate used reward-history equality, not full internal bit-exactness.
The new focused gate checks actions/rewards exactly and internal floating-point
state within roundoff. The original gate now returns a failing exit code on a
failed comparison instead of merely printing FAIL.
