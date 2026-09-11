# M0 decision record: what the five slices closed, and what fork (if any)

A five-slice program set out to retire V2.md's open questions before the
continuous-time fork. All five slices are merged to master with full CI
green (404 confirmation rows total). This record states what each slice
closed, audits which V2.md premises survived contact with current code,
and lays out the fork decision with costs. It makes no code change and
runs no rows; it is a synthesis artifact, the slice-5 deliverable.

## The five slices

| Slice | Question | Verdict | Evidence | PR |
| --- | --- | --- | --- | --- |
| V2 M0-motor | per-tick 1-of-N without aggregates | learning_negative | 36 rows | #32 `b96cf87` |
| Q5 rank-1 | trace pair vs per-synapse eligibility | replaceable | 112 rows | #34 `5c4a83b` |
| L-sweep | replay window L on lock-10 | confirmed-20 | 40 rows | #35 `de33813` |
| Q2 tau | consumption rule × tau, sparse regime | vetoed-none-200, carry full@200 | 88 rows | #36 `6648d92` |
| Q3 pools | capacity vs pools and scale | dead-end (+ premise refuted) | 128 rows | #37 `db27c21` |

Result docs: [V2-M0-RESULTS.md](V2-M0-RESULTS.md),
[Q5-RANK1-RESULTS.md](Q5-RANK1-RESULTS.md),
[L-SWEEP-RESULTS.md](L-SWEEP-RESULTS.md),
[Q2-TAU-RESULTS.md](Q2-TAU-RESULTS.md),
[Q3-POOLS-RESULTS.md](Q3-POOLS-RESULTS.md). Registrations: `DESIGN-v2-m0-motor.md`,
`DESIGN-q5-rank1.md`, `DESIGN-L-sweep.md`, `DESIGN-q2-tau.md`,
`DESIGN-q3-pools.md`.

## Premise audit: what survived current code

| V2.md premise (as written) | Current-code measurement | Status |
| --- | --- | --- |
| Motor sparsity failed: 0.319/0.158 (`19_local_alternatives.py`) | re-implemented aggregate: 0.979/0.894; per-tick fails at 0.266/0.128 | premise refuted; failure was the decide() tie bug + missing aggregation, not sparsity |
| Capacity cliff: 0.946 → 0.385 at 4 → 16 combos | combos-16 memorizes at 0.964 | premise refuted; tie-bug era (4-action task) |
| Event-driven worth ~1000x | 5.4x at our rates (Q1 probe) | demoted to conditional before this program; unchanged |
| L=20 assumed for replay | L=20 is the measured knee (40/167/415/438/410) | assumed → measured |
| Tau 200 / consume-on-reward assumed | tau peaks at 200 in all rules; decay-alone vetoed on dense | assumed → measured, with the sparse specialist logged |
| Per-synapse eligibility load-bearing | trace pair matches on all 7 tasks | lever banked (ebar follow-up open) |

The pattern: this project twice mistook decide()-tie-bug damage for a
structural limit (motor sparsity, capacity cliff). Both corrections came
from re-implemented controls, not new theory. Any future premise quoted
from pre-fix code should be treated as unmeasured until a control says
otherwise.

## Open questions, final status

- **Q1 (event-driven savings): RESOLVED.** 5.4x, conditional. Unchanged
  by this program; M0-motor closed the last escape route (per-tick
  sparsity without aggregates fails at chance).
- **Q2 (eligibility consumption): RESOLVED CONSERVATIVELY.** M0 starts
  at full@200. Logged alongside: none@200 (+129.6 lock, −0.097 nway-8)
  and proportional@200 (+55.5 lock) for a mixed regime.
- **Q3 (pool sizing): DEAD-END.** Pools inert (±0.003); scale-alone hurts
  (−0.31). No gap instrument exists, so per method rules there is
  nothing to build. M2 as framed has no limit to beat.
- **Q4 (episode delimitation): RESOLVED.** Ring buffer + fixed window
  (design); L=20 now measured. M0 sizes buffers at episode scale.
- **Q5 (rank-1 eligibility): REPLACEABLE.** 3x lever banked; M×H `ebar`
  baseline remains as a named follow-up slice.

## Founding-changes scoreboard

| V2.md founding change | Standing after this program |
| --- | --- |
| local pools | OUT — unmotivated, no gap instrument |
| continuous time | LAST ONE STANDING — untested, untestable in v1 |
| parallel NM loops | UNTESTED — never probed; testable in v1 without a fork |
| event-driven | conditional (unchanged); stays out of the fork |

## Options and costs

**A. Fork for continuous time now.** Scope: the fork itself (task
interface, runner, replay episode definition, eligibility consumption
break at once — V2.md's own warning) + parallel loops + ring buffer at
L=20 + full@200 start rule (+ proportional@200 in the pocket for a mixed
regime). Pools out, event-driven out. Cost: the single most expensive
step in the roadmap, taken while one founding-adjacent item (parallel
loops) is still unmeasured. Benefit: answers the last founding question
in its native regime; nothing else can.

**B. Incremental substrate in v1, then fork.** Land seed-generated
connectivity (zero-memory fixed synapses — the only SOLID-scale lever)
and parallel NM loops in v1, parity-checked per step per V2.md's own
build order, then fork for continuous time alone against a v1 that
already carries the fast core. Cost: slower to the fork; two more
v1 slices with their own CI cycles. Benefit: the fork diff shrinks to
one change (the only one V2.md says forces a fork), and each substrate
item arrives with its own falsifier instead of riding the fork's.

**C. Hold.** v1 stands everywhere probed; no fork until a new gap
instrument shows one. Cost: near zero. Risk: stagnation dressed as
discipline — but note the program's actual yield curve: four of five
slices retired risk or banked levers without building the thing. Hold is
a legitimate reading of "do not build what no instrument can show a gap
for" applied to the fork itself.

## Recommendation (agent's, marked)

**B, with C as the default if B's slices come back negative.** The
program's meta-lesson is that premises decay under current code and
controls are cheap: seed-connectivity and parallel loops are both
falsifiable in v1 at slice cost, and each one that lands shrinks the
fork. Forking now (A) bundles the last unmeasured substrate item into
the most expensive step — exactly the big-bang shape V2.md warns made
every v1 breakage. If B's slices fail (seed-gen neutral, loops
unmotivated), that IS the C verdict arriving honestly, and the fork
question answers itself: continuous time alone, or not at all.

## What this record does not do

- It does not rewrite V2.md. Sections contradicted above (pools as
  founding, M2 as framed, the 0.319/0.385 premises) are stale in place;
  rewriting the PRD is the owner's call. This record is the cited
  supersession until then.
- It does not claim population guarantees, deep-learning comparisons,
  or cross-seed generalisation for any slice — each result doc states
  its own limits.
- It does not spend the ebar follow-up, the H160-degradation mechanism,
  or the continuous-time rule-vs-regime lockdown — all three are logged
  open in their slice docs.
