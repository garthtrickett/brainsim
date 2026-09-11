# Parallel-loops probe — registration

Protocol `loops-20260911-v1`. V2.md's untested founding-adjacent item:
one global neuromodulator scalar (volatility → LR + exploration noise)
for the whole net. Do per-action loops earn their place? Each action
tracks its own fast/slow reward-rate averages (reward attributed to the
taken action) and gets its own LR multiplier — and, in the full variant,
its own exploration noise. Smallest falsifiable form of "parallel loops".

Harness `loops_rule.py`: `LoopsBrainSim(BrainSim)` carrying the exact
`reward()` text (AST-extracted; global branches unchanged) with the loop
algebra behind `MODE ∈ {global, loops-LR, loops-full}`; `FastLoops`
composes the shared kernel (which gains a default-identical per-action
noise path) with the loop-aware reward by MRO. No v1 source changes —
subclass fork precedent; zero collateral by construction. `loops-LR`
keeps noise global (one difference); `loops-full` parallels noise too.

## Arms and instrument

Arms measured: `loops-LR`, `loops-full`. Control: shipped global loop =
frozen reference columns (NOT re-measured; `check_reference.py` green
is the shipped-equals-frozen proof, Q5 precedent). Tasks: volatile-4
(volatility home turf), lock-10 (sparse regime), nway-8 (dense guard).
Frozen seeds 0–7, same-seed paired vs frozen. 48 rows (2 arms × 3 tasks
× 8 seeds).

## Falsifier

- ADOPT-loops-{LR,full} iff the arm beats frozen with paired 95% lower
  > 0 on volatile-4 OR lock-10, AND nway-8 stays within ±0.03 of frozen.
  Several clearers → highest paired delta (Q2/Q3 tiebreak precedent).
- Else carry-global (loops ride nowhere; the fork gets simpler).

Fidelity gates (Q5 pattern): LoopsBrainSim(global) == BrainSim
head-to-head EXACT; FastLoops(global) == FastBrainSim EXACT;
FastLoops(mode) == LoopsBrainSim(mode) EXACT per arm (shared-kernel
port gate). A port or copy that changes numbers is broken, not a
finding.

No re-tuning, no fourth mode, no band changes after observation.
Volatile/lock adoption tests share the frozen control; multiplicity
disclosed, bar is lower > 0 outright plus a clean dense guard.

## Explicit non-claims

- Per-action attribution (reward → taken action) is the tested
  mechanism; per-pool/per-context loops are not tested here.
- Same-seed paired design on the reference instrument; not cross-seed
  generalisation.
- Lock-10 total reward is high-variance; n=8 paired, reported whole.
- A win here sends loops to the substrate phase for parity + replication;
  this probe alone adopts nothing into v1.

## Phases and evidence

Registration (this file, before any observation) → implementation +
checks → manifest freeze → confirmation (48 rows) → report → PR.
Results directory `results/loops/`. New files: `loops_rule.py`,
`study_loops.py`, `report_loops.py`, `check_loops.py`,
`.github/workflows/loops-checks.yml`, this registration,
`LOOPS-RESULTS.md`.
