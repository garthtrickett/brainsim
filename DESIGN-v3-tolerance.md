# Registered V3 timing-tolerance experiment

Protocol `v3-tolerance-20260909-v1`. The operator authorized a tolerance
measurement on the granted retention schedule plus one deployable
ADWIN-schedule arm, with true abrupt-target times as the unperturbed
reference, equal small tuning budgets for the y-only controls, fresh
confirmation, and separate measurement/advancement dispositions. Register
before study observations. Preserve all earlier protocols, scientific sources,
evidence and ten CI workflows. No dependency or agent/default change.

## Hypothesis and why this follows retention

The retention study held the adaptation/stability tradeoff under privilege
(primary 0.082702 against every control, every stable/noise cell against
ADWIN passed) and closed learning-negative on drift. Its headline win exists
only on granted true change times, yet the win is concentrated: the selected
config spends ~99% of coordinate-updates in the ADWIN state (core 0.0064,
mixed 0.0128, zero elsewhere), and that ~1% carries the entire primary gap
(0.082702 vs 0.197654 for ADWIN). A win concentrated in a handful of
well-placed steps should be destroyed fast by timing error — but nobody knows
how fast, and building a detector to find out repeats the seven closed
attempts. This experiment prices the privilege first: perturb the granted
schedule, find where the win dies, and test the real operating point alongside
the curve.

The drift-ontology follow-up (granting drift-boundary times to the frozen
candidate) stays queued behind this one: it inherits the same privilege
overhang, and its design depends on nothing measured here being disturbed.
Drift is isolated, not rotting.

## Anchor: ADWIN's measured alarm-error profile

The perturbation menu is derived from frozen evidence, not swept blind. On the
retention confirmation seeds (32 seeds,
`results/v3-retention/confirmation.json`, ADWIN delta=.1/clock=1), shrink
flags against true abrupt-target events read:

| Cell | Hits | Mean latency |
| --- | ---: | ---: |
| core switch_quiet | 64/64 | 1.55 |
| core switch_noisy | 64/64 | 5.34 |
| mixed increase_first | 64/64 | 3.22 |
| mixed decrease_first | 64/64 | 3.36 |

Mean false-shrink counts per 6000-step run: core quiet 0.00, core noisy 2.22,
noise_jump 5.78, drift 73.81, exactly_quiet 0.00. Miss rate on abrupt events:
0/256. A realistic detector errs by single-digit delays with a handful of
false alarms per noisy run. The menu below spans inside that band (±2),
through its top edge (±8), bisects the decision-ambiguous band (±16), and
reaches well beyond it (±32, one full fast regime; ±128). Drop fractions {0.1, 0.5} test a slightly-worse and a much-worse
miss profile against the observed zero; add rates {0.0005 (~3/run, at the
observed false rate), 0.002 (~12/run, several times observed)} do the same
for false alarms.

## The deployable arm and its control status

Alongside the synthetic perturbation families, the menu carries the real
thing: the frozen candidate (retention delta=.1, H=32) scheduled by ADWIN's
actual alarm times. ADWIN already runs as a control, its alarms are computed
from observable data only, and no new mechanism is needed. That arm is not
diagnostic. Its schedule derives from observables alone, so it is deployable
and carries the full advancement gate, disposed separately from the
measurement.

On leakage: there is none privileged. The alarm-generating ADWIN run is
standalone on y; the candidate's fast-window state never feeds back into it,
unlike the failed learning-coupled persistent cells. The alarm source and the
slow state share delta and config, but that coupling is behavioral, not
informational — the schedule tells the slow state nothing it does not already
compute; it only switches regimes. The alarm-generating config is the
concurrently SELECTED ADWIN control config (best-foot-forward ADWIN): a rule
stated here, not a choice made later. If selection lands elsewhere than
delta=.1/clock=1, the alarms come from wherever it lands.

Pre-stated expectation, neutrally: ADWIN alarms ~74 times per drift run, so
this arm will sit in the fast regime constantly on drift fixtures. Whether
that helps (faster re-aiming on the ramp) or hurts (stale fast means) is
measured, not assumed.

## Learner semantics

Reuse the EXACT y/target/events generation of the forgetting study (five
fixtures `core, noise_jump, drift, exactly_quiet, mixed`, nine coordinates,
6000 observations, burn 1000, same `v3_persistent.fixture` process). Seeds are
fresh so y bytes differ; the process is unchanged. There is no cue and no
hidden context. All arms see history of y alone.

The learner is the frozen retention dual-state policy at its selected
configuration (delta=.1, H=32, K_fast=4, W_fast=32): at most 32 observations
after a request it predicts from the fast mean, otherwise from the ADWIN
prior-window mean. Only the request schedule varies across arms:

- **reference:** true abrupt-target times (the retention oracle schedule).
  Diagnostic; the unperturbed baseline every perturbed arm is read against.
- **jitter_k, k in [2,8,16,32,128]:** each true trigger shifted by an independent
  uniform integer draw in [-k,+k] per coordinate. Diagnostic.
- **drop_q, q in [0.1,0.5]:** each true trigger kept independently with
  probability 1-q. Diagnostic.
- **add_r, r in [0.0005,0.002]:** per-step Bernoulli(r) false triggers,
  independent of everything, no suppression. Diagnostic.
- **adwin_schedule:** request at every shrink flag of the ADWIN control run at
  its selected configuration on the same observations. Deployable; the only
  arm that can advance.

**window/sgd/adwin:** the unchanged y-only controls; they receive no schedule
of any kind.

Jitter draws use PCG64 `SeedSequence([study_seed, 116000+level*100+fixture_ordinal,
coordinate])` with level order jitter_2=0, jitter_8=1, jitter_16=2,
jitter_32=3, jitter_128=4, drop_10=5, drop_50=6, add_0005=7, add_0020=8, generated per
coordinate to preserve prefix/width invariance, using the fixed fixture order
core, noise_jump, drift, exactly_quiet, mixed. Jittered times are clipped to
[0,5999] (never binds in practice: true events sit ≥1800, k ≤ 128) and
collisions merge by set semantics. Dropped and added triggers are
unsuppressed, matching the oracle passthrough; collisions are allowed and
pre-stated here, with the drop/add arms carrying the decomposition. No arm
sees target values, noise labels, drift slopes, or future samples.

## ADWIN baseline and scope

The paper-based ADWIN2 implementation, Eq.(3.1) threshold, bucket compression
and bounded-input disclaimer are unchanged from the forgetting study. A
separate slow implementation using explicit bucket contents must agree before
study data. Established prior art, not a new proposed detector.

## Fixed finite menus and objective

Three searched families, each **12 configurations × 8 paired seeds × all five
fixtures** (288 tuning rows): window, SGD and ADWIN2 on their unchanged menus.
The candidate configuration is frozen from the retention manifest
(delta=.1, H=32); the perturbed and ADWIN-schedule arms receive no search —
they are schedule variants of a settled mechanism, run in confirmation only.
Order below breaks exact objective ties (inherited grids only; nothing new is
searched).

Reuse the EXACT nine-coordinate fixtures/metrics and selection objective of
the burst/forgetting/discovery/retention registrations: P is the equal mean
post-200 MSE over core quiet/noisy switching and both mixed coordinates; R
comprises the same 14 cells. Select minimum seed-mean (P+mean(R))/2 for every
searched family.

A configuration with any non-finite tuning trajectory/metric is ineligible,
with its failure retained. Finish all 288 rows. If any family lacks a
complete finite configuration, close tuning_inconclusive and forbid
confirmation. Otherwise freeze all selected configurations, schedule
definitions, RNG domains, source identity and complete tuning evidence in a
committed manifest BEFORE independent confirmation.

## Two dispositions, cleanly separated

**Measurement (diagnostic families).** The reference, jitter, drop and add
arms are evaluated with the same 45-comparison instrument used for the
forgetting oracle gate: primary ≥10% improvement and all 14 retention bounds
against EACH of window, SGD and ADWIN. The reported object per family is
pass/fail per level; the tolerance point is the largest jitter k passing all
45, with intervals. This disposition authorizes nothing, under any outcome.
Pre-stated reading rules, anchored to the profile above:

- win dies within ±8 (the top edge of observed detector delay): the line
  closes with a number — no realistic detector delivers it;
- win survives at/above ±32 with miss/add at observed rates: a detector
  experiment is authorized, by a NEW registration, never by this one;
- in between: report the curve, no automatic follow-up.

**Advancement (ADWIN-schedule arm).** The deployable arm faces the same 45
comparisons against window, SGD and ADWIN. All 45 must pass for
learning_positive; otherwise learning_negative. A positive reports the first
deployable composition win in the chain and justifies only a separately
authorized broader benchmark with the ADWIN-driven schedule — never agent
integration. A negative closes alongside whatever the curve says; neither
disposition contaminates the other.

There is no falsifier for the curve itself; the pre-stated reading rules play
that role. The only pass/fail in this registration is the ADWIN-schedule
gate.

## Partitions, confirmation and disposition

| Partition | Seeds | Rows |
| --- | --- | ---: |
| Development only | 110000–110007 | unit/synthetic only |
| Tuning | 111000–111007 | 3×12×8 = 288 |
| Independent confirmation | 113000–113031 | 14×32 = 448 |
| Bootstrap RNG only | 115000 | 10000 whole-seed resamples |

All seed ranges and the 116000+ RNG domains are fresh, including unused
reservations of previous studies. Do not reopen old studies or substitute
seeds. Run all 448 confirmation rows if tuning permits: window, sgd, adwin,
reference, jitter_2/8/16/32/128, drop_10/50, add_0005/0020, adwin_schedule.
There is no detector calibration in this study; the anchor numbers above are
frozen provenance, not re-measured evidence. Do not stop measuring any arm
based on another arm's outcome.

Report regime use rates (fast vs ADWIN prediction share per condition) for
every scheduled arm, request-count summaries per schedule family, and realized
versus expected jitter/drop/add activity. Distinguish granted true times from
perturbed times from observed alarms in every record: the three schedule
provenances must never mix. A failed result limits this finite schedule menu,
not all forms of timing robustness.

## Evidence, implementation phases and refinement

Archive every policy/seed's learning metrics and actual update norms by
fixture; per-coordinate request indices with schedule provenance
(true/jittered/dropped/added/observed), event hit/latency against true target
changes, fast/ADWIN widths and regime at each prediction, jitter draws,
drop/add realizations, and alarm provenance records tying each observed
request to its generating control run. Always expose finite-seed counts and
expected versus realized schedule activity.

Phases: (1) register/refine; (2) implement/test and commit all scientific
sources; (3) tune all 288/freeze manifest; (4) confirm all 448; (5) reproduce
every reached row, manifest, selection and report; (6) publish a draft
codex/** PR, monitor all eleven workflows at exact HEAD, mark ready and merge
when green and reviews resolved. Use separate v3_tolerance runtime/policy/
study/report/check modules plus an eleventh workflow. Reuse frozen
retention/forgetting/ADWIN functions without monkeypatching module globals.
Preserve all earlier files except README/PLAN/V3 status pointers.

Before observations verify schedule-construction parity on hand-worked
triggers (uniform bounds per level, clipping, collision merging, drop/add
RNG independence and domain separation, prefix and coordinate causality,
alarm provenance from the selected control config, no true-index access in
the add arms, no schedule access in window/sgd/adwin); frozen candidate
parity against the retention oracle arm at matched configuration; all menus,
common objective, finite/tie selection; all 45 vetoes for the advancement
arm and the per-level measurement instrument; missing/invalid/non-finite
records, changed sources, uncommitted manifests and forbidden confirmation.
Snapshot all transitive local code, report/check sources, applicable
protocols and pinned requirements. No source change after observations except
a diagnosed, explicitly reported instrument defect. Registration SHA is
immutable.

Reproduce all reached rows if eligible at rtol1e-11/atol1e-13; only execution
timing and regenerated input digests are exempt. Old retention+discovery+
forgetting+burst evidence must also reproduce unchanged, and all ten prior
workflows remain intact. Statistical intervals are descriptive; finite menus,
small synthetic fixtures and granted schedules cannot establish population
guarantees or general neural-memory utility. No new dependencies are needed.
