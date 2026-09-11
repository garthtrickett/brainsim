# Replay window sweep: lock-10 screen and collateral check

Disposition: **confirmed-20**.

| Stage | Rows |
| --- | ---: |
| screen | 40 |
| collateral | 0 |

## Screen (lock-10 total reward by window)

| Window | Mean | 95% interval |
| ---: | ---: | --- |
| 5 | 40.3750 | [27.1219, 55.3750] |
| 10 | 167.2500 | [123.8750, 223.7500] |
| 20 | 415.1250 | [331.5000, 511.7531] |
| 40 | 437.8750 | [252.4938, 604.8750] |
| 80 | 410.1250 | [226.4969, 574.3781] |

## Screen contrasts vs L=20 (paired, adopt needs lower > 0)

| Window | Treatment | Control | Delta | 95% interval | Pass |
| ---: | ---: | ---: | ---: | --- | --- |
| 5 | 40.3750 | 415.1250 | -374.7500 | [-461.7500, -297.6250] | False |
| 10 | 167.2500 | 415.1250 | -247.8750 | [-306.2500, -191.9969] | False |
| 40 | 437.8750 | 415.1250 | +22.7500 | [-124.3750, +141.7500] | False |
| 80 | 410.1250 | 415.1250 | -5.0000 | [-186.5094, +148.8750] | False |

## Scope and reproduction

Same-seed (0–7) paired design on the reference instrument; lock-10 is total reward (high variance, reported whole). Re-running a screened window on the same seeds is bit-identical, hence lock is excluded from stage 2 by design. Eight seeds cannot establish population guarantees.

`python check_Lsweep.py --evidence results/L-sweep --reproduce` regenerates every row at rtol1e-11/atol1e-13. `python report_Lsweep.py --check` verifies both generated reports.
