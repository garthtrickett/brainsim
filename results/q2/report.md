# Q2 consumption × tau: screen, selection, guard

Disposition: **vetoed-none-200**.

| Stage | Rows |
| --- | ---: |
| screen | 72 |
| guard | 16 |

## Screen (lock-10 total reward)

| Rule / tau | Mean | 95% interval | Paired delta vs full@200 | 95% interval |
| --- | ---: | --- | ---: | --- |
| full/100 | 389.88 | [248.73, 527.88] | -25.25 | [-107.38, +36.50] |
| full/200 | 415.12 | [331.50, 511.75] | +0.00 | [+0.00, +0.00] |
| full/400 | 416.50 | [334.25, 508.00] | +1.38 | [-13.12, +14.38] |
| none/100 | 474.12 | [359.25, 595.62] | +59.00 | [+3.25, +105.88] |
| none/200 | 544.75 | [452.37, 655.25] | +129.62 | [+91.88, +158.00] |
| none/400 | 495.50 | [328.49, 636.88] | +80.38 | [-34.50, +162.38] |
| proportional/100 | 459.25 | [368.25, 552.50] | +44.12 | [+21.75, +68.88] |
| proportional/200 | 470.62 | [378.62, 573.88] | +55.50 | [+25.00, +82.75] |
| proportional/400 | 463.75 | [304.62, 600.88] | +48.62 | [-54.12, +115.12] |

Candidate: **none@200**.

## Dense guard (candidate vs frozen, band ±0.03)

| Task | Delta | 95% interval | Pass |
| --- | ---: | --- | --- |
| nway-8 | -0.096500 | [-0.106750, -0.087250] | False |
| volatile-4 | -0.017500 | [-0.098375, +0.061128] | True |

## Scope and reproduction

Same-seed (0–7) paired design on the reference instrument; lock-10 is total reward (high variance, reported whole). Three champion comparisons share one control — multiplicity disclosed, adoption bar is paired lower > 0 outright. Eight seeds cannot establish population guarantees.

`python check_q2.py --evidence results/q2 --reproduce` regenerates every row at rtol1e-11/atol1e-13. `python report_q2.py --check` verifies both generated reports.
