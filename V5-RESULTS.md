# V5 embodied volatility closes learning-negative

No toolkit arm beats the frozen ADAPTIVE baseline on either noisy-volatile
task. The experiment closes as **learning_negative** on both levels, with
one significant harm (strong bursts at σ=0.5: -0.047 [-0.085, -0.011]) and
one genuine negative with headroom (dualV at σ=0.5 fails while its oracle
twin gains +0.053). Everything else is indistinguishable from baseline.

Both noise levels calibrated usable (baseline 21% and 15% of the way from
floor to ceiling). All **96 confirmation rows** were completed and finite.
No new default, embodiment benchmark, mechanism change or agent integration
is activated.

## What was implemented

The [registration](DESIGN-v5-embodied.md) grafts switch-gated LR bursts
(endo and oracle twins at two strengths) and dual-timescale value blending
(endo and oracle) onto the frozen v1 agent via additive default-off flags,
and tests them on NoisyVolatile tasks (Volatile-4 with stationary
observation noise σ ∈ {0.25, 0.5}) the deterministic suite cannot probe.
Six arms, eight paired seeds per usable level, tail reward rate over 2100
decisions (7 contingency switches), seed-paired bootstrap intervals.

No scientific source changed after calibration began.

## Calibration: both levels usable

| Noise σ | Floor | Ceiling | Baseline | Position | Usable |
| --- | ---: | ---: | ---: | ---: | ---: |
| 0.25 | 0.2495 | 1.0000 | 0.4063 | 0.21 | True |
| 0.5 | 0.2495 | 1.0000 | 0.3638 | 0.15 | True |

## Independent confirmation

| Endo arm, σ=0.25 | Gain Δ | 95% interval | Headroom Δ | 95% interval |
| --- | ---: | --- | ---: | --- |
| burstA (1.0,2,50) | +0.0579 | [-0.0143,+0.1379] | -0.0645 | [-0.1621,+0.0426] |
| burstB (1.5,4,100) | -0.0267 | [-0.0619,+0.0071] | +0.0200 | [-0.0188,+0.0693] |
| dualV | +0.0060 | [-0.0343,+0.0479] | +0.0662 | [-0.0210,+0.1300] |

| Endo arm, σ=0.5 | Gain Δ | 95% interval | Headroom Δ | 95% interval |
| --- | ---: | --- | ---: | --- |
| burstA (1.0,2,50) | +0.0233 | [-0.0386,+0.0929] | -0.0448 | [-0.1031,+0.0033] |
| burstB (1.5,4,100) | -0.0469 | [-0.0850,-0.0105] | +0.0255 | [+0.0052,+0.0481] |
| dualV | -0.0140 | [-0.0257,-0.0036] | +0.0531 | [+0.0143,+0.0919] |

Oracle-timed bursts do not beat baseline either — at σ=0.25 the oracle twin
sits *below* its endo arm — so three of the six comparisons are void-leaning
rather than informative: perfectly-timed discrete bursts buy nothing in the
agent, which means endogenous ones failing says little. The dualV pair at
σ=0.5 is the experiment's one sharp result: headroom exists (+0.053) and the
endogenous composition cannot take it (-0.014).

## Reading

The agent's continuous ADAPTIVE modulation already prices in what
volatility-gating can buy; discrete bursts add nothing (strong ones harm),
and dual-timescale value cannot convert demonstrated headroom. Embodiment
did not redeem the toolkit — the v1 agent's own surprise machinery marks
the spot, but neither bursts nor a second value head dig there. The
falsifier as stated closes this experiment negative.

## Privilege caveat

Oracle twins are privileged bounds, never deployable arms. Nothing here
advances a default or an integration.

## Evidence, phases and changed files

| Phase | Evidence | Status |
| --- | --- | --- |
| Registration/refinement | branch commit | Before study observations |
| Implementation/checks | branch commits | Before calibration |
| Calibration | 2 levels | Eligible; both usable |
| Confirmation | 6 arms × 8 seeds × 2 levels | 96 rows; learning-negative |
| Reproduction/publication | All rows; twenty workflows | See validation below |

Protocol `v5-embodied-20260910-v1`. Calibration agent seeds 100–102/task
100; confirmation agent 110–117/task 110; bootstrap RNG 205000. All ranges
are fresh; v1's seeds are not reused for measurement.

New files: `v5_tasks.py`, `study_v5.py`, `report_v5.py`, `check_v5.py`,
`.github/workflows/v5-embodied-checks.yml`, the registration, this results
file and `results/v5/`. Modified: `brainsim.py` (additive default-off flags
only; defaults-off output verified bit-identical against pre-change code).
Earlier scientific sources, evidence, protocols, all nineteen previous
workflows, dependencies and agent defaults remain unchanged. No capability
or registry row is promoted.

The [generated report](results/v5/report.md) includes the calibration
table, all six paired contrasts with headroom checks, and per-seed evidence.

## Validation and limits

All commands below passed locally, including reproduction of all
calibration and confirmation rows. Python commands use the project's
existing `.venv`:

```sh
python check_v5.py --evidence results/v5 --reproduce
python report_v5.py --check
python check_reference.py --out results/local-reference.json
python check_evidence.py
git diff --check
```

Checks cover noisy-task RNG preservation, runner parity with `tasks.run`,
defaults-off flag parity, oracle-mark provenance, paired-seed discipline,
calibration math, invalid/non-finite records, immutable sources/manifests/
stages, and full archive reproduction. The frozen 56-score reference passes
unchanged (defaults-off bit-identity verified hash-equal pre/post change).
CI must pass all twenty workflows before merge.

Paired bootstrap intervals (10000 resamples, seed 205000) at eight seeds are
descriptive; two noise levels and one agent architecture cannot establish
population guarantees, embodiment in general, or superiority over deep
learning. The authoritative outcome is the independent learning-negative
result on both levels.
