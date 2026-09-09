# V3 oracle-schedule retention

Disposition: **learning_negative**.

| Stage | Rows |
| --- | ---: |
| tuning | 384 |
| confirmation | 192 |

## Finite-menu tuning

Each searched family: 12 configurations ×8 seeds ×5 fixtures. Same objective: half primary post-switch MSE plus half mean of14 retention metrics.

| Family | Index | Configuration | Tuning objective | Menu endpoint fields |
| --- | ---: | --- | ---: | --- |
| retain | 8 | `{"delta": 0.1, "H": 32}` | 0.055560 | delta, H |
| window | 3 | `{"window": 8}` | 0.099261 | none |
| sgd | 8 | `{"lr": 0.128}` | 0.085162 | none |
| adwin | 9 | `{"delta": 0.1, "clock": 1}` | 0.131456 | delta, clock |

Endpoint choices remain in the registered finite menu; no extension or global-optimum claim. Oracle_nofallback is the fixed fast base without slow state. Random_fallback uses the selected delta/H.

Frozen random p=0.000148500149, from 64 requests / 432000 tuning coordinate-updates, 16-update suppression, opportunities from t0. Expected pooled frequency is matched, not actual counts or memory age.


## Independent primary performance

| Policy | Finite seeds | Primary MSE | 95% interval |
| --- | ---: | ---: | --- |
| retain | 32 | 0.082702 | [0.07889603275179136, 0.08678345220785012] |
| window | 32 | 0.128206 | [0.12446042875818428, 0.13204650042160984] |
| sgd | 32 | 0.119466 | [0.11603116976198932, 0.12288558329346695] |
| adwin | 32 | 0.197654 | [0.19260533609590813, 0.20293179895025024] |
| oracle_nofallback | 32 | 0.086763 | [0.08293839378411308, 0.09072041274982973] |
| random_fallback | 32 | 0.197029 | [0.1920718779367453, 0.2023374917541373] |

## retain: learning_negative

All75 comparisons are required: >=10% primary improvement over window/sgd/adwin/random_fallback, primary preservation against oracle_nofallback, every retention bound, and strict improvement on the8 stable/noise cells against oracle_nofallback.

| Contrast | Mode | Control | Policy | Delta | 95% interval | Pass |
| --- | --- | ---: | ---: | ---: | --- | --- |
| window/primary | improve | 0.128206 | 0.082702 | -0.045504 | [-0.049688, -0.041408] | True |
| window/quiet | preserve | 0.000309 | 0.000001 | -0.000308 | [-0.000313, -0.000304] | True |
| window/noisy | preserve | 0.125427 | 0.001187 | -0.124240 | [-0.126087, -0.122314] | True |
| window/switch_quiet | preserve | 0.064363 | 0.068302 | 0.003939 | [0.003528, 0.004343] | True |
| window/switch_noisy | preserve | 0.196086 | 0.101907 | -0.094179 | [-0.104690, -0.083336] | True |
| window/noise_jump | preserve | 0.050907 | 0.000732 | -0.050176 | [-0.052057, -0.048263] | True |
| window/drift | preserve | 0.000322 | 0.003148 | 0.002826 | [0.002796, 0.002853] | False |
| window/exactly_quiet | preserve | 0.000000 | 0.000000 | 0.000000 | [0.000000, 0.000000] | True |
| window/noise_jump/noise_increase | preserve | 0.120146 | 0.006020 | -0.114126 | [-0.123432, -0.105366] | True |
| window/noise_jump/noise_decrease | preserve | 0.004230 | 0.000445 | -0.003786 | [-0.004981, -0.002684] | True |
| window/drift/drift | preserve | 0.000334 | 0.007562 | 0.007228 | [0.007042, 0.007426] | False |
| window/mixed/increase_first/post_mse | preserve | 0.122998 | 0.077716 | -0.045281 | [-0.051135, -0.039554] | True |
| window/mixed/increase_first/stable_mse | preserve | 0.050475 | 0.000691 | -0.049784 | [-0.052308, -0.047299] | True |
| window/mixed/decrease_first/post_mse | preserve | 0.129376 | 0.082882 | -0.046494 | [-0.052248, -0.040731] | True |
| window/mixed/decrease_first/stable_mse | preserve | 0.075216 | 0.000926 | -0.074290 | [-0.076297, -0.072318] | True |
| sgd/primary | improve | 0.119466 | 0.082702 | -0.036764 | [-0.039927, -0.033676] | True |
| sgd/quiet | preserve | 0.000170 | 0.000001 | -0.000169 | [-0.000172, -0.000166] | True |
| sgd/noisy | preserve | 0.068254 | 0.001187 | -0.067067 | [-0.068149, -0.065919] | True |
| sgd/switch_quiet | preserve | 0.083819 | 0.068302 | -0.015517 | [-0.015900, -0.015152] | True |
| sgd/switch_noisy | preserve | 0.158604 | 0.101907 | -0.056697 | [-0.065426, -0.047985] | True |
| sgd/noise_jump | preserve | 0.027925 | 0.000732 | -0.027193 | [-0.028203, -0.026177] | True |
| sgd/drift | preserve | 0.000195 | 0.003148 | 0.002952 | [0.002924, 0.002978] | False |
| sgd/exactly_quiet | preserve | 0.000000 | 0.000000 | -0.000000 | [-0.000000, -0.000000] | True |
| sgd/noise_jump/noise_increase | preserve | 0.066863 | 0.006020 | -0.060843 | [-0.066595, -0.055393] | True |
| sgd/noise_jump/noise_decrease | preserve | 0.001992 | 0.000445 | -0.001547 | [-0.002265, -0.000883] | True |
| sgd/drift/drift | preserve | 0.000229 | 0.007562 | 0.007333 | [0.007150, 0.007528] | False |
| sgd/mixed/increase_first/post_mse | preserve | 0.114799 | 0.077716 | -0.037082 | [-0.041054, -0.032989] | True |
| sgd/mixed/increase_first/stable_mse | preserve | 0.027614 | 0.000691 | -0.026923 | [-0.028410, -0.025457] | True |
| sgd/mixed/decrease_first/post_mse | preserve | 0.120643 | 0.082882 | -0.037761 | [-0.042125, -0.033408] | True |
| sgd/mixed/decrease_first/stable_mse | preserve | 0.041088 | 0.000926 | -0.040162 | [-0.041462, -0.038885] | True |
| adwin/primary | improve | 0.197654 | 0.082702 | -0.114952 | [-0.118086, -0.111738] | True |
| adwin/quiet | preserve | 0.000001 | 0.000001 | 0.000000 | [0.000000, 0.000000] | True |
| adwin/noisy | preserve | 0.001187 | 0.001187 | 0.000000 | [0.000000, 0.000000] | True |
| adwin/switch_quiet | preserve | 0.152486 | 0.068302 | -0.084184 | [-0.086242, -0.081970] | True |
| adwin/switch_noisy | preserve | 0.245482 | 0.101907 | -0.143575 | [-0.154120, -0.133123] | True |
| adwin/noise_jump | preserve | 0.000732 | 0.000732 | 0.000000 | [0.000000, 0.000000] | True |
| adwin/drift | preserve | 0.003148 | 0.003148 | 0.000000 | [0.000000, 0.000000] | True |
| adwin/exactly_quiet | preserve | 0.000000 | 0.000000 | 0.000000 | [0.000000, 0.000000] | True |
| adwin/noise_jump/noise_increase | preserve | 0.006020 | 0.006020 | 0.000000 | [0.000000, 0.000000] | True |
| adwin/noise_jump/noise_decrease | preserve | 0.000445 | 0.000445 | 0.000000 | [0.000000, 0.000000] | True |
| adwin/drift/drift | preserve | 0.007562 | 0.007562 | 0.000000 | [0.000000, 0.000000] | True |
| adwin/mixed/increase_first/post_mse | preserve | 0.197021 | 0.077716 | -0.119305 | [-0.124169, -0.114276] | True |
| adwin/mixed/increase_first/stable_mse | preserve | 0.000691 | 0.000691 | 0.000000 | [0.000000, 0.000000] | True |
| adwin/mixed/decrease_first/post_mse | preserve | 0.195626 | 0.082882 | -0.112744 | [-0.119028, -0.106558] | True |
| adwin/mixed/decrease_first/stable_mse | preserve | 0.000926 | 0.000926 | 0.000000 | [0.000000, 0.000000] | True |
| random_fallback/primary | improve | 0.197029 | 0.082702 | -0.114327 | [-0.117380, -0.111218] | True |
| random_fallback/quiet | preserve | 0.000002 | 0.000001 | -0.000001 | [-0.000001, -0.000000] | True |
| random_fallback/noisy | preserve | 0.001528 | 0.001187 | -0.000341 | [-0.000533, -0.000177] | True |
| random_fallback/switch_quiet | preserve | 0.152404 | 0.068302 | -0.084102 | [-0.086167, -0.081880] | True |
| random_fallback/switch_noisy | preserve | 0.245482 | 0.101907 | -0.143575 | [-0.154120, -0.133123] | True |
| random_fallback/noise_jump | preserve | 0.000915 | 0.000732 | -0.000184 | [-0.000391, -0.000048] | True |
| random_fallback/drift | preserve | 0.003135 | 0.003148 | 0.000013 | [0.000005, 0.000024] | True |
| random_fallback/exactly_quiet | preserve | 0.000000 | 0.000000 | 0.000000 | [0.000000, 0.000000] | True |
| random_fallback/noise_jump/noise_increase | preserve | 0.006346 | 0.006020 | -0.000326 | [-0.000977, 0.000000] | True |
| random_fallback/noise_jump/noise_decrease | preserve | 0.000443 | 0.000445 | 0.000001 | [0.000000, 0.000004] | True |
| random_fallback/drift/drift | preserve | 0.007531 | 0.007562 | 0.000031 | [0.000010, 0.000059] | True |
| random_fallback/mixed/increase_first/post_mse | preserve | 0.196362 | 0.077716 | -0.118646 | [-0.123778, -0.113442] | True |
| random_fallback/mixed/increase_first/stable_mse | preserve | 0.000778 | 0.000691 | -0.000087 | [-0.000155, -0.000032] | True |
| random_fallback/mixed/decrease_first/post_mse | preserve | 0.193867 | 0.082882 | -0.110985 | [-0.117729, -0.104254] | True |
| random_fallback/mixed/decrease_first/stable_mse | preserve | 0.001053 | 0.000926 | -0.000127 | [-0.000235, -0.000042] | True |
| oracle_nofallback/primary | preserve | 0.086763 | 0.082702 | -0.004061 | [-0.005675, -0.002360] | True |
| oracle_nofallback/quiet | strict | 0.000078 | 0.000001 | -0.000077 | [-0.000079, -0.000075] | True |
| oracle_nofallback/noisy | strict | 0.031134 | 0.001187 | -0.029947 | [-0.030737, -0.029088] | True |
| oracle_nofallback/switch_quiet | preserve | 0.066096 | 0.068302 | 0.002206 | [0.001840, 0.002584] | True |
| oracle_nofallback/switch_noisy | preserve | 0.111484 | 0.101907 | -0.009577 | [-0.014499, -0.004228] | True |
| oracle_nofallback/noise_jump | strict | 0.012708 | 0.000732 | -0.011976 | [-0.012528, -0.011434] | True |
| oracle_nofallback/drift | preserve | 0.000184 | 0.003148 | 0.002963 | [0.002938, 0.002987] | False |
| oracle_nofallback/exactly_quiet | strict | 0.000000 | 0.000000 | 0.000000 | [0.000000, 0.000000] | False |
| oracle_nofallback/noise_jump/noise_increase | strict | 0.029683 | 0.006020 | -0.023662 | [-0.027531, -0.020009] | True |
| oracle_nofallback/noise_jump/noise_decrease | strict | 0.002739 | 0.000445 | -0.002294 | [-0.003188, -0.001451] | True |
| oracle_nofallback/drift/drift | preserve | 0.000339 | 0.007562 | 0.007223 | [0.007051, 0.007406] | False |
| oracle_nofallback/mixed/increase_first/post_mse | preserve | 0.081647 | 0.077716 | -0.003931 | [-0.006359, -0.001386] | True |
| oracle_nofallback/mixed/increase_first/stable_mse | strict | 0.012734 | 0.000691 | -0.012043 | [-0.012948, -0.011173] | True |
| oracle_nofallback/mixed/decrease_first/post_mse | preserve | 0.087823 | 0.082882 | -0.004941 | [-0.007370, -0.002371] | True |
| oracle_nofallback/mixed/decrease_first/stable_mse | strict | 0.018795 | 0.000926 | -0.017869 | [-0.018763, -0.016991] | True |

## Absolute errors and memory

| Policy/fixture/coordinate | Excess MSE | Post MSE | Stable MSE | Recovery latency | Mean vector update norm | Total requests | Fast mean width | Fast final width | Fast discarded | ADWIN mean width | Fast share |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| retain/core/quiet | 0.000001 | — | 0.000001 | — | 0.004443 | 0.000000 | 32.000000 | 32.000000 | 5968.000000 | 3500.500000 | 0.000000 |
| retain/core/noisy | 0.001187 | — | 0.001187 | — | 0.004443 | 0.000000 | 32.000000 | 32.000000 | 5968.000000 | 2613.523000 | 0.000000 |
| retain/core/switch_quiet | 0.005489 | 0.068302 | 0.000027 | 30.062500 | 0.004443 | 64.000000 | 31.837600 | 32.000000 | 5968.000000 | 1106.197950 | 0.012800 |
| retain/core/switch_noisy | 0.009369 | 0.101907 | 0.001322 | 45.203125 | 0.004443 | 64.000000 | 31.837600 | 32.000000 | 5968.000000 | 1037.967050 | 0.012800 |
| retain/noise_jump/noise_jump | 0.000732 | — | 0.000732 | — | 0.000682 | 0.000000 | 32.000000 | 32.000000 | 5968.000000 | 1801.918625 | 0.000000 |
| retain/drift/drift | 0.003148 | — | 0.003148 | — | 0.000567 | 0.000000 | 32.000000 | 32.000000 | 5968.000000 | 834.107200 | 0.000000 |
| retain/exactly_quiet/exactly_quiet | 0.000000 | — | 0.000000 | — | 0.000167 | 0.000000 | 32.000000 | 32.000000 | 5968.000000 | 3500.500000 | 0.000000 |
| retain/mixed/increase_first | 0.006853 | 0.077716 | 0.000691 | 33.187500 | 0.003556 | 64.000000 | 31.837600 | 32.000000 | 5968.000000 | 1071.399750 | 0.012800 |
| retain/mixed/decrease_first | 0.007482 | 0.082882 | 0.000926 | 30.937500 | 0.003556 | 64.000000 | 31.837600 | 32.000000 | 5968.000000 | 1066.322550 | 0.012800 |
| window/core/quiet | 0.000309 | — | 0.000309 | — | 0.223051 | 0.000000 | 8.000000 | 8.000000 | 5992.000000 | — | — |
| window/core/noisy | 0.125427 | — | 0.125427 | — | 0.223051 | 0.000000 | 8.000000 | 8.000000 | 5992.000000 | — | — |
| window/core/switch_quiet | 0.005438 | 0.064363 | 0.000314 | 8.000000 | 0.223051 | 0.000000 | 8.000000 | 8.000000 | 5992.000000 | — | — |
| window/core/switch_noisy | 0.130716 | 0.196086 | 0.125031 | 302.875000 | 0.223051 | 0.000000 | 8.000000 | 8.000000 | 5992.000000 | — | — |
| window/noise_jump/noise_jump | 0.050907 | — | 0.050907 | — | 0.052512 | 0.000000 | 8.000000 | 8.000000 | 5992.000000 | — | — |
| window/drift/drift | 0.000322 | — | 0.000322 | — | 0.007245 | 0.000000 | 8.000000 | 8.000000 | 5992.000000 | — | — |
| window/exactly_quiet/exactly_quiet | 0.000000 | — | 0.000000 | — | 0.000167 | 0.000000 | 8.000000 | 8.000000 | 5992.000000 | — | — |
| window/mixed/increase_first | 0.056277 | 0.122998 | 0.050475 | 153.578125 | 0.143051 | 0.000000 | 8.000000 | 8.000000 | 5992.000000 | — | — |
| window/mixed/decrease_first | 0.079549 | 0.129376 | 0.075216 | 105.781250 | 0.143051 | 0.000000 | 8.000000 | 8.000000 | 5992.000000 | — | — |
| sgd/core/quiet | 0.000170 | — | 0.000170 | — | 0.166565 | 0.000000 | — | — | — | — | — |
| sgd/core/noisy | 0.068254 | — | 0.068254 | — | 0.166565 | 0.000000 | — | — | — | — | — |
| sgd/core/switch_quiet | 0.006863 | 0.083819 | 0.000171 | 17.328125 | 0.166565 | 0.000000 | — | — | — | — | — |
| sgd/core/switch_noisy | 0.075051 | 0.158604 | 0.067785 | 66.187500 | 0.166565 | 0.000000 | — | — | — | — | — |
| sgd/noise_jump/noise_jump | 0.027925 | — | 0.027925 | — | 0.039263 | 0.000000 | — | — | — | — | — |
| sgd/drift/drift | 0.000195 | — | 0.000195 | — | 0.005441 | 0.000000 | — | — | — | — | — |
| sgd/exactly_quiet/exactly_quiet | 0.000000 | — | 0.000000 | — | 0.000167 | 0.000000 | — | — | — | — | — |
| sgd/mixed/increase_first | 0.034589 | 0.114799 | 0.027614 | 44.468750 | 0.106688 | 0.000000 | — | — | — | — | — |
| sgd/mixed/decrease_first | 0.047452 | 0.120643 | 0.041088 | 40.578125 | 0.106688 | 0.000000 | — | — | — | — | — |
| adwin/core/quiet | 0.000001 | — | 0.000001 | — | 0.004576 | 0.000000 | 3500.500000 | 6000.000000 | 0.000000 | — | — |
| adwin/core/noisy | 0.001187 | — | 0.001187 | — | 0.004576 | 71.000000 | 2613.523000 | 3906.000000 | 2094.000000 | — | — |
| adwin/core/switch_quiet | 0.012223 | 0.152486 | 0.000027 | 29.171875 | 0.004576 | 458.000000 | 1106.197950 | 1981.000000 | 4019.000000 | — | — |
| adwin/core/switch_noisy | 0.020855 | 0.245482 | 0.001322 | 54.765625 | 0.004576 | 448.000000 | 1037.967050 | 1705.750000 | 4294.250000 | — | — |
| adwin/noise_jump/noise_jump | 0.000732 | — | 0.000732 | — | 0.000682 | 185.000000 | 1801.918625 | 3757.500000 | 2242.500000 | — | — |
| adwin/drift/drift | 0.003148 | — | 0.003148 | — | 0.000567 | 2362.000000 | 834.107200 | 2050.000000 | 3950.000000 | — | — |
| adwin/exactly_quiet/exactly_quiet | 0.000000 | — | 0.000000 | — | 0.000167 | 0.000000 | 3500.500000 | 6000.000000 | 0.000000 | — | — |
| adwin/mixed/increase_first | 0.016397 | 0.197021 | 0.000691 | 40.281250 | 0.003680 | 464.000000 | 1071.399750 | 1981.125000 | 4018.875000 | — | — |
| adwin/mixed/decrease_first | 0.016502 | 0.195626 | 0.000926 | 35.453125 | 0.003680 | 452.000000 | 1066.322550 | 1844.125000 | 4155.875000 | — | — |
| oracle_nofallback/core/quiet | 0.000078 | — | 0.000078 | — | 0.057122 | 0.000000 | 32.000000 | 32.000000 | 5968.000000 | — | — |
| oracle_nofallback/core/noisy | 0.031134 | — | 0.031134 | — | 0.057122 | 0.000000 | 32.000000 | 32.000000 | 5968.000000 | — | — |
| oracle_nofallback/core/switch_quiet | 0.005359 | 0.066096 | 0.000078 | 27.546875 | 0.057122 | 64.000000 | 31.837600 | 32.000000 | 5968.000000 | — | — |
| oracle_nofallback/core/switch_noisy | 0.036709 | 0.111484 | 0.030207 | 29.968750 | 0.057122 | 64.000000 | 31.837600 | 32.000000 | 5968.000000 | — | — |
| oracle_nofallback/noise_jump/noise_jump | 0.012708 | — | 0.012708 | — | 0.013350 | 0.000000 | 32.000000 | 32.000000 | 5968.000000 | — | — |
| oracle_nofallback/drift/drift | 0.000184 | — | 0.000184 | — | 0.002004 | 0.000000 | 32.000000 | 32.000000 | 5968.000000 | — | — |
| oracle_nofallback/exactly_quiet/exactly_quiet | 0.000000 | — | 0.000000 | — | 0.000167 | 0.000000 | 32.000000 | 32.000000 | 5968.000000 | — | — |
| oracle_nofallback/mixed/increase_first | 0.018247 | 0.081647 | 0.012734 | 24.875000 | 0.036806 | 64.000000 | 31.837600 | 32.000000 | 5968.000000 | — | — |
| oracle_nofallback/mixed/decrease_first | 0.024317 | 0.087823 | 0.018795 | 27.218750 | 0.036806 | 64.000000 | 31.837600 | 32.000000 | 5968.000000 | — | — |
| random_fallback/core/quiet | 0.000002 | — | 0.000002 | — | 0.005035 | 33.000000 | 31.939100 | 32.000000 | 5968.000000 | 3500.500000 | 0.004800 |
| random_fallback/core/noisy | 0.001528 | — | 0.001528 | — | 0.005035 | 25.000000 | 31.939100 | 32.000000 | 5968.000000 | 2613.523000 | 0.004800 |
| random_fallback/core/switch_quiet | 0.012217 | 0.152404 | 0.000027 | 29.015625 | 0.005035 | 20.000000 | 31.960056 | 31.531250 | 5968.468750 | 1106.197950 | 0.003100 |
| random_fallback/core/switch_noisy | 0.021085 | 0.245482 | 0.001572 | 54.765625 | 0.005035 | 26.000000 | 31.948763 | 32.000000 | 5968.000000 | 1037.967050 | 0.004106 |
| random_fallback/noise_jump/noise_jump | 0.000915 | — | 0.000915 | — | 0.000785 | 30.000000 | 31.945900 | 31.250000 | 5968.750000 | 1801.918625 | 0.004225 |
| random_fallback/drift/drift | 0.003135 | — | 0.003135 | — | 0.000579 | 28.000000 | 31.934119 | 31.812500 | 5968.187500 | 834.107200 | 0.005137 |
| random_fallback/exactly_quiet/exactly_quiet | 0.000000 | — | 0.000000 | — | 0.000167 | 17.000000 | 31.959400 | 32.000000 | 5968.000000 | 3500.500000 | 0.003200 |
| random_fallback/mixed/increase_first | 0.016425 | 0.196362 | 0.000778 | 40.281250 | 0.003965 | 28.000000 | 31.941463 | 31.125000 | 5968.875000 | 1071.399750 | 0.004600 |
| random_fallback/mixed/decrease_first | 0.016478 | 0.193867 | 0.001053 | 35.171875 | 0.003965 | 30.000000 | 31.939850 | 31.500000 | 5968.500000 | 1066.322550 | 0.004675 |

Width counts retained observations, not physical storage. SGD uses exponential weights and has no literal window. Fixed windows evict routinely without reset flags; ADWIN flags window shrinkage, and the ADWIN slow state manages its own shrinkage untouched by requests. Discarded totals include routine cap evictions. Vector norms repeat per fixture. Fast share is the post-burn fraction of predictions taken from the fast window.

## Actual request timing

| Policy/fixture/coordinate/event | Hits/finite seeds | Censored latency |
| --- | --- | ---: |
| retain/core/switch_quiet/target_down | 32/32 | 0.000000 |
| retain/core/switch_quiet/target_up | 32/32 | 0.000000 |
| retain/core/switch_noisy/target_down | 32/32 | 0.000000 |
| retain/core/switch_noisy/target_up | 32/32 | 0.000000 |
| retain/noise_jump/noise_jump/noise_increase | 0/32 | 100.000000 |
| retain/noise_jump/noise_jump/noise_decrease | 0/32 | 100.000000 |
| retain/drift/drift/drift_start | 0/32 | 100.000000 |
| retain/drift/drift/drift_end | 0/32 | 100.000000 |
| retain/mixed/increase_first/target_down | 32/32 | 0.000000 |
| retain/mixed/increase_first/target_up | 32/32 | 0.000000 |
| retain/mixed/decrease_first/target_down | 32/32 | 0.000000 |
| retain/mixed/decrease_first/target_up | 32/32 | 0.000000 |
| oracle_nofallback/core/switch_quiet/target_down | 32/32 | 0.000000 |
| oracle_nofallback/core/switch_quiet/target_up | 32/32 | 0.000000 |
| oracle_nofallback/core/switch_noisy/target_down | 32/32 | 0.000000 |
| oracle_nofallback/core/switch_noisy/target_up | 32/32 | 0.000000 |
| oracle_nofallback/noise_jump/noise_jump/noise_increase | 0/32 | 100.000000 |
| oracle_nofallback/noise_jump/noise_jump/noise_decrease | 0/32 | 100.000000 |
| oracle_nofallback/drift/drift/drift_start | 0/32 | 100.000000 |
| oracle_nofallback/drift/drift/drift_end | 0/32 | 100.000000 |
| oracle_nofallback/mixed/increase_first/target_down | 32/32 | 0.000000 |
| oracle_nofallback/mixed/increase_first/target_up | 32/32 | 0.000000 |
| oracle_nofallback/mixed/decrease_first/target_down | 32/32 | 0.000000 |
| oracle_nofallback/mixed/decrease_first/target_up | 32/32 | 0.000000 |
| random_fallback/core/switch_quiet/target_down | 0/32 | 100.000000 |
| random_fallback/core/switch_quiet/target_up | 1/32 | 97.531250 |
| random_fallback/core/switch_noisy/target_down | 0/32 | 100.000000 |
| random_fallback/core/switch_noisy/target_up | 0/32 | 100.000000 |
| random_fallback/noise_jump/noise_jump/noise_increase | 1/32 | 99.156250 |
| random_fallback/noise_jump/noise_jump/noise_decrease | 0/32 | 100.000000 |
| random_fallback/drift/drift/drift_start | 1/32 | 99.343750 |
| random_fallback/drift/drift/drift_end | 1/32 | 97.687500 |
| random_fallback/mixed/increase_first/target_down | 0/32 | 100.000000 |
| random_fallback/mixed/increase_first/target_up | 1/32 | 98.250000 |
| random_fallback/mixed/decrease_first/target_down | 0/32 | 100.000000 |
| random_fallback/mixed/decrease_first/target_up | 1/32 | 96.906250 |

## Measured execution time

| Stage | Family | Seconds |
| --- | --- | ---: |
| tuning | retain | 4.47 |
| tuning | window | 0.10 |
| tuning | sgd | 0.09 |
| tuning | adwin | 4.46 |
| confirmation | retain | 3.44 |
| confirmation | window | 0.28 |
| confirmation | sgd | 0.05 |
| confirmation | adwin | 1.46 |
| confirmation | oracle_nofallback | 0.15 |
| confirmation | random_fallback | 2.16 |

Each searched family consumes 5,184,000 coordinate observations. Times exclude archive writes and share cached fixtures. Configuration budgets are equal, not CPU costs.

## Scope and reproduction

ADWIN2 is independently implemented from the paper: practical Eq.(3.1), five buckets per size, minimum subwindow5. Gaussian observations violate the bounded-input premise; no corresponding formal guarantee or library-release parity is claimed. All policies see unchanged raw observations.

Perfect timing is privileged, not perfect segmentation: retaining K_fast=4 at the true event may retain old-regime data. In stationary fixtures the candidate reduces to ADWIN2 by construction; that is not reported as a discovery. No schedule outcome overrides candidate performance. Candidate success requires all75 comparisons. All outcomes close this registration.

Intervals resample whole seeds10000 times with seed105000. Finite menus and synthetic fixtures do not establish global optimizer superiority, population guarantees or general neural-memory utility. Every reached row and source is archived; prior studies remain intact.

`python check_v3_retention.py --evidence results/v3-retention --reproduce` regenerates every reached row and scientific manifest/summary at rtol1e-11/atol1e-13. `python report_v3_retention.py --check` verifies both generated reports.
