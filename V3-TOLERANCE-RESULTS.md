# Timing tolerance closes the detector line with a number

The registered tolerance point is **None**: every jitter level fails at least
one of its 45 cells, including ±2 (40/45). The deployable ADWIN-schedule arm
closes **learning_negative** at 42/45: its primary win holds on all three
controls (0.104354 vs 0.116510 SGD, 0.125197 W=8, 0.194754 ADWIN2) but it
fails three retention cells. Neither disposition authorizes a detector, and
the pre-stated reading rules say to close the line rather than build one.

The None needs an immediate qualification, because part of it is an instrument
defect, not a result — see below. The schedule-attributable finding, labeled
as the post-hoc analysis it is: the primary win survives ±2 steps and is dead
by ±8 (0.089387 passing vs 0.123764 worse than SGD). Tolerance sits inside
the realistic band's top edge, far tighter than ADWIN's own error profile.
That is the number the detector line closes with.

All **288 tuning and 448 confirmation rows** were completed and finite. No new
default, broader benchmark, detector experiment or agent integration is
activated.

## What was implemented

The [registration](DESIGN-v3-tolerance.md) freezes the retention candidate
(delta=.1, H=32) and varies only its request schedule: true abrupt-target
times (reference), uniform-jitter families ±{2,8,16,32,128}, drop fractions
{0.1,0.5}, add rates {0.0005,0.002}, and the deployable arm scheduled by
ADWIN's actual alarm times at the concurrently selected control config
(delta=.1, clock=1). The y-only window/SGD/ADWIN controls were re-searched on
fresh seeds. Jitter draws are per-coordinate uniform with fresh RNG domains;
times clip to [0,5999], collisions merge, drops/adds are unsuppressed, and
every record carries schedule provenance that never mixes.

The registration was amended once before tuning for the reviewed +16 level
and once for the registration merge hash; doc bytes are unchanged since the
merge. One instrument defect was fixed pre-confirmation (provenance label),
which required regenerating the not-yet-frozen evidence under the final code;
scientific row content is unaffected. Details below.

## Equal-budget finite tuning

Three families, **12 configurations × 8 paired seeds × all five fixtures**
(288 rows), same objective as every predecessor. The candidate configuration
is frozen from the retention manifest; all schedule variants run in
confirmation only.

| Policy | Selected setting |
| --- | --- |
| Fixed window | W=8 |
| SGD | lr=.128 |
| ADWIN2 | delta=.1, clock=1 |

The control trio selected identically for the fifth consecutive study
(forgetting, discovery, retention, tolerance). The y-only instrument is not
drifting under re-selection; that stability is evidence, whichever way any
single study lands.

## The tolerance curve

Primary post-switch MSE by schedule arm (32 fresh confirmation seeds, lower
is better; intervals are paired-bootstrap 95% on the mean):

| Arm | Primary MSE | 95% interval |
| --- | ---: | --- |
| reference (true times) | 0.081348 | [0.078037, 0.084729] |
| jitter_2 | 0.089387 | [0.085791, 0.093089] |
| adwin_schedule (observed alarms) | 0.104354 | [0.101251, 0.107430] |
| SGD control | 0.116510 | [0.113795, 0.119377] |
| jitter_8 | 0.123764 | [0.118789, 0.128845] |
| Fixed window W=8 | 0.125197 | [0.121986, 0.128667] |
| drop_50 | 0.134296 | [0.126603, 0.141968] |
| jitter_16 | 0.159616 | [0.152551, 0.166278] |
| jitter_32 | 0.172438 | [0.165924, 0.178979] |
| jitter_128 | 0.193027 | [0.187885, 0.198220] |
| ADWIN control | 0.194754 | [0.190124, 0.199454] |

Degradation is monotone in jitter: ±2 costs ~10% of the primary gap, ±8
crosses SGD (0.123764 vs 0.116510, paired interval entirely positive), and
±128 converges to the ADWIN control itself (0.193027 vs 0.194754) — a fully
mistimed fast window contributes nothing, and the policy *is* its slow
state. Drop_10 mirrors ±2 (primary intact); drop_50 kills it. Both add arms
are catastrophic (25–29/45): unsuppressed false alarms at 0.0005–0.002 per
step destroy adaptation and stability alike.

## The instrument defect, stated as mine

The registered tolerance point counts all 45 cells per level, but 4 of them —
the drift cells vs SGD and W=8 — are schedule-invariant: jitter and drop arms
never touch drift fixtures (no target events there), so their drift values
are bit-identical to reference (0.003142/0.007698 at every level). An all-45
tolerance was unpassable before the first row ran, and "None" on that
definition carries no information about timing. The 45-cell gate, borrowed
from the forgetting-oracle precedent, was the wrong measuring device for a
schedule perturbation, and the registration's own worry about unseen control
problems is where this should have been caught — at the draft, not at the
report.

What survives that correction, labeled post-hoc: excluding the 4 invariant
drift cells, ±2 fails one further cell (`window/switch_quiet` 0.077717 vs
0.063926) with primary intact, and ±8 fails primary outright. The
schedule-attributable tolerance is therefore inside (±2, ±8] — within the
realistic band's top edge, far below what ADWIN itself delivers (mean alarm
latencies to 5.34 with tails beyond, plus false shrinks every noisy run).
Under the pre-stated reading rules, that says close the detector line with
this number rather than build detector number eight.

## The deployable arm corroborates from the other side

ADWIN-schedule primary beats every control, yet the arm fails exactly where a
too-loose schedule should fail: `adwin/noise_jump` (0.004367 vs 0.001038),
`adwin/noise-increase` (0.054374 vs 0.002520), and `sgd/switch_noisy`
(0.154381 vs 0.146897). False alarms on noise changes throw the fast window
open on pure noise — the stability cost of observed timing, measured
directly. Its effective precision sits between ±2 and ±8 on the curve above
(primary 0.104354), which is consistent: ADWIN's error profile exceeds the
tolerance its alarms would need. Both dispositions point the same way, by
independent routes.

## Privilege caveat

Every jitter/drop schedule is evaluator-built from true times and stays
diagnostic; only the ADWIN-schedule arm derives timing from observables, and
it failed its gate. Nothing here advances a deployable policy. The tolerance
number constrains what could work; it does not demonstrate anything working.

## Evidence, phases and changed files

| Phase | Evidence | Status |
| --- | --- | --- |
| Registration/refinement | `9e20345` | Before study observations; +16 level reviewed in |
| Implementation/checks | branch commits | Before tuning; one provenance-label fix pre-confirmation |
| Tuning / manifest freeze | 288 rows | Eligible; trio identical to four predecessors |
| Confirmation | seeds 113000–113031, fourteen policies | 448 rows; tolerance None, advancement negative |
| Reproduction/publication | All 736 reached rows; eleven workflows | See validation below |

Protocol SHA-256:
`1f3229edb5a3ca1cd351c47bfee1bc95d70a8b924970e4796b80ae59a22b7e3f`. Development
110000–110007, tuning 111000–111007, confirmation 113000–113031, bootstrap
115000 and the 116000+ schedule RNG domains are separate and disjoint from
all previous studies. An early tuning freeze bound to pre-amend protocol
metadata was superseded before confirmation: after the provenance-label fix,
all evidence was regenerated under the final code and re-frozen. No frozen
evidence was edited; the superseded freeze remains visible in history.

New files: `v3_tolerance.py`, `v3_tolerance_policy.py`,
`study_v3_tolerance.py`, `report_v3_tolerance.py`, `check_v3_tolerance.py`,
`.github/workflows/v3-tolerance-checks.yml`, the registration, this results
file and `results/v3-tolerance/`. README and PLAN/V3 status pointers report
the outcome. Earlier scientific sources, evidence, protocols, all ten
previous workflows, dependencies and agent defaults remain unchanged. No
capability or registry row is promoted.

The [generated report](results/v3-tolerance/report.md) includes per-level
pass tables, the tolerance point, the full 45-cell tables for the
ADWIN-schedule and reference arms, per-fixture absolute errors with regime
shares, and execution times. Raw records retain request indices with
schedule provenance, jitter draws, drop/add realizations, and alarm
provenance tying each observed request to its generating control run.

## Validation and limits

All commands below passed locally, including reproduction of all 736 new rows.
Python commands use the project's existing `.venv`:

```sh
python check_v3_tolerance.py --evidence results/v3-tolerance --reproduce
python report_v3_tolerance.py --check
python check_evidence.py
git diff --check
```

Checks cover schedule-construction parity (uniform bounds, clipping,
collision merging, drop/add RNG independence and domain separation, alarm
provenance from the selected control config), frozen dual-state parity,
causal prefixes, coordinate isolation, privilege isolation of granted
schedules, the 45-cell instrument and tolerance-point logic, the advancement
gate, per-arm provenance accounting, immutable sources/manifests/stages,
missing/invalid/non-finite evidence, and dual memory accounting. The parity
suite caught four genuine implementation bugs before any observation,
including a tolerance-point test that would have silently inflated the
headline number. Every reached row, manifest, selection, schedule, decision
and scientific summary is reproduced at rtol1e-11/atol1e-13, excluding only
timing and regenerated input digests. CI must pass all eleven workflows
before merge.

Intervals use 10000 whole-seed resamples (seed 115000). Small Gaussian
supervised fixtures, finite schedule menus and granted true times cannot
establish population guarantees, detector rankings, or neural-memory utility.
The authoritative outcomes are the registered tolerance None with its
schedule-attributable (±2, ±8] reading, and the ADWIN-schedule arm's
independent learning-negative result.
