# V3 drift-boundary schedule

Disposition: **learning_negative**.

| Stage | Rows |
| --- | ---: |
| tuning | 288 |
| confirmation | 192 |

## Finite-menu tuning

Each searched family: 12 configurations ×8 seeds ×5 fixtures. Same objective: half primary post-switch MSE plus half mean of14 retention metrics. The candidate configuration is frozen from the retention manifest; enriched-schedule arms run in confirmation only.

| Family | Index | Configuration | Tuning objective | Menu endpoint fields |
| --- | ---: | --- | ---: | --- |
| window | 3 | `{"window": 8}` | 0.101396 | none |
| sgd | 8 | `{"lr": 0.128}` | 0.085293 | none |
| adwin | 9 | `{"delta": 0.1, "clock": 1}` | 0.127305 | delta, clock |

Endpoint choices remain in the registered finite menu; no extension or global-optimum claim. Oracle_nofallback is the fixed fast base on the enriched schedule. Random_drift uses the frozen candidate configuration.

Frozen random p=0.000185735513, from 80 enriched requests / 432000 tuning coordinate-updates, 16-update suppression, opportunities from t0. Expected pooled frequency is matched, not actual counts or memory age.


## Independent primary performance

| Policy | Finite seeds | Primary MSE | 95% interval |
| --- | ---: | ---: | --- |
| window | 32 | 0.126196 | [0.1223794077355737, 0.13006084730166248] |
| sgd | 32 | 0.118311 | [0.11542929106849112, 0.12126419393640278] |
| adwin | 32 | 0.199363 | [0.1956488000965471, 0.20315793640037794] |
| retain_drift | 32 | 0.083613 | [0.08018084773953582, 0.08721832061243846] |
| oracle_nofallback | 32 | 0.085909 | [0.08281361194472928, 0.08908326192512467] |
| random_drift | 32 | 0.199235 | [0.1953488020993503, 0.20319925958607885] |

## retain_drift: learning_negative

All75 comparisons are required: >=10% primary improvement over window/sgd/adwin/random_drift, primary preservation against oracle_nofallback, every retention bound, and strict improvement on the8 stable/noise cells against oracle_nofallback (both-perfect cells pass as preservation).

| Contrast | Mode | Control | Policy | Delta | 95% interval | Pass |
| --- | --- | ---: | ---: | ---: | --- | --- |
| window/primary | improve | 0.126196 | 0.083613 | -0.042583 | [-0.046238, -0.039029] | True |
| window/quiet | preserve | 0.000310 | 0.000001 | -0.000309 | [-0.000313, -0.000304] | True |
| window/noisy | preserve | 0.124671 | 0.000736 | -0.123935 | [-0.125795, -0.122045] | True |
| window/switch_quiet | preserve | 0.063999 | 0.067590 | 0.003591 | [0.003037, 0.004136] | True |
| window/switch_noisy | preserve | 0.181877 | 0.100257 | -0.081620 | [-0.091659, -0.071932] | True |
| window/noise_jump | preserve | 0.048572 | 0.000606 | -0.047966 | [-0.049482, -0.046436] | True |
| window/drift | preserve | 0.000319 | 0.003115 | 0.002796 | [0.002765, 0.002825] | False |
| window/exactly_quiet | preserve | 0.000000 | 0.000000 | 0.000000 | [0.000000, 0.000000] | True |
| window/noise_jump/noise_increase | preserve | 0.118522 | 0.003449 | -0.115073 | [-0.122806, -0.107515] | True |
| window/noise_jump/noise_decrease | preserve | 0.003431 | 0.000568 | -0.002863 | [-0.004498, -0.001586] | True |
| window/drift/drift | preserve | 0.000334 | 0.007974 | 0.007640 | [0.007426, 0.007851] | False |
| window/mixed/increase_first/post_mse | preserve | 0.126994 | 0.082106 | -0.044888 | [-0.053478, -0.036774] | True |
| window/mixed/increase_first/stable_mse | preserve | 0.047703 | 0.000802 | -0.046902 | [-0.049006, -0.044804] | True |
| window/mixed/decrease_first/post_mse | preserve | 0.131914 | 0.084499 | -0.047415 | [-0.052941, -0.041818] | True |
| window/mixed/decrease_first/stable_mse | preserve | 0.078950 | 0.000908 | -0.078042 | [-0.080127, -0.075870] | True |
| sgd/primary | improve | 0.118311 | 0.083613 | -0.034698 | [-0.037427, -0.031966] | True |
| sgd/quiet | preserve | 0.000169 | 0.000001 | -0.000169 | [-0.000172, -0.000166] | True |
| sgd/noisy | preserve | 0.068177 | 0.000736 | -0.067441 | [-0.068673, -0.066234] | True |
| sgd/switch_quiet | preserve | 0.083478 | 0.067590 | -0.015888 | [-0.016360, -0.015435] | True |
| sgd/switch_noisy | preserve | 0.149368 | 0.100257 | -0.049111 | [-0.056042, -0.042193] | True |
| sgd/noise_jump | preserve | 0.026559 | 0.000606 | -0.025954 | [-0.026848, -0.025071] | True |
| sgd/drift | preserve | 0.000196 | 0.003115 | 0.002919 | [0.002891, 0.002947] | False |
| sgd/exactly_quiet | preserve | 0.000000 | 0.000000 | -0.000000 | [-0.000000, -0.000000] | True |
| sgd/noise_jump/noise_increase | preserve | 0.064566 | 0.003449 | -0.061117 | [-0.065293, -0.056961] | True |
| sgd/noise_jump/noise_decrease | preserve | 0.001912 | 0.000568 | -0.001344 | [-0.002293, -0.000502] | True |
| sgd/drift/drift | preserve | 0.000237 | 0.007974 | 0.007736 | [0.007525, 0.007944] | False |
| sgd/mixed/increase_first/post_mse | preserve | 0.118004 | 0.082106 | -0.035899 | [-0.041746, -0.030368] | True |
| sgd/mixed/increase_first/stable_mse | preserve | 0.026266 | 0.000802 | -0.025465 | [-0.026764, -0.024216] | True |
| sgd/mixed/decrease_first/post_mse | preserve | 0.122395 | 0.084499 | -0.037896 | [-0.042151, -0.033550] | True |
| sgd/mixed/decrease_first/stable_mse | preserve | 0.043338 | 0.000908 | -0.042430 | [-0.043662, -0.041106] | True |
| adwin/primary | improve | 0.199363 | 0.083613 | -0.115750 | [-0.119097, -0.112385] | True |
| adwin/quiet | preserve | 0.000001 | 0.000001 | 0.000000 | [0.000000, 0.000000] | True |
| adwin/noisy | preserve | 0.000736 | 0.000736 | 0.000000 | [0.000000, 0.000000] | True |
| adwin/switch_quiet | preserve | 0.150857 | 0.067590 | -0.083267 | [-0.085526, -0.081002] | True |
| adwin/switch_noisy | preserve | 0.255147 | 0.100257 | -0.154889 | [-0.164356, -0.144679] | True |
| adwin/noise_jump | preserve | 0.000606 | 0.000606 | 0.000000 | [0.000000, 0.000000] | True |
| adwin/drift | preserve | 0.003152 | 0.003115 | -0.000037 | [-0.000039, -0.000035] | True |
| adwin/exactly_quiet | preserve | 0.000000 | 0.000000 | 0.000000 | [0.000000, 0.000000] | True |
| adwin/noise_jump/noise_increase | preserve | 0.003449 | 0.003449 | 0.000000 | [0.000000, 0.000000] | True |
| adwin/noise_jump/noise_decrease | preserve | 0.000568 | 0.000568 | 0.000000 | [0.000000, 0.000000] | True |
| adwin/drift/drift | preserve | 0.007975 | 0.007974 | -0.000002 | [-0.000003, -0.000000] | True |
| adwin/mixed/increase_first/post_mse | preserve | 0.195123 | 0.082106 | -0.113017 | [-0.118009, -0.107489] | True |
| adwin/mixed/increase_first/stable_mse | preserve | 0.000802 | 0.000802 | 0.000000 | [0.000000, 0.000000] | True |
| adwin/mixed/decrease_first/post_mse | preserve | 0.196327 | 0.084499 | -0.111828 | [-0.117178, -0.106507] | True |
| adwin/mixed/decrease_first/stable_mse | preserve | 0.000908 | 0.000908 | 0.000000 | [0.000000, 0.000000] | True |
| random_drift/primary | improve | 0.199235 | 0.083613 | -0.115622 | [-0.118974, -0.112239] | True |
| random_drift/quiet | preserve | 0.000001 | 0.000001 | -0.000001 | [-0.000001, -0.000000] | True |
| random_drift/noisy | preserve | 0.001196 | 0.000736 | -0.000460 | [-0.000676, -0.000272] | True |
| random_drift/switch_quiet | preserve | 0.151860 | 0.067590 | -0.084270 | [-0.086892, -0.081736] | True |
| random_drift/switch_noisy | preserve | 0.253768 | 0.100257 | -0.153511 | [-0.163621, -0.142698] | True |
| random_drift/noise_jump | preserve | 0.000887 | 0.000606 | -0.000282 | [-0.000522, -0.000089] | True |
| random_drift/drift | preserve | 0.003132 | 0.003115 | -0.000017 | [-0.000025, -0.000010] | True |
| random_drift/exactly_quiet | preserve | 0.000000 | 0.000000 | 0.000000 | [0.000000, 0.000000] | True |
| random_drift/noise_jump/noise_increase | preserve | 0.003661 | 0.003449 | -0.000212 | [-0.000561, 0.000000] | True |
| random_drift/noise_jump/noise_decrease | preserve | 0.000657 | 0.000568 | -0.000089 | [-0.000266, 0.000000] | True |
| random_drift/drift/drift | preserve | 0.007923 | 0.007974 | 0.000050 | [0.000028, 0.000073] | True |
| random_drift/mixed/increase_first/post_mse | preserve | 0.195123 | 0.082106 | -0.113017 | [-0.118009, -0.107489] | True |
| random_drift/mixed/increase_first/stable_mse | preserve | 0.000855 | 0.000802 | -0.000053 | [-0.000120, -0.000003] | True |
| random_drift/mixed/decrease_first/post_mse | preserve | 0.196190 | 0.084499 | -0.111691 | [-0.117223, -0.106149] | True |
| random_drift/mixed/decrease_first/stable_mse | preserve | 0.001269 | 0.000908 | -0.000361 | [-0.000544, -0.000201] | True |
| oracle_nofallback/primary | preserve | 0.085909 | 0.083613 | -0.002296 | [-0.004084, -0.000554] | True |
| oracle_nofallback/quiet | strict | 0.000077 | 0.000001 | -0.000077 | [-0.000080, -0.000074] | True |
| oracle_nofallback/noisy | strict | 0.031100 | 0.000736 | -0.030363 | [-0.031244, -0.029503] | True |
| oracle_nofallback/switch_quiet | preserve | 0.065477 | 0.067590 | 0.002113 | [0.001735, 0.002478] | True |
| oracle_nofallback/switch_noisy | preserve | 0.104377 | 0.100257 | -0.004120 | [-0.008998, 0.000782] | True |
| oracle_nofallback/noise_jump | strict | 0.012088 | 0.000606 | -0.011482 | [-0.012054, -0.010910] | True |
| oracle_nofallback/drift | preserve | 0.000191 | 0.003115 | 0.002924 | [0.002897, 0.002950] | False |
| oracle_nofallback/exactly_quiet | preserve | 0.000000 | 0.000000 | 0.000000 | [0.000000, 0.000000] | True |
| oracle_nofallback/noise_jump/noise_increase | strict | 0.027617 | 0.003449 | -0.024168 | [-0.026594, -0.021762] | True |
| oracle_nofallback/noise_jump/noise_decrease | strict | 0.002766 | 0.000568 | -0.002198 | [-0.003204, -0.001273] | True |
| oracle_nofallback/drift/drift | preserve | 0.000375 | 0.007974 | 0.007599 | [0.007401, 0.007794] | False |
| oracle_nofallback/mixed/increase_first/post_mse | preserve | 0.084922 | 0.082106 | -0.002816 | [-0.006024, 0.000508] | True |
| oracle_nofallback/mixed/increase_first/stable_mse | strict | 0.012267 | 0.000802 | -0.011465 | [-0.012351, -0.010608] | True |
| oracle_nofallback/mixed/decrease_first/post_mse | preserve | 0.088862 | 0.084499 | -0.004363 | [-0.007204, -0.001324] | True |
| oracle_nofallback/mixed/decrease_first/stable_mse | strict | 0.020125 | 0.000908 | -0.019217 | [-0.020064, -0.018363] | True |

## Absolute errors and memory

| Policy/fixture/coordinate | Excess MSE | Post MSE | Stable MSE | Recovery latency | Mean vector update norm | Total requests | Fast mean width | Fast discarded | ADWIN mean width | Fast share |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| window/core/quiet | 0.000310 | — | 0.000310 | — | 0.223172 | 0.000000 | 8.000000 | 5992.000000 | — | — |
| window/core/noisy | 0.124671 | — | 0.124671 | — | 0.223172 | 0.000000 | 8.000000 | 5992.000000 | — | — |
| window/core/switch_quiet | 0.005404 | 0.063999 | 0.000308 | 7.984375 | 0.223172 | 0.000000 | 8.000000 | 5992.000000 | — | — |
| window/core/switch_noisy | 0.129962 | 0.181877 | 0.125448 | 209.187500 | 0.223172 | 0.000000 | 8.000000 | 5992.000000 | — | — |
| window/noise_jump/noise_jump | 0.048572 | — | 0.048572 | — | 0.050495 | 0.000000 | 8.000000 | 5992.000000 | — | — |
| window/drift/drift | 0.000319 | — | 0.000319 | — | 0.007223 | 0.000000 | 8.000000 | 5992.000000 | — | — |
| window/exactly_quiet/exactly_quiet | 0.000000 | — | 0.000000 | — | 0.000167 | 0.000000 | 8.000000 | 5992.000000 | — | — |
| window/mixed/increase_first | 0.054047 | 0.126994 | 0.047703 | 109.625000 | 0.143275 | 0.000000 | 8.000000 | 5992.000000 | — | — |
| window/mixed/decrease_first | 0.083187 | 0.131914 | 0.078950 | 142.546875 | 0.143275 | 0.000000 | 8.000000 | 5992.000000 | — | — |
| sgd/core/quiet | 0.000169 | — | 0.000169 | — | 0.166785 | 0.000000 | — | — | — | — |
| sgd/core/noisy | 0.068177 | — | 0.068177 | — | 0.166785 | 0.000000 | — | — | — | — |
| sgd/core/switch_quiet | 0.006833 | 0.083478 | 0.000168 | 17.281250 | 0.166785 | 0.000000 | — | — | — | — |
| sgd/core/switch_noisy | 0.074996 | 0.149368 | 0.068529 | 71.828125 | 0.166785 | 0.000000 | — | — | — | — |
| sgd/noise_jump/noise_jump | 0.026559 | — | 0.026559 | — | 0.037817 | 0.000000 | — | — | — | — |
| sgd/drift/drift | 0.000196 | — | 0.000196 | — | 0.005434 | 0.000000 | — | — | — | — |
| sgd/exactly_quiet/exactly_quiet | 0.000000 | — | 0.000000 | — | 0.000167 | 0.000000 | — | — | — | — |
| sgd/mixed/increase_first | 0.033605 | 0.118004 | 0.026266 | 47.843750 | 0.106972 | 0.000000 | — | — | — | — |
| sgd/mixed/decrease_first | 0.049662 | 0.122395 | 0.043338 | 48.015625 | 0.106972 | 0.000000 | — | — | — | — |
| adwin/core/quiet | 0.000001 | — | 0.000001 | — | 0.004576 | 0.000000 | 3500.500000 | 0.000000 | — | — |
| adwin/core/noisy | 0.000736 | — | 0.000736 | — | 0.004576 | 84.000000 | 2660.958900 | 2118.000000 | — | — |
| adwin/core/switch_quiet | 0.012092 | 0.150857 | 0.000026 | 28.968750 | 0.004576 | 461.000000 | 1107.393875 | 3980.375000 | — | — |
| adwin/core/switch_noisy | 0.022062 | 0.255147 | 0.001794 | 56.828125 | 0.004576 | 478.000000 | 1008.054975 | 4289.625000 | — | — |
| adwin/noise_jump/noise_jump | 0.000606 | — | 0.000606 | — | 0.000689 | 157.000000 | 1803.025500 | 2269.250000 | — | — |
| adwin/drift/drift | 0.003152 | — | 0.003152 | — | 0.000565 | 2270.000000 | 869.810800 | 3909.000000 | — | — |
| adwin/exactly_quiet/exactly_quiet | 0.000000 | — | 0.000000 | — | 0.000167 | 0.000000 | 3500.500000 | 0.000000 | — | — |
| adwin/mixed/increase_first | 0.016347 | 0.195123 | 0.000802 | 42.968750 | 0.003696 | 473.000000 | 1055.892450 | 3980.187500 | — | — |
| adwin/mixed/decrease_first | 0.016541 | 0.196327 | 0.000908 | 41.656250 | 0.003696 | 473.000000 | 1055.839600 | 4115.375000 | — | — |
| retain_drift/core/quiet | 0.000001 | — | 0.000001 | — | 0.004456 | 0.000000 | 32.000000 | 5968.000000 | 3500.500000 | 0.000000 |
| retain_drift/core/noisy | 0.000736 | — | 0.000736 | — | 0.004456 | 0.000000 | 32.000000 | 5968.000000 | 2660.958900 | 0.000000 |
| retain_drift/core/switch_quiet | 0.005431 | 0.067590 | 0.000026 | 30.015625 | 0.004456 | 64.000000 | 31.837600 | 5968.000000 | 1107.393875 | 0.012800 |
| retain_drift/core/switch_noisy | 0.009671 | 0.100257 | 0.001794 | 46.890625 | 0.004456 | 64.000000 | 31.837600 | 5968.000000 | 1008.054975 | 0.012800 |
| retain_drift/noise_jump/noise_jump | 0.000606 | — | 0.000606 | — | 0.000689 | 0.000000 | 32.000000 | 5968.000000 | 1803.025500 | 0.000000 |
| retain_drift/drift/drift | 0.003115 | — | 0.003115 | — | 0.000591 | 64.000000 | 31.837600 | 5968.000000 | 869.810800 | 0.012800 |
| retain_drift/exactly_quiet/exactly_quiet | 0.000000 | — | 0.000000 | — | 0.000167 | 0.000000 | 32.000000 | 5968.000000 | 3500.500000 | 0.000000 |
| retain_drift/mixed/increase_first | 0.007306 | 0.082106 | 0.000802 | 40.078125 | 0.003573 | 64.000000 | 31.837600 | 5968.000000 | 1055.892450 | 0.012800 |
| retain_drift/mixed/decrease_first | 0.007595 | 0.084499 | 0.000908 | 34.359375 | 0.003573 | 64.000000 | 31.837600 | 5968.000000 | 1055.839600 | 0.012800 |
| oracle_nofallback/core/quiet | 0.000077 | — | 0.000077 | — | 0.057100 | 0.000000 | 32.000000 | 5968.000000 | — | — |
| oracle_nofallback/core/noisy | 0.031100 | — | 0.031100 | — | 0.057100 | 0.000000 | 32.000000 | 5968.000000 | — | — |
| oracle_nofallback/core/switch_quiet | 0.005308 | 0.065477 | 0.000076 | 27.359375 | 0.057100 | 64.000000 | 31.837600 | 5968.000000 | — | — |
| oracle_nofallback/core/switch_noisy | 0.037163 | 0.104377 | 0.031319 | 31.593750 | 0.057100 | 64.000000 | 31.837600 | 5968.000000 | — | — |
| oracle_nofallback/noise_jump/noise_jump | 0.012088 | — | 0.012088 | — | 0.012832 | 0.000000 | 32.000000 | 5968.000000 | — | — |
| oracle_nofallback/drift/drift | 0.000191 | — | 0.000191 | — | 0.002017 | 64.000000 | 31.837600 | 5968.000000 | — | — |
| oracle_nofallback/exactly_quiet/exactly_quiet | 0.000000 | — | 0.000000 | — | 0.000167 | 0.000000 | 32.000000 | 5968.000000 | — | — |
| oracle_nofallback/mixed/increase_first | 0.018079 | 0.084922 | 0.012267 | 28.859375 | 0.036958 | 64.000000 | 31.837600 | 5968.000000 | — | — |
| oracle_nofallback/mixed/decrease_first | 0.025624 | 0.088862 | 0.020125 | 28.171875 | 0.036958 | 64.000000 | 31.837600 | 5968.000000 | — | — |
| random_drift/core/quiet | 0.000001 | — | 0.000001 | — | 0.005292 | 28.000000 | 31.944175 | 5968.000000 | 3500.500000 | 0.004400 |
| random_drift/core/noisy | 0.001196 | — | 0.001196 | — | 0.005292 | 35.000000 | 31.923875 | 5968.000000 | 2660.958900 | 0.006000 |
| random_drift/core/switch_quiet | 0.012173 | 0.151860 | 0.000027 | 29.062500 | 0.005292 | 34.000000 | 31.918800 | 5968.000000 | 1107.393875 | 0.006400 |
| random_drift/core/switch_noisy | 0.022626 | 0.253768 | 0.002526 | 56.500000 | 0.005292 | 42.000000 | 31.911188 | 5968.000000 | 1008.054975 | 0.007000 |
| random_drift/noise_jump/noise_jump | 0.000887 | — | 0.000887 | — | 0.000827 | 45.000000 | 31.895962 | 5968.000000 | 1803.025500 | 0.008200 |
| random_drift/drift/drift | 0.003132 | — | 0.003132 | — | 0.000581 | 38.000000 | 31.917613 | 5968.000000 | 869.810800 | 0.006550 |
| random_drift/exactly_quiet/exactly_quiet | 0.000000 | — | 0.000000 | — | 0.000167 | 41.000000 | 31.906112 | 5968.000000 | 3500.500000 | 0.007400 |
| random_drift/mixed/increase_first | 0.016396 | 0.195123 | 0.000855 | 42.968750 | 0.004084 | 33.000000 | 31.942144 | 5968.000000 | 1055.892450 | 0.004588 |
| random_drift/mixed/decrease_first | 0.016863 | 0.196190 | 0.001269 | 41.656250 | 0.004084 | 46.000000 | 31.898500 | 5968.000000 | 1055.839600 | 0.008000 |

Width counts retained observations, not physical storage. SGD uses exponential weights and has no literal window. Target and drift-boundary requests are distinguished by provenance in every record and never mix; random requests carry random provenance. Fast share is the post-burn fraction of predictions taken from the fast window.

## Actual request timing

| Policy/fixture/coordinate/event | Hits/finite seeds | Censored latency |
| --- | --- | ---: |
| retain_drift/core/switch_quiet/target_down | 32/32 | 0.000000 |
| retain_drift/core/switch_quiet/target_up | 32/32 | 0.000000 |
| retain_drift/core/switch_noisy/target_down | 32/32 | 0.000000 |
| retain_drift/core/switch_noisy/target_up | 32/32 | 0.000000 |
| retain_drift/noise_jump/noise_jump/noise_increase | 0/32 | 100.000000 |
| retain_drift/noise_jump/noise_jump/noise_decrease | 0/32 | 100.000000 |
| retain_drift/drift/drift/drift_start | 32/32 | 0.000000 |
| retain_drift/drift/drift/drift_end | 32/32 | 0.000000 |
| retain_drift/mixed/increase_first/target_down | 32/32 | 0.000000 |
| retain_drift/mixed/increase_first/target_up | 32/32 | 0.000000 |
| retain_drift/mixed/decrease_first/target_down | 32/32 | 0.000000 |
| retain_drift/mixed/decrease_first/target_up | 32/32 | 0.000000 |
| oracle_nofallback/core/switch_quiet/target_down | 32/32 | 0.000000 |
| oracle_nofallback/core/switch_quiet/target_up | 32/32 | 0.000000 |
| oracle_nofallback/core/switch_noisy/target_down | 32/32 | 0.000000 |
| oracle_nofallback/core/switch_noisy/target_up | 32/32 | 0.000000 |
| oracle_nofallback/noise_jump/noise_jump/noise_increase | 0/32 | 100.000000 |
| oracle_nofallback/noise_jump/noise_jump/noise_decrease | 0/32 | 100.000000 |
| oracle_nofallback/drift/drift/drift_start | 32/32 | 0.000000 |
| oracle_nofallback/drift/drift/drift_end | 32/32 | 0.000000 |
| oracle_nofallback/mixed/increase_first/target_down | 32/32 | 0.000000 |
| oracle_nofallback/mixed/increase_first/target_up | 32/32 | 0.000000 |
| oracle_nofallback/mixed/decrease_first/target_down | 32/32 | 0.000000 |
| oracle_nofallback/mixed/decrease_first/target_up | 32/32 | 0.000000 |
| random_drift/core/switch_quiet/target_down | 1/32 | 97.812500 |
| random_drift/core/switch_quiet/target_up | 0/32 | 100.000000 |
| random_drift/core/switch_noisy/target_down | 0/32 | 100.000000 |
| random_drift/core/switch_noisy/target_up | 1/32 | 97.093750 |
| random_drift/noise_jump/noise_jump/noise_increase | 1/32 | 99.312500 |
| random_drift/noise_jump/noise_jump/noise_decrease | 0/32 | 100.000000 |
| random_drift/drift/drift/drift_start | 0/32 | 100.000000 |
| random_drift/drift/drift/drift_end | 1/32 | 96.906250 |
| random_drift/mixed/increase_first/target_down | 0/32 | 100.000000 |
| random_drift/mixed/increase_first/target_up | 0/32 | 100.000000 |
| random_drift/mixed/decrease_first/target_down | 0/32 | 100.000000 |
| random_drift/mixed/decrease_first/target_up | 1/32 | 98.093750 |

## Measured execution time

| Stage | Family | Seconds |
| --- | --- | ---: |
| tuning | window | 1.48 |
| tuning | sgd | 0.92 |
| tuning | adwin | 4.72 |
| confirmation | window | 0.85 |
| confirmation | sgd | 0.29 |
| confirmation | adwin | 1.52 |
| confirmation | retain_drift | 2.20 |
| confirmation | oracle_nofallback | 0.26 |
| confirmation | random_drift | 2.08 |

Configuration budgets are equal, not CPU costs. Times exclude archive writes and share cached fixtures.

## Scope and reproduction

ADWIN2 is independently implemented from the paper: practical Eq.(3.1), five buckets per size, minimum subwindow5. Gaussian observations violate the bounded-input premise; no corresponding formal guarantee or library-release parity is claimed. All policies see unchanged raw observations.

Granted timing is privileged, not perfect segmentation: retaining K_fast=4 at any boundary may retain old-regime data. No schedule outcome overrides candidate performance. Candidate success requires all75 comparisons. All outcomes close this registration.

Intervals resample whole seeds10000 times with seed125000. Finite menus and synthetic fixtures do not establish global optimizer superiority, population guarantees or general neural-memory utility. Every reached row and source is archived; prior studies remain intact.

`python check_v3_drift.py --evidence results/v3-drift --reproduce` regenerates every reached row and scientific manifest/summary at rtol1e-11/atol1e-13. `python report_v3_drift.py --check` verifies both generated reports.
