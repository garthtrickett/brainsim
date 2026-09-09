# V3 separate-reference experiment

Disposition: **awaiting_diagnostics**.

| Stage | Rows |
| --- | ---: |
| calibration | 48 |
| diagnostics | 0 |
| performance | 0 |

## Fixed configurations and native thresholds

| Policy | Configuration | Fixed threshold | Active threshold |
| --- | --- | ---: | ---: |
| coupled | `{"lr": 0.004, "gain": 64.0, "beta2": 0.999}` | 0.469023 | 0.813103 |
| watch_adam | `{"lr": 0.004, "gain": 0.0, "beta2": 0.999}` | 0.469023 | 0.456573 |
| separate | `{"lr": 0.004, "gain": 64.0, "beta2": 0.999}` | 0.469023 | 0.469023 |
| adam | `{"lr": 0.032, "beta2": 0.9999}` | — | — |
| sgd | `{"lr": 0.035743040182210514}` | — | — |
| single | `{"lr": 0.016, "gain": 1.0, "beta2": 0.999}` | — | — |
| constant | `{"lr": 0.004, "gain": 64.0, "beta2": 0.999}` | — | — |

## Limits

Separate observes a fixed zero reference. Its fixed/active gate sequences are identical by construction; their two sets of cells are not independent replications. The toy exposes supervised observations; this does not establish an efficient reference-gradient mechanism for a general neural model.

Native detector criteria remain >=80% target detection and <=5% false alarms in every registered cell, including mixed changes. All 90 performance contrasts must pass for positive. Settings are fixed/transferred, not globally optimized; matching mean q does not match realized update norms. A common-threshold improvement cannot repair the native decision. Diagnostic prediction metrics cannot substitute for the independent performance partition.

Intervals use 10,000 whole-seed bootstrap resamples, seed 65000. Point screens and degenerate zero/one-rate bootstrap intervals are not population guarantees. No agent/default integration follows. Every old experiment remains intact.

Reproduce every reached row and summary with `python check_v3_reference.py --evidence results/v3-reference --reproduce`; check this report with `python report_v3_reference.py --check`. Numerical tolerance is rtol 1e-11/atol 1e-13, excluding only timing and regenerated input hashes.
