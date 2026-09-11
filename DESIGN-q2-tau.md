# Q2 consumption × tau under sparse reward — registration

Protocol `q2-tau-20260911-v1`. V2.md Q2, sharpened: with rewards arriving
every ~10²–10³ ticks (the lock regime, which IS the sparse regime — no new
task machinery needed), does ELIG_D decay alone suffice, and at what tau?
Carry `proportional` as the leading candidate. M0 must be told a NAMED
rule+tau, so this slice ends in a selection, not a comparison.

Experiment 41 already ran {full, none, half, proportional} at tau 200 in
the every-decision regime (full best dense; proportional best sparse at
414 vs 356 on lock). Untested: every rule off its home tau, and any rule
at any tau on the frozen 8-seed instrument. That is this slice.

## Design (two stages)

Rule harness `q2_rule.py`: `Rule(BrainSim)` restoring a kept fraction of
the cashed trace after `super().reward()` (experiment-41 mechanism, full
reward signature). Modes {full (keep 0), none (keep all — decay alone),
proportional (keep 1−min(1,|RPE|))}. `half` is dropped: bimodal 258.0 in
41 ([289, 8, 477]) with no regime where it leads. No v1 source changes —
subclass fork precedent; zero collateral by construction.

Stage 1 — screen on lock-10: {full, none, proportional} × tau {100, 200,
400} (ELIG_D {0.99, 0.995, 0.9975} via the setattr seam), frozen seeds
0–7, 72 rows. full@200 is the shipped control and coincides with the
frozen lock column.

Stage 2 — dense guard for the adopted candidate only (if it is not
full@200): candidate on nway-8 AND volatile-4 × 8 seeds (16 rows) vs
frozen, band ±0.03 each. Experiment 41 shows dense costs are real
(proportional −0.03/−0.074), so a lock winner that breaks dense tasks
must fail here.

## Falsifier (decision procedure, pre-registered)

1. Per rule, champion tau = max mean on the screen (descriptive).
2. A rule champions against full@200 iff paired 95% lower bound > 0.
3. Exactly one clearer → adoption candidate; several → highest-mean
   clearer (pre-registered tiebreak); none → carry full@200.
4. Candidate (if not full@200) faces the stage-2 guard: both dense tasks
   within ±0.03 → `adopt-{rule}-{tau}`; any miss → `vetoed-{rule}-{tau},
   carry full@200` (tradeoff reported whole — M0 sees it).
5. full@200 clearing nothing → `carry-full-200` (Q2 resolved
   conservatively: consume-on-reward at tau 200).

Fidelity gate (check_q5 pattern): Rule(full@200) reproduces the frozen
lock column EXACTLY in-process — else the harness is unfaithful and
nothing proceeds.

No re-tuning, no fourth rule, no fourth tau, no band changes after
observation. Three champion comparisons share one control; multiplicity
disclosed, adoption bar is lower > 0 outright.

## Explicit non-claims

- Same-seed (0–7) design on the reference instrument; not cross-seed
  generalisation. Selection favors the luckiest arm — guards are the bar
  itself plus the stage-2 dense check on untouched tasks.
- Lock-10 total reward is high-variance (seed range spans hundreds);
  n=8 paired, reported whole.
- `half`, second-trace gating, and reward-arrival consumption as a
  separate fourth rule are out of scope (41 refuted/narrowed them or they
  need continuous time itself to test).
- The verdict names M0's starting rule+tau; continuous-time validation
  itself belongs to M0, not here.

## Phases and evidence

Registration (this file, before any observation) → implementation +
checks → manifest freeze → stage-1 screen (72 rows) → stage-2 guard if
needed (16 rows) → report → PR. Results directory `results/q2/`. New
files: `q2_rule.py`, `study_q2.py`, `report_q2.py`, `check_q2.py`,
`.github/workflows/q2-checks.yml`, this registration,
`Q2-TAU-RESULTS.md`.
