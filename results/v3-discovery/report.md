# V3 interference-as-discovery

Disposition: **awaiting_confirmation**.

| Stage | Rows |
| --- | ---: |
| tuning | 480 |
| confirmation | 0 |

## Finite-menu tuning

Each searched family: 12 configurations × 8 seeds × 5 fixtures. Same objective: half primary post-switch MSE plus half mean of 14 retention metrics.

| Family | Index | Configuration | Tuning objective | Menu endpoint fields |
| --- | ---: | --- | ---: | --- |
| discover | 9 | `{"tau": 0.5, "alpha": 0.01, "cue_lr": 0.01, "lr": 0.2}` | 0.103299 | tau, alpha, cue_lr, lr |
| oracle | 4 | `{"tau": 0.05, "alpha": 0.1, "cue_lr": 0.01, "lr": 0.05}` | 0.032826 | tau, alpha, cue_lr, lr |
| window | 3 | `{"window": 8}` | 0.095185 | window |
| sgd | 8 | `{"lr": 0.128}` | 0.084388 | none |
| adwin | 9 | `{"delta": 0.1, "clock": 1}` | 0.127667 | delta, clock |

Endpoint choices remain in the registered finite menu; no extension or global-optimum claim. Matched oracle/random/shuffled/nocontext use the discover configuration without extra search.


## Measured execution time

| Stage | Family | Seconds |
| --- | --- | ---: |
| tuning | discover | 1.58 |
| tuning | oracle | 0.48 |
| tuning | window | 0.81 |
| tuning | sgd | 0.41 |
| tuning | adwin | 4.92 |

Each searched family consumes 5,184,000 coordinate observations. Configuration budgets are equal, not CPU costs.

## Scope and reproduction

Cues are evaluator-generated noisy observations of the hidden context (SEP=0.5, unit cue noise; single-sample AUC ≈ 0.76). y bytes are identical to the forgetting fixtures at equal seeds. Perfect context is privileged, not perfect prediction: conditionals must still learn each regime mean. No oracle or discovery outcome overrides candidate learning performance; MSE cannot pass the discovery gate either. Candidate success requires the gate plus all 90 comparisons, including >= 10% primary improvement and every retention bound. Oracle arms each have 45 comparisons. All outcomes close this registration.

Intervals resample whole seeds 10000 times with seed 95000. Finite menus and synthetic fixtures do not establish global optimizer superiority, population guarantees or general neural-memory utility. Every reached row and source is archived; prior studies remain intact.

`python check_v3_discovery.py --evidence results/v3-discovery --reproduce` regenerates every reached row and scientific manifest/summary at rtol1e-11/atol1e-13. `python report_v3_discovery.py --check` verifies both generated reports.
