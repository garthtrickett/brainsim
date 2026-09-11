# Q5 rank-1 eligibility: the trace pair replaces the matrix

Rank-1 eligibility (outer product of pre/post traces formed on demand)
matches per-synapse eligibility on all 7 reference tasks: 5 tasks within
±0.0013, volatile-4 at +0.0258 (band ±0.03), lock-10 at +14.75 (band
±41.5). The experiment closes as **replaceable**. The eligibility-trace
component of plasticity state drops from M×H floats to M+H+1 with no
measured behavior change.

All **112 confirmation rows** (2 arms × 8 frozen seeds × 7 tasks) were
completed and finite, with the shipped arm reproducing the frozen table
bit-exactly in-process. No default change, no integration into v1: the
rule lives in the `q5_rank1.py` subclass fork. Landing it in BrainSim
itself — with deliberate re-freezes of the three manifests that pin
`brainsim.py` — is a follow-up slice.

## What was implemented

The [registration](DESIGN-q5-rank1.md) (protocol `q5-rank1-20260911-v2`)
tests a different rule, not a refactor: decaying sum of outer products
(shipped) vs outer product of decayed traces (candidate). `Rank1BrainSim`
carries the exact `BrainSim.step()`/`reward()` text with the algebra
behind the flag; `FastRank1` composes the shared numba kernel (which
gained a default-off-identical rank-1 path) with the rank-aware reward.
`ebar`, replay, sleep, and the WM pathway are untouched and matched in
both arms.

An in-place implementation was started under protocol v1 and reverted
before any confirmation: three frozen manifests (v2-m0, v5, v6) pin
`brainsim.py` byte-for-byte. Engineering smoke of the discarded path
(n=1 seed, nway-4: 0.99 both runners) is disclosed in the registration;
it contains no information about the frozen seeds' paired diffs.

## Independent confirmation

| Task | rank1 mean | frozen mean | delta | band | Pass |
| --- | ---: | ---: | ---: | ---: | --- |
| nway-4 | 0.997375 | 0.996875 | +0.0005 | 0.0300 | True |
| nway-8 | 0.979500 | 0.978250 | +0.0013 | 0.0300 | True |
| xor-2 | 0.824625 | 0.825250 | −0.0006 | 0.0300 | True |
| volatile-4 | 0.397250 | 0.371500 | +0.0258 | 0.0300 | True |
| tmaze-within-30 | 0.998583 | 0.999250 | −0.0007 | 0.0300 | True |
| tmaze-within-60 | 0.998083 | 0.998250 | −0.0002 | 0.0300 | True |
| lock-10 | 429.875000 | 415.125000 | +14.7500 | 41.5125 | True |

(95% paired intervals in `results/q5/report.md`; all cover small deltas.)

## Reading the result

Five tasks are indistinguishable (≤0.0013). The two loose ends both lean
rank-1, not against it: volatile-4 +0.026 — the project's hardest accuracy
task, where any credit-assignment difference should show first — and
lock-10 +14.75 on a ±41.5 band, the sparse-reward regime where the trace
algebra matters most. Neither is a superiority claim (bands are wide by
design, and volatile's band is nearly touched); both are the opposite of
the degradation a wrong rule would produce. The honest summary: no
measured cost, with the two sensitive tasks inviting a follow-up at more
seeds rather than a victory lap.

## Privilege caveat

None needed beyond the usual: no oracle arms exist in this study, and no
schedule is granted. The comparison is between observable-derived policies
throughout, on identical seeds.

## Evidence, phases and changed files

| Phase | Evidence | Status |
| --- | --- | --- |
| Registration | branch commits (v1, then v2 supersession with disclosure) | Before confirmatory observations |
| Implementation/checks | branch commits | Before manifest freeze |
| Manifest freeze | eligible | Before confirmation |
| Confirmation | 2 arms × 8 seeds × 7 tasks | 112 rows; replaceable |
| Reproduction/publication | All rows; twenty-three workflows | See validation below |

Frozen reference seeds 0–7 (same-seed paired design). Bootstrap RNG
225000.

New files: `q5_rank1.py`, `study_q5.py`, `report_q5.py`, `check_q5.py`,
`.github/workflows/q5-checks.yml`, the registration, this results file
and `results/q5/`. `brainsim.py` and `tasks.py` byte-identical to the
frozen tree; `fastsim.py` gains the default-off-identical rank-1 kernel
path. Earlier evidence, protocols, workflows, dependencies and defaults
unchanged. No capability or registry row is promoted.

The [generated report](results/q5/report.md) includes per-task paired
contrasts, absolute scores, and per-seed evidence.

## Validation and limits

All commands below passed locally, including reproduction of all 112 rows.
Python commands use the project's existing `.venv`:

```sh
python check_port.py
python check_reference.py --out results/local-reference.json
python check_q5.py --evidence results/q5 --reproduce
python report_q5.py --check
python check_evidence.py
git diff --check
```

Checks cover credit-state shape (no M×H array under the flag),
classic-mode copy fidelity 12/12 EXACT, rank-1 port 12/12 EXACT, paired
contrasts, band validation, invalid handling, immutable sources/manifests,
missing/non-finite evidence, and full archive reproduction. The frozen
56-score reference passes unchanged, and the v2-m0/v5/v6 frozen manifests
verify unchanged (their pinned sources untouched). CI must pass all
twenty-three workflows before merge.

Paired bootstrap intervals (10000 resamples, seed 225000) at eight seeds
are descriptive; seven tasks and one harness cannot establish population
guarantees or superiority over deep learning. The authoritative outcome is
the pre-registered replaceable verdict on the reference instrument. The
full 12B→4B lever additionally needs the M×H `ebar` baseline addressed —
a follow-up slice, explicitly out of scope here.
