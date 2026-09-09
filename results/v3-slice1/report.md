# Slice1 registered result

Status: **tuning_inconclusive**.

This is the mean-disagreement successor, not a revision of the original centered-variance result. The registered scientific gates determine the disposition.

## Tuning choices

| Arm | Configuration | Tuning excess MSE |
| --- | --- | ---: |
| sgd | `{"lr": 0.0406158598837698}` | 0.01983428 |
| adam | `{"lr": 0.016, "beta2": 0.9999}` | 0.02167431 |
| single | `{"lr": 0.016, "gain": 1.0}` | 0.01859112 |
| historical | `{"lr": 0.016, "gain": 8.0}` | 0.01756072 |
| candidate | `{"lr": 0.004, "gain": 64.0}` | 0.01188590 |

## Screening reasons

- candidate: selected gain 64 is a search boundary

## Reached evidence

| Stage | Rows | Disposition |
| --- | ---: | --- |
| tuning | 1920 | complete |
| calibration | 0 | not run: prerequisite failed |
| diagnostics | 0 | not run: prerequisite failed |
| performance | 0 | not run: prerequisite failed |

## Interpretation

The bounded search did not establish adequate tuning. No independent detector or performance confirmation was run. These selected tuning scores are not held-out evidence of superiority or a refutation of the candidate. The registered rule requires closure without grid extension or integration.

## Limits and reproducibility

Five tuned arms receive 24 configurations × 16 seeds × 6,000 four-coordinate observations: 1,920 trajectories and 46,080,000 coordinate updates. The constant ablation, if reached, is derived from calibration without an extra tuning search. Gate timescales are fixed. Point detector screens and percentile intervals do not establish universal guarantees. These are separable quadratics, not agent tasks.

State used by the mathematical updates differs across arms, but the simple reference kernel allocates seven width-sized state arrays for every arm plus recorded output arrays. No optimized memory-cost advantage is claimed. High-resolution elapsed seconds are archived for learning runs and excluded from scientific reproduction.

Run `python check_v3_slice1.py --evidence results/v3-slice1 --reproduce` and `python report_v3_slice1.py --check`. Validation requires every reached scientific row, recomputed selections/decisions, unchanged source hashes, and absence of forbidden later-stage evidence. The older V1/V3 gates remain independent.
