# Q2 consumption × tau: decay-alone wins sparse, breaks dense — carry full@200

The lock-10 screen over {full, none, proportional} × tau {100, 200, 400}
plus the dense guard closes as **vetoed-none-200, carry full@200**.
Decay-alone at tau 200 is the best sparse-reward rule (+129.6 over
shipped on lock, CI [+91.9, +158.0]) — and it costs nway-8 nearly a tenth
(−0.0965, band ±0.03). M0's starting rule stays consume-on-reward at
tau 200, with the tradeoff on the record: the sparse specialist exists,
and what it costs is measured.

## What was done

The [registration](DESIGN-q2-tau.md) (protocol `q2-tau-20260911-v1`)
asks V2.md's sharpened question — with rewards every ~10²–10³ ticks, does
ELIG_D decay alone suffice, and at what tau? — on lock-10, which IS the
sparse regime, no new task machinery. `Rule(BrainSim)` restores a kept
fraction of the cashed trace (experiment-41 mechanism, full signature);
`FastRule` composes it with the shared kernel by MRO. No v1 source
changed. 72 screen rows + 16 guard rows, same-seed paired throughout.

## Independent confirmation (screen, lock-10 total reward)

| Rule / tau | Mean | Paired delta vs full@200 | 95% interval |
| --- | ---: | ---: | --- |
| full/100 | 389.88 | −25.25 | [−107.38, +36.50] |
| full/200 | 415.12 | — | control |
| full/400 | 416.50 | +1.38 | [−13.12, +14.38] |
| none/100 | 474.12 | +59.00 | [+3.25, +105.88] |
| none/200 | 544.75 | +129.62 | [+91.88, +158.00] |
| none/400 | 495.50 | +80.38 | [−34.50, +162.38] |
| proportional/100 | 459.25 | +44.12 | [+21.75, +68.88] |
| proportional/200 | 470.62 | +55.50 | [+25.00, +82.75] |
| proportional/400 | 463.75 | +48.62 | [−54.12, +115.12] |

Two rules clear the bar; the pre-registered highest-mean tiebreak names
none@200. Tau shows an inverted U peaking at 200 in every rule —
faster consumption starves the maze, slower lets stale credit linger.

## Guard (candidate none@200 vs frozen, band ±0.03)

| Task | Delta | 95% interval | Pass |
| --- | ---: | --- | --- |
| nway-8 | −0.0965 | [−0.1067, −0.0872] | False |
| volatile-4 | −0.0175 | [−0.0984, +0.0611] | True |

The veto is decisive, not marginal: none@200 surrenders a tenth on the
dense task where reward arrives every decision. Unconsumed trace averages
both classes together across dense decisions — the same contamination the
consume-the-tag fix (0.58 → 0.97) removed. Under sparse reward there is
nothing to average together, so decay alone wins by keeping the trail
alive. Each regime wants its own rule; the shipped rule is the dense one,
and dense is what the reference suite mostly measures.

## Reading the result for M0

Continuous time with rare rewards IS the lock regime, not the nway
regime — so M0 should not read "carry full@200" as "the question is
settled". What this slice establishes: (a) tau 200 is the peak in all
three rules — M0 sweeps nothing, it starts at 200; (b) the failure mode
of decay-alone is located (dense decisions), not mysterious; (c) the
runner-up, proportional@200 (+55.50 lock, −0.03/−0.07 dense in 41), is
the natural compromise candidate if M0's regime turns out mixed. A
continuous-time lockdown of rule-vs-regime belongs to M0 with its own
instrument, not to this slice.

## Privilege caveat

None needed beyond the usual: no oracle arms exist in this study, and no
schedule is granted.

## Evidence, phases and changed files

| Phase | Evidence | Status |
| --- | --- | --- |
| Registration | branch commit | Before any observation |
| Implementation/checks | branch commits | Before manifest freeze |
| Manifest freeze | eligible | Before screen |
| Screen | 3 rules × 3 taus × 8 seeds | 72 rows; candidate none@200 |
| Guard | candidate × 2 tasks × 8 seeds | 16 rows; vetoed |
| Reproduction/publication | All rows; twenty-five workflows | See validation below |

Frozen reference seeds 0–7. Bootstrap RNG 225000.

New files: `q2_rule.py`, `study_q2.py`, `report_q2.py`, `check_q2.py`,
`.github/workflows/q2-checks.yml`, the registration, this results file
and `results/q2/`. v1 sources untouched. Earlier evidence, protocols,
workflows, dependencies and defaults unchanged. No capability or registry
row is promoted.

The [generated report](results/q2/report.md) includes screen contrasts,
the decision trail, guard verdicts, and per-seed evidence.

## Validation and limits

All commands below passed locally, including reproduction of all 88 rows.
Python commands use the project's existing `.venv`:

```sh
python check_reference.py --out results/local-reference.json
python check_q2.py --evidence results/q2 --reproduce
python report_q2.py --check
python check_evidence.py
git diff --check
```

Checks cover harness fidelity (Rule == BrainSim and FastRule == Rule
head-to-head, full@200 reproduces the frozen lock column 8/8 EXACT),
paired contrasts, the decision procedure, invalid handling, immutable
sources/manifests, missing/non-finite evidence, and full archive
reproduction. The frozen 56-score reference passes unchanged. CI must
pass all twenty-five workflows before merge.

Lock-10 total reward is high-variance; n=8 paired, reported whole. Three
champion comparisons share one control — multiplicity disclosed,
adoption bar was paired lower > 0 outright. Seven tasks and one harness
cannot establish population guarantees.
