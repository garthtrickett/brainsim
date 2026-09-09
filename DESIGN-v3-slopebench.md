# Registered V3 slope broader-benchmark experiment

Protocol `v3-slopebench-20260909-v1`. The operator authorized the broader
benchmark the slope registration promised on a positive: the frozen OLS-128
trend regime against new ramp shapes it was never tuned on. Steeper, shallower
and noisier ramps ask whether the mechanism generalizes or only fits the one
trained linspace(1,-1) ramp. Granted enriched boundaries throughout; no new
estimator, no detector arm, equal small tuning budgets, fresh confirmation,
and a 75-comparison gate on adapted cells. Register before study
observations. Preserve all earlier protocols, scientific sources, evidence
and fourteen CI workflows. No dependency or agent/default change.

## Hypothesis and why this follows slope

The slope study closed the first full V3 positive with aoline fitted to one
exact ramp: linspace(1,-1) over ~2000 steps at σ=0.05. Its tuning objectives
were flat across all twelve estimators, which means the selection carries no
information about robustness — and a mechanism that only fits its training
ramp is a narrower result than the gate suggests. This benchmark replays the
frozen policy against ramps outside its experience — steeper, shallower,
noisier — with abrupt-change fixtures riding along unchanged so the primary
metric stays comparable.

Falsifier, stated in advance: if the frozen trend regime fails any new ramp
while the fast trackers track it, trend following does not generalize beyond
its tuned shape — and the slope positive shrinks to a single-ramp result. If
all ramps pass with everything preserved, the mechanism earns the broader
claim. Either outcome closes this registration with no automatic follow-up.

## Fixtures: three new ramps

Reuse core and mixed EXACTLY (`v3_persistent.fixture`, same process, fresh
seeds) so primary post-switch MSE keeps its definition. Add three
single-coordinate fixtures on the same 6000-step, burn-1000 process with the
same first/second schedule draws (uniform 1800–2200 and 3800–4200):

- **steep:** target linspace(1,-1) over [first,first+500), flat -1 after;
  σ=0.05. Events (first,'drift_start'), (first+500,'drift_end').
- **shallow:** target linspace(0.5,-0.5) over [first,first+4000), flat after;
  σ=0.05. Same event kinds.
- **noisy:** target linspace(1,-1) over [first,second) (the trained shape);
  σ=0.5, ten times the training noise. Same event kinds.

Nine coordinates total (4+2+1+1+1). The trained drift fixture is NOT
re-run: its result stands frozen in the slope study, and re-running it here
would double-count one ramp as two.

## Learner semantics

The learner is the frozen slope policy at its selected configuration
(OLS-128, K_fast=4, W_fast=32, ADWIN2 delta=.1, clock 1, H=32) with the
drift_start-gated trend regime, unchanged. Controls are the unchanged y-only
trio (re-searched), the enriched no-fallback ablation, and enriched random
fallback (frozen p recomputed on the new fixture set's tuning requests).
Schedules are granted true target times plus ramp boundaries on the new
fixtures; target/drift/random provenance enforced per request as before.
Window, SGD and ADWIN receive no schedule of any kind.

## ADWIN baseline and scope

Unchanged from the forgetting study, including the bounded-input disclaimer
and the pre-data slow-implementation agreement.

## Fixed finite menus, objective, and adapted cells

Three searched families, each **12 configurations × 8 paired seeds × all five
fixtures** (288 tuning rows): window, SGD and ADWIN2 on their unchanged
menus. The candidate configuration is frozen from the slope manifest; all
matched arms run in confirmation only.

Metrics reuse `learning_metrics` on core/mixed unchanged. Each new ramp
fixture reports excess_mse (post-burn), post_mse None (no target events),
stable_mse, adaptation_latency None, update norms, plus a custom ramp_mse:
mean squared error over [start,end) pre-update predictions. SPECS keeps the
15-cell shape of every predecessor: primary (same 4 switching cells);
core quiet/noisy excess and quiet/noisy switching post (4); mixed post/stable
per coordinate (4); steep/shallow/noisy excess plus steep/shallow/noisy ramp
windows (6). Select minimum seed-mean (P+mean(R))/2 for every searched
family.

The advancement gate is the slope 75-structure verbatim: primary ≥10% over
window/SGD/ADWIN/random with preservation against no-fallback, every
retention bound, strict improvement on the 8 stable/noise cells against
no-fallback with the both-perfect repair — where "stable/noise" now reads
the adapted cell set (core quiet/noisy excess, noise-free stationary
excesses, transition windows, mixed stable, and the three ramp excess cells
against no-fallback). All **75 comparisons** must pass for
learning_positive; otherwise learning_negative. Non-finite required
trajectories fail; missing/malformed evidence remains incomplete. Controls
cannot be dropped. Every final disposition closes this registration with no
automatic next experiment, mechanism change, default change or agent
integration. A positive broadens the slope claim to ramp shapes; it still
authorizes no integration.

Random-request probability is frozen from the SELECTED slope-candidate tuning
requests on the new fixture set, counted evaluator-side: pool N over
S=6000*9*8, p=f/(1-16*f), finite 0<=p<=1, opportunities from t0.

A configuration with any non-finite tuning trajectory/metric is ineligible,
with its failure retained. Finish all 288 rows. If any family lacks a
complete finite configuration, close tuning_inconclusive and forbid
confirmation. Otherwise freeze all selected configurations, random p, fixture
definitions, RNG domains, source identity and complete tuning evidence in a
committed manifest BEFORE independent confirmation.

## Partitions, confirmation and disposition

| Partition | Seeds | Rows |
| --- | --- | --- |
| Development only | 150000–150007 | unit/synthetic only |
| Tuning | 151000–151007 | 3×12×8 = 288 |
| Independent confirmation | 153000–153031 | 6×32 = 192 |
| Bootstrap RNG only | 155000 | 10000 whole-seed resamples |

All seed ranges and the 156000+ RNG domains are fresh. New-fixture RNG uses
SeedSequence([study_seed, 156000+fixture_ordinal, domain]) with ordinals
core=0, mixed=1, steep=2, shallow=3, noisy=4, disjoint from every prior
study. Do not reopen old studies or substitute seeds. Run all 192
confirmation rows if tuning permits: slope, window, sgd, adwin,
oracle_nofallback, random_slope. Do not stop measuring any arm based on
another arm's outcome.

Report regime shares per fixture (fast/slope/ADWIN, new ramps separately),
estimator slope magnitudes on each ramp against its true slope, and realized
versus expected random activity. A failed ramp limits the mechanism to the
shapes that pass; name them exactly.

## Evidence, implementation phases and refinement

Archive every policy/seed's learning metrics and actual update norms by
fixture; per-coordinate request indices with provenance, event hit/latency,
estimator states and regime at each prediction, and realized versus expected
random activity. Always expose finite-seed counts and expected versus
realized schedule activity.

Phases: (1) register/refine; (2) implement/test and commit all scientific
sources; (3) tune all 288/freeze manifest; (4) confirm all 192; (5) reproduce
every reached row, manifest, selection and report; (6) publish a draft
codex/** PR, monitor all fifteen workflows at exact HEAD, mark ready and
merge when green and reviews resolved. Use separate v3_slopebench
runtime/policy/study/report/check modules plus a fifteenth workflow. Reuse
frozen slope/retention/forgetting/ADWIN functions without monkeypatching
module globals. Preserve all earlier files except README/PLAN/V3 status
pointers.

Before observations verify new-fixture parity (event indices, ramp values,
noise levels, burn/metrics boundaries against hand-computed traces);
custom ramp-window metrics against direct computation; frozen candidate
parity against the slope oracle arm at matched configuration; all menus,
common objective, finite/tie selection; all 75 vetoes on the adapted cells;
missing/invalid/non-finite records, changed sources, uncommitted manifests
and forbidden confirmation. Snapshot all transitive local code, report/check
sources, applicable protocols and pinned requirements. No source change after
observations except a diagnosed, explicitly reported instrument defect.
Registration SHA is immutable.

Reproduce all reached rows if eligible at rtol1e-11/atol1e-13; only execution
timing and regenerated input digests are exempt. All fourteen prior studies'
evidence must also reproduce unchanged, and all fourteen prior workflows
remain intact. Statistical intervals are descriptive; finite menus, synthetic
fixtures and granted schedules cannot establish population guarantees or
general neural-memory utility. No new dependencies are needed.
