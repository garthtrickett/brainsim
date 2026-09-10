# V2 M0-motor: 1-of-N without aggregates fails at chance

Per-tick 1-of-N motor selection scores **0.2663 on nway-4** (chance 0.25)
and **0.1281 on nway-8** (chance 0.125) — at chance on both, against
trial-aggregated 1-of-N at 0.9793/0.8938 and shipped global-kWTA at
0.9712/0.8670. The experiment closes as **learning_negative** on both
class counts, decisively: paired intervals miss by ~0.7, not by noise.

All **36 confirmation rows** were completed and finite. No default change,
no integration, no fork. Per the pre-stated rule, the motor-sparsity line
closes permanently and event-driven computing stays conditional forever.

## What was implemented

The [registration](DESIGN-v2-m0-motor.md) removes the vote aggregate in a
throwaway prototype harness: per-tick 1-of-N motor winners act every tick
(silence scores 0), each 30-tick trial pays fraction-correct reward once,
and eligibility is consumed on that reward. The MotorWTA step mirrors the
frozen `BrainSim.step` line-for-line except the motor block. All three arms
— per-tick candidate, trial-aggregated 1-of-N control, shipped ceiling —
share trial structure, rewards timing, and consumption; only action
selection differs.

No v1 source changed. No scientific source changed after the manifest
freeze.

## Independent confirmation

| Class count / arm | Per-tick accuracy | 95% interval | Winner rate |
| --- | ---: | --- | ---: |
| 4/pertick | 0.266337 | [0.264602,0.268298] | 1.0000 |
| 4/aggregate | 0.979278 | [0.977889,0.980501] | 1.0000 |
| 4/shipped | 0.971222 | [0.964222,0.976500] | 1.0000 |
| 8/pertick | 0.128119 | [0.127711,0.128467] | 1.0000 |
| 8/aggregate | 0.893833 | [0.886389,0.900278] | 1.0000 |
| 8/shipped | 0.867000 | [0.852833,0.881056] | 1.0000 |

| Contrast | Delta | 95% interval | Pass |
| --- | ---: | --- | --- |
| nway-4 beats_aggregate | -0.7129 | [-0.7152,-0.7107] | False |
| nway-4 matches_shipped | -0.7049 | [-0.7109,-0.6983] | False |
| nway-8 beats_aggregate | -0.7657 | [-0.7721,-0.7582] | False |
| nway-8 matches_shipped | -0.7389 | [-0.7530,-0.7250] | False |

## The stale premise, stated plainly

The re-implemented aggregate control scores 0.979/0.894 — nothing like the
0.319/0.158 that `19_local_alternatives.py` measured and V2.md bet against.
That old number was produced under ancient code carrying the decide() tie
bug the project later found depressed *every* n>2 result, with the
tie-heavy 1-of-N motor suffering most. Under current code, trial-aggregated
1-of-N learns about as well as shipped global-kWTA. V2.md's premise — "v1
tried motor sparsity and it failed" — does not survive contact with the
current sources: what failed then was substantially the tie bug, not
obviously sparsity.

This reframes rather than softens the verdict. Aggregation is doing the
work: the same single-winner motor that reaches 0.979 with votes collapses
to chance without them. Removing the aggregate destroys learning even where
sparsity itself is harmless. The per-tick regime fails on its own terms, in
the exact shape the registration named in advance.

## Privilege caveat

None needed beyond the usual: no oracle arms exist in this study, and no
schedule is granted. The comparison is between observable-derived policies
throughout.

## Evidence, phases and changed files

| Phase | Evidence | Status |
| --- | --- | --- |
| Registration | branch commit | Before study observations |
| Implementation/checks | branch commits | Before manifest freeze |
| Manifest freeze | eligible | Before confirmation |
| Confirmation | 3 arms × 6 seeds × 2 classes | 36 rows; learning-negative |
| Reproduction/publication | All rows; twenty-two workflows | See validation below |

Protocol `v2-m0-motor-20260910-v1`. Development seeds 300–305,
confirmation seeds 310–315, bootstrap RNG 225000. All ranges are fresh.

New files: `v2_m0.py`, `study_v2_m0.py`, `report_v2_m0.py`,
`check_v2_m0.py`, `.github/workflows/v2-m0-checks.yml`, the registration,
this results file and `results/v2-m0/`. v1 sources frozen; earlier evidence,
protocols, workflows, dependencies and defaults unchanged. No capability or
registry row is promoted.

The [generated report](results/v2-m0/report.md) includes per-class paired
contrasts, absolute accuracies with winner rates, and per-seed evidence.

## Validation and limits

All commands below passed locally, including reproduction of all 36 rows.
Python commands use the project's existing `.venv`:

```sh
python check_v2_m0.py --evidence results/v2-m0 --reproduce
python report_v2_m0.py --check
python check_reference.py --out results/local-reference.json
python check_evidence.py
git diff --check
```

Checks cover per-tick winner validity, harness causality (no vote-array
residue), silent-tick null scoring, paired contrasts, invalid handling,
immutable sources/manifests, missing/non-finite evidence, and full archive
reproduction. The frozen 56-score reference passes unchanged. CI must pass
all twenty-two workflows before merge.

Paired bootstrap intervals (10000 resamples, seed 225000) at six seeds are
descriptive; two class counts and one harness cannot establish population
guarantees, sparsity in general, or superiority over deep learning. The
authoritative outcome is the independent learning-negative result on both
class counts.
