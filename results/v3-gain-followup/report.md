# V3 bounded gain follow-up

Overall disposition: **awaiting_diagnostics**.

Search disposition: **eligible**. Search limits and detector findings are separate.

## Frozen tuning choices

| Arm | Configuration | Added step amplitude (lr × gain) | Tuning excess MSE |
| --- | --- | ---: | ---: |
| sgd | `{"lr": 0.035743040182210514}` | — | 0.02050238 |
| adam | `{"lr": 0.032, "beta2": 0.9999}` | — | 0.01906885 |
| single | `{"lr": 0.016, "gain": 1.0}` | 0.016 | 0.01934858 |
| historical | `{"lr": 0.016, "gain": 8.0}` | 0.128 | 0.01877149 |
| candidate | `{"lr": 0.004, "gain": 64.0}` | 0.256 | 0.01230101 |

## Reached stages

| Stage | Rows | Status |
| --- | ---: | --- |
| tuning | 3840 | complete |
| calibration | 48 | complete |
| diagnostics | 0 | pending |
| performance | 0 | pending |

## Limits and decision

Five arms each receive 48 configurations × 16 tuning seeds × 6,000 four-coordinate observations: 3,840 trajectories, 92,160,000 coordinate updates. Tuning scores are selected training evidence, not independent performance results. The kernel, tasks and metrics are unchanged from slice1.

A wider-search boundary flag remains an unresolved search limit. This follow-up independently tests the detector at a specified finite configuration even with such a flag; it cannot run performance unless search adequacy AND every detector criterion pass. No existing experiment was reopened or its outcome changed. No automatic grid extension or agent integration follows.

A detector-negative result rejects the claimed detection behavior of this specified signal/policy on these fixtures, not all v3 ideas. A positive result would justify only a separately registered agent experiment. The synthetic separable coordinates do not test representation interference. Detector rate thresholds are point screens, not population-wide guarantees.

Reproduce with `python check_v3_gain.py --evidence results/v3-gain-followup --reproduce`; check this generated report with `python report_v3_gain.py --check`. Every reached scientific row, selection, calibrated threshold and decision is checked. Only timing and regenerated input hashes are excluded from numerical comparisons.
