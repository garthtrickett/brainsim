# V2 M0-motor: 1-of-N without aggregates

Disposition: **learning_negative**.

| Stage | Rows |
| --- | ---: |
| confirmation | 36 |

## nway-4: fail

| Contrast | Treatment | Control | Delta | 95% interval | Pass |
| --- | ---: | ---: | ---: | --- | --- |
| beats_aggregate | 0.266337 | 0.979278 | -0.712941 | [-0.715209, -0.710672] | False |
| matches_shipped | 0.266337 | 0.971222 | -0.704885 | [-0.710913, -0.698346] | False |

## nway-8: fail

| Contrast | Treatment | Control | Delta | 95% interval | Pass |
| --- | ---: | ---: | ---: | --- | --- |
| beats_aggregate | 0.128119 | 0.893833 | -0.765715 | [-0.772056, -0.758161] | False |
| matches_shipped | 0.128119 | 0.867000 | -0.738881 | [-0.752954, -0.725037] | False |

## Absolute per-tick accuracy and winner rates

| Class count / arm | Accuracy | 95% interval | Winner rate |
| --- | ---: | --- | ---: |
| 4/pertick | 0.266337 | [0.264602, 0.268298] | 1.0000 |
| 4/aggregate | 0.979278 | [0.977889, 0.980501] | 1.0000 |
| 4/shipped | 0.971222 | [0.964222, 0.976500] | 1.0000 |
| 8/pertick | 0.128119 | [0.127711, 0.128467] | 1.0000 |
| 8/aggregate | 0.893833 | [0.886389, 0.900278] | 1.0000 |
| 8/shipped | 0.867000 | [0.852833, 0.881056] | 1.0000 |

## Scope and reproduction

Per-tick units throughout; silence scores 0. Cross-study comparison with v1 tail accuracies is forbidden. Six seeds cannot establish population guarantees. Every reached row and source is archived; prior studies remain intact.

`python check_v2_m0.py --evidence results/v2-m0 --reproduce` regenerates every reached row at rtol1e-11/atol1e-13. `python report_v2_m0.py --check` verifies both generated reports.
