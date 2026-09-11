# Q5 rank-1 eligibility — registration

Protocol `q5-rank1-20260911-v2` (supersedes `-v1`, which specified the same
question, arms, instrument, and bands but an in-place implementation; no
confirmation ran under v1 and no evidence path exists for it).

v1 DESIGN FLAW, found during implementation: three frozen manifests (v2-m0,
v5, v6) pin `brainsim.py` byte-for-byte, so landing the flag in BrainSim
itself turns their `--check`/`--reproduce` red (`manifest differs`). The
revert was verified (`report_v2_m0.py --check` green again). The flag lands
in a subclass fork instead (MotorWTA precedent): if rank-1 matches, moving
it into v1 with deliberate re-freezes is a follow-up slice; if it fails,
nothing was integrated.

SMOKE DISCLOSURE (engineering probes of the discarded v1 implementation,
n=1 seed, 300 decisions, nway-4): 0.99 both runners. Weakly suggestive that
rank-1 learns nway-4; contains no information about the 8 frozen seeds'
paired diffs against which the pre-stated bands decide. Recorded here so
the audit trail is complete.

Question. V2.md Q5: is the per-synapse eligibility trace replaceable by an
outer product of pre- and post-traces formed on demand? This is a DIFFERENT
RULE (decaying sum of outer products vs outer product of decayed traces),
so per the project's own verdict — "do not count it until measured" — it is
tested, not assumed. If it matches, the eligibility-trace component of
plasticity state drops from M×H floats to M+H; if not, the scale table loses
its second-largest lever.

## Candidate (exact equations, the only item on the menu)

Implemented in `q5_rank1.py` as `Rank1BrainSim(BrainSim)`; `brainsim.py` and
`tasks.py` are byte-identical to the frozen tree. The subclass carries the
exact `BrainSim.step()`/`reward()` text (AST-extracted; classic branches
unchanged, plus one defensive `_credit_init()` call at `reward()` head that
is a no-op when the flag is off) with the rank-1 algebra behind the
subclass flag `RANK1_ELIG` (class default `False`, set per-instance via the
`brainsim_run(..., **over)` seam). No shipped default changes; no other
constant moves (ELIG_D, TRACE_D, TRM_D, THETA, TAGGATE all frozen at shipped
values — no tuning). `FastRank1(FastBrainSim, Rank1BrainSim)` composes
buffered steps + the shared numba kernel with the rank-aware reward by MRO;
the kernel's default-off path is arithmetically identical (gated by
`check_port.py` still passing).

Under `RANK1_ELIG=True`, `self.elig` (M×H) is dropped to `None` on the
first tick (flags arrive via post-construction setattr, so conversion is
lazy via `_ensure_credit`, before any tick math) and never reallocated;
these replace the matrix EMA:

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
`_tick_block`, flag + arrays threaded through `observe` via getattr with a
`False` default so plain agents are untouched); the default-off path must
remain bit-identical. No frozen manifest pins `fastsim.py` alone
(`check_evidence.py` does not compare manifests), so the kernel edit carries
no collateral — verified by `check_port.py` and `report_v2_m0.py --check`
staying green after the edit.

## Arms and instrument

- Arms: `shipped` (`RANK1_ELIG=False`) vs `rank1` (`RANK1_ELIG=True`).
- Instrument: the 7 reference tasks × the 8 frozen seeds = 56 paired
  scores, `rank1` compared against the `brainsim` column of the frozen
  `reference.json`. Same-seed paired design — this is a
  port-equivalence question against the reference instrument, not a
  generalization question, so the frozen seeds are the correct matched
  control (mirrors `check_reference.py`'s exact per-seed logic).
- Bit-exact probe, two legs on the same 12 (task, seed) pairs (check_port
  case shape: nway-4/8, volatile-4, xor-2, tmaze-2, lock-10 × seeds 0–1 at
  400 decisions, full histories compared): (i) classic-mode subclass vs
  BrainSim head-to-head must match exactly (copy fidelity); (ii)
  rank1-numpy vs rank1-fast must match exactly (port gate — a port that
  changes numbers is a broken port, not a finding).

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
   classic-mode subclass vs BrainSim head-to-head EXACT on the 12 probe
   pairs (copy fidelity — the only difference under test is the algebra),
   rank1-numpy vs rank1-fast 12/12 exact (shared-kernel port gate).

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

Registration (this file, before any confirmatory observation) →
implementation + checks → manifest freeze (sources incl. `q5_rank1.py` and
`fastsim.py`; `brainsim.py`/`tasks.py` frozen) → confirmation (112 fast
rows: 2 arms × 8 seeds × 7 tasks) + 12-row exact probe (classic-fidelity
and rank-1 port legs) → report → PR. Results directory `results/q5/`.
New files: `q5_rank1.py`, `study_q5.py`, `report_q5.py`, `check_q5.py`,
`.github/workflows/q5-checks.yml`, this registration,
`Q5-RANK1-RESULTS.md`.
