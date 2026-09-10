# V5 embodied volatility

Disposition: **learning_negative**.

| Stage | Rows |
| --- | ---: |
| calibration | 2 levels |
| usable | [0.25, 0.5] |
| confirmation | 96 |

## Calibration (floor / ceiling / baseline, tail reward rate)

| Noise σ | Floor | Ceiling | Baseline | Position | Usable |
| --- | ---: | ---: | ---: | ---: | ---: |
| 0.25 | 0.249524 | 1.000000 | 0.406349 | 0.21 | True |
| 0.5 | 0.249524 | 1.000000 | 0.363810 | 0.15 | True |

## Noise σ=0.25: learning_negative

Gain = endo minus baseline (paired); headroom = oracle minus endo (paired). A pass needs both intervals strictly above zero.

| Endo arm | Gain Δ | 95% interval | Headroom Δ | 95% interval | Pass |
| --- | ---: | --- | ---: | --- | --- |
| burstA | 0.0579 | [-0.0143, 0.1379] | -0.0645 | [-0.1621, 0.0426] | False |
| burstB | -0.0267 | [-0.0619, 0.0071] | 0.0200 | [-0.0188, 0.0693] | False |
| dualV | 0.0060 | [-0.0343, 0.0479] | 0.0662 | [-0.0210, 0.1300] | False |

## Noise σ=0.5: learning_negative

Gain = endo minus baseline (paired); headroom = oracle minus endo (paired). A pass needs both intervals strictly above zero.

| Endo arm | Gain Δ | 95% interval | Headroom Δ | 95% interval | Pass |
| --- | ---: | --- | ---: | --- | --- |
| burstA | 0.0233 | [-0.0386, 0.0929] | -0.0448 | [-0.1031, 0.0033] | False |
| burstB | -0.0469 | [-0.0850, -0.0105] | 0.0255 | [0.0052, 0.0481] | False |
| dualV | -0.0140 | [-0.0257, -0.0036] | 0.0531 | [0.0143, 0.0919] | False |

## Scope and reproduction

Paired seed design; intervals resample whole seeds10000 times with seed205000. Eight seeds cannot establish population guarantees or embodiment in general. Oracle twins are privileged bounds, never deployable arms. Every reached row and source is archived; prior studies remain intact.

`python check_v5.py --evidence results/v5 --reproduce` regenerates every reached row and scientific manifest/summary at rtol1e-11/atol1e-13. `python report_v5.py --check` verifies both generated reports.
