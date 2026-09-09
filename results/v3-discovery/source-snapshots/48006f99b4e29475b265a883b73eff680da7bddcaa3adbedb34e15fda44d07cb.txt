# Registered V3 interference-as-discovery experiment

Protocol `v3-discovery-20260909-v1`. The operator authorized a test of V3
§11.1: conflicting evidence widens an interval instead of overwriting it, the
free label "what predicts which way this weight wants to move" trains a
discovery unit from a cue available before each observation, and contested
coordinates condition on it. Tested against y-only SGD, fixed windows and
ADWIN2, plus random-split, shuffled-cue and no-conditioning ablations, with a
privileged true-context oracle as diagnostic only. Register before study data.
Preserve all earlier protocols, scientific sources, evidence and eight CI
workflows. No dependency or agent/default change.

## Hypothesis and why this follows forgetting

The bounded-burst and change-triggered forgetting studies closed
learning-negative with the same shape: detector/oracle scheduling beats matched
random/no-reset controls on the primary metric but cannot beat the fast
deployable trackers (SGD, fixed W=8) while preserving ADWIN's stable-noise
accuracy. No single (K, W, schedule) beats both specialists. This experiment
tests the §11.1 escape from that tradeoff: do not choose one memory, keep the
conflict and discover the missing variable that resolves it.

Falsifier, stated in advance per V3 §12: on a task where a hidden context
determines the mapping, the contested-weight set must localize the right
variable. If the discovered unit is uncorrelated with the true hidden context,
the signal is noise and this dies — even if extra capacity wins MSE against
weak controls. Shuffled-cue and random-split ablations exist to enforce that.

## Generative process: same y, plus a cue and a hidden context

Reuse the EXACT y/target/events generation of the forgetting study (five
fixtures `core, noise_jump, drift, exactly_quiet, mixed`, nine coordinates,
6000 observations, burn 1000, same `v3_persistent.fixture` seeds). y is
unchanged so the y-only controls remain comparable. The evaluator adds, per
coordinate and step:

- True hidden context `c[t,j] ∈ {0,1}`. Coordinates with target events toggle
  context at each `target_*` event (0 before the first switch, 1 between the
  two switches, 0 after). Coordinates without target events (quiet, noisy,
  exactly_quiet, noise_jump, drift) hold `c = 0` throughout. Context is
  evaluator-owned ground truth, never shown to deployable arms.
- Cue `x[t,j] = (2*c[t,j]-1)*SEP + cue_noise[t,j]`, `SEP = 0.5`,
  `cue_noise ~ N(0,1)` i.i.d. from PCG64
  `SeedSequence([study_seed, 96000+fixture_ordinal, coordinate])`, generated per
  coordinate to preserve prefix/width invariance. Single-sample d' = 1.0,
  AUC ≈ 0.76: learnable but not trivial. The cue is available BEFORE the
  prediction at t (like a context observation); y[t,j] is observed after.
- y itself is NOT regenerated: the existing target/noise process already flips
  its mean at exactly the context toggles on switching coordinates, so the
  hidden context determines the mapping by construction. Cue RNG is independent
  of y RNG; y bytes are identical to the forgetting fixtures at equal seeds.

Deployable arms see `(history of y, current x)`. y-only baselines see history
of y alone. Oracle arms receive true `c[t,j]` pre-update (privileged timing +
identity, no target values, no noise labels, no future). No arm sees future
samples, target values, noise labels, drift slopes, or other coordinates'
ground truth.

## Learner semantics

All policies predict each coordinate's y[t,j] before seeing it
(initial prediction 0), then update. Causal, per-coordinate, no resurrection
of discarded information, no cross-coordinate leakage.

**discover candidate (interval + discovery + conditioning), per coordinate:**
state is pooled mean `mu`, conditional means `mu0, mu1`, interval scale
`s >= 0`, and cue weights `(w, b)` with score `z = w*x + b`,
`hat_c = 1[z > 0]`.

- Predict: if `s < TAU` (uncontested) predict `mu`; else predict
  `mu_{hat_c}` computed from the CURRENT cue.
- Observe y. Free label `s_pull = sign(y - pred)` (0 pull maps to +1
  arbitrarily but deterministically; exact tie rule fixed in implementation
  and tested). Update cue by one online logistic step on `(x, s_pull)` with
  rate `cue_lr`.
- Interval update: `err = y - mu_before`; `s <- (1-alpha)*s + alpha*err^2`
  (centered second-moment style, finite `alpha`). Agreement shrinks s,
  conflict grows it; pooled `mu` moves with rate `pool_lr` scaled DOWN when s
  is large (`mu <- mu + pool_lr * y_err / (1 + kappa*s)`), so conflict widens
  instead of overwriting. The active conditional mean moves with rate
  `cond_lr`: `mu_{hat} <- mu_{hat} + cond_lr*(y - mu_{hat}})`. The inactive
  conditional is untouched. All rates finite, fixed per configuration; no
  momentum, Adam, burst gain, or window-reset machinery.

**oracle:** identical architecture and menu, but `hat_c = c` (true context
supplied by the evaluator pre-update). Independently tuned with the same
budget. Privileged diagnostic; cannot authorize candidate advancement.
**oracle_matched:** discover's EXACT selected config with true `c`. No search.

**window:** identical growing-then-capped arithmetic mean on y with no cue,
no splits (same as forgetting window). **sgd:** unchanged plain SGD
`w <- w - lr*(w-y)` on y. **adwin:** paper-based ADWIN2 on y (same module and
fixed bucket/minimum/grace settings as forgetting). y-only deployable
controls; cue-blind by construction.

**random:** discover architecture + selected discover config, but
`hat_c[t,j] ~ Bernoulli(0.5)` i.i.d. from PCG64
`SeedSequence([study_seed, 97000+fixture_ordinal, coordinate])`,
independent of cue/context/y. Tests timing/capacity vs discovery.
**shuffled:** discover architecture + selected config, but the cue series is
time-permuted WITHIN each coordinate (fixed permutation from
`SeedSequence([study_seed, 98000+fixture_ordinal, coordinate])`, applied
before the run). Marginal cue distribution preserved, cue-context correlation
destroyed. If candidate wins by capacity alone, shuffled wins too.
**nocontext_matched:** same state and updates as discover with the selected
config, but prediction ALWAYS uses pooled `mu` (conditioning disabled).
Measures the benefit of conditioning beyond tracking s and two memories.

## Fixed finite menus and objective

Five searched families, each **12 configurations × 8 paired seeds × all five
fixtures**. Order below breaks exact objective ties.

- discover and oracle: `TAU in [0.05, 0.5]`, `alpha in [0.01, 0.1]`,
  `cue_lr in [0.01, 0.1]`, `pool_lr = cond_lr in [0.05, 0.2]` —
  Cartesian 2×2×2×... trimmed to exactly 12 by taking the first 12 in
  lexicographic order `(TAU, alpha, cue_lr, lr)` with
  `kappa = 1.0` fixed. The 12-set is frozen in code; endpoint report required.
- window: `W in [1,2,4,8,16,32,64,128,256,512,1024,6000]` (unchanged).
- sgd: `lr in [.0001,.0004,.001,.004,.008,.016,.035743040182210514,
  .064,.128,.256,.512,1]` (unchanged).
- adwin: `delta in [.0001,.001,.01,.1]`, `clock in [1,8,32]` Cartesian
  (unchanged); five buckets/size, minimum subwindow 5, grace 10 fixed.

Finite menus, not global optimization. Report endpoint selections; no
automatic extension or post-result boundary veto. Equal
configuration/seed/fixture budgets, not identical CPU costs. Record measured
execution times.

Reuse the EXACT nine-coordinate learning fixtures/metrics and selection
objective of the burst/forgetting registrations: P = equal-mean post-200 MSE
over core quiet/noisy switching + both mixed coordinates; R = the same 14
cells; select minimum seed-mean `(P+mean(R))/2` per searched family. A
configuration with any non-finite tuning trajectory/metric is ineligible, its
failure retained. Finish all 480 rows. If any family lacks a complete finite
configuration, close `tuning_inconclusive` and forbid confirmation. Otherwise
freeze all selected configs, cue/shuffle/random RNG domains, source identity
and complete tuning evidence in a committed manifest BEFORE confirmation.

## Discovery gate (ground-truth falsifier)

On confirmation seeds, for each switching coordinate (core switch_quiet,
switch_noisy, mixed increase_first, decrease_first), compute the
polarity-invariant AUC* of the candidate's pre-update score `z[t,j]` vs true
`c[t,j]` over steps 1000..5999: AUC* = max(AUC, 1 - AUC). Aggregate the
seed-mean AUC* over the four switching coordinates.

- `discovery_pass` requires: candidate mean polarity-invariant AUC* >= 0.65
  with paired-bootstrap 95% lower bound > 0.55; shuffled mean AUC* in
  [0.40, 0.60]; candidate-minus-shuffled mean delta > 0.10 with 95% lower
  bound > 0.05. AUC* = max(AUC(z, c), 1 - AUC(z, c)): the allocated unit
  fires on one pull direction and which binary label attaches to it is
  arbitrary, so inversion is not failure (shuffled AUC* stays ~0.5 by
  symmetry). Oracle AUC* is reported (expected ≈ 1.0 modulo toggle
  alignment) but is not part of the gate. If the gate fails, disposition is
  `discovery_negative` regardless of MSE outcomes; extra capacity cannot
  pass as discovery.

## Partitions, confirmation and disposition

| Partition | Seeds | Rows |
| --- | --- | ---: |
| Development only | 90000–90007 | unit/synthetic only |
| Tuning | 91000–91007 | 5×12×8 = 480 |
| Independent confirmation | 93000–93031 | 9×32 = 288 |
| Bootstrap RNG only | 95000 | 10000 whole-seed resamples |

All seed ranges are fresh, including unused reservations of previous studies.
Do not reopen old studies or substitute seeds. Run all 288 confirmation rows
if tuning permits: discover, oracle, window, sgd, adwin, oracle_matched,
random, shuffled, nocontext_matched. Do not stop measuring candidate
performance based on oracle outcomes or discovery diagnostics. Privileged
context provides interpretation, not a route around the full gate.

Candidate must (a) pass the discovery gate AND (b) improve P by >= 10% over
EACH of window, sgd, adwin, random, shuffled and nocontext_matched, with
paired 95% upper candidate-minus-control delta < 0, AND (c) pass every one of
14 R retention cells against each of the six controls with paired upper
delta <= max(.002, .1*control mean). All **90 learning comparisons** plus the
discovery gate must pass for `learning_positive`; otherwise
`learning_negative` (`discovery_negative` names the gate-failure case).
Non-finite required trajectories fail; missing/malformed evidence remains
incomplete. Controls cannot be dropped because they are strong or fail other
diagnostics. Oracle is separately tested against window/sgd/adwin with the
same 45 criteria (`oracle_pass`/`oracle_negative`); it cannot repair a
candidate failure. Every final disposition closes this registration with no
automatic next experiment, architecture growth, default change or agent
integration. A positive would justify only a separately authorized broader
benchmark with a grown-context agent.

## Evidence, implementation phases and refinement

Archive every policy/seed's learning metrics and update norms by fixture;
per-coordinate cue-weight trajectories, interval-scale summaries, split
counts, discovery scores/AUCs and their nulls (shuffled/random realized
splits); memory/conditioning records (pooled vs conditional use rate when
contested). Distinguish routine pooled-mean movement from conditional use:
baselines never condition. SGD has no window; windows evict without events;
ADWIN flags shrinkage. Always expose finite-seed counts and expected versus
realized random/shuffled activity.

Phases: (1) register/refine; (2) implement/test and commit all scientific
sources; (3) tune all 480/freeze manifest; (4) confirm all 288; (5) reproduce
every reached row, manifest, selection and report; (6) publish a draft
codex/** PR, monitor all nine workflows at exact HEAD, mark ready and merge
when green and reviews resolved. Use separate v3_discovery
runtime/policy/study/report/check modules plus a ninth workflow. Reuse frozen
functions without monkeypatching module globals. Preserve all earlier files
except README/PLAN/V3 status pointers.

Before observations verify direct pooled/conditional-mean parity on
hand-worked traces (including TAU = 0/always-conditional and TAU = inf/never-
conditional endpoints, alpha = 0/1 endpoints, tie-pull rule, inactive-memory
frozen, cue-logistic step parity vs a slow explicit implementation, shuffle
permutation invariance of marginals with destroyed correlation, random-split
RNG independence); causality/prefix invariance; no oracle/true-context access
in deployable arms; all menus, common objective, finite/tie selection; the
discovery gate math (AUC, null band, delta) on synthetic scores; all 90
vetoes, all 45 oracle cells, gate non-authority in the wrong direction (MSE
cannot pass discovery) and oracle non-authority; missing/invalid/non-finite
records, changed sources, uncommitted manifests and forbidden confirmation.
Snapshot all transitive local code, report/check sources, applicable protocols
and pinned requirements. No source change after observations except a
diagnosed, explicitly reported instrument defect. Registration SHA immutable.

Reproduce all 768 reached rows if eligible at rtol1e-11/atol1e-13; only
execution timing and regenerated input digests exempt. Old forgetting+burst
evidence must also reproduce unchanged, and all eight prior workflows remain
intact. Intervals are descriptive; finite menus, small synthetic fixtures and
observed zeros cannot establish population guarantees or general
neural-memory utility. No new dependencies needed.
