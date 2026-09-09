# Registered V3 drift-timing tolerance experiment

Protocol `v3-drifttol-20260909-v1`. The operator authorized the unpriced half
of the timing question: perturb granted drift boundaries and find where the
slope win dies. Abrupt timing was priced at ±2–8 steps with the detector line
closed; drift boundaries were never perturbed, and slopetime's observed-alarm
failure (false alarms, not precision) says nothing about how precisely the
slope regime must be placed. Frozen OLS-128 slope candidate, same 45-cell
instrument per level as the tolerance study, no advancement arm — pure
measurement with pre-stated reading rules. Register before study
observations. Preserve all earlier protocols, scientific sources, evidence
and sixteen CI workflows. No dependency or agent/default change.

## Hypothesis and why this follows slopeguard

The slope win survives only inside a granted drift regime, and nobody knows
how much boundary error it tolerates. Ramps run ~2000 steps against a 128-fit
window and a 32-step fast fallback: misplacing onset by a hundred steps
should cost little, misplacing it past the kink should cost exactly the
kink-smearing the benchmark measured, and dropping a boundary should reduce
to the dual policy. This experiment maps that curve. Its outcome gates
whether any drift-selective alarm is worth building: wide tolerance keeps a
deployable slope path open, narrow tolerance closes it with a number.

Falsifier-analogue, stated in advance (measurement, not advancement): the
tolerance point is the largest boundary jitter passing all 45 cells. Win
alive at/above ±512 with misses tolerated: a drift-selective alarm experiment
is authorized, by a NEW registration, never by this one. Win dead within
±128: the deployable slope line closes alongside the abrupt one. In between:
report the curve, no automatic follow-up. No outcome authorizes integration.

## Learner semantics

The learner is the frozen slope policy at its selected configuration
(OLS-128, K_fast=4, W_fast=32, ADWIN2 delta=.1, clock 1, H=32): drift_start
enters the trend regime, drift_end or abrupt-target requests exit it. Only
the drift boundaries move across arms; abrupt-target times stay granted and
exact in every arm, isolating boundary precision from the priced abrupt
tolerance.

- **reference:** true drift boundaries (the slope-study schedule exactly).
  Diagnostic baseline.
- **jitter_k, k in [32,256,1024]:** each drift boundary shifted by an
  independent uniform integer draw in [-k,+k] per coordinate. Diagnostic.
  ±32 spans one fast window, ±256 an eighth of a ramp, ±1024 half a ramp.
- **drop_50:** each drift boundary kept independently with probability 0.5.
  Diagnostic; a dropped onset reduces to the dual policy, a dropped end
  extends trend onto the flat.

**window/sgd/adwin:** the unchanged y-only controls; they receive no schedule
of any kind.

Boundary draws use PCG64 `SeedSequence([study_seed, 176000+level*100+
fixture_ordinal, coordinate])` with level order jitter_32=0, jitter_256=1,
jitter_1024=2, drop_50=3, generated per coordinate to preserve prefix/width
invariance, fixed fixture order core, noise_jump, drift, exactly_quiet,
mixed. Jittered times clip to [0,5999]; ordering is then enforced
(end ≤ start resolves to end = start+1, a degenerate but valid ramp) —
pre-stated here because ±1024 jitter on a ~2000-step ramp can invert a
boundary pair. Collisions with abrupt-target times merge by set semantics;
drift fixtures carry the only drift boundaries, so other fixtures' schedules
are untouched by construction. No arm sees target values, noise labels, ramp
slopes, or future samples.

## ADWIN baseline and scope

Unchanged from the forgetting study, including the bounded-input disclaimer
and the pre-data slow-implementation agreement.

## Fixed finite menus and objective

Three searched families, each **12 configurations × 8 paired seeds × all five
fixtures** (288 tuning rows): window, SGD and ADWIN2 on their unchanged
menus. The candidate configuration is frozen from the slope manifest; all
schedule variants run in confirmation only. Order breaks exact objective ties
(inherited grids only; nothing new is searched).

Reuse the EXACT drift-study fixtures/metrics (core, noise_jump, drift,
exactly_quiet, mixed) and selection objective: P is the equal mean post-200
MSE over core quiet/noisy switching and both mixed coordinates; R comprises
the same 14 cells (core quiet/noisy excess and switching post; three
scalar-extra excess errors; noise-increase/noise-decrease/drift windows;
mixed post/stable per coordinate). Select minimum seed-mean (P+mean(R))/2 for
every searched family.

A configuration with any non-finite tuning trajectory/metric is ineligible,
with its failure retained. Finish all 288 rows. If any family lacks a
complete finite configuration, close tuning_inconclusive and forbid
confirmation. Otherwise freeze all selected configurations, schedule
definitions, RNG domains, source identity and complete tuning evidence in a
committed manifest BEFORE independent confirmation.

## Partitions, confirmation and disposition

| Partition | Seeds | Rows |
| --- | --- | --- |
| Development only | 170000–170007 | unit/synthetic only |
| Tuning | 171000–171007 | 3×12×8 = 288 |
| Independent confirmation | 173000–173031 | 8×32 = 256 |
| Bootstrap RNG only | 175000 | 10000 whole-seed resamples |

All seed ranges and the 176000+ RNG domains are fresh, including unused
reservations of previous studies. Do not reopen old studies or substitute
seeds. Run all 256 confirmation rows if tuning permits: window, sgd, adwin,
reference, jitter_32/256/1024, drop_50, oracle_nofallback — the fast base on
the enriched schedule, carried as the diagnostic floor showing what losing
the regime entirely costs. Do not stop measuring any arm based on another
arm's outcome.

The per-level 45-comparison instrument (primary ≥10% improvement, all 14
retention bounds, each against window/SGD/ADWIN) reports pass/fail per level;
the tolerance point is the largest passing jitter. This disposition
authorizes nothing under any outcome. Every final disposition closes this
registration with no automatic next experiment, mechanism change, default
change or agent integration.

Report regime use rates (fast/slope/ADWIN share per condition, drift
fixtures separately), realized boundary displacements per level, and the
abrupt-only floor. A failed level limits the schedule it tested, not trend
tracking in general.

## Evidence, implementation phases and refinement

Archive every policy/seed's learning metrics and actual update norms by
fixture; per-coordinate request indices with granted/perturbed provenance,
realized displacements, event hit/latency against true boundaries, estimator
states and regime at each prediction. Always expose finite-seed counts and
expected versus realized schedule activity.

Phases: (1) register/refine; (2) implement/test and commit all scientific
sources; (3) tune all 288/freeze manifest; (4) confirm all 256; (5) reproduce
every reached row, manifest, selection and report; (6) publish a draft
codex/** PR, monitor all seventeen workflows at exact HEAD, mark ready and
merge when green and reviews resolved. Use separate v3_drifttol
runtime/policy/study/report/check modules plus a seventeenth workflow. Reuse
frozen slope/retention/forgetting/ADWIN functions without monkeypatching
module globals. Preserve all earlier files except README/PLAN/V3 status
pointers.

Before observations verify boundary-perturbation parity on hand-built event
sequences (uniform bounds per level, clipping, order enforcement, collision
merging, drop RNG independence and domain separation, prefix and coordinate
causality, no true-index access beyond granted times, no schedule access in
window/sgd/adwin); frozen candidate parity against the slope oracle arm at
matched configuration; all menus, common objective, finite/tie selection;
the per-level instrument and tolerance-point logic; missing/invalid/
non-finite records, changed sources, uncommitted manifests and forbidden
confirmation. Snapshot all transitive local code, report/check sources,
applicable protocols and pinned requirements. No source change after
observations except a diagnosed, explicitly reported instrument defect.
Registration SHA is immutable.

Reproduce all reached rows if eligible at rtol1e-11/atol1e-13; only execution
timing and regenerated input digests are exempt. All sixteen prior studies'
evidence must also reproduce unchanged, and all sixteen prior workflows
remain intact. Statistical intervals are descriptive; finite menus, small
synthetic fixtures and granted schedules cannot establish population
guarantees or general neural-memory utility. No new dependencies are needed.
