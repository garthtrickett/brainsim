# Q3 capacity: the cliff is gone — dead-end for pools, and for the premise

The pools×scale screen closes as **dead-end**, but the headline is bigger
than the verdict: the capacity cliff that motivated local pools as a
founding change does not reproduce under current code. Combos-16 at v1
scale memorizes at **0.964**, not the premise's 0.385. Pools change
nothing (±0.003, every interval straddling zero), and doubling units with
sparsity held makes things decisively worse (0.655/0.596). There is no
capacity problem here for pools — or scale — to solve.

## What was done

The [registration](DESIGN-q3-pools.md) (protocol `q3-pools-20260911-v1`)
measures memorization (`Compositional(n,n,held_out=0)` train accuracy) at
v1 scale (H=80, k=6: P ∈ {1,2,3,6} × combos {4,9,16}) and at doubled
scale with sparsity held (H=160, k=12: P ∈ {1,4} × combos {9,16}).
Total sparsity held constant across pools within each H, so differences
are competition geometry. 128 rows, fresh seeds 320–327, same-seed
pairing within cells. No v1 source changed.

## Independent confirmation (absolute train accuracy)

| Cell H/k/pools/combos | Mean | 95% interval |
| --- | ---: | --- |
| 80/6/1/4 | 0.9830 | [0.9772, 0.9879] |
| 80/6/1/9 | 0.9848 | [0.9800, 0.9896] |
| 80/6/1/16 | 0.9640 | [0.9591, 0.9692] |
| 80/6/2/16 | 0.9610 | [0.9517, 0.9700] |
| 80/6/3/16 | 0.9626 | [0.9521, 0.9712] |
| 80/6/6/16 | 0.9631 | [0.9556, 0.9710] |
| 160/12/1/9 | 0.7933 | [0.7560, 0.8351] |
| 160/12/1/16 | 0.6551 | [0.6249, 0.6819] |
| 160/12/4/9 | 0.7835 | [0.7484, 0.8195] |
| 160/12/4/16 | 0.5962 | [0.5076, 0.6710] |

Key paired contrasts on combos-16: every H80 P>1 vs P=1 within ±0.01
(all CIs straddle zero — adopters: none, regressions: none);
(H160,P4) vs (H80,P1): −0.3678 [−0.4556, −0.2915];
scale-alone (H160,P1) vs (H80,P1): −0.3089 [−0.3376, −0.2851].

(Full per-cell table and intervals in `results/q3/report.md`.)

## Reading the result

Three facts, in increasing order of importance:

1. **Pools are inert here.** ±0.003 with tight seed spreads (0.955–0.976
   across all H80 cells). Competition geometry has nothing to relieve
   because nothing is crowded.
2. **Scale hurts.** H=160/k=12 loses 0.31 paired on combos-16 with the
   interval far from zero — and the (H160,P1) control proves it is not
   pooling, it is scale itself (more winners, denser codes, dynamics
   tuned for k=6 — mechanism unknown, reported as measured). "Add units"
   is not a remedy; it is a second problem.
3. **The premise is refuted.** 16 combos memorize at 0.964 under current
   code. The old 0.385 dates to the tie-bug era — Compositional has 4
   actions, and the decide() bug depressed every n>2 result, hardest
   where votes split most. Same story as the M0-motor premise
   correction: the project has now twice mistaken tie-bug damage for a
   structural capacity limit.

Consequence for the roadmap: M2 as framed ("pooled competition beats
global k-WTA on the measured 0.946→0.385 limit") has no limit to beat.
Local pools drop from founding to unmotivated — not refuted as a
mechanism (an uncongested regime cannot test a decongestion mechanism),
but with no instrument showing a gap, per our own method rules there is
nothing to build. If a harder capacity task ever shows a real cliff,
this slice's harness (16 arms, 128 rows, ~minutes) re-runs verbatim.

## Privilege caveat

None needed beyond the usual: no oracle arms exist in this study, and no
schedule is granted.

## Evidence, phases and changed files

| Phase | Evidence | Status |
| --- | --- | --- |
| Registration | branch commits | Before any observation |
| Implementation/checks | branch commits | Before manifest freeze |
| Manifest freeze | eligible | Before screen |
| Screen | 16 arms × 8 seeds | 128 rows; dead-end |
| Reproduction/publication | All rows; twenty-six workflows | See validation below |

Fresh seeds 320–327. Bootstrap RNG 225000.

New files: `study_q3.py`, `report_q3.py`, `check_q3.py`,
`.github/workflows/q3-checks.yml`, the registration, this results file
and `results/q3/`. v1 sources untouched. Earlier evidence, protocols,
workflows, dependencies and defaults unchanged. No capability or registry
row is promoted.

The [generated report](results/q3/report.md) includes the full per-cell
table, all paired contrasts, and per-seed evidence.

## Validation and limits

All commands below passed locally, including reproduction of all 128
rows. Python commands use the project's existing `.venv`:

```sh
python check_q3.py --evidence results/q3 --reproduce
python report_q3.py --check
python check_evidence.py
git diff --check
```

Checks cover pools-port exactness (8/8, full histories), paired
contrasts, invalid handling, immutable sources/manifests,
missing/non-finite evidence, and full archive reproduction. No frozen
table covers this task, so no reference gate applies; shared sources are
byte-identical, which is the collateral control. CI must pass all
twenty-six workflows before merge.

Memorization capacity only (train accuracy, held_out=0): no
generalisation claim. Same-seed pairing within cells; cross-seed
generalisation out of scope. The H160 degradation mechanism is
unidentified — reported, not explained.
