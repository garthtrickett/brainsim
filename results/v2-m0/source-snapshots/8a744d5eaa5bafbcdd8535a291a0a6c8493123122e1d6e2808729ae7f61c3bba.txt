# Registered V2 M0-motor experiment: 1-of-N without aggregates

Protocol `v2-m0-motor-20260910-v1`. The operator authorized the smallest
slice that can falsify the largest v2 claim: V2.md bets that 1-of-N motor
selection failed in v1 *only* because per-tick winners smeared credit across
the 30-tick vote aggregate (`19_local_alternatives.py`: 0.319/0.158 at 4/8
classes), and that continuous time — where the per-tick winner and the
decision are the same event — redeems it. This experiment removes the
aggregate and re-tests, in a throwaway prototype harness that is explicitly
not the v2 fork. Register before study observations. Preserve all earlier
protocols, scientific sources, evidence and twenty-one CI workflows. No
dependency change; v1 sources untouched (the harness imports them).

## Hypothesis and what rides on it

If per-tick 1-of-N motor selection matches the shipped global-kWTA baseline
on nway-4/8, the motor-sparsity hypothesis survives and event-driven
computing keeps its conditional place in the v2 plan. If it fails again at
the same level, the hypothesis dies **and event-driven stays conditional
forever** — V2.md's own words — reducing the founding changes to local
pools, parallel loops, and continuous time. Either outcome closes this
registration; only the first authorizes further motor-sparsity work.

Falsifier, stated in advance: per-tick 1-of-N tail accuracy within the
trial-aggregated 1-of-N band (paired interval includes zero or favors the
aggregate) on nway-4 with 6 seeds. A pass requires beating the aggregate
with the paired 95% interval strictly above zero AND matching the shipped
baseline within its interval — beating a broken control is not the claim;
matching the shipped agent is.

## The prototype (throwaway by design)

New module `v2_m0.py`, importing the frozen agent kernels where they apply
and duplicating nothing silently. Per-tick loop, no vote array, no
`decide()` aggregate: each tick presents the stimulus, steps all units once,
reads the single motor winner above threshold (or no action when silent),
and applies the unchanged local learning rule with eligibility consumed on
reward arrival (Q2's leading candidate for regimes where rewards delimit
episodes; here every trial ends rewarded-or-not, so this matches trial
consumption by construction).

**Task adapter** (V2.md's own design): the nway-4/8 trial task ports by
presenting each class pattern for a fixed 30-tick window — the same exposure
the trial runner gives. All three arms are scored in per-tick units: the
candidate scores its per-tick winner (a silent tick scores 0, ties toward
the null); the shipped ceiling scores per-tick argmax over motor membrane
potentials (never silent); the aggregate control broadcasts its one trial
action across all 30 ticks. Shared units, pre-stated asymmetry: silence can
only hurt the candidate, so the falsifier's match requirement is
conservative by construction. Cross-study number comparison with v1 tail
accuracies is forbidden; only within-study paired contrasts count.

**Deliberately out of scope:** replay window L sweep, tau sweep, eligibility
consumption variants beyond consume-on-reward, lock/volatile/tmaze tasks,
parallel loops, batching, and any v2 substrate beyond this harness. Those
belong to full M0, which starts only if this slice passes. Q2/Q3/Q5 stay
open and untouched.

## Partitions and disposition

| Partition | Seeds | Runs |
| --- | --- | --- |
| Development only | 300–305 | unit/synthetic only |
| Independent confirmation | 310–315 | 3 arms × 6 seeds (nway-4, nway-8) |

Fresh seeds throughout; the 19 script's 0–2 seeds are not reused. Arms:
per-tick 1-of-N (candidate), trial-aggregated 1-of-N (the 19 control,
re-implemented against current sources), shipped global-kWTA (ceiling
reference). 3000 trials per run at 30 ticks, matching the 19 probe's scale.
Do not substitute seeds. Missing/malformed evidence remains incomplete.
Pass = candidate beats aggregate (paired interval above zero) AND matches
shipped (paired interval covers zero against the ceiling reference);
anything else closes negative with no automatic follow-up. No default
change, no integration, no fork: on a pass, full M0 planning begins by new
registration; on a fail, the motor-sparsity line closes permanently.

## Evidence and phases

Archive per-seed per-trial accuracy traces, per-tick winner rates (the
sparsity number itself: 73.8% is what must fall), and eligibility norms.
Phases: (1) register; (2) implement prototype + checks and commit; (3) run
all confirmation rows; (4) reproduce every row and report; (5) publish a
draft PR from the implementation branch, monitor all twenty-two workflows
at exact HEAD, mark ready and merge when green and reviews resolved. New
files: `v2_m0.py`, `check_v2_m0.py`, the registration, this results file
and `results/v2-m0/`, plus a twenty-second workflow. v1 sources frozen;
earlier evidence, protocols, workflows, dependencies and defaults unchanged.

Before observations verify the harness (tick loop causality, no vote-array
residue, threshold crossing semantics, silent-tick scoring), the re-implemented
aggregate control against the archived 19 numbers within seed noise, paired-seed
discipline, invalid/non-finite records, changed sources, uncommitted manifests
and forbidden confirmation. Snapshot all transitive local code and pinned
requirements. No source change after observations except a diagnosed,
explicitly reported instrument defect. Registration SHA is immutable.

Reproduce all reached rows at rtol1e-11/atol1e-13; only execution timing is
exempt. Small synthetic tasks and six seeds cannot establish population
guarantees, sparsity in general, or superiority over deep learning. No new
dependencies are needed.
