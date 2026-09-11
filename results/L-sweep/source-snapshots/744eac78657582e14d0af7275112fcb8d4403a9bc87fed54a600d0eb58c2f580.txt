# Replay window L sweep — registration

Protocol `L-sweep-20260911-v1`. V2.md residual risk: v1's best result
(lock-10, ~9.5 → ~419) rests on `HIPPO_WINDOW=20`, which was never swept.
A bad L could cost most of it, and M0's ring-buffer design hard-codes a
window choice — so the choice must be measured before it becomes
infrastructure. No v1 source changes: L rides the existing
`brainsim_run(..., **over)` setattr seam. Zero collateral by construction.

## Design (two stages, both pre-registered)

Stage 1 — screen on lock-10 (the result that rests on L). Menu
`L ∈ {5, 10, 20, 40, 80}` (16x span; L=20 is the shipped control), frozen
seeds 0–7, 40 rows. Everything else frozen at shipped values
(HIPPO_MIN_LEN=2, HIPPO_N=8, all other flags); L is the only difference
under test.

Stage 2 — collateral check of the stage-1 winner (if the winner is not
20): winner window vs the frozen reference table on the 6 non-lock tasks
× 8 seeds (48 rows), same-seed paired design (Q5 precedent). Lock-10 is
EXCLUDED from stage 2: same window plus same seeds is bit-identical to
the screen rows, hence evidence-free. The MIN_LEN comment documents
window↔task interactions (nway-4, xor-2, volatile-4 lose 0.07–0.21
without replay gating), so a winner that helps lock while hurting the
suite must fail here.

## Falsifier

- ADOPT (new L) iff some L≠20 beats L=20 on lock-10 with paired 95%
  lower bound > 0, AND the stage-2 collateral check lands every non-lock
  task within the Q5 bands (accuracy ±0.03).
- CONFIRMED-20 iff no L≠20 clears the bar: the residual risk retires and
  M0 takes L=20 as measured, not assumed. A negative result is a result.
- Any stage-2 collateral failure vetoes adoption regardless of the screen.

No re-tuning, no sixth L value, no band changes after observation. The
four screen comparisons share one control; multiplicity is disclosed, not
corrected — adoption additionally requires clearing the bar outright
(lower > 0, not merely best-of-five) plus a clean collateral check.

## Explicit non-claims

- Same-seed (0–7) design throughout: the claim is selection on the
  reference instrument, not cross-seed generalisation. The winner's-curse
  direction is disclosed: stage-1 selection favors the luckiest L. The
  guards are the adoption bar itself (paired lower > 0, not best-of-five
  point estimates) and the stage-2 collateral check on six untouched
  tasks.
- HIPPO_MIN_LEN, HIPPO_N, and all other replay constants are out of
  scope; interactions with them are not tested here.
- The screen measures total reward (tail=0), a high-variance metric
  (frozen seed range spans hundreds); n=8 paired is the instrument the
  project has, reported whole.

## Phases and evidence

Registration (this file, before any observation) → implementation +
checks → manifest freeze → stage-1 screen (40 rows) → stage-2 suite
confirmation if needed (48 rows) → report → PR. Results directory
`results/L-sweep/`. New files: `study_Lsweep.py`, `report_Lsweep.py`,
`check_Lsweep.py`, `.github/workflows/L-sweep-checks.yml`, this
registration, `L-SWEEP-RESULTS.md`.
