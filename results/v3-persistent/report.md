# V3 persistent detector experiment

Disposition: **awaiting_diagnostics**.

Four fixed detector policies; no hyperparameter selection. Calibration precedes fresh confirmation. All 24 candidate cells must pass before independent performance.

| Stage | Rows |
| --- | ---: |
| calibration | 64 |
| diagnostics | 0 |
| performance | 0 |

## Fixed policies and thresholds

| Policy | Configuration | Fixed threshold | Closed threshold |
| --- | --- | ---: | ---: |
| current | `{"lr": 0.004, "gain": 64.0, "beta2": 0.999}` | 0.21194271589472133 | 0.19560052134623715 |
| persistence | `{"lr": 0.004, "gain": 64.0, "beta2": 0.999}` | 0.15631722071536694 | 0.1519824470480801 |
| candidate | `{"lr": 0.004, "gain": 64.0, "beta2": 0.999}` | 0.4682240285231746 | 0.8161801210201912 |
| cusum | `{"lr": 0.004, "gain": 64.0, "beta2": 0.999}` | 0.32808257365743465 | 0.3014929352662185 |
| sgd | `{"lr": 0.035743040182210514}` | — | — |
| adam | `{"lr": 0.032, "beta2": 0.9999}` | — | — |
| single | `{"lr": 0.016, "gain": 1.0}` | — | — |
| constant | `{"lr": 0.004, "gain": 64.0, "beta2": 0.999}` | — | — |

## Interpretation and limits

Only stationary core coordinates use block alarm rates as false alarms. Mixed increase_first pairs target-down with noise increase and target-up with noise decrease; decrease_first reverses that pairing. Each direction remains separate. Exactly quiet and drift are descriptive.

Intervals resample whole seeds (10,000 resamples, seed 55000). Rate thresholds are point screens, not population guarantees. Four overlapping signed scores are correlated, not four independent pieces of evidence. The standardized mean score is not a calibrated p-value. The CUSUM reference uses moving estimates and empirical calibration, not known-parameter textbook guarantees.

All settings are transferred or fixed before data. This tests specified finite policies, not globally optimal tuning or optimizer-wide superiority. Passing detection alone establishes no learning gain. A failure closes this experiment; a positive performance result warrants only a separately registered agent experiment. No existing result or default is changed.

Reproduce every reached row and decision with `python check_v3_persistent.py --evidence results/v3-persistent --reproduce`. Verify this report with `python report_v3_persistent.py --check`. Only timings and regenerated scientific-input hashes are excluded from numerical reproduction.
