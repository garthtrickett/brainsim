# V3 change-triggered forgetting

Disposition: **awaiting_confirmation**.

| Stage | Rows |
| --- | ---: |
| tuning | 480 |
| confirmation | 0 |

Frozen strict detector threshold: 0.4690234346011377.

## Finite-menu tuning

Each searched family: 12 configurations ×8 seeds ×5 fixtures. Same objective: half primary post-switch MSE plus half mean of14 retention metrics.

| Family | Index | Configuration | Tuning objective | Menu endpoint fields |
| --- | ---: | --- | ---: | --- |
| forget | 4 | `{"keep": 4, "window": 32}` | 0.127751 | window |
| oracle | 1 | `{"keep": 1, "window": 128}` | 0.024315 | keep |
| window | 3 | `{"window": 8}` | 0.096777 | none |
| sgd | 8 | `{"lr": 0.128}` | 0.085129 | none |
| adwin | 9 | `{"delta": 0.1, "clock": 1}` | 0.127719 | delta, clock |

Endpoint choices remain in the registered finite menu; no extension or global-optimum claim. Matched oracle/random use candidate K/W. Noreset_matched uses its exact W without resets.

Frozen random p=0.000480548543, from 201 requests / 421488 tuning coordinate-updates, corrected for16-update cooldown. Expected pooled frequency is matched, not actual counts or memory age.


## Measured execution time

| Stage | Family | Seconds |
| --- | --- | ---: |
| tuning | forget | 3.47 |
| tuning | oracle | 2.17 |
| tuning | window | 1.15 |
| tuning | sgd | 0.89 |
| tuning | adwin | 9.68 |

Each searched family consumes 5,184,000 coordinate observations. Times exclude archive writes and share cached gates; the first family pays cache initialization. Configuration budgets are equal, not CPU costs.

## Scope and reproduction

ADWIN2 is independently implemented from the paper: practical Eq.(3.1), five buckets per size, minimum subwindow5. Gaussian observations violate the bounded-input premise; no corresponding formal guarantee or library-release parity is claimed. All policies see unchanged raw observations.

Perfect timing is privileged, not perfect segmentation: retaining K>1 at the true event may retain old-regime data. No oracle or detector outcome overrides candidate performance. Candidate success requires all75 comparisons, including >=10% primary improvement and every retention bound. Oracle arms each have45 comparisons. All outcomes close this registration.

Intervals resample whole seeds10000 times with seed85000. Finite menus and synthetic fixtures do not establish global optimizer superiority, population guarantees or general neural-memory utility. Every reached row and source is archived; prior studies remain intact.

`python check_v3_forgetting.py --evidence results/v3-forgetting --reproduce` regenerates every reached row and scientific manifest/summary at rtol1e-11/atol1e-13. `python report_v3_forgetting.py --check` verifies both generated reports.
