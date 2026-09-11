# Replay window sweep: L=20 is the knee, measured not assumed

The lock-10 screen across L ∈ {5, 10, 20, 40, 80} closes as
**confirmed-20**: no window beats shipped L=20 with paired 95% lower > 0.
Shorter windows collapse (L=5: 40.4, L=10: 167.2 vs control 415.1);
longer windows plateau (L=40: 437.9, CI [−124, +142]; L=80: 410.1).
The shape is a knee at 20, not a peak to climb: truncation below 20
destroys credit assignment across the maze, extension past 20 adds
nothing. No stage-2 collateral check was triggered (no candidate), and
none is needed. M0 takes L=20 as measured.

## What was done

The [registration](DESIGN-L-sweep.md) (protocol `L-sweep-20260911-v1`)
screens the replay window on the one result that rests on it, with
everything else frozen at shipped values and L riding the existing
setattr seam — no v1 source changed, zero collateral by construction.
40 rows (5 windows × frozen seeds 0–7), same-seed paired design against
the L=20 control, which coincides with the frozen reference column.

## Independent confirmation (screen)

| Window | Mean total reward | 95% interval | Paired delta vs 20 | 95% interval | Adopt |
| ---: | ---: | --- | ---: | --- | --- |
| 5 | 40.38 | [27.12, 55.38] | −374.75 | [−461.75, −297.62] | False |
| 10 | 167.25 | [123.88, 223.75] | −247.88 | [−306.25, −192.00] | False |
| 20 | 415.12 | [331.50, 511.75] | — | — | control |
| 40 | 437.88 | [252.49, 604.88] | +22.75 | [−124.38, +141.75] | False |
| 80 | 410.12 | [226.50, 574.38] | −5.00 | [−186.51, +148.88] | False |

(Absolute intervals in `results/L-sweep/report.md`; all paired intervals
cover zero or lie wholesale below it.)

## Reading the result

The informative comparison is not 40-vs-20 (+22.75, noise) but the cliff
below 20: halving the window more than halves the score twice over
(415 → 167 → 40). Credit in the maze must cross ~10+ decisions in reverse
order; a 5-step window keeps only the maze's tail, so replay rehearses
fragments that never connect reward to the choices that earned it. Past
20 the episode is already whole — extra retention is dead weight the
paired intervals correctly refuse to distinguish from noise.

For M0's ring buffer this says: size the window at the episode scale
(~20 decisions here), not larger "to be safe" — larger buys nothing and
costs memory linearly. The residual risk V2.md flagged (a bad L costing
most of 9.5 → 419) retires in the favorable direction: 20 was already
right, and now it is right on the record.

## Privilege caveat

None needed beyond the usual: no oracle arms exist in this study, and no
schedule is granted. Window length is observable-derived infrastructure,
identical for all arms.

## Evidence, phases and changed files

| Phase | Evidence | Status |
| --- | --- | --- |
| Registration | branch commit | Before any observation |
| Implementation/checks | branch commits | Before manifest freeze |
| Manifest freeze | eligible | Before screen |
| Screen | 5 windows × 8 seeds | 40 rows; confirmed-20 |
| Reproduction/publication | All rows; twenty-four workflows | See validation below |

Frozen reference seeds 0–7. Bootstrap RNG 225000.

New files: `study_Lsweep.py`, `report_Lsweep.py`, `check_Lsweep.py`,
`.github/workflows/L-sweep-checks.yml`, the registration, this results
file and `results/L-sweep/`. v1 sources untouched. Earlier evidence,
protocols, workflows, dependencies and defaults unchanged. No capability
or registry row is promoted.

The [generated report](results/L-sweep/report.md) includes absolute
window means, paired contrasts, and per-seed evidence.

## Validation and limits

All commands below passed locally, including reproduction of all 40 rows.
Python commands use the project's existing `.venv`:

```sh
python check_reference.py --out results/local-reference.json
python check_Lsweep.py --evidence results/L-sweep --reproduce
python report_Lsweep.py --check
python check_evidence.py
git diff --check
```

Checks cover the window seam, paired contrasts, invalid handling,
immutable sources/manifests, missing/non-finite evidence, and full
archive reproduction. The frozen 56-score reference passes unchanged. CI
must pass all twenty-four workflows before merge.

Lock-10 total reward is high-variance (seed range spans hundreds); n=8
paired is the instrument the project has, reported whole. Four screen
comparisons share one control — multiplicity disclosed; adoption required
paired lower > 0 outright, which nothing cleared. Seven tasks and one
harness cannot establish population guarantees.
