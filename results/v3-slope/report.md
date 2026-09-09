# V3 slope state

Disposition: **learning_positive**.

| Stage | Rows |
| --- | ---: |
| tuning | 384 |
| confirmation | 192 |

## Finite-menu tuning

Each searched family: 12 configurations ×8 seeds ×5 fixtures. Same objective: half primary post-switch MSE plus half mean of14 retention metrics. The dual base is frozen; the estimator family alone is searched.

| Family | Index | Configuration | Tuning objective | Menu endpoint fields |
| --- | ---: | --- | ---: | --- |
| slope | 4 | `{"method": "ols", "W": 128}` | 0.055843 | method, W |
| window | 3 | `{"window": 8}` | 0.098727 | window |
| sgd | 8 | `{"lr": 0.128}` | 0.085539 | none |
| adwin | 9 | `{"delta": 0.1, "clock": 1}` | 0.129342 | delta, clock |

Endpoint choices remain in the registered finite menu; no extension or global-optimum claim. Oracle_nofallback is the fixed fast base on the enriched schedule. Random_slope uses the selected estimator.

Frozen random p=0.000185735513, from 80 enriched requests / 432000 tuning coordinate-updates, 16-update suppression, opportunities from t0. Expected pooled frequency is matched, not actual counts or memory age.


## Independent primary performance

| Policy | Finite seeds | Primary MSE | 95% interval |
| --- | ---: | ---: | --- |
| slope | 32 | 0.079480 | [0.07588565470002813, 0.08296676058339776] |
| window | 32 | 0.125866 | [0.12237627595498975, 0.12945341792319948] |
| sgd | 32 | 0.117088 | [0.1139968487063434, 0.12015811422304563] |
| adwin | 32 | 0.192391 | [0.18813249222993103, 0.19662100516321693] |
| oracle_nofallback | 32 | 0.083258 | [0.07996233343441583, 0.086509525112139] |
| random_slope | 32 | 0.192386 | [0.1880819530252744, 0.1966459246123662] |

## slope: learning_positive

All75 comparisons are required: >=10% primary improvement over window/sgd/adwin/random_slope, primary preservation against oracle_nofallback, every retention bound, and strict improvement on the8 stable/noise cells against oracle_nofallback (both-perfect cells pass as preservation).

| Contrast | Mode | Control | Policy | Delta | 95% interval | Pass |
| --- | --- | ---: | ---: | ---: | --- | --- |
| window/primary | improve | 0.125866 | 0.079480 | -0.046385 | [-0.049636, -0.043289] | True |
| window/quiet | preserve | 0.000308 | 0.000001 | -0.000307 | [-0.000312, -0.000302] | True |
| window/noisy | preserve | 0.122874 | 0.000927 | -0.121946 | [-0.124151, -0.119738] | True |
| window/switch_quiet | preserve | 0.064252 | 0.067874 | 0.003622 | [0.003248, 0.004001] | True |
| window/switch_noisy | preserve | 0.188651 | 0.089354 | -0.099297 | [-0.108485, -0.090546] | True |
| window/noise_jump | preserve | 0.051106 | 0.000706 | -0.050400 | [-0.052193, -0.048567] | True |
| window/drift | preserve | 0.000320 | 0.000091 | -0.000229 | [-0.000237, -0.000221] | True |
| window/exactly_quiet | preserve | 0.000000 | 0.000000 | 0.000000 | [0.000000, 0.000000] | True |
| window/noise_jump/noise_increase | preserve | 0.120517 | 0.004227 | -0.116290 | [-0.125562, -0.107438] | True |
| window/noise_jump/noise_decrease | preserve | 0.003956 | 0.000385 | -0.003571 | [-0.005080, -0.002325] | True |
| window/drift/drift | preserve | 0.000328 | 0.000088 | -0.000240 | [-0.000249, -0.000231] | True |
| window/mixed/increase_first/post_mse | preserve | 0.128148 | 0.081525 | -0.046623 | [-0.052665, -0.040377] | True |
| window/mixed/increase_first/stable_mse | preserve | 0.051170 | 0.000838 | -0.050331 | [-0.052607, -0.048038] | True |
| window/mixed/decrease_first/post_mse | preserve | 0.122411 | 0.079169 | -0.043242 | [-0.048884, -0.037595] | True |
| window/mixed/decrease_first/stable_mse | preserve | 0.076135 | 0.000955 | -0.075181 | [-0.077740, -0.072553] | True |
| sgd/primary | improve | 0.117088 | 0.079480 | -0.037607 | [-0.040043, -0.035359] | True |
| sgd/quiet | preserve | 0.000167 | 0.000001 | -0.000166 | [-0.000170, -0.000163] | True |
| sgd/noisy | preserve | 0.067184 | 0.000927 | -0.066257 | [-0.067616, -0.064873] | True |
| sgd/switch_quiet | preserve | 0.083825 | 0.067874 | -0.015951 | [-0.016352, -0.015545] | True |
| sgd/switch_noisy | preserve | 0.149892 | 0.089354 | -0.060538 | [-0.067562, -0.053839] | True |
| sgd/noise_jump | preserve | 0.027584 | 0.000706 | -0.026878 | [-0.027852, -0.025880] | True |
| sgd/drift | preserve | 0.000193 | 0.000091 | -0.000103 | [-0.000110, -0.000096] | True |
| sgd/exactly_quiet | preserve | 0.000000 | 0.000000 | -0.000000 | [-0.000000, -0.000000] | True |
| sgd/noise_jump/noise_increase | preserve | 0.066228 | 0.004227 | -0.062001 | [-0.068472, -0.056158] | True |
| sgd/noise_jump/noise_decrease | preserve | 0.001938 | 0.000385 | -0.001553 | [-0.002378, -0.000860] | True |
| sgd/drift/drift | preserve | 0.000227 | 0.000088 | -0.000139 | [-0.000147, -0.000131] | True |
| sgd/mixed/increase_first/post_mse | preserve | 0.118473 | 0.081525 | -0.036948 | [-0.041681, -0.031894] | True |
| sgd/mixed/increase_first/stable_mse | preserve | 0.027947 | 0.000838 | -0.027109 | [-0.028465, -0.025757] | True |
| sgd/mixed/decrease_first/post_mse | preserve | 0.116162 | 0.079169 | -0.036993 | [-0.040727, -0.032999] | True |
| sgd/mixed/decrease_first/stable_mse | preserve | 0.041665 | 0.000955 | -0.040710 | [-0.042227, -0.039134] | True |
| adwin/primary | improve | 0.192391 | 0.079480 | -0.112911 | [-0.115900, -0.109708] | True |
| adwin/quiet | preserve | 0.000001 | 0.000001 | 0.000000 | [0.000000, 0.000000] | True |
| adwin/noisy | preserve | 0.000927 | 0.000927 | 0.000000 | [0.000000, 0.000000] | True |
| adwin/switch_quiet | preserve | 0.150885 | 0.067874 | -0.083011 | [-0.085536, -0.080540] | True |
| adwin/switch_noisy | preserve | 0.229183 | 0.089354 | -0.139829 | [-0.149887, -0.130270] | True |
| adwin/noise_jump | preserve | 0.000706 | 0.000706 | 0.000000 | [0.000000, 0.000000] | True |
| adwin/drift | preserve | 0.003154 | 0.000091 | -0.003063 | [-0.003090, -0.003037] | True |
| adwin/exactly_quiet | preserve | 0.000000 | 0.000000 | 0.000000 | [0.000000, 0.000000] | True |
| adwin/noise_jump/noise_increase | preserve | 0.004227 | 0.004227 | 0.000000 | [0.000000, 0.000000] | True |
| adwin/noise_jump/noise_decrease | preserve | 0.000385 | 0.000385 | 0.000000 | [0.000000, 0.000000] | True |
| adwin/drift/drift | preserve | 0.007551 | 0.000088 | -0.007463 | [-0.007686, -0.007257] | True |
| adwin/mixed/increase_first/post_mse | preserve | 0.195956 | 0.081525 | -0.114431 | [-0.120065, -0.108770] | True |
| adwin/mixed/increase_first/stable_mse | preserve | 0.000838 | 0.000838 | 0.000000 | [0.000000, 0.000000] | True |
| adwin/mixed/decrease_first/post_mse | preserve | 0.193541 | 0.079169 | -0.114373 | [-0.119193, -0.109239] | True |
| adwin/mixed/decrease_first/stable_mse | preserve | 0.000955 | 0.000955 | 0.000000 | [0.000000, 0.000000] | True |
| random_slope/primary | improve | 0.192386 | 0.079480 | -0.112906 | [-0.115908, -0.109700] | True |
| random_slope/quiet | preserve | 0.000002 | 0.000001 | -0.000001 | [-0.000002, -0.000001] | True |
| random_slope/noisy | preserve | 0.001272 | 0.000927 | -0.000344 | [-0.000518, -0.000195] | True |
| random_slope/switch_quiet | preserve | 0.150882 | 0.067874 | -0.083008 | [-0.085527, -0.080539] | True |
| random_slope/switch_noisy | preserve | 0.229206 | 0.089354 | -0.139852 | [-0.149908, -0.130270] | True |
| random_slope/noise_jump | preserve | 0.000920 | 0.000706 | -0.000214 | [-0.000333, -0.000111] | True |
| random_slope/drift | preserve | 0.003133 | 0.000091 | -0.003042 | [-0.003071, -0.003014] | True |
| random_slope/exactly_quiet | preserve | 0.000000 | 0.000000 | 0.000000 | [0.000000, 0.000000] | True |
| random_slope/noise_jump/noise_increase | preserve | 0.004451 | 0.004227 | -0.000225 | [-0.000581, 0.000000] | True |
| random_slope/noise_jump/noise_decrease | preserve | 0.000387 | 0.000385 | -0.000002 | [-0.000005, 0.000000] | True |
| random_slope/drift/drift | preserve | 0.007498 | 0.000088 | -0.007410 | [-0.007629, -0.007204] | True |
| random_slope/mixed/increase_first/post_mse | preserve | 0.195763 | 0.081525 | -0.114238 | [-0.119828, -0.108633] | True |
| random_slope/mixed/increase_first/stable_mse | preserve | 0.001005 | 0.000838 | -0.000167 | [-0.000359, -0.000029] | True |
| random_slope/mixed/decrease_first/post_mse | preserve | 0.193695 | 0.079169 | -0.114526 | [-0.119379, -0.109301] | True |
| random_slope/mixed/decrease_first/stable_mse | preserve | 0.001099 | 0.000955 | -0.000144 | [-0.000261, -0.000051] | True |
| oracle_nofallback/primary | preserve | 0.083258 | 0.079480 | -0.003778 | [-0.005331, -0.002231] | True |
| oracle_nofallback/quiet | strict | 0.000075 | 0.000001 | -0.000074 | [-0.000077, -0.000071] | True |
| oracle_nofallback/noisy | strict | 0.030488 | 0.000927 | -0.029561 | [-0.030481, -0.028637] | True |
| oracle_nofallback/switch_quiet | preserve | 0.065779 | 0.067874 | 0.002095 | [0.001719, 0.002455] | True |
| oracle_nofallback/switch_noisy | preserve | 0.099970 | 0.089354 | -0.010616 | [-0.014975, -0.006315] | True |
| oracle_nofallback/noise_jump | strict | 0.012347 | 0.000706 | -0.011641 | [-0.012217, -0.011065] | True |
| oracle_nofallback/drift | preserve | 0.000184 | 0.000091 | -0.000093 | [-0.000102, -0.000085] | True |
| oracle_nofallback/exactly_quiet | preserve | 0.000000 | 0.000000 | 0.000000 | [0.000000, 0.000000] | True |
| oracle_nofallback/noise_jump/noise_increase | strict | 0.028376 | 0.004227 | -0.024150 | [-0.028613, -0.020053] | True |
| oracle_nofallback/noise_jump/noise_decrease | strict | 0.003266 | 0.000385 | -0.002880 | [-0.003971, -0.001928] | True |
| oracle_nofallback/drift/drift | preserve | 0.000340 | 0.000088 | -0.000252 | [-0.000273, -0.000233] | True |
| oracle_nofallback/mixed/increase_first/post_mse | preserve | 0.084053 | 0.081525 | -0.002528 | [-0.006005, 0.001421] | True |
| oracle_nofallback/mixed/increase_first/stable_mse | strict | 0.012799 | 0.000838 | -0.011961 | [-0.012779, -0.011141] | True |
| oracle_nofallback/mixed/decrease_first/post_mse | preserve | 0.083231 | 0.079169 | -0.004063 | [-0.007093, -0.001055] | True |
| oracle_nofallback/mixed/decrease_first/stable_mse | strict | 0.019102 | 0.000955 | -0.018148 | [-0.019136, -0.017140] | True |

## Absolute errors and memory

| Policy/fixture/coordinate | Excess MSE | Post MSE | Stable MSE | Recovery latency | Mean vector update norm | Total requests | Fast mean width | Fast discarded | ADWIN mean width | Fast share | Slope share | Slope mean |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| slope/core/quiet | 0.000001 | — | 0.000001 | — | 0.004400 | 0.000000 | 32.000000 | 5968.000000 | 3500.500000 | 0.000000 | 0.000000 | 0.000000 |
| slope/core/noisy | 0.000927 | — | 0.000927 | — | 0.004400 | 0.000000 | 32.000000 | 5968.000000 | 2551.729700 | 0.000000 | 0.000000 | 0.000000 |
| slope/core/switch_quiet | 0.005454 | 0.067874 | 0.000026 | 29.640625 | 0.004400 | 64.000000 | 31.837600 | 5968.000000 | 1107.583425 | 0.012800 | 0.000000 | 0.000000 |
| slope/core/switch_noisy | 0.008481 | 0.089354 | 0.001449 | 37.875000 | 0.004400 | 64.000000 | 31.837600 | 5968.000000 | 1013.786100 | 0.012800 | 0.000000 | 0.000000 |
| slope/noise_jump/noise_jump | 0.000706 | — | 0.000706 | — | 0.000674 | 0.000000 | 32.000000 | 5968.000000 | 1874.146550 | 0.000000 | 0.000000 | 0.000000 |
| slope/drift/drift | 0.000091 | — | 0.000091 | — | 0.000805 | 64.000000 | 31.837600 | 5968.000000 | 833.138200 | 0.006400 | 0.408288 | -0.000955 |
| slope/exactly_quiet/exactly_quiet | 0.000000 | — | 0.000000 | — | 0.000167 | 0.000000 | 32.000000 | 5968.000000 | 3500.500000 | 0.000000 | 0.000000 | 0.000000 |
| slope/mixed/increase_first | 0.007293 | 0.081525 | 0.000838 | 38.281250 | 0.003584 | 64.000000 | 31.837600 | 5968.000000 | 1054.642850 | 0.012800 | 0.000000 | 0.000000 |
| slope/mixed/decrease_first | 0.007212 | 0.079169 | 0.000955 | 34.609375 | 0.003584 | 64.000000 | 31.837600 | 5968.000000 | 1049.205000 | 0.012800 | 0.000000 | 0.000000 |
| window/core/quiet | 0.000308 | — | 0.000308 | — | 0.223203 | 0.000000 | 8.000000 | 5992.000000 | — | — | — | — |
| window/core/noisy | 0.122874 | — | 0.122874 | — | 0.223203 | 0.000000 | 8.000000 | 5992.000000 | — | — | — | — |
| window/core/switch_quiet | 0.005427 | 0.064252 | 0.000312 | 8.000000 | 0.223203 | 0.000000 | 8.000000 | 5992.000000 | — | — | — | — |
| window/core/switch_noisy | 0.129919 | 0.188651 | 0.124812 | 227.078125 | 0.223203 | 0.000000 | 8.000000 | 5992.000000 | — | — | — | — |
| window/noise_jump/noise_jump | 0.051106 | — | 0.051106 | — | 0.052938 | 0.000000 | 8.000000 | 5992.000000 | — | — | — | — |
| window/drift/drift | 0.000320 | — | 0.000320 | — | 0.007243 | 0.000000 | 8.000000 | 5992.000000 | — | — | — | — |
| window/exactly_quiet/exactly_quiet | 0.000000 | — | 0.000000 | — | 0.000167 | 0.000000 | 8.000000 | 5992.000000 | — | — | — | — |
| window/mixed/increase_first | 0.057328 | 0.128148 | 0.051170 | 98.640625 | 0.142862 | 0.000000 | 8.000000 | 5992.000000 | — | — | — | — |
| window/mixed/decrease_first | 0.079837 | 0.122411 | 0.076135 | 121.921875 | 0.142862 | 0.000000 | 8.000000 | 5992.000000 | — | — | — | — |
| sgd/core/quiet | 0.000167 | — | 0.000167 | — | 0.166773 | 0.000000 | — | — | — | — | — | — |
| sgd/core/noisy | 0.067184 | — | 0.067184 | — | 0.166773 | 0.000000 | — | — | — | — | — | — |
| sgd/core/switch_quiet | 0.006863 | 0.083825 | 0.000171 | 17.343750 | 0.166773 | 0.000000 | — | — | — | — | — | — |
| sgd/core/switch_noisy | 0.074482 | 0.149892 | 0.067924 | 63.500000 | 0.166773 | 0.000000 | — | — | — | — | — | — |
| sgd/noise_jump/noise_jump | 0.027584 | — | 0.027584 | — | 0.039361 | 0.000000 | — | — | — | — | — | — |
| sgd/drift/drift | 0.000193 | — | 0.000193 | — | 0.005437 | 0.000000 | — | — | — | — | — | — |
| sgd/exactly_quiet/exactly_quiet | 0.000000 | — | 0.000000 | — | 0.000167 | 0.000000 | — | — | — | — | — | — |
| sgd/mixed/increase_first | 0.035190 | 0.118473 | 0.027947 | 44.078125 | 0.106794 | 0.000000 | — | — | — | — | — | — |
| sgd/mixed/decrease_first | 0.047624 | 0.116162 | 0.041665 | 45.578125 | 0.106794 | 0.000000 | — | — | — | — | — | — |
| adwin/core/quiet | 0.000001 | — | 0.000001 | — | 0.004524 | 0.000000 | 3500.500000 | 0.000000 | — | — | — | — |
| adwin/core/noisy | 0.000927 | — | 0.000927 | — | 0.004524 | 94.000000 | 2551.729700 | 2754.750000 | — | — | — | — |
| adwin/core/switch_quiet | 0.012095 | 0.150885 | 0.000026 | 28.125000 | 0.004524 | 458.000000 | 1107.583425 | 4032.625000 | — | — | — | — |
| adwin/core/switch_noisy | 0.019668 | 0.229183 | 0.001449 | 45.562500 | 0.004524 | 418.000000 | 1013.786100 | 4148.250000 | — | — | — | — |
| adwin/noise_jump/noise_jump | 0.000706 | — | 0.000706 | — | 0.000674 | 193.000000 | 1874.146550 | 2102.250000 | — | — | — | — |
| adwin/drift/drift | 0.003154 | — | 0.003154 | — | 0.000566 | 2369.000000 | 833.138200 | 3955.000000 | — | — | — | — |
| adwin/exactly_quiet/exactly_quiet | 0.000000 | — | 0.000000 | — | 0.000167 | 0.000000 | 3500.500000 | 0.000000 | — | — | — | — |
| adwin/mixed/increase_first | 0.016448 | 0.195956 | 0.000838 | 42.734375 | 0.003717 | 453.000000 | 1054.642850 | 4032.250000 | — | — | — | — |
| adwin/mixed/decrease_first | 0.016362 | 0.193541 | 0.000955 | 40.453125 | 0.003717 | 466.000000 | 1049.205000 | 4315.750000 | — | — | — | — |
| oracle_nofallback/core/quiet | 0.000075 | — | 0.000075 | — | 0.057084 | 0.000000 | 32.000000 | 5968.000000 | — | — | — | — |
| oracle_nofallback/core/noisy | 0.030488 | — | 0.030488 | — | 0.057084 | 0.000000 | 32.000000 | 5968.000000 | — | — | — | — |
| oracle_nofallback/core/switch_quiet | 0.005335 | 0.065779 | 0.000079 | 27.500000 | 0.057084 | 64.000000 | 31.837600 | 5968.000000 | — | — | — | — |
| oracle_nofallback/core/switch_noisy | 0.036279 | 0.099970 | 0.030741 | 27.234375 | 0.057084 | 64.000000 | 31.837600 | 5968.000000 | — | — | — | — |
| oracle_nofallback/noise_jump/noise_jump | 0.012347 | — | 0.012347 | — | 0.013392 | 0.000000 | 32.000000 | 5968.000000 | — | — | — | — |
| oracle_nofallback/drift/drift | 0.000184 | — | 0.000184 | — | 0.002021 | 64.000000 | 31.837600 | 5968.000000 | — | — | — | — |
| oracle_nofallback/exactly_quiet/exactly_quiet | 0.000000 | — | 0.000000 | — | 0.000167 | 0.000000 | 32.000000 | 5968.000000 | — | — | — | — |
| oracle_nofallback/mixed/increase_first | 0.018500 | 0.084053 | 0.012799 | 26.171875 | 0.036881 | 64.000000 | 31.837600 | 5968.000000 | — | — | — | — |
| oracle_nofallback/mixed/decrease_first | 0.024233 | 0.083231 | 0.019102 | 28.281250 | 0.036881 | 64.000000 | 31.837600 | 5968.000000 | — | — | — | — |
| random_slope/core/quiet | 0.000002 | — | 0.000002 | — | 0.005011 | 44.000000 | 31.911188 | 5968.000000 | 3500.500000 | 0.007000 | 0.000000 | 0.000000 |
| random_slope/core/noisy | 0.001272 | — | 0.001272 | — | 0.005011 | 24.000000 | 31.941637 | 5968.000000 | 2551.729700 | 0.004600 | 0.000000 | 0.000000 |
| random_slope/core/switch_quiet | 0.012095 | 0.150882 | 0.000026 | 28.125000 | 0.005011 | 40.000000 | 31.908650 | 5968.000000 | 1107.583425 | 0.007200 | 0.000000 | 0.000000 |
| random_slope/core/switch_noisy | 0.020141 | 0.229206 | 0.001961 | 45.390625 | 0.005011 | 29.000000 | 31.941637 | 5968.000000 | 1013.786100 | 0.004600 | 0.000000 | 0.000000 |
| random_slope/noise_jump/noise_jump | 0.000920 | — | 0.000920 | — | 0.000820 | 36.000000 | 31.916263 | 5968.000000 | 1874.146550 | 0.006600 | 0.000000 | 0.000000 |
| random_slope/drift/drift | 0.003133 | — | 0.003133 | — | 0.000584 | 46.000000 | 31.910100 | 5968.718750 | 833.138200 | 0.007100 | 0.000000 | 0.000000 |
| random_slope/exactly_quiet/exactly_quiet | 0.000000 | — | 0.000000 | — | 0.000167 | 42.000000 | 31.921337 | 5968.000000 | 3500.500000 | 0.006200 | 0.000000 | 0.000000 |
| random_slope/mixed/increase_first | 0.016586 | 0.195763 | 0.001005 | 42.046875 | 0.003946 | 29.000000 | 31.939100 | 5968.000000 | 1054.642850 | 0.004800 | 0.000000 | 0.000000 |
| random_slope/mixed/decrease_first | 0.016506 | 0.193695 | 0.001099 | 40.453125 | 0.003946 | 30.000000 | 31.934025 | 5968.000000 | 1049.205000 | 0.005200 | 0.000000 | 0.000000 |

Width counts retained observations, not physical storage. SGD uses exponential weights and has no literal window. Target, drift-boundary and random requests are distinguished by provenance in every record and never mix. Regime shares are post-burn fractions; slope mean averages the estimator slope over in-regime post-burn steps (0 when the regime never fires).


## Measured execution time

| Stage | Family | Seconds |
| --- | --- | ---: |
| tuning | slope | 6.58 |
| tuning | window | 1.07 |
| tuning | sgd | 0.12 |
| tuning | adwin | 3.18 |
| confirmation | slope | 2.83 |
| confirmation | window | 0.03 |
| confirmation | sgd | 0.01 |
| confirmation | adwin | 1.34 |
| confirmation | oracle_nofallback | 0.19 |
| confirmation | random_slope | 2.37 |

Configuration budgets are equal, not CPU costs. Times exclude archive writes and share cached fixtures.

## Scope and reproduction

ADWIN2 is independently implemented from the paper: practical Eq.(3.1), five buckets per size, minimum subwindow5. Gaussian observations violate the bounded-input premise; no corresponding formal guarantee or library-release parity is claimed. All policies see unchanged raw observations.

Granted timing is privileged, not perfect segmentation: retaining K_fast=4 at any boundary may retain old-regime data. No schedule outcome overrides candidate performance. Candidate success requires all75 comparisons. All outcomes close this registration.

Intervals resample whole seeds10000 times with seed135000. Finite menus and synthetic fixtures do not establish global optimizer superiority, population guarantees or general neural-memory utility. Every reached row and source is archived; prior studies remain intact.

`python check_v3_slope.py --evidence results/v3-slope --reproduce` regenerates every reached row and scientific manifest/summary at rtol1e-11/atol1e-13. `python report_v3_slope.py --check` verifies both generated reports.
