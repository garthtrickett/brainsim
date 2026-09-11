# Q5 rank-1 eligibility — registration

Protocol `q5-rank1-20260911-v1`. V2.md Q5: is the per-synapse eligibility
trace replaceable by an outer product of pre- and post-traces formed on
demand? This is a DIFFERENT RULE (decaying sum of outer products vs outer
product of decayed traces), so per the project's own verdict — "do not count
it until measured" — it is tested, not assumed. If it matches, the
eligibility-trace component of plasticity state drops from M×H floats to
M+H; if not, the scale table loses its second-largest lever.

## Candidate (exact equations, the only item on the menu)

New flag `RANK1_ELIG`, class attribute default `False`, settable via the
`brainsim_run(..., **over)` seam like every other flag. No shipped default
changes; no other constant moves (ELIG_D, TRACE_D, TRM_D, THETA, TAGGATE
all frozen at shipped values — no tuning).

Under `RANK1_ELIG=True`, `self.elig` (M×H) is never allocated
(`None` by construction) and these replace `brainsim.py:408-409`:

```
etr_m = etr_m*ELIG_D + (1-ELIG_D)*(fm*gate)      # motor side, M floats
etr_h = etr_h*ELIG_D + (1-ELIG_D)*trh            # hidden side, H floats
etrw  = etrw*ELIG_D + (1-ELIG_D)                 # shared weight, scalar
```

`gate` is the existing TAGGATE gate from `trm`, computed exactly as now.
Lifecycle mirrors `elig` exactly: zeroed in `__init__`, consumed
(zeroed) at the same two sites (`reward()` normal path and ACTION_GATED
path), untouched by `_reset_dynamics` — which does not touch `elig`
either. The only difference under test is the algebra.

At `reward()`, in place of `elig/elig_w` (`brainsim.py:608`):

```
formed = outer(etr_m, etr_h) / max(etrw*etrw, 1e-9)
```

`formed` is a transient M×H array: it flows into `de`, `ebar`, the
buffer entry, and consumption exactly as `elig` does today, so `sleep()`,
replay, WM pathway, `ebar`, and the ACTION_GATED path are untouched.
Credit state across ticks is M+H floats plus one scalar; no (M,H) array
persists between rewards.

The fastsim numba kernel gets the mirror implementation (trace updates in
`_tick_block`, flag + arrays threaded through `observe`); the default-off
path must remain bit-identical.

## Arms and instrument

- Arms: `shipped` (`RANK1_ELIG=False`) vs `rank1` (`RANK1_ELIG=True`).
- Instrument: the 7 reference tasks × the 8 frozen seeds = 56 paired
  scores, `rank1` compared against the `brainsim` column of the frozen
  `reference.json`. Same-seed paired design — this is a
  port-equivalence question against the reference instrument, not a
  generalization question, so the frozen seeds are the correct matched
  control (mirrors `check_reference.py`'s exact per-seed logic).
- Bit-exact probe: rank1-numpy vs rank1-fast on 12 (task, seed) pairs
  must match exactly (check_port pattern: a port that changes numbers is
  a broken port, not a finding).

## Falsifier (equivalence → "replaceable")

PASS iff ALL hold:

1. For each of the 6 accuracy tasks (nway-4/8, xor-2, volatile-4,
   tmaze-within-30/60): |paired mean diff (rank1 − frozen)| ≤ 0.03.
2. For lock-10 (total-reward scale): |paired mean diff| ≤ 0.10 ×
   |frozen mean|.
3. Memory: under RANK1, `agent.elig is None` at every probe point and
   persistent credit state is exactly M+H+1 floats (asserted, not
   eyeballed).
4. Negative controls green: `check_reference.py` bit-exact (default-off
   path unchanged), `check_port.py` 12/12 (default-off port unchanged),
   rank1-numpy vs rank1-fast 12/12 exact.

Any single failure closes the slice as **not-replaceable**. No
re-tuning, no second candidate, no band widening after observation.

## Explicit non-claims

- `ebar` stays M×H in both arms (common infrastructure, matched). The
  full 12B→4B lever additionally needs the baseline addressed — that is
  a follow-up slice, not smuggled into this one.
- volatile-4 sits near its floor (0.420 vs 1.000 ceiling); the ±0.03
  band applies identically — a rule that collapses there fails loudly.
- Cross-seed generalization beyond the 8 frozen seeds is out of scope;
  the claim is equivalence on the reference instrument.

## Phases and evidence

Registration (this file, before any implementation observation) →
implementation + checks → manifest freeze (sources incl. modified
`brainsim.py`/`fastsim.py`) → confirmation (56 fast rows + 12-row exact
probe) → report → PR. Results directory `results/q5/`. New files:
`study_q5.py`, `report_q5.py`, `check_q5.py`,
`.github/workflows/q5-checks.yml`, this registration,
`Q5-RANK1-RESULTS.md`.
