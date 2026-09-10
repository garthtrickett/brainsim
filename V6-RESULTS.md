# V6 margin-directed exploration closes learning-negative

No explorer beats the frozen baseline on any task. The experiment closes as
**learning_negative** overall, with one task-level **no_verdict** (noisy) and
two informative failures (volatile, lock) — both in the harmful direction.

All **96 confirmation rows** were completed and finite. No new default,
benchmark, mechanism change or agent integration is activated.

## What was implemented

The [registration](DESIGN-v6-explore.md) adds two default-off flags to the
frozen agent: margin-directed uniform deviation (EXPLORE_K = 0.5 / 2.0,
driven by pre-reset vote closeness) and epsilon-correct oracle exploration
(ε = 0.1, label via a new `decide()` keyword the study passes only to the
oracle arm). Tested on volatile-4, noisy-volatile σ=0.5, and lock-10 — the
last because exploration matters most under sparsity. Four arms, eight
paired seeds per task, frozen metric scales.

No scientific source changed after the manifest freeze.

## Task usability (remeasured baseline vs frozen bounds)

| Task | Floor | Ceiling | Baseline | Position | Verdict |
| --- | ---: | ---: | ---: | ---: | --- |
| volatile | 0.251 | 1.0 | 0.331 | 0.11 | learning_negative |
| noisy | 0.2495 | 1.0 | 0.316 | 0.09 | no_verdict |
| lock | 12.5 | 1333.0 | 475.0 | 0.35 | learning_negative |

The noisy task remeasured at 0.09 — just below the 10% band (V5 saw 0.15 on
different seeds) — and closed without a verdict exactly as the USABLE rule
requires. Sampling variation at this distance from the floor moves tasks
across the line; the rule held rather than the data being stretched.

## Independent confirmation

| Explorer, volatile | Gain Δ | 95% interval | Headroom Δ | 95% interval |
| --- | ---: | --- | ---: | --- |
| exploreA (k=0.5) | -0.0626 | [-0.0986,-0.0238] | +0.1590 | [+0.1128,+0.1995] |
| exploreB (k=2.0) | -0.0745 | [-0.1124,-0.0293] | +0.1710 | [+0.1286,+0.2107] |

| Explorer, lock | Gain Δ | 95% interval | Headroom Δ | 95% interval |
| --- | ---: | --- | ---: | --- |
| exploreA (k=0.5) | -340.3750 | [-405.6281,-274.2500] | +449.1250 | [+375.2469,+514.3750] |
| exploreB (k=2.0) | -462.8750 | [-549.1250,-390.6250] | +571.6250 | [+499.0000,+647.8750] |

Deviation on narrow margins is actively harmful — on lock, catastrophically
so — while the oracle shows headroom in the hundreds of points. Exploration
matters enormously here and margin-uniform randomization points the wrong
way: narrow margins coincide with states where the argmax is right but
uncertain, and randomizing there throws away wins. The failure is
informative precisely because the headroom is real — the gap is
*discrimination*, not exploration volume.

## Privilege caveat

The oracle is a privileged bound, never a deployable arm. Nothing here
advances a default or an integration.

## Evidence, phases and changed files

| Phase | Evidence | Status |
| --- | --- | --- |
| Registration/refinement | `c3901e6` | Before study observations |
| Implementation/checks | `8e647a9` | Before manifest freeze |
| Manifest freeze | usable all three tasks | Before confirmation |
| Confirmation | 4 arms × 8 seeds × 3 tasks | 96 rows; learning-negative |
| Reproduction/publication | All rows; twenty-one workflows | See validation below |

Protocol `v6-explore-20260910-v1`. Agent seeds 130–137, task seed 130,
bootstrap RNG 215000. All ranges are fresh; no prior study's seeds are
reused for measurement.

New files: `study_v6.py`, `report_v6.py`, `check_v6.py`,
`.github/workflows/v6-explore-checks.yml`, the registration, this results
file and `results/v6/`. Modified: `brainsim.py` (additive default-off flags
only; defaults-off output verified bit-identical against pre-change code).
Earlier scientific sources, evidence, protocols, all twenty previous
workflows, dependencies and agent defaults remain unchanged. No capability
or registry row is promoted.

The [generated report](results/v6/report.md) includes task usability,
all paired contrasts with headroom checks, and per-seed evidence.

## Validation and limits

All commands below passed locally, including reproduction of all
confirmation rows. Python commands use the project's existing `.venv`:

```sh
python check_v6.py --evidence results/v6 --reproduce
python report_v6.py --check
python check_reference.py --out results/local-reference.json
python check_evidence.py
git diff --check
```

Checks cover closeness math on hand vote vectors, deviation provenance
(correct label reaches only the oracle arm), defaults-off flag parity,
paired-seed discipline, calibration math, invalid/non-finite records,
immutable sources/manifests, and full archive reproduction. The frozen
56-score reference passes unchanged. CI must pass all twenty-one workflows
before merge.

Paired bootstrap intervals (10000 resamples, seed 215000) at eight seeds are
descriptive; three tasks and one agent architecture cannot establish
population guarantees, exploration in general, or superiority over deep
learning. The authoritative outcome is the independent learning-negative
result on volatile and lock, with noisy closed without verdict.
