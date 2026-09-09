# V3 slope broader benchmark

Disposition: **learning_negative**.

| Stage | Rows |
| --- | ---: |
| tuning | 288 |
| confirmation | 192 |

## Finite-menu tuning

Each searched family: 12 configurations ×8 seeds ×5 fixtures. Same objective: half primary post-switch MSE plus half mean of14 adapted retention metrics. The candidate configuration is frozen from the slope manifest.

| Family | Index | Configuration | Tuning objective | Menu endpoint fields |
| --- | ---: | --- | ---: | --- |
| window | 3 | `{"window": 8}` | 0.093556 | none |
| sgd | 8 | `{"lr": 0.128}` | 0.083313 | none |
| adwin | 9 | `{"delta": 0.1, "clock": 1}` | 0.129125 | delta, clock |

Endpoint choices remain in the registered finite menu; no extension or global-optimum claim. Oracle_nofallback is the fixed fast base on the enriched schedule. Random_slope uses the frozen estimator.

Frozen random p=0.000260339185, from 112 enriched requests / 432000 tuning coordinate-updates, 16-update suppression, opportunities from t0. Expected pooled frequency is matched, not actual counts or memory age.


## Independent primary performance

| Policy | Finite seeds | Primary MSE | 95% interval |
| --- | ---: | ---: | --- |
| window | 32 | 0.125080 | [0.1221226873626198, 0.12809379543312402] |
| sgd | 32 | 0.115912 | [0.11324565154720913, 0.11867366143651442] |
| adwin | 32 | 0.192259 | [0.18751806226758055, 0.19693710718478116] |
| slope | 32 | 0.079994 | [0.0763089203285206, 0.08407792519275743] |
| oracle_nofallback | 32 | 0.083458 | [0.08033532783823073, 0.08668257105229153] |
| random_slope | 32 | 0.191738 | [0.1869124869672622, 0.1965275370329471] |

## slope: learning_negative

All75 comparisons are required: >=10% primary improvement over window/sgd/adwin/random_slope, primary preservation against oracle_nofallback, every retention bound, and strict improvement on the7 adapted stable cells against oracle_nofallback (both-perfect cells pass as preservation).

| Contrast | Mode | Control | Policy | Delta | 95% interval | Pass |
| --- | --- | ---: | ---: | ---: | --- | --- |
| window/primary | improve | 0.125080 | 0.079994 | -0.045085 | [-0.048299, -0.041951] | True |
| window/quiet | preserve | 0.000315 | 0.000001 | -0.000314 | [-0.000319, -0.000309] | True |
| window/noisy | preserve | 0.122613 | 0.001063 | -0.121550 | [-0.123268, -0.119841] | True |
| window/switch_quiet | preserve | 0.064167 | 0.068125 | 0.003957 | [0.003638, 0.004284] | True |
| window/switch_noisy | preserve | 0.192459 | 0.091840 | -0.100618 | [-0.110523, -0.090980] | True |
| window/mixed/increase_first/post_mse | preserve | 0.122079 | 0.082644 | -0.039435 | [-0.045669, -0.033205] | True |
| window/mixed/increase_first/stable_mse | preserve | 0.048754 | 0.000781 | -0.047973 | [-0.049534, -0.046390] | True |
| window/mixed/decrease_first/post_mse | preserve | 0.121613 | 0.077368 | -0.044245 | [-0.051860, -0.036933] | True |
| window/mixed/decrease_first/stable_mse | preserve | 0.076362 | 0.001035 | -0.075328 | [-0.077202, -0.073578] | True |
| window/ramp_steep | preserve | 0.000344 | 0.000143 | -0.000201 | [-0.000212, -0.000190] | True |
| window/ramp_shallow | preserve | 0.000479 | 0.000960 | 0.000481 | [0.000470, 0.000492] | True |
| window/ramp_noisy | preserve | 0.031000 | 0.003648 | -0.027353 | [-0.027861, -0.026870] | True |
| window/ramp_steep/ramp | preserve | 0.000615 | 0.000733 | 0.000118 | [0.000064, 0.000172] | True |
| window/ramp_shallow/ramp | preserve | 0.000522 | 0.001212 | 0.000690 | [0.000676, 0.000704] | True |
| window/ramp_noisy/ramp | preserve | 0.030147 | 0.007475 | -0.022672 | [-0.023189, -0.022114] | True |
| sgd/primary | improve | 0.115912 | 0.079994 | -0.035918 | [-0.038630, -0.033187] | True |
| sgd/quiet | preserve | 0.000173 | 0.000001 | -0.000172 | [-0.000175, -0.000169] | True |
| sgd/noisy | preserve | 0.066889 | 0.001063 | -0.065827 | [-0.066929, -0.064720] | True |
| sgd/switch_quiet | preserve | 0.083761 | 0.068125 | -0.015637 | [-0.015957, -0.015318] | True |
| sgd/switch_noisy | preserve | 0.151496 | 0.091840 | -0.059656 | [-0.068478, -0.051206] | True |
| sgd/mixed/increase_first/post_mse | preserve | 0.114527 | 0.082644 | -0.031883 | [-0.036921, -0.026901] | True |
| sgd/mixed/increase_first/stable_mse | preserve | 0.026601 | 0.000781 | -0.025820 | [-0.026735, -0.024934] | True |
| sgd/mixed/decrease_first/post_mse | preserve | 0.113862 | 0.077368 | -0.036494 | [-0.041368, -0.031599] | True |
| sgd/mixed/decrease_first/stable_mse | preserve | 0.041491 | 0.001035 | -0.040456 | [-0.041595, -0.039381] | True |
| sgd/ramp_steep | preserve | 0.000266 | 0.000143 | -0.000123 | [-0.000133, -0.000113] | True |
| sgd/ramp_shallow | preserve | 0.000386 | 0.000960 | 0.000574 | [0.000564, 0.000584] | True |
| sgd/ramp_noisy | preserve | 0.016952 | 0.003648 | -0.013304 | [-0.013670, -0.012959] | True |
| sgd/ramp_steep/ramp | preserve | 0.001110 | 0.000733 | -0.000376 | [-0.000435, -0.000317] | True |
| sgd/ramp_shallow/ramp | preserve | 0.000443 | 0.001212 | 0.000769 | [0.000756, 0.000781] | True |
| sgd/ramp_noisy/ramp | preserve | 0.016481 | 0.007475 | -0.009006 | [-0.009350, -0.008653] | True |
| adwin/primary | improve | 0.192259 | 0.079994 | -0.112265 | [-0.115682, -0.108841] | True |
| adwin/quiet | preserve | 0.000001 | 0.000001 | 0.000000 | [0.000000, 0.000000] | True |
| adwin/noisy | preserve | 0.001063 | 0.001063 | 0.000000 | [0.000000, 0.000000] | True |
| adwin/switch_quiet | preserve | 0.151650 | 0.068125 | -0.083526 | [-0.085250, -0.081762] | True |
| adwin/switch_noisy | preserve | 0.229889 | 0.091840 | -0.138048 | [-0.146188, -0.129766] | True |
| adwin/mixed/increase_first/post_mse | preserve | 0.193946 | 0.082644 | -0.111301 | [-0.117322, -0.105233] | True |
| adwin/mixed/increase_first/stable_mse | preserve | 0.000781 | 0.000781 | 0.000000 | [0.000000, 0.000000] | True |
| adwin/mixed/decrease_first/post_mse | preserve | 0.193551 | 0.077368 | -0.116183 | [-0.121600, -0.110805] | True |
| adwin/mixed/decrease_first/stable_mse | preserve | 0.001035 | 0.001035 | 0.000000 | [0.000000, 0.000000] | True |
| adwin/ramp_steep | preserve | 0.003329 | 0.000143 | -0.003186 | [-0.003210, -0.003162] | True |
| adwin/ramp_shallow | preserve | 0.002503 | 0.000960 | -0.001543 | [-0.001565, -0.001524] | True |
| adwin/ramp_noisy | preserve | 0.009758 | 0.003648 | -0.006110 | [-0.006620, -0.005583] | True |
| adwin/ramp_steep/ramp | preserve | 0.031445 | 0.000733 | -0.030712 | [-0.030942, -0.030474] | True |
| adwin/ramp_shallow/ramp | preserve | 0.003166 | 0.001212 | -0.001954 | [-0.001981, -0.001930] | True |
| adwin/ramp_noisy/ramp | preserve | 0.022834 | 0.007475 | -0.015359 | [-0.016773, -0.013925] | True |
| random_slope/primary | improve | 0.191738 | 0.079994 | -0.111743 | [-0.115110, -0.108400] | True |
| random_slope/quiet | preserve | 0.000003 | 0.000001 | -0.000002 | [-0.000002, -0.000001] | True |
| random_slope/noisy | preserve | 0.001434 | 0.001063 | -0.000371 | [-0.000530, -0.000230] | True |
| random_slope/switch_quiet | preserve | 0.151167 | 0.068125 | -0.083042 | [-0.084935, -0.081144] | True |
| random_slope/switch_noisy | preserve | 0.228559 | 0.091840 | -0.136719 | [-0.145178, -0.127961] | True |
| random_slope/mixed/increase_first/post_mse | preserve | 0.193676 | 0.082644 | -0.111032 | [-0.117140, -0.104707] | True |
| random_slope/mixed/increase_first/stable_mse | preserve | 0.000901 | 0.000781 | -0.000120 | [-0.000195, -0.000058] | True |
| random_slope/mixed/decrease_first/post_mse | preserve | 0.193549 | 0.077368 | -0.116181 | [-0.121598, -0.110803] | True |
| random_slope/mixed/decrease_first/stable_mse | preserve | 0.001472 | 0.001035 | -0.000438 | [-0.000704, -0.000211] | True |
| random_slope/ramp_steep | preserve | 0.003324 | 0.000143 | -0.003181 | [-0.003209, -0.003150] | True |
| random_slope/ramp_shallow | preserve | 0.002492 | 0.000960 | -0.001532 | [-0.001551, -0.001513] | True |
| random_slope/ramp_noisy | preserve | 0.009814 | 0.003648 | -0.006166 | [-0.006677, -0.005638] | True |
| random_slope/ramp_steep/ramp | preserve | 0.031385 | 0.000733 | -0.030652 | [-0.030926, -0.030346] | True |
| random_slope/ramp_shallow/ramp | preserve | 0.003151 | 0.001212 | -0.001939 | [-0.001964, -0.001916] | True |
| random_slope/ramp_noisy/ramp | preserve | 0.022765 | 0.007475 | -0.015290 | [-0.016692, -0.013861] | True |
| oracle_nofallback/primary | preserve | 0.083458 | 0.079994 | -0.003463 | [-0.004971, -0.001840] | True |
| oracle_nofallback/quiet | strict | 0.000080 | 0.000001 | -0.000079 | [-0.000081, -0.000077] | True |
| oracle_nofallback/noisy | strict | 0.030370 | 0.001063 | -0.029307 | [-0.030137, -0.028482] | True |
| oracle_nofallback/switch_quiet | preserve | 0.065803 | 0.068125 | 0.002322 | [0.002026, 0.002623] | True |
| oracle_nofallback/switch_noisy | preserve | 0.104153 | 0.091840 | -0.012313 | [-0.016254, -0.008200] | True |
| oracle_nofallback/mixed/increase_first/post_mse | preserve | 0.084302 | 0.082644 | -0.001658 | [-0.004307, 0.001058] | True |
| oracle_nofallback/mixed/increase_first/stable_mse | strict | 0.012034 | 0.000781 | -0.011253 | [-0.011886, -0.010681] | True |
| oracle_nofallback/mixed/decrease_first/post_mse | preserve | 0.079573 | 0.077368 | -0.002205 | [-0.005337, 0.001249] | True |
| oracle_nofallback/mixed/decrease_first/stable_mse | strict | 0.018623 | 0.001035 | -0.017588 | [-0.018425, -0.016839] | True |
| oracle_nofallback/ramp_steep | strict | 0.000498 | 0.000143 | -0.000355 | [-0.000367, -0.000342] | True |
| oracle_nofallback/ramp_shallow | strict | 0.000259 | 0.000960 | 0.000701 | [0.000691, 0.000711] | False |
| oracle_nofallback/ramp_noisy | strict | 0.007939 | 0.003648 | -0.004292 | [-0.004596, -0.003989] | True |
| oracle_nofallback/ramp_steep/ramp | preserve | 0.004253 | 0.000733 | -0.003520 | [-0.003612, -0.003425] | True |
| oracle_nofallback/ramp_shallow/ramp | preserve | 0.000306 | 0.001212 | 0.000906 | [0.000892, 0.000919] | True |
| oracle_nofallback/ramp_noisy/ramp | preserve | 0.007773 | 0.007475 | -0.000298 | [-0.000628, 0.000039] | True |

## Absolute errors and memory

| Policy/fixture/coordinate | Excess MSE | Post MSE | Stable MSE | Ramp MSE | Recovery latency | Mean vector update norm | Total requests | Fast mean width | Fast discarded | ADWIN mean width | Fast share | Slope share | Slope mean |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| window/core/quiet | 0.000315 | — | 0.000315 | — | — | 0.222694 | 0.000000 | 8.000000 | 5992.000000 | — | — | — | — |
| window/core/noisy | 0.122613 | — | 0.122613 | — | — | 0.222694 | 0.000000 | 8.000000 | 5992.000000 | — | — | — | — |
| window/core/switch_quiet | 0.005418 | 0.064167 | 0.000309 | — | 8.000000 | 0.222694 | 0.000000 | 8.000000 | 5992.000000 | — | — | — | — |
| window/core/switch_noisy | 0.130225 | 0.192459 | 0.124813 | — | 190.328125 | 0.222694 | 0.000000 | 8.000000 | 5992.000000 | — | — | — | — |
| window/mixed/increase_first | 0.054620 | 0.122079 | 0.048754 | — | 83.281250 | 0.143030 | 0.000000 | 8.000000 | 5992.000000 | — | — | — | — |
| window/mixed/decrease_first | 0.079982 | 0.121613 | 0.076362 | — | 113.359375 | 0.143030 | 0.000000 | 8.000000 | 5992.000000 | — | — | — | — |
| window/steep/steep | 0.000344 | — | 0.000344 | 0.000615 | — | 0.007287 | 0.000000 | 8.000000 | 5992.000000 | — | — | — | — |
| window/shallow/shallow | 0.000479 | — | 0.000479 | 0.000522 | — | 0.007298 | 0.000000 | 8.000000 | 5992.000000 | — | — | — | — |
| window/noisy/noisy | 0.031000 | — | 0.031000 | 0.030147 | — | 0.070695 | 0.000000 | 8.000000 | 5992.000000 | — | — | — | — |
| sgd/core/quiet | 0.000173 | — | 0.000173 | — | — | 0.166562 | 0.000000 | — | — | — | — | — | — |
| sgd/core/noisy | 0.066889 | — | 0.066889 | — | — | 0.166562 | 0.000000 | — | — | — | — | — | — |
| sgd/core/switch_quiet | 0.006856 | 0.083761 | 0.000168 | — | 17.312500 | 0.166562 | 0.000000 | — | — | — | — | — | — |
| sgd/core/switch_noisy | 0.075314 | 0.151496 | 0.068689 | — | 72.843750 | 0.166562 | 0.000000 | — | — | — | — | — | — |
| sgd/mixed/increase_first | 0.033635 | 0.114527 | 0.026601 | — | 32.875000 | 0.106884 | 0.000000 | — | — | — | — | — | — |
| sgd/mixed/decrease_first | 0.047280 | 0.113862 | 0.041491 | — | 41.796875 | 0.106884 | 0.000000 | — | — | — | — | — | — |
| sgd/steep/steep | 0.000266 | — | 0.000266 | 0.001110 | — | 0.005500 | 0.000000 | — | — | — | — | — | — |
| sgd/shallow/shallow | 0.000386 | — | 0.000386 | 0.000443 | — | 0.005487 | 0.000000 | — | — | — | — | — | — |
| sgd/noisy/noisy | 0.016952 | — | 0.016952 | 0.016481 | — | 0.052859 | 0.000000 | — | — | — | — | — | — |
| adwin/core/quiet | 0.000001 | — | 0.000001 | — | — | 0.004516 | 0.000000 | 3500.500000 | 0.000000 | — | — | — | — |
| adwin/core/noisy | 0.001063 | — | 0.001063 | — | — | 0.004516 | 67.000000 | 2732.541900 | 1779.250000 | — | — | — | — |
| adwin/core/switch_quiet | 0.012155 | 0.151650 | 0.000025 | — | 29.531250 | 0.004516 | 453.000000 | 1105.538050 | 4027.125000 | — | — | — | — |
| adwin/core/switch_noisy | 0.019770 | 0.229889 | 0.001499 | — | 47.906250 | 0.004516 | 438.000000 | 1048.147725 | 4198.625000 | — | — | — | — |
| adwin/mixed/increase_first | 0.016235 | 0.193946 | 0.000781 | — | 44.796875 | 0.003665 | 440.000000 | 1068.425150 | 4025.750000 | — | — | — | — |
| adwin/mixed/decrease_first | 0.016436 | 0.193551 | 0.001035 | — | 40.968750 | 0.003665 | 471.000000 | 1036.328975 | 4284.125000 | — | — | — | — |
| adwin/steep/steep | 0.003329 | — | 0.003329 | 0.031445 | — | 0.000569 | 1334.000000 | 1571.837000 | 2491.500000 | — | — | — | — |
| adwin/shallow/shallow | 0.002503 | — | 0.002503 | 0.003166 | — | 0.000483 | 2125.000000 | 584.710750 | 5635.000000 | — | — | — | — |
| adwin/noisy/noisy | 0.009758 | — | 0.009758 | 0.022834 | — | 0.001435 | 1322.000000 | 940.279200 | 3995.500000 | — | — | — | — |
| slope/core/quiet | 0.000001 | — | 0.000001 | — | — | 0.004402 | 0.000000 | 32.000000 | 5968.000000 | 3500.500000 | 0.000000 | 0.000000 | 0.000000 |
| slope/core/noisy | 0.001063 | — | 0.001063 | — | — | 0.004402 | 0.000000 | 32.000000 | 5968.000000 | 2732.541900 | 0.000000 | 0.000000 | 0.000000 |
| slope/core/switch_quiet | 0.005473 | 0.068125 | 0.000025 | — | 30.593750 | 0.004402 | 64.000000 | 31.837600 | 5968.000000 | 1105.538050 | 0.012800 | 0.000000 | 0.000000 |
| slope/core/switch_noisy | 0.008726 | 0.091840 | 0.001499 | — | 38.750000 | 0.004402 | 64.000000 | 31.837600 | 5968.000000 | 1048.147725 | 0.012800 | 0.000000 | 0.000000 |
| slope/mixed/increase_first | 0.007330 | 0.082644 | 0.000781 | — | 42.156250 | 0.003526 | 64.000000 | 31.837600 | 5968.000000 | 1068.425150 | 0.012800 | 0.000000 | 0.000000 |
| slope/mixed/decrease_first | 0.007141 | 0.077368 | 0.001035 | — | 37.578125 | 0.003526 | 64.000000 | 31.837600 | 5968.000000 | 1036.328975 | 0.012800 | 0.000000 | 0.000000 |
| slope/steep/steep | 0.000143 | — | 0.000143 | 0.000733 | — | 0.000602 | 64.000000 | 31.837600 | 5968.000000 | 1571.837000 | 0.006400 | 0.100000 | -0.003491 |
| slope/shallow/shallow | 0.000960 | — | 0.000960 | 0.001212 | — | 0.001269 | 64.000000 | 31.879438 | 5984.062500 | 584.710750 | 0.002687 | 0.787894 | -0.000377 |
| slope/noisy/noisy | 0.003648 | — | 0.003648 | 0.007475 | — | 0.005701 | 64.000000 | 31.837600 | 5968.000000 | 940.279200 | 0.006400 | 0.400956 | -0.000971 |
| oracle_nofallback/core/quiet | 0.000080 | — | 0.000080 | — | — | 0.057057 | 0.000000 | 32.000000 | 5968.000000 | — | — | — | — |
| oracle_nofallback/core/noisy | 0.030370 | — | 0.030370 | — | — | 0.057057 | 0.000000 | 32.000000 | 5968.000000 | — | — | — | — |
| oracle_nofallback/core/switch_quiet | 0.005333 | 0.065803 | 0.000075 | — | 27.500000 | 0.057057 | 64.000000 | 31.837600 | 5968.000000 | — | — | — | — |
| oracle_nofallback/core/switch_noisy | 0.037512 | 0.104153 | 0.031717 | — | 27.281250 | 0.057057 | 64.000000 | 31.837600 | 5968.000000 | — | — | — | — |
| oracle_nofallback/mixed/increase_first | 0.017816 | 0.084302 | 0.012034 | — | 30.750000 | 0.036898 | 64.000000 | 31.837600 | 5968.000000 | — | — | — | — |
| oracle_nofallback/mixed/decrease_first | 0.023499 | 0.079573 | 0.018623 | — | 28.703125 | 0.036898 | 64.000000 | 31.837600 | 5968.000000 | — | — | — | — |
| oracle_nofallback/steep/steep | 0.000498 | — | 0.000498 | 0.004253 | — | 0.002150 | 64.000000 | 31.837600 | 5968.000000 | — | — | — | — |
| oracle_nofallback/shallow/shallow | 0.000259 | — | 0.000259 | 0.000306 | — | 0.002032 | 64.000000 | 31.879438 | 5984.062500 | — | — | — | — |
| oracle_nofallback/noisy/noisy | 0.007939 | — | 0.007939 | 0.007773 | — | 0.018098 | 64.000000 | 31.837600 | 5968.000000 | — | — | — | — |
| random_slope/core/quiet | 0.000003 | — | 0.000003 | — | — | 0.005311 | 50.000000 | 31.896188 | 5968.000000 | 3500.500000 | 0.008125 | 0.000000 | 0.000000 |
| random_slope/core/noisy | 0.001434 | — | 0.001434 | — | — | 0.005311 | 47.000000 | 31.906112 | 5968.000000 | 2732.541900 | 0.007400 | 0.000000 | 0.000000 |
| random_slope/core/switch_quiet | 0.012117 | 0.151167 | 0.000026 | — | 29.531250 | 0.005311 | 56.000000 | 31.875888 | 5968.187500 | 1105.538050 | 0.009675 | 0.000000 | 0.000000 |
| random_slope/core/switch_noisy | 0.020115 | 0.228559 | 0.001989 | — | 48.234375 | 0.005311 | 40.000000 | 31.903575 | 5968.000000 | 1048.147725 | 0.007600 | 0.000000 | 0.000000 |
| random_slope/mixed/increase_first | 0.016323 | 0.193676 | 0.000901 | — | 44.156250 | 0.003985 | 47.000000 | 31.903575 | 5968.000000 | 1068.425150 | 0.007600 | 0.000000 | 0.000000 |
| random_slope/mixed/decrease_first | 0.016838 | 0.193549 | 0.001472 | — | 41.093750 | 0.003985 | 39.000000 | 31.908650 | 5968.000000 | 1036.328975 | 0.007200 | 0.000000 | 0.000000 |
| random_slope/steep/steep | 0.003324 | — | 0.003324 | 0.031385 | — | 0.000590 | 47.000000 | 31.906863 | 5968.500000 | 1571.837000 | 0.007275 | 0.000000 | 0.000000 |
| random_slope/shallow/shallow | 0.002492 | — | 0.002492 | 0.003151 | — | 0.000504 | 50.000000 | 31.886044 | 5968.531250 | 584.710750 | 0.008944 | 0.000000 | 0.000000 |
| random_slope/noisy/noisy | 0.009814 | — | 0.009814 | 0.022765 | — | 0.001653 | 48.000000 | 31.900875 | 5969.156250 | 940.279200 | 0.007719 | 0.000000 | 0.000000 |

Width counts retained observations, not physical storage. SGD uses exponential weights and has no literal window. Target, drift-boundary and random requests are distinguished by provenance in every record and never mix. Ramp MSE averages pre-update squared error over the ramp segment; it is None-free on ramp fixtures and absent elsewhere.


## Measured execution time

| Stage | Family | Seconds |
| --- | --- | ---: |
| tuning | window | 0.44 |
| tuning | sgd | 0.11 |
| tuning | adwin | 3.01 |
| confirmation | window | 0.73 |
| confirmation | sgd | 0.32 |
| confirmation | adwin | 1.58 |
| confirmation | slope | 2.30 |
| confirmation | oracle_nofallback | 0.12 |
| confirmation | random_slope | 2.49 |

Configuration budgets are equal, not CPU costs. Times exclude archive writes and share cached fixtures.

## Scope and reproduction

ADWIN2 is independently implemented from the paper: practical Eq.(3.1), five buckets per size, minimum subwindow5. Gaussian observations violate the bounded-input premise; no corresponding formal guarantee or library-release parity is claimed. All policies see unchanged raw observations.

Granted timing is privileged. No schedule outcome overrides candidate performance. Candidate success requires all75 comparisons. All outcomes close this registration.

Intervals resample whole seeds10000 times with seed155000. Finite menus and synthetic fixtures do not establish global optimizer superiority, population guarantees or general neural-memory utility. Every reached row and source is archived; prior studies remain intact.

`python check_v3_slopebench.py --evidence results/v3-slopebench --reproduce` regenerates every reached row and scientific manifest/summary at rtol1e-11/atol1e-13. `python report_v3_slopebench.py --check` verifies both generated reports.
