# Parallel loops: per-action modulation wins sparse, idles elsewhere

The loops probe closes as **adopt-loops-loops-full**: per-action LR plus
per-action exploration noise beats the frozen global loop on lock-10
(+30.62, CI [+20.88, +40.88]) with the dense guard clean (nway-8
−0.0171, band ±0.03). The LR-only variant does nothing anywhere. The
win's shape carries the surprise: the active ingredient looks like the
*noise* loop, not the learning-rate loop — and the volatility task that
motivated loops shows no gain at all.

## What was done

The [registration](DESIGN-loops-probe.md) (protocol `loops-20260911-v1`)
tests the last unmeasured founding-adjacent item: one global
neuromodulator scalar for the whole net. `LoopsBrainSim` carries the
exact `BrainSim.reward()` text with per-action fast/slow reward-rate
averages behind `MODE`; `FastLoops` composes the shared kernel (which
gained a default-identical per-action noise path) with the loop-aware
reward. The shipped global averages keep running in all modes, so
volatility history, burst triggers, and the WM pathway are preserved.
No v1 source changed. 48 rows (2 arms × 3 tasks × frozen seeds 0–7),
same-seed paired vs the frozen columns.

## Independent confirmation

| Task / arm | Arm mean | Frozen mean | Delta | 95% interval | Pass |
| --- | ---: | ---: | ---: | --- | --- |
| lock-10/loops-LR | 409.6250 | 415.1250 | −5.5000 | [−39.7500, +23.8750] | False |
| lock-10/loops-full | 445.7500 | 415.1250 | +30.6250 | [+20.8750, +40.8750] | True |
| volatile-4/loops-LR | 0.3167 | 0.3715 | −0.0548 | [−0.1893, +0.1004] | False |
| volatile-4/loops-full | 0.3086 | 0.3715 | −0.0629 | [−0.1860, +0.0548] | False |
| nway-8/loops-LR | 0.9662 | 0.9782 | −0.0120 | [−0.0519, +0.0128] | True |
| nway-8/loops-full | 0.9611 | 0.9782 | −0.0171 | [−0.0508, +0.0056] | True |

(Adoption bar: paired lower > 0 on volatile OR lock, plus the arm's own
nway rows within ±0.03. Highest-delta clearer wins ties.)

## Reading the result

Three observations, in increasing order of awkwardness:

1. **The adoption is mechanical and stands.** loops-full clears on lock
   with the tightest lock interval this program has measured, and its
   own guard passes. The pre-registered rule fires; the verdict is
   adopt-loops-loops-full.
2. **The ingredient is noise, not LR — suggestively.** loops-LR
   (LR vector, global noise) is a null everywhere (−5.50 lock, −0.012
   nway, −0.055 volatile); adding the noise vector moves lock +36 while
   nothing else moves. No noise-only arm exists (finite menu), so the
   attribution is suggestive, not proven: per-action exploration is the
   prime suspect for the lock gain. A natural follow-up isolates it —
   but that follow-up is not this slice.
3. **Volatility, the motivating task, shows nothing.** Both loop arms
   sit slightly *below* frozen on volatile-4 with wide intervals. If
   per-action modulation mattered where modulation matters, it should
   have shown here. Hypothesis (marked): volatile's contingency switches
   punish slow per-action averages — each action's rates update only
   when taken (~1/4 of decisions), so the loops adapt slower than the
   world changes, exactly where speed matters. The global loop, updated
   every decision, keeps up. Under sparse reward there is nothing to
   keep up with, so the local loops' patience wins.

Net for the substrate phase: loops-full rides (parity + replication
still required there — this probe adopts the *candidate*, not the
integration), loops-LR is out, and the noise-only isolation is logged
open.

## Privilege caveat

None needed beyond the usual: no oracle arms exist in this study, and no
schedule is granted.

## Evidence, phases and changed files

| Phase | Evidence | Status |
| --- | --- | --- |
| Registration | branch commits | Before any observation |
| Implementation/checks | branch commits | Before manifest freeze |
| Manifest freeze | eligible | Before confirmation |
| Confirmation | 2 arms × 3 tasks × 8 seeds | 48 rows; adopt-loops-loops-full |
| Reproduction/publication | All rows; twenty-seven workflows | See validation below |

Frozen reference seeds 0–7. Bootstrap RNG 225000.

New files: `loops_rule.py`, `study_loops.py`, `report_loops.py`,
`check_loops.py`, `.github/workflows/loops-checks.yml`, the
registration, this results file and `results/loops/`. `brainsim.py` and
`tasks.py` byte-identical to the frozen tree; `fastsim.py` gains the
default-identical per-action noise path. Earlier evidence, protocols,
workflows, dependencies and defaults unchanged. No capability or registry
row is promoted.

The [generated report](results/loops/report.md) includes per-task paired
contrasts, absolute scores, and per-seed evidence.

## Validation and limits

All commands below passed locally, including reproduction of all 48 rows.
Python commands use the project's existing `.venv`:

```sh
python check_reference.py --out results/local-reference.json
python check_loops.py --evidence results/loops --reproduce
python report_loops.py --check
python check_evidence.py
git diff --check
```

Checks cover global-mode copy fidelity (numpy and fast, EXACT),
per-mode port exactness (16/16, full histories), credit-state shapes,
paired contrasts, bands, invalid handling, immutable sources/manifests,
missing/non-finite evidence, and full archive reproduction. The frozen
56-score reference passes unchanged. CI must pass all twenty-seven
workflows before merge.

Same-seed paired design on the reference instrument; not cross-seed
generalisation. Lock-10 total reward is high-variance (tamed here by
pairing — the tightest lock interval on record). The noise-attribution
and volatile-slowness readings are hypotheses, not verdicts.
