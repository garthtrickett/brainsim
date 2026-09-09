# V3 kink-guarded slope

Disposition: **learning_negative**.

| Stage | Rows |
| --- | ---: |
| tuning | 384 |
| confirmation | 224 |

## Finite-menu tuning

Each searched family: 12 configurations ×8 seeds ×5 fixtures. Same objective: half primary post-switch MSE plus half mean of14 adapted retention metrics. Only the guard horizon is searched; estimator and base are frozen.

| Family | Index | Configuration | Tuning objective | Menu endpoint fields |
| --- | ---: | --- | ---: | --- |
| guard | 3 | `{"J": 96}` | 0.050560 | none |
| window | 3 | `{"window": 8}` | 0.089341 | none |
| sgd | 8 | `{"lr": 0.128}` | 0.079478 | none |
| adwin | 9 | `{"delta": 0.1, "clock": 1}` | 0.127872 | delta, clock |

Endpoint choices remain in the registered finite menu; no extension or global-optimum claim. Reference is the no-guard slope policy. Random_guard uses the selected guard horizon.

Frozen random p=0.000260339185, from 112 enriched requests / 432000 tuning coordinate-updates, 16-update suppression, opportunities from t0. Expected pooled frequency is matched, not actual counts or memory age.


## Independent primary performance

| Policy | Finite seeds | Primary MSE | 95% interval |
| --- | ---: | ---: | --- |
| guard | 32 | 0.080223 | [0.0771318752936916, 0.08317326072258163] |
| window | 32 | 0.125129 | [0.12243843293995017, 0.12789170953289938] |
| sgd | 32 | 0.116707 | [0.11468446212437881, 0.11872747092788502] |
| adwin | 32 | 0.193361 | [0.1893076443795139, 0.19762190319015735] |
| reference | 32 | 0.080223 | [0.0771318752936916, 0.08317326072258163] |
| random_guard | 32 | 0.193052 | [0.18887456186944374, 0.19742622736856846] |
| oracle_nofallback | 32 | 0.082834 | [0.0801922368055095, 0.08543549269452586] |

## guard: learning_negative

All75 comparisons are required: >=10% primary improvement over window/sgd/adwin/random_guard, primary preservation against oracle_nofallback, every retention bound, and strict improvement on the7 adapted stable cells against oracle_nofallback (both-perfect cells pass as preservation).

| Contrast | Mode | Control | Policy | Delta | 95% interval | Pass |
| --- | --- | ---: | ---: | ---: | ---: | --- |
| window/primary | improve | 0.125129 | 0.080223 | -0.044906 | [-0.047966, -0.041878] | True |
| window/quiet | preserve | 0.000315 | 0.000001 | -0.000314 | [-0.000318, -0.000310] | True |
| window/noisy | preserve | 0.124075 | 0.000866 | -0.123210 | [-0.125254, -0.121242] | True |
| window/switch_quiet | preserve | 0.064021 | 0.067964 | 0.003943 | [0.003547, 0.004336] | True |
| window/switch_noisy | preserve | 0.187497 | 0.091325 | -0.096171 | [-0.104580, -0.087663] | True |
| window/mixed/increase_first/post_mse | preserve | 0.120422 | 0.077912 | -0.042510 | [-0.047624, -0.037670] | True |
| window/mixed/increase_first/stable_mse | preserve | 0.048724 | 0.000767 | -0.047957 | [-0.050029, -0.045961] | True |
| window/mixed/decrease_first/post_mse | preserve | 0.128574 | 0.083691 | -0.044884 | [-0.051666, -0.038016] | True |
| window/mixed/decrease_first/stable_mse | preserve | 0.076661 | 0.000861 | -0.075799 | [-0.077668, -0.073857] | True |
| window/ramp_steep | preserve | 0.000346 | 0.000143 | -0.000203 | [-0.000210, -0.000196] | True |
| window/ramp_shallow | preserve | 0.000477 | 0.000313 | -0.000164 | [-0.000172, -0.000156] | True |
| window/ramp_noisy | preserve | 0.030971 | 0.003887 | -0.027083 | [-0.027578, -0.026603] | True |
| window/ramp_steep/ramp | preserve | 0.000612 | 0.000741 | 0.000130 | [0.000084, 0.000176] | True |
| window/ramp_shallow/ramp | preserve | 0.000522 | 0.000389 | -0.000134 | [-0.000142, -0.000125] | True |
| window/ramp_noisy/ramp | preserve | 0.031001 | 0.007949 | -0.023053 | [-0.023663, -0.022425] | True |
| sgd/primary | improve | 0.116707 | 0.080223 | -0.036483 | [-0.039072, -0.033897] | True |
| sgd/quiet | preserve | 0.000172 | 0.000001 | -0.000171 | [-0.000173, -0.000168] | True |
| sgd/noisy | preserve | 0.068064 | 0.000866 | -0.067199 | [-0.068587, -0.065851] | True |
| sgd/switch_quiet | preserve | 0.083604 | 0.067964 | -0.015640 | [-0.016038, -0.015249] | True |
| sgd/switch_noisy | preserve | 0.150273 | 0.091325 | -0.058947 | [-0.065477, -0.052365] | True |
| sgd/mixed/increase_first/post_mse | preserve | 0.113205 | 0.077912 | -0.035293 | [-0.039445, -0.031109] | True |
| sgd/mixed/increase_first/stable_mse | preserve | 0.026784 | 0.000767 | -0.026017 | [-0.027220, -0.024856] | True |
| sgd/mixed/decrease_first/post_mse | preserve | 0.119744 | 0.083691 | -0.036054 | [-0.041071, -0.030881] | True |
| sgd/mixed/decrease_first/stable_mse | preserve | 0.041950 | 0.000861 | -0.041088 | [-0.042226, -0.039946] | True |
| sgd/ramp_steep | preserve | 0.000266 | 0.000143 | -0.000123 | [-0.000131, -0.000116] | True |
| sgd/ramp_shallow | preserve | 0.000389 | 0.000313 | -0.000076 | [-0.000083, -0.000070] | True |
| sgd/ramp_noisy | preserve | 0.016888 | 0.003887 | -0.013001 | [-0.013341, -0.012661] | True |
| sgd/ramp_steep/ramp | preserve | 0.001107 | 0.000741 | -0.000366 | [-0.000421, -0.000309] | True |
| sgd/ramp_shallow/ramp | preserve | 0.000448 | 0.000389 | -0.000060 | [-0.000066, -0.000054] | True |
| sgd/ramp_noisy/ramp | preserve | 0.016951 | 0.007949 | -0.009002 | [-0.009302, -0.008691] | True |
| adwin/primary | improve | 0.193361 | 0.080223 | -0.113138 | [-0.116577, -0.109839] | True |
| adwin/quiet | preserve | 0.000001 | 0.000001 | 0.000000 | [0.000000, 0.000000] | True |
| adwin/noisy | preserve | 0.000866 | 0.000866 | 0.000000 | [0.000000, 0.000000] | True |
| adwin/switch_quiet | preserve | 0.149664 | 0.067964 | -0.081700 | [-0.083961, -0.079395] | True |
| adwin/switch_noisy | preserve | 0.229971 | 0.091325 | -0.138646 | [-0.148790, -0.128733] | True |
| adwin/mixed/increase_first/post_mse | preserve | 0.192758 | 0.077912 | -0.114846 | [-0.119751, -0.109618] | True |
| adwin/mixed/increase_first/stable_mse | preserve | 0.000767 | 0.000767 | 0.000000 | [0.000000, 0.000000] | True |
| adwin/mixed/decrease_first/post_mse | preserve | 0.201050 | 0.083691 | -0.117360 | [-0.124649, -0.110163] | True |
| adwin/mixed/decrease_first/stable_mse | preserve | 0.000861 | 0.000861 | 0.000000 | [0.000000, 0.000000] | True |
| adwin/ramp_steep | preserve | 0.003329 | 0.000143 | -0.003186 | [-0.003211, -0.003160] | True |
| adwin/ramp_shallow | preserve | 0.002526 | 0.000313 | -0.002214 | [-0.002241, -0.002188] | True |
| adwin/ramp_noisy | preserve | 0.009979 | 0.003887 | -0.006092 | [-0.006672, -0.005491] | True |
| adwin/ramp_steep/ramp | preserve | 0.031439 | 0.000741 | -0.030697 | [-0.030933, -0.030456] | True |
| adwin/ramp_shallow/ramp | preserve | 0.003192 | 0.000389 | -0.002804 | [-0.002844, -0.002765] | True |
| adwin/ramp_noisy/ramp | preserve | 0.023211 | 0.007949 | -0.015262 | [-0.016777, -0.013704] | True |
| random_guard/primary | improve | 0.193052 | 0.080223 | -0.112829 | [-0.116220, -0.109605] | True |
| random_guard/quiet | preserve | 0.000003 | 0.000001 | -0.000002 | [-0.000002, -0.000001] | True |
| random_guard/noisy | preserve | 0.001385 | 0.000866 | -0.000520 | [-0.000755, -0.000302] | True |
| random_guard/switch_quiet | preserve | 0.150008 | 0.067964 | -0.082044 | [-0.084696, -0.079503] | True |
| random_guard/switch_noisy | preserve | 0.229479 | 0.091325 | -0.138153 | [-0.148682, -0.127751] | True |
| random_guard/mixed/increase_first/post_mse | preserve | 0.191605 | 0.077912 | -0.113693 | [-0.119243, -0.107667] | True |
| random_guard/mixed/increase_first/stable_mse | preserve | 0.000892 | 0.000767 | -0.000125 | [-0.000220, -0.000048] | True |
| random_guard/mixed/decrease_first/post_mse | preserve | 0.201117 | 0.083691 | -0.117427 | [-0.124714, -0.110228] | True |
| random_guard/mixed/decrease_first/stable_mse | preserve | 0.001245 | 0.000861 | -0.000384 | [-0.000661, -0.000167] | True |
| random_guard/ramp_steep | preserve | 0.003311 | 0.000143 | -0.003169 | [-0.003200, -0.003135] | True |
| random_guard/ramp_shallow | preserve | 0.002508 | 0.000313 | -0.002196 | [-0.002223, -0.002169] | True |
| random_guard/ramp_noisy | preserve | 0.010038 | 0.003887 | -0.006151 | [-0.006721, -0.005565] | True |
| random_guard/ramp_steep/ramp | preserve | 0.031256 | 0.000741 | -0.030515 | [-0.030815, -0.030193] | True |
| random_guard/ramp_shallow/ramp | preserve | 0.003169 | 0.000389 | -0.002781 | [-0.002822, -0.002741] | True |
| random_guard/ramp_noisy/ramp | preserve | 0.023173 | 0.007949 | -0.015225 | [-0.016720, -0.013668] | True |
| oracle_nofallback/primary | preserve | 0.082834 | 0.080223 | -0.002611 | [-0.004193, -0.000904] | True |
| oracle_nofallback/quiet | strict | 0.000078 | 0.000001 | -0.000077 | [-0.000079, -0.000075] | True |
| oracle_nofallback/noisy | strict | 0.031288 | 0.000866 | -0.030422 | [-0.031595, -0.029297] | True |
| oracle_nofallback/switch_quiet | preserve | 0.065694 | 0.067964 | 0.002270 | [0.001955, 0.002592] | True |
| oracle_nofallback/switch_noisy | preserve | 0.101768 | 0.091325 | -0.010442 | [-0.014339, -0.006161] | True |
| oracle_nofallback/mixed/increase_first/post_mse | preserve | 0.079440 | 0.077912 | -0.001528 | [-0.004118, 0.001297] | True |
| oracle_nofallback/mixed/increase_first/stable_mse | strict | 0.012515 | 0.000767 | -0.011748 | [-0.012497, -0.011015] | True |
| oracle_nofallback/mixed/decrease_first/post_mse | preserve | 0.084434 | 0.083691 | -0.000744 | [-0.003977, 0.002764] | True |
| oracle_nofallback/mixed/decrease_first/stable_mse | strict | 0.019314 | 0.000861 | -0.018452 | [-0.019295, -0.017611] | True |
| oracle_nofallback/ramp_steep | strict | 0.000497 | 0.000143 | -0.000354 | [-0.000364, -0.000343] | True |
| oracle_nofallback/ramp_shallow | strict | 0.000264 | 0.000313 | 0.000049 | [0.000042, 0.000055] | False |
| oracle_nofallback/ramp_noisy | strict | 0.007860 | 0.003887 | -0.003973 | [-0.004255, -0.003675] | True |
| oracle_nofallback/ramp_steep/ramp | preserve | 0.004248 | 0.000741 | -0.003506 | [-0.003597, -0.003412] | True |
| oracle_nofallback/ramp_shallow/ramp | preserve | 0.000314 | 0.000389 | 0.000075 | [0.000069, 0.000080] | True |
| oracle_nofallback/ramp_noisy/ramp | preserve | 0.008049 | 0.007949 | -0.000101 | [-0.000348, 0.000142] | True |

## Absolute errors and memory

| Policy/fixture/coordinate | Excess MSE | Post MSE | Stable MSE | Ramp MSE | Recovery latency | Mean vector update norm | Total requests | Fast mean width | Fast discarded | ADWIN mean width | Fast share | Guard share | Slope share | Slope mean |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| guard/core/quiet | 0.000001 | — | 0.000001 | — | — | 0.004303 | 0.000000 | 32.000000 | 5968.000000 | 3500.500000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| guard/core/noisy | 0.000866 | — | 0.000866 | — | — | 0.004303 | 0.000000 | 32.000000 | 5968.000000 | 2593.077350 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| guard/core/switch_quiet | 0.005465 | 0.067964 | 0.000031 | — | 29.406250 | 0.004303 | 64.000000 | 31.837600 | 5968.000000 | 1107.117600 | 0.012800 | 0.000000 | 0.000000 | 0.000000 |
| guard/core/switch_noisy | 0.008808 | 0.091325 | 0.001633 | — | 42.343750 | 0.004303 | 64.000000 | 31.837600 | 5968.000000 | 1053.217400 | 0.012800 | 0.000000 | 0.000000 | 0.000000 |
| guard/mixed/increase_first | 0.006939 | 0.077912 | 0.000767 | — | 36.562500 | 0.003550 | 64.000000 | 31.837600 | 5968.000000 | 1078.259625 | 0.012800 | 0.000000 | 0.000000 | 0.000000 |
| guard/mixed/decrease_first | 0.007488 | 0.083691 | 0.000861 | — | 38.203125 | 0.003550 | 64.000000 | 31.837600 | 5968.000000 | 1040.267925 | 0.012800 | 0.000000 | 0.000000 | 0.000000 |
| guard/steep/steep | 0.000143 | — | 0.000143 | 0.000741 | — | 0.000604 | 64.000000 | 31.837600 | 5968.000000 | 1574.516000 | 0.006400 | 0.019200 | 0.080800 | -0.003979 |
| guard/shallow/shallow | 0.000313 | — | 0.000313 | 0.000389 | — | 0.001233 | 64.000000 | 31.884850 | 5985.500000 | 582.252450 | 0.002388 | 0.019200 | 0.769019 | -0.000273 |
| guard/noisy/noisy | 0.003887 | — | 0.003887 | 0.007949 | — | 0.005761 | 64.000000 | 31.837600 | 5968.000000 | 962.346250 | 0.006400 | 0.019200 | 0.380925 | -0.001012 |
| window/core/quiet | 0.000315 | — | 0.000315 | — | — | 0.223112 | 0.000000 | 8.000000 | 5992.000000 | — | — | — | — | — |
| window/core/noisy | 0.124075 | — | 0.124075 | — | — | 0.223112 | 0.000000 | 8.000000 | 5992.000000 | — | — | — | — | — |
| window/core/switch_quiet | 0.005408 | 0.064021 | 0.000311 | — | 7.984375 | 0.223112 | 0.000000 | 8.000000 | 5992.000000 | — | — | — | — | — |
| window/core/switch_noisy | 0.129267 | 0.187497 | 0.124204 | — | 281.515625 | 0.223112 | 0.000000 | 8.000000 | 5992.000000 | — | — | — | — | — |
| window/mixed/increase_first | 0.054460 | 0.120422 | 0.048724 | — | 118.640625 | 0.142754 | 0.000000 | 8.000000 | 5992.000000 | — | — | — | — | — |
| window/mixed/decrease_first | 0.080814 | 0.128574 | 0.076661 | — | 120.531250 | 0.142754 | 0.000000 | 8.000000 | 5992.000000 | — | — | — | — | — |
| window/steep/steep | 0.000346 | — | 0.000346 | 0.000612 | — | 0.007287 | 0.000000 | 8.000000 | 5992.000000 | — | — | — | — | — |
| window/shallow/shallow | 0.000477 | — | 0.000477 | 0.000522 | — | 0.007313 | 0.000000 | 8.000000 | 5992.000000 | — | — | — | — | — |
| window/noisy/noisy | 0.030971 | — | 0.030971 | 0.031001 | — | 0.070984 | 0.000000 | 8.000000 | 5992.000000 | — | — | — | — | — |
| sgd/core/quiet | 0.000172 | — | 0.000172 | — | — | 0.166532 | 0.000000 | — | — | — | — | — | — | — |
| sgd/core/noisy | 0.068064 | — | 0.068064 | — | — | 0.166532 | 0.000000 | — | — | — | — | — | — | — |
| sgd/core/switch_quiet | 0.006846 | 0.083604 | 0.000171 | — | 17.359375 | 0.166532 | 0.000000 | — | — | — | — | — | — | — |
| sgd/core/switch_noisy | 0.074408 | 0.150273 | 0.067811 | — | 73.656250 | 0.166532 | 0.000000 | — | — | — | — | — | — | — |
| sgd/mixed/increase_first | 0.033697 | 0.113205 | 0.026784 | — | 40.312500 | 0.106329 | 0.000000 | — | — | — | — | — | — | — |
| sgd/mixed/decrease_first | 0.048173 | 0.119744 | 0.041950 | — | 47.562500 | 0.106329 | 0.000000 | — | — | — | — | — | — | — |
| sgd/steep/steep | 0.000266 | — | 0.000266 | 0.001107 | — | 0.005504 | 0.000000 | — | — | — | — | — | — | — |
| sgd/shallow/shallow | 0.000389 | — | 0.000389 | 0.000448 | — | 0.005498 | 0.000000 | — | — | — | — | — | — | — |
| sgd/noisy/noisy | 0.016888 | — | 0.016888 | 0.016951 | — | 0.053019 | 0.000000 | — | — | — | — | — | — | — |
| adwin/core/quiet | 0.000001 | — | 0.000001 | — | — | 0.004437 | 0.000000 | 3500.500000 | 0.000000 | — | — | — | — | — |
| adwin/core/noisy | 0.000866 | — | 0.000866 | — | — | 0.004437 | 67.000000 | 2593.077350 | 1980.000000 | — | — | — | — | — |
| adwin/core/switch_quiet | 0.012001 | 0.149664 | 0.000031 | — | 26.765625 | 0.004437 | 448.000000 | 1107.117600 | 4012.250000 | — | — | — | — | — |
| adwin/core/switch_noisy | 0.019900 | 0.229971 | 0.001633 | — | 55.562500 | 0.004437 | 426.000000 | 1053.217400 | 4257.625000 | — | — | — | — | — |
| adwin/mixed/increase_first | 0.016126 | 0.192758 | 0.000767 | — | 41.843750 | 0.003692 | 453.000000 | 1078.259625 | 4012.375000 | — | — | — | — | — |
| adwin/mixed/decrease_first | 0.016877 | 0.201050 | 0.000861 | — | 44.296875 | 0.003692 | 473.000000 | 1040.267925 | 4348.750000 | — | — | — | — | — |
| adwin/steep/steep | 0.003329 | — | 0.003329 | 0.031439 | — | 0.000573 | 1332.000000 | 1574.516000 | 2483.500000 | — | — | — | — | — |
| adwin/shallow/shallow | 0.002526 | — | 0.002526 | 0.003192 | — | 0.000483 | 2136.000000 | 582.252450 | 5632.500000 | — | — | — | — | — |
| adwin/noisy/noisy | 0.009979 | — | 0.009979 | 0.023211 | — | 0.001438 | 1304.000000 | 962.346250 | 3911.250000 | — | — | — | — | — |
| reference/core/quiet | 0.000001 | — | 0.000001 | — | — | 0.004303 | 0.000000 | 32.000000 | 5968.000000 | — | — | — | — | — |
| reference/core/noisy | 0.000866 | — | 0.000866 | — | — | 0.004303 | 0.000000 | 32.000000 | 5968.000000 | — | — | — | — | — |
| reference/core/switch_quiet | 0.005465 | 0.067964 | 0.000031 | — | 29.406250 | 0.004303 | 64.000000 | 31.837600 | 5968.000000 | — | — | — | — | — |
| reference/core/switch_noisy | 0.008808 | 0.091325 | 0.001633 | — | 42.343750 | 0.004303 | 64.000000 | 31.837600 | 5968.000000 | — | — | — | — | — |
| reference/mixed/increase_first | 0.006939 | 0.077912 | 0.000767 | — | 36.562500 | 0.003550 | 64.000000 | 31.837600 | 5968.000000 | — | — | — | — | — |
| reference/mixed/decrease_first | 0.007488 | 0.083691 | 0.000861 | — | 38.203125 | 0.003550 | 64.000000 | 31.837600 | 5968.000000 | — | — | — | — | — |
| reference/steep/steep | 0.000140 | — | 0.000140 | 0.000714 | — | 0.000605 | 64.000000 | 31.837600 | 5968.000000 | — | — | — | — | — |
| reference/shallow/shallow | 0.000968 | — | 0.000968 | 0.001220 | — | 0.001267 | 64.000000 | 31.884850 | 5985.500000 | — | — | — | — | — |
| reference/noisy/noisy | 0.003820 | — | 0.003820 | 0.007788 | — | 0.005647 | 64.000000 | 31.837600 | 5968.000000 | — | — | — | — | — |
| random_guard/core/quiet | 0.000003 | — | 0.000003 | — | — | 0.005274 | 50.000000 | 31.885813 | 5968.000000 | 3500.500000 | 0.009000 | 0.000000 | 0.000000 | 0.000000 |
| random_guard/core/noisy | 0.001385 | — | 0.001385 | — | — | 0.005274 | 49.000000 | 31.901038 | 5968.000000 | 2593.077350 | 0.007788 | 0.000000 | 0.000000 | 0.000000 |
| random_guard/core/switch_quiet | 0.012030 | 0.150008 | 0.000032 | — | 26.765625 | 0.005274 | 51.000000 | 31.883781 | 5968.000000 | 1107.117600 | 0.009188 | 0.000000 | 0.000000 | 0.000000 |
| random_guard/core/switch_noisy | 0.020254 | 0.229479 | 0.002060 | — | 55.296875 | 0.005274 | 39.000000 | 31.911188 | 5968.000000 | 1053.217400 | 0.006988 | 0.000000 | 0.000000 | 0.000000 |
| random_guard/mixed/increase_first | 0.016149 | 0.191605 | 0.000892 | — | 41.765625 | 0.004086 | 47.000000 | 31.908994 | 5968.343750 | 1078.259625 | 0.007094 | 0.000000 | 0.000000 | 0.000000 |
| random_guard/mixed/decrease_first | 0.017235 | 0.201117 | 0.001245 | — | 44.296875 | 0.004086 | 46.000000 | 31.906112 | 5968.000000 | 1040.267925 | 0.007400 | 0.000000 | 0.000000 | 0.000000 |
| random_guard/steep/steep | 0.003311 | — | 0.003311 | 0.031256 | — | 0.000597 | 57.000000 | 31.892469 | 5968.000000 | 1574.516000 | 0.008537 | 0.000000 | 0.000000 | 0.000000 |
| random_guard/shallow/shallow | 0.002508 | — | 0.002508 | 0.003169 | — | 0.000508 | 59.000000 | 31.871775 | 5968.625000 | 582.252450 | 0.010050 | 0.000000 | 0.000000 | 0.000000 |
| random_guard/noisy/noisy | 0.010038 | — | 0.010038 | 0.023173 | — | 0.001659 | 47.000000 | 31.903800 | 5968.281250 | 962.346250 | 0.007519 | 0.000000 | 0.000000 | 0.000000 |
| oracle_nofallback/core/quiet | 0.000078 | — | 0.000078 | — | — | 0.057063 | 0.000000 | 32.000000 | 5968.000000 | — | — | — | — | — |
| oracle_nofallback/core/noisy | 0.031288 | — | 0.031288 | — | — | 0.057063 | 0.000000 | 32.000000 | 5968.000000 | — | — | — | — | — |
| oracle_nofallback/core/switch_quiet | 0.005328 | 0.065694 | 0.000079 | — | 27.531250 | 0.057063 | 64.000000 | 31.837600 | 5968.000000 | — | — | — | — | — |
| oracle_nofallback/core/switch_noisy | 0.036394 | 0.101768 | 0.030709 | — | 27.812500 | 0.057063 | 64.000000 | 31.837600 | 5968.000000 | — | — | — | — | — |
| oracle_nofallback/mixed/increase_first | 0.017869 | 0.079440 | 0.012515 | — | 27.968750 | 0.036745 | 64.000000 | 31.837600 | 5968.000000 | — | — | — | — | — |
| oracle_nofallback/mixed/decrease_first | 0.024523 | 0.084434 | 0.019314 | — | 28.109375 | 0.036745 | 64.000000 | 31.837600 | 5968.000000 | — | — | — | — | — |
| oracle_nofallback/steep/steep | 0.000497 | — | 0.000497 | 0.004248 | — | 0.002155 | 64.000000 | 31.837600 | 5968.000000 | — | — | — | — | — |
| oracle_nofallback/shallow/shallow | 0.000264 | — | 0.000264 | 0.000314 | — | 0.002037 | 64.000000 | 31.884850 | 5985.500000 | — | — | — | — | — |
| oracle_nofallback/noisy/noisy | 0.007860 | — | 0.007860 | 0.008049 | — | 0.018118 | 64.000000 | 31.837600 | 5968.000000 | — | — | — | — | — |

Width counts retained observations, not physical storage. SGD uses exponential weights and has no literal window. Target, drift-boundary and random requests are distinguished by provenance in every record and never mix. Guard share counts in-segment fast predictions; fast share counts out-of-segment ones.


## Measured execution time

| Stage | Family | Seconds |
| --- | --- | ---: |
| tuning | guard | 7.36 |
| tuning | window | 0.15 |
| tuning | sgd | 0.09 |
| tuning | adwin | 3.21 |
| confirmation | guard | 2.49 |
| confirmation | window | 0.00 |
| confirmation | sgd | 0.01 |
| confirmation | adwin | 1.23 |
| confirmation | reference | 2.42 |
| confirmation | random_guard | 2.91 |
| confirmation | oracle_nofallback | 0.25 |

Configuration budgets are equal, not CPU costs. Times exclude archive writes and share cached fixtures.

## Scope and reproduction

ADWIN2 is independently implemented from the paper: practical Eq.(3.1), five buckets per size, minimum subwindow5. Gaussian observations violate the bounded-input premise; no corresponding formal guarantee or library-release parity is claimed. All policies see unchanged raw observations.

Granted timing is privileged. No schedule outcome overrides candidate performance. Candidate success requires all75 comparisons. All outcomes close this registration.

Intervals resample whole seeds10000 times with seed165000. Finite menus and synthetic fixtures do not establish global optimizer superiority, population guarantees or general neural-memory utility. Every reached row and source is archived; prior studies remain intact.

`python check_v3_slopeguard.py --evidence results/v3-slopeguard --reproduce` regenerates every reached row and scientific manifest/summary at rtol1e-11/atol1e-13. `python report_v3_slopeguard.py --check` verifies both generated reports.
