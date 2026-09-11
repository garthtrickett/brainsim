# Q3 capacity: pools and scale on memorized combinations

Disposition: **dead-end**.

| Stage | Rows |
| --- | ---: |
| confirmation | 128 |

## Absolute train accuracy by cell (H/k/pools/combos)

| Cell | Mean | 95% interval |
| --- | ---: | --- |
| 80/6/1/4 | 0.9830 | [0.9772, 0.9879] |
| 80/6/1/9 | 0.9848 | [0.9800, 0.9896] |
| 80/6/1/16 | 0.9640 | [0.9591, 0.9692] |
| 80/6/2/4 | 0.9857 | [0.9730, 0.9943] |
| 80/6/2/9 | 0.9822 | [0.9742, 0.9892] |
| 80/6/2/16 | 0.9610 | [0.9517, 0.9700] |
| 80/6/3/4 | 0.9865 | [0.9814, 0.9911] |
| 80/6/3/9 | 0.9826 | [0.9766, 0.9880] |
| 80/6/3/16 | 0.9626 | [0.9521, 0.9712] |
| 80/6/6/4 | 0.9882 | [0.9841, 0.9923] |
| 80/6/6/9 | 0.9774 | [0.9719, 0.9832] |
| 80/6/6/16 | 0.9631 | [0.9556, 0.9710] |
| 160/12/1/9 | 0.7933 | [0.7560, 0.8351] |
| 160/12/1/16 | 0.6551 | [0.6249, 0.6819] |
| 160/12/4/9 | 0.7835 | [0.7484, 0.8195] |
| 160/12/4/16 | 0.5962 | [0.5076, 0.6710] |

## Paired contrasts (same-seed, same cell control)

| Contrast | Treatment | Control | Delta | 95% interval |
| --- | ---: | ---: | ---: | --- |
| 80/6/2/4-vs-P1 | 0.9857 | 0.9830 | +0.0028 | [-0.0053, +0.0091] |
| 80/6/2/9-vs-P1 | 0.9822 | 0.9848 | -0.0025 | [-0.0073, +0.0025] |
| 80/6/2/16-vs-P1 | 0.9610 | 0.9640 | -0.0030 | [-0.0094, +0.0034] |
| 80/6/3/4-vs-P1 | 0.9865 | 0.9830 | +0.0035 | [-0.0019, +0.0093] |
| 80/6/3/9-vs-P1 | 0.9826 | 0.9848 | -0.0021 | [-0.0059, +0.0015] |
| 80/6/3/16-vs-P1 | 0.9626 | 0.9640 | -0.0014 | [-0.0097, +0.0051] |
| 80/6/6/4-vs-P1 | 0.9882 | 0.9830 | +0.0053 | [-0.0003, +0.0098] |
| 80/6/6/9-vs-P1 | 0.9774 | 0.9848 | -0.0074 | [-0.0120, -0.0035] |
| 80/6/6/16-vs-P1 | 0.9631 | 0.9640 | -0.0009 | [-0.0099, +0.0074] |
| 160/12/4/9-vs-80P1 | 0.7835 | 0.9848 | -0.2012 | [-0.2354, -0.1657] |
| 160/12/1/9-vs-80P1 | 0.7933 | 0.9848 | -0.1915 | [-0.2280, -0.1511] |
| 160/12/4/16-vs-80P1 | 0.5962 | 0.9640 | -0.3678 | [-0.4556, -0.2915] |
| 160/12/1/16-vs-80P1 | 0.6551 | 0.9640 | -0.3089 | [-0.3376, -0.2851] |

Adopters: []; regressions: [].


## Scope and reproduction

Memorization capacity only (train accuracy, held_out=0): no generalisation claim. Total sparsity held constant across pools within each H, so differences are competition geometry. Same-seed pairing within cells; cross-seed generalisation out of scope.

`python check_q3.py --evidence results/q3 --reproduce` regenerates every row at rtol1e-11/atol1e-13. `python report_q3.py --check` verifies both generated reports.
