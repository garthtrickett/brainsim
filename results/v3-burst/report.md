# V3 bounded burst-controller experiment

Disposition: **awaiting_confirmation**.

| Stage | Rows |
| --- | ---: |
| tuning | 480 |
| confirmation | 0 |

Frozen strict detector threshold: 0.4690234346011377.

## Finite-menu tuning

All searched families: 12 configurations × 8 seeds × 5 fixtures. Objective: half primary post-switch MSE plus half mean of 14 retention metrics.

| Family | Index | Configuration | Tuning objective | Menu endpoint fields |
| --- | ---: | --- | ---: | --- |
| burst | 8 | `{"lr": 0.032, "factor": 2.0, "duration": 16, "beta2": 0.999}` | 0.176564 | lr, factor, duration |
| oracle | 10 | `{"lr": 0.032, "factor": 8.0, "duration": 16, "beta2": 0.999}` | 0.094467 | lr, factor, duration |
| continuous | 9 | `{"lr": 0.032, "gain": 8.0, "beta2": 0.999}` | 0.182309 | lr |
| adam | 10 | `{"lr": 0.128, "beta2": 0.999}` | 0.138365 | lr, beta2 |
| sgd | 8 | `{"lr": 0.128}` | 0.085671 | none |

Endpoints are reported, not expanded: these are fixed menus, not global optima. oracle_matched and random use burst settings exactly, with no additional tuning.

Frozen random opportunity probability: **0.000401142**, from 167 candidate starts / 421488 tuning coordinate-updates. Expected pooled frequency is matched; realized per-condition counts and movement are not.

## Measured row execution time

| Stage | Family | Seconds |
| --- | --- | ---: |
| tuning | burst | 5.76 |
| tuning | oracle | 3.69 |
| tuning | continuous | 4.09 |
| tuning | adam | 3.48 |
| tuning | sgd | 1.29 |

Each searched family executes 5,184,000 learner coordinate-updates. Times exclude archive writes and share a causal signal cache: the first family pays cache initialization. These are observed times, not equal CPU-cost claims.

## Scope and evidence

Rate caps do not cap realized Adam update norms. Perfect timing is privileged and is not a mathematical upper bound. The separately tuned oracle tests this finite controller menu; the matched oracle holds candidate parameters fixed. Random scheduling matches expected pooled frequency only, so actual activity and per-condition differences remain visible.

Candidate advancement requires >=10% primary improvement over Adam, SGD, continuous and random with paired upper delta <0, plus every retention upper delta <=max(.002,.1*control). No oracle or alarm score overrides that decision. A positive result would warrant only a separately authorized broader supervised benchmark; all outcomes close this registration.

Whole-seed intervals: 10,000 resamples, seed75000. The archive retains every reached row, tuning score, source snapshot, event start and candidate event-error/recovery record. Small synthetic fixtures and finite menus do not establish global optimizer superiority or a scalable reference-gradient mechanism. Every earlier study remains unchanged.

`python check_v3_burst.py --evidence results/v3-burst --reproduce` regenerates every reached row and manifest/summary at rtol1e-11/atol1e-13. `python report_v3_burst.py --check` checks both generated reports.
