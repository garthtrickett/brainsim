# Q3 capacity vs pools and scale — registration

Protocol `q3-pools-20260911-v1`. V2.md Q3: v1 fails at 16 stimulus
combinations with 80 units, so four pools of 20 inherit a quarter of an
already-insufficient capacity — pooling likely needs MORE total units,
which collides with M0's same-scale non-goal. Measure capacity against
pool count and size before committing either way.

Instrument: `Compositional(n,n,held_out=0)` train accuracy (tail mean) —
pure memorization of N=n² combos (labels are shape identity, colour is
nuisance). The old premise (0.946/0.644/0.385 at 4/9/16 combos, one
global k-WTA) is historical context only; it was measured under ancient
code and is expected to differ. Decisions/tail 4000/1000 (premise setup).

## Menu (16 arms, no v1 source changes)

POOLS/H/k ride constructor + setattr seams (P must divide k):

- H=80, k=6 (v1 scale, sparsity 7.5%): P ∈ {1,2,3,6} × combos ∈ {4,9,16}
  = 12 arms. Total sparsity held (P pools × k/P winners = k), so any
  difference is competition geometry, not sparsity (step-9 confound
  control, inherited).
- H=160, k=12 (sparsity held at 7.5%): P ∈ {1,4} × combos ∈ {9,16} =
  4 arms. (H=160,P=1) isolates scale-alone from pooling; combos-4
  skipped (easy everywhere — verified in-screen, not assumed: if P=1@80
  fails combos-4 the premise is broken and the slice stops).

Fresh seeds 320–327 (8). No frozen table covers this task, so there is
no same-seed obligation; controls are same-seed P=1 arms within each
(H, combos) cell.

## Falsifier (three-way, pre-registered)

- POOL-WIN: some P>1 at H=80 beats P=1 on combos-16 with paired 95%
  lower > 0, AND no regression anywhere at H=80: every (P, combos) cell
  paired lower > −0.03 vs its P=1 control. → M0 parity WITH pools at
  same scale.
- NEEDS-SCALE: no POOL-WIN, AND (H=160,P=4) beats (H=80,P=1) on
  combos-16 with paired lower > 0. → M0 parity with pools DISABLED;
  same-scale non-goal relaxed for M2.
- Else DEAD-END: pools earn no place at either scale → M0 drops local
  pools (founding changes reduce to continuous time + parallel loops).

(H=160,P=1) vs (H=80,P=1) reported descriptively in all cases — if scale
alone fixes capacity, pools are not the mechanism and no pools verdict
may claim otherwise.

Fidelity gate (Q5 pattern): numba kernel vs numpy EXACT on pools probe
pairs (all P|6 × 2 seeds, full histories) — orientation already shows
8/8 EXACT; the gate re-runs in-check. A port that changes numbers is a
broken port.

No re-tuning, no fifth pool count, no extra H, no band changes after
observation. Twelve pool comparisons share per-cell controls;
multiplicity disclosed, bars are lower > 0 outright (adoption) and
lower > −0.03 (regression).

## Explicit non-claims

- Memorization capacity only: nothing here shows generalisation,
  compositionality, or superiority over deep learning. Held-out
  generalisation is a different slice (the encoder question is closed
  per V2.md — do not reopen it here).
- k scales with H to hold sparsity; k=12 dynamics differ from k=6 beyond
  sparsity, which is exactly what the (H=160,P=1) control is for.
- Same-seed pairing within cells; cross-seed generalisation out of scope.

## Phases and evidence

Registration (this file, before any observation) → implementation +
checks → manifest freeze → screen (16 arms × 8 seeds = 128 rows) →
report → PR. Results directory `results/q3/`. New files: `study_q3.py`,
`report_q3.py`, `check_q3.py`, `.github/workflows/q3-checks.yml`, this
registration, `Q3-POOLS-RESULTS.md`.
