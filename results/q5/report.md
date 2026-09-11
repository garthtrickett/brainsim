# Q5 rank-1 eligibility: trace pair vs per-synapse matrix

Disposition: **replaceable**.

| Stage | Rows |
| --- | ---: |
| confirmation | 112 |

## nway-4: within band

| rank1 mean | frozen mean | delta | 95% interval | band | Pass |
| ---: | ---: | ---: | --- | ---: | --- |
| 0.997375 | 0.996875 | 0.000500 | [-0.001250, 0.001750] | 0.030000 | True |

## nway-8: within band

| rank1 mean | frozen mean | delta | 95% interval | band | Pass |
| ---: | ---: | ---: | --- | ---: | --- |
| 0.979500 | 0.978250 | 0.001250 | [-0.005750, 0.008000] | 0.030000 | True |

## xor-2: within band

| rank1 mean | frozen mean | delta | 95% interval | band | Pass |
| ---: | ---: | ---: | --- | ---: | --- |
| 0.824625 | 0.825250 | -0.000625 | [-0.009750, 0.007375] | 0.030000 | True |

## volatile-4: within band

| rank1 mean | frozen mean | delta | 95% interval | band | Pass |
| ---: | ---: | ---: | --- | ---: | --- |
| 0.397250 | 0.371500 | 0.025750 | [-0.100250, 0.149753] | 0.030000 | True |

## tmaze-within-30: within band

| rank1 mean | frozen mean | delta | 95% interval | band | Pass |
| ---: | ---: | ---: | --- | ---: | --- |
| 0.998583 | 0.999250 | -0.000667 | [-0.001250, -0.000083] | 0.030000 | True |

## tmaze-within-60: within band

| rank1 mean | frozen mean | delta | 95% interval | band | Pass |
| ---: | ---: | ---: | --- | ---: | --- |
| 0.998083 | 0.998250 | -0.000167 | [-0.000833, 0.000500] | 0.030000 | True |

## lock-10: within band

| rank1 mean | frozen mean | delta | 95% interval | band | Pass |
| ---: | ---: | ---: | --- | ---: | --- |
| 429.875000 | 415.125000 | 14.750000 | [-7.628125, 37.375000] | 41.512500 | True |

## Absolute scores by arm

| Task / arm | Mean | 95% interval |
| --- | ---: | --- |
| nway-4/shipped | 0.996875 | [0.995375, 0.998250] |
| nway-4/rank1 | 0.997375 | [0.996000, 0.998625] |
| nway-8/shipped | 0.978250 | [0.972500, 0.982625] |
| nway-8/rank1 | 0.979500 | [0.973750, 0.985003] |
| xor-2/shipped | 0.825250 | [0.810000, 0.844000] |
| xor-2/rank1 | 0.824625 | [0.808500, 0.843000] |
| volatile-4/shipped | 0.371500 | [0.292372, 0.444125] |
| volatile-4/rank1 | 0.397250 | [0.298488, 0.491634] |
| tmaze-within-30/shipped | 0.999250 | [0.998750, 0.999750] |
| tmaze-within-30/rank1 | 0.998583 | [0.998083, 0.999167] |
| tmaze-within-60/shipped | 0.998250 | [0.996833, 0.999417] |
| tmaze-within-60/rank1 | 0.998083 | [0.997000, 0.999000] |
| lock-10/shipped | 415.125000 | [331.500000, 511.753125] |
| lock-10/rank1 | 429.875000 | [344.625000, 527.125000] |

## Scope and reproduction

Same-seed paired design against the frozen reference instrument: the claim is equivalence on the reference table, not cross-seed generalisation. ebar stays M×H in both arms (common infrastructure); the full 12B→4B lever needs a follow-up slice. Eight seeds cannot establish population guarantees.

`python check_q5.py --evidence results/q5 --reproduce` regenerates every row at rtol1e-11/atol1e-13. `python report_q5.py --check` verifies both generated reports.
