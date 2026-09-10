# V3 adaptive-window slope

Disposition: **learning_negative**.

| Stage | Rows |
| --- | ---: |
| tuning | 384 |
| confirmation | 224 |

## Finite-menu tuning

Each searched family: 12 configurations ×8 seeds ×5 fixtures. Same objective: half primary post-switch MSE plus half mean of14 adapted retention metrics. Only the window schedule is searched; estimator and base are frozen.

| Family | Index | Configuration | Tuning objective | Menu endpoint fields |
| --- | ---: | --- | ---: | --- |
| win | 8 | `{"W_near": 8, "W_far": 128, "S": 16}` | 0.052962 | W_near, W_far, S |
| window | 3 | `{"window": 8}` | 0.093188 | window |
| sgd | 8 | `{"lr": 0.128}` | 0.082000 | none |
| adwin | 9 | `{"delta": 0.1, "clock": 1}` | 0.128934 | delta, clock |

Endpoint choices remain in the registered finite menu; no extension or global-optimum claim. Reference is the fixed-window slope policy. Random_win uses the selected window schedule.

Frozen random p=0.000260339185, from 112 enriched requests / 432000 tuning coordinate-updates, 16-update suppression, opportunities from t0. Expected pooled frequency is matched, not actual counts or memory age.


## Independent primary performance

| Policy | Finite seeds | Primary MSE | 95% interval |
| --- | ---: | ---: | --- |
| win | 32 | 0.084815 | [0.08068070657250025, 0.08901532360489743] |
| window | 32 | 0.127287 | [0.12391622513385496, 0.13070780708952792] |
| sgd | 32 | 0.119566 | [0.11652498911170625, 0.12270759886798949] |
| adwin | 32 | 0.197919 | [0.19267738312418023, 0.20329693581795635] |
| reference | 32 | 0.084815 | [0.08068070657250025, 0.08901532360489743] |
| random_win | 32 | 0.197774 | [0.19293981891645842, 0.2026191904073251] |
| oracle_nofallback | 32 | 0.088002 | [0.08447718042795105, 0.09160054709066226] |

## win: learning_negative

All75 comparisons are required: >=10% primary improvement over window/sgd/adwin/random_win, primary preservation against oracle_nofallback, every retention bound, and strict improvement on the7 adapted stable cells against oracle_nofallback (both-perfect cells pass as preservation).

| Contrast | Mode | Control | Policy | Delta | 95% interval | Pass |
| --- | --- | ---: | ---: | ---: | ---: | --- |
| window/primary | improve | 0.127287 | 0.084815 | -0.042472 | [-0.045255, -0.039787] | True |
| window/quiet | preserve | 0.000316 | 0.000001 | -0.000315 | [-0.000319, -0.000311] | True |
| window/noisy | preserve | 0.123775 | 0.001012 | -0.122763 | [-0.124377, -0.121126] | True |
| window/switch_quiet | preserve | 0.063919 | 0.067773 | 0.003854 | [0.003247, 0.004459] | True |
| window/switch_noisy | preserve | 0.199149 | 0.106097 | -0.093052 | [-0.102037, -0.083593] | True |
| window/mixed/increase_first/post_mse | preserve | 0.122814 | 0.080018 | -0.042796 | [-0.048928, -0.036555] | True |
| window/mixed/increase_first/stable_mse | preserve | 0.048760 | 0.000587 | -0.048173 | [-0.049915, -0.046487] | True |
| window/mixed/decrease_first/post_mse | preserve | 0.123266 | 0.085372 | -0.037894 | [-0.043818, -0.031764] | True |
| window/mixed/decrease_first/stable_mse | preserve | 0.076540 | 0.000861 | -0.075679 | [-0.077920, -0.073519] | True |
| window/ramp_steep | preserve | 0.000347 | 0.000148 | -0.000199 | [-0.000209, -0.000190] | True |
| window/ramp_shallow | preserve | 0.000474 | 0.000521 | 0.000047 | [0.000036, 0.000058] | True |
| window/ramp_noisy | preserve | 0.030902 | 0.004083 | -0.026820 | [-0.027320, -0.026338] | True |
| window/ramp_steep/ramp | preserve | 0.000650 | 0.000747 | 0.000098 | [0.000054, 0.000142] | True |
| window/ramp_shallow/ramp | preserve | 0.000517 | 0.000653 | 0.000136 | [0.000121, 0.000151] | True |
| window/ramp_noisy/ramp | preserve | 0.030620 | 0.008798 | -0.021822 | [-0.022602, -0.021001] | True |
| sgd/primary | improve | 0.119566 | 0.084815 | -0.034751 | [-0.037157, -0.032314] | True |
| sgd/quiet | preserve | 0.000173 | 0.000001 | -0.000172 | [-0.000175, -0.000170] | True |
| sgd/noisy | preserve | 0.068057 | 0.001012 | -0.067045 | [-0.068054, -0.065998] | True |
| sgd/switch_quiet | preserve | 0.083485 | 0.067773 | -0.015711 | [-0.016258, -0.015170] | True |
| sgd/switch_noisy | preserve | 0.161446 | 0.106097 | -0.055350 | [-0.062551, -0.047066] | True |
| sgd/mixed/increase_first/post_mse | preserve | 0.115131 | 0.080018 | -0.035113 | [-0.039645, -0.030433] | True |
| sgd/mixed/increase_first/stable_mse | preserve | 0.026677 | 0.000587 | -0.026090 | [-0.027069, -0.025127] | True |
| sgd/mixed/decrease_first/post_mse | preserve | 0.118202 | 0.085372 | -0.032831 | [-0.037696, -0.027843] | True |
| sgd/mixed/decrease_first/stable_mse | preserve | 0.042002 | 0.000861 | -0.041141 | [-0.042572, -0.039820] | True |
| sgd/ramp_steep | preserve | 0.000270 | 0.000148 | -0.000122 | [-0.000130, -0.000115] | True |
| sgd/ramp_shallow | preserve | 0.000383 | 0.000521 | 0.000138 | [0.000127, 0.000149] | True |
| sgd/ramp_noisy | preserve | 0.016886 | 0.004083 | -0.012803 | [-0.013126, -0.012477] | True |
| sgd/ramp_steep/ramp | preserve | 0.001158 | 0.000747 | -0.000410 | [-0.000457, -0.000363] | True |
| sgd/ramp_shallow/ramp | preserve | 0.000439 | 0.000653 | 0.000214 | [0.000198, 0.000229] | True |
| sgd/ramp_noisy/ramp | preserve | 0.016810 | 0.008798 | -0.008011 | [-0.008499, -0.007488] | True |
| adwin/primary | improve | 0.197919 | 0.084815 | -0.113104 | [-0.116495, -0.109518] | True |
| adwin/quiet | preserve | 0.000001 | 0.000001 | 0.000000 | [0.000000, 0.000000] | True |
| adwin/noisy | preserve | 0.001012 | 0.001012 | 0.000000 | [0.000000, 0.000000] | True |
| adwin/switch_quiet | preserve | 0.150094 | 0.067773 | -0.082320 | [-0.084886, -0.079820] | True |
| adwin/switch_noisy | preserve | 0.241790 | 0.106097 | -0.135694 | [-0.145584, -0.125878] | True |
| adwin/mixed/increase_first/post_mse | preserve | 0.200214 | 0.080018 | -0.120196 | [-0.126500, -0.114180] | True |
| adwin/mixed/increase_first/stable_mse | preserve | 0.000587 | 0.000587 | 0.000000 | [0.000000, 0.000000] | True |
| adwin/mixed/decrease_first/post_mse | preserve | 0.199577 | 0.085372 | -0.114205 | [-0.120666, -0.107704] | True |
| adwin/mixed/decrease_first/stable_mse | preserve | 0.000861 | 0.000861 | 0.000000 | [0.000000, 0.000000] | True |
| adwin/ramp_steep | preserve | 0.003359 | 0.000148 | -0.003211 | [-0.003235, -0.003188] | True |
| adwin/ramp_shallow | preserve | 0.002536 | 0.000521 | -0.002015 | [-0.002046, -0.001985] | True |
| adwin/ramp_noisy | preserve | 0.010300 | 0.004083 | -0.006217 | [-0.006818, -0.005591] | True |
| adwin/ramp_steep/ramp | preserve | 0.031662 | 0.000747 | -0.030914 | [-0.031135, -0.030701] | True |
| adwin/ramp_shallow/ramp | preserve | 0.003199 | 0.000653 | -0.002546 | [-0.002584, -0.002508] | True |
| adwin/ramp_noisy/ramp | preserve | 0.024499 | 0.008798 | -0.015700 | [-0.017253, -0.014164] | True |
| random_win/primary | improve | 0.197774 | 0.084815 | -0.112959 | [-0.116238, -0.109520] | True |
| random_win/quiet | preserve | 0.000002 | 0.000001 | -0.000001 | [-0.000002, -0.000001] | True |
| random_win/noisy | preserve | 0.001566 | 0.001012 | -0.000554 | [-0.000821, -0.000327] | True |
| random_win/switch_quiet | preserve | 0.150791 | 0.067773 | -0.083017 | [-0.085987, -0.080182] | True |
| random_win/switch_noisy | preserve | 0.240526 | 0.106097 | -0.134429 | [-0.143260, -0.125502] | True |
| random_win/mixed/increase_first/post_mse | preserve | 0.200326 | 0.080018 | -0.120308 | [-0.126599, -0.114318] | True |
| random_win/mixed/increase_first/stable_mse | preserve | 0.000866 | 0.000587 | -0.000279 | [-0.000413, -0.000156] | True |
| random_win/mixed/decrease_first/post_mse | preserve | 0.199453 | 0.085372 | -0.114082 | [-0.120751, -0.107387] | True |
| random_win/mixed/decrease_first/stable_mse | preserve | 0.001123 | 0.000861 | -0.000263 | [-0.000407, -0.000136] | True |
| random_win/ramp_steep | preserve | 0.003348 | 0.000148 | -0.003200 | [-0.003225, -0.003173] | True |
| random_win/ramp_shallow | preserve | 0.002527 | 0.000521 | -0.002006 | [-0.002038, -0.001975] | True |
| random_win/ramp_noisy | preserve | 0.010358 | 0.004083 | -0.006275 | [-0.006865, -0.005650] | True |
| random_win/ramp_steep/ramp | preserve | 0.031536 | 0.000747 | -0.030789 | [-0.031036, -0.030536] | True |
| random_win/ramp_shallow/ramp | preserve | 0.003186 | 0.000653 | -0.002533 | [-0.002573, -0.002494] | True |
| random_win/ramp_noisy/ramp | preserve | 0.024447 | 0.008798 | -0.015649 | [-0.017191, -0.014122] | True |
| oracle_nofallback/primary | preserve | 0.088002 | 0.084815 | -0.003187 | [-0.004856, -0.001434] | True |
| oracle_nofallback/quiet | strict | 0.000080 | 0.000001 | -0.000079 | [-0.000081, -0.000077] | True |
| oracle_nofallback/noisy | strict | 0.031364 | 0.001012 | -0.030353 | [-0.031103, -0.029567] | True |
| oracle_nofallback/switch_quiet | preserve | 0.065637 | 0.067773 | 0.002137 | [0.001737, 0.002525] | True |
| oracle_nofallback/switch_noisy | preserve | 0.115250 | 0.106097 | -0.009154 | [-0.014211, -0.002628] | True |
| oracle_nofallback/mixed/increase_first/post_mse | preserve | 0.085061 | 0.080018 | -0.005043 | [-0.008540, -0.001528] | True |
| oracle_nofallback/mixed/increase_first/stable_mse | strict | 0.012145 | 0.000587 | -0.011558 | [-0.012207, -0.010923] | True |
| oracle_nofallback/mixed/decrease_first/post_mse | preserve | 0.086059 | 0.085372 | -0.000687 | [-0.003191, 0.001930] | True |
| oracle_nofallback/mixed/decrease_first/stable_mse | strict | 0.019351 | 0.000861 | -0.018490 | [-0.019487, -0.017572] | True |
| oracle_nofallback/ramp_steep | strict | 0.000506 | 0.000148 | -0.000358 | [-0.000368, -0.000348] | True |
| oracle_nofallback/ramp_shallow | strict | 0.000256 | 0.000521 | 0.000264 | [0.000251, 0.000278] | False |
| oracle_nofallback/ramp_noisy | strict | 0.007925 | 0.004083 | -0.003843 | [-0.004114, -0.003570] | True |
| oracle_nofallback/ramp_steep/ramp | preserve | 0.004346 | 0.000747 | -0.003599 | [-0.003681, -0.003520] | True |
| oracle_nofallback/ramp_shallow/ramp | preserve | 0.000304 | 0.000653 | 0.000349 | [0.000331, 0.000368] | True |
| oracle_nofallback/ramp_noisy/ramp | preserve | 0.008166 | 0.008798 | 0.000632 | [0.000246, 0.001066] | True |

## Absolute errors and memory

| Policy/fixture/coordinate | Excess MSE | Post MSE | Stable MSE | Ramp MSE | Recovery latency | Mean vector update norm | Total requests | Fast mean width | Fast discarded | ADWIN mean width | Fast share | Slope share | Slope mean | Win mean |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| win/core/quiet | 0.000001 | — | 0.000001 | — | — | 0.004420 | 0.000000 | 32.000000 | 5968.000000 | 3500.500000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| win/core/noisy | 0.001012 | — | 0.001012 | — | — | 0.004420 | 0.000000 | 32.000000 | 5968.000000 | 2625.379250 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| win/core/switch_quiet | 0.005445 | 0.067773 | 0.000025 | — | 29.625000 | 0.004420 | 64.000000 | 31.837600 | 5968.000000 | 1107.101175 | 0.012800 | 0.000000 | 0.000000 | 0.000000 |
| win/core/switch_noisy | 0.009825 | 0.106097 | 0.001453 | — | 45.687500 | 0.004420 | 64.000000 | 31.837600 | 5968.000000 | 1027.643375 | 0.012800 | 0.000000 | 0.000000 | 0.000000 |
| win/mixed/increase_first | 0.006941 | 0.080018 | 0.000587 | — | 37.671875 | 0.003536 | 64.000000 | 31.837600 | 5968.000000 | 1083.232325 | 0.012800 | 0.000000 | 0.000000 | 0.000000 |
| win/mixed/decrease_first | 0.007621 | 0.085372 | 0.000861 | — | 36.531250 | 0.003536 | 64.000000 | 31.837600 | 5968.000000 | 1057.862900 | 0.012800 | 0.000000 | 0.000000 | 0.000000 |
| win/steep/steep | 0.000148 | — | 0.000148 | 0.000747 | — | 0.000670 | 64.000000 | 31.837600 | 5968.000000 | 1567.788700 | 0.006400 | 0.100000 | -0.003592 | 124.160000 |
| win/shallow/shallow | 0.000521 | — | 0.000521 | 0.000653 | — | 0.001370 | 64.000000 | 31.881594 | 5984.750000 | 582.520900 | 0.002525 | 0.789881 | -0.000497 | 127.513716 |
| win/noisy/noisy | 0.004083 | — | 0.004083 | 0.008798 | — | 0.006271 | 64.000000 | 31.837600 | 5968.000000 | 972.260300 | 0.006400 | 0.395525 | -0.000974 | 127.021944 |
| window/core/quiet | 0.000316 | — | 0.000316 | — | — | 0.222521 | 0.000000 | 8.000000 | 5992.000000 | — | — | — | — | — |
| window/core/noisy | 0.123775 | — | 0.123775 | — | — | 0.222521 | 0.000000 | 8.000000 | 5992.000000 | — | — | — | — | — |
| window/core/switch_quiet | 0.005401 | 0.063919 | 0.000312 | — | 7.984375 | 0.222521 | 0.000000 | 8.000000 | 5992.000000 | — | — | — | — | — |
| window/core/switch_noisy | 0.131721 | 0.199149 | 0.125858 | — | 235.203125 | 0.222521 | 0.000000 | 8.000000 | 5992.000000 | — | — | — | — | — |
| window/mixed/increase_first | 0.054684 | 0.122814 | 0.048760 | — | 136.312500 | 0.142687 | 0.000000 | 8.000000 | 5992.000000 | — | — | — | — | — |
| window/mixed/decrease_first | 0.080278 | 0.123266 | 0.076540 | — | 105.812500 | 0.142687 | 0.000000 | 8.000000 | 5992.000000 | — | — | — | — | — |
| window/steep/steep | 0.000347 | — | 0.000347 | 0.000650 | — | 0.007286 | 0.000000 | 8.000000 | 5992.000000 | — | — | — | — | — |
| window/shallow/shallow | 0.000474 | — | 0.000474 | 0.000517 | — | 0.007283 | 0.000000 | 8.000000 | 5992.000000 | — | — | — | — | — |
| window/noisy/noisy | 0.030902 | — | 0.030902 | 0.030620 | — | 0.070438 | 0.000000 | 8.000000 | 5992.000000 | — | — | — | — | — |
| sgd/core/quiet | 0.000173 | — | 0.000173 | — | — | 0.166615 | 0.000000 | — | — | — | — | — | — | — |
| sgd/core/noisy | 0.068057 | — | 0.068057 | — | — | 0.166615 | 0.000000 | — | — | — | — | — | — | — |
| sgd/core/switch_quiet | 0.006836 | 0.083485 | 0.000171 | — | 17.250000 | 0.166615 | 0.000000 | — | — | — | — | — | — | — |
| sgd/core/switch_noisy | 0.076646 | 0.161446 | 0.069273 | — | 73.921875 | 0.166615 | 0.000000 | — | — | — | — | — | — | — |
| sgd/mixed/increase_first | 0.033753 | 0.115131 | 0.026677 | — | 36.843750 | 0.106695 | 0.000000 | — | — | — | — | — | — | — |
| sgd/mixed/decrease_first | 0.048098 | 0.118202 | 0.042002 | — | 41.437500 | 0.106695 | 0.000000 | — | — | — | — | — | — | — |
| sgd/steep/steep | 0.000270 | — | 0.000270 | 0.001158 | — | 0.005490 | 0.000000 | — | — | — | — | — | — | — |
| sgd/shallow/shallow | 0.000383 | — | 0.000383 | 0.000439 | — | 0.005473 | 0.000000 | — | — | — | — | — | — | — |
| sgd/noisy/noisy | 0.016886 | — | 0.016886 | 0.016810 | — | 0.052715 | 0.000000 | — | — | — | — | — | — | — |
| adwin/core/quiet | 0.000001 | — | 0.000001 | — | — | 0.004519 | 0.000000 | 3500.500000 | 0.000000 | — | — | — | — | — |
| adwin/core/noisy | 0.001012 | — | 0.001012 | — | — | 0.004519 | 75.000000 | 2625.379250 | 2076.500000 | — | — | — | — | — |
| adwin/core/switch_quiet | 0.012031 | 0.150094 | 0.000025 | — | 27.921875 | 0.004519 | 453.000000 | 1107.101175 | 3992.500000 | — | — | — | — | — |
| adwin/core/switch_noisy | 0.020680 | 0.241790 | 0.001453 | — | 53.750000 | 0.004519 | 433.000000 | 1027.643375 | 4264.500000 | — | — | — | — | — |
| adwin/mixed/increase_first | 0.016557 | 0.200214 | 0.000587 | — | 41.203125 | 0.003649 | 462.000000 | 1083.232325 | 3992.500000 | — | — | — | — | — |
| adwin/mixed/decrease_first | 0.016758 | 0.199577 | 0.000861 | — | 42.109375 | 0.003649 | 459.000000 | 1057.862900 | 4276.875000 | — | — | — | — | — |
| adwin/steep/steep | 0.003359 | — | 0.003359 | 0.031662 | — | 0.000570 | 1344.000000 | 1567.788700 | 2495.000000 | — | — | — | — | — |
| adwin/shallow/shallow | 0.002536 | — | 0.002536 | 0.003199 | — | 0.000480 | 2133.000000 | 582.520900 | 5630.250000 | — | — | — | — | — |
| adwin/noisy/noisy | 0.010300 | — | 0.010300 | 0.024499 | — | 0.001431 | 1288.000000 | 972.260300 | 3873.500000 | — | — | — | — | — |
| reference/core/quiet | 0.000001 | — | 0.000001 | — | — | 0.004420 | 0.000000 | 32.000000 | 5968.000000 | — | — | — | — | — |
| reference/core/noisy | 0.001012 | — | 0.001012 | — | — | 0.004420 | 0.000000 | 32.000000 | 5968.000000 | — | — | — | — | — |
| reference/core/switch_quiet | 0.005445 | 0.067773 | 0.000025 | — | 29.625000 | 0.004420 | 64.000000 | 31.837600 | 5968.000000 | — | — | — | — | — |
| reference/core/switch_noisy | 0.009825 | 0.106097 | 0.001453 | — | 45.687500 | 0.004420 | 64.000000 | 31.837600 | 5968.000000 | — | — | — | — | — |
| reference/mixed/increase_first | 0.006941 | 0.080018 | 0.000587 | — | 37.671875 | 0.003536 | 64.000000 | 31.837600 | 5968.000000 | — | — | — | — | — |
| reference/mixed/decrease_first | 0.007621 | 0.085372 | 0.000861 | — | 36.531250 | 0.003536 | 64.000000 | 31.837600 | 5968.000000 | — | — | — | — | — |
| reference/steep/steep | 0.000146 | — | 0.000146 | 0.000728 | — | 0.000604 | 64.000000 | 31.837600 | 5968.000000 | — | — | — | — | — |
| reference/shallow/shallow | 0.000945 | — | 0.000945 | 0.001190 | — | 0.001262 | 64.000000 | 31.881594 | 5984.750000 | — | — | — | — | — |
| reference/noisy/noisy | 0.003646 | — | 0.003646 | 0.007692 | — | 0.005615 | 64.000000 | 31.837600 | 5968.000000 | — | — | — | — | — |
| random_win/core/quiet | 0.000002 | — | 0.000002 | — | — | 0.005361 | 44.000000 | 31.903575 | 5968.000000 | 3500.500000 | 0.007600 | 0.000000 | 0.000000 | 0.000000 |
| random_win/core/noisy | 0.001566 | — | 0.001566 | — | — | 0.005361 | 48.000000 | 31.898500 | 5968.000000 | 2625.379250 | 0.008006 | 0.000000 | 0.000000 | 0.000000 |
| random_win/core/switch_quiet | 0.012088 | 0.150791 | 0.000027 | — | 27.937500 | 0.005361 | 47.000000 | 31.908650 | 5968.000000 | 1107.101175 | 0.007175 | 0.000000 | 0.000000 | 0.000000 |
| random_win/core/switch_noisy | 0.020995 | 0.240526 | 0.001905 | — | 54.062500 | 0.005361 | 44.000000 | 31.898500 | 5968.000000 | 1027.643375 | 0.008000 | 0.000000 | 0.000000 | 0.000000 |
| random_win/mixed/increase_first | 0.016823 | 0.200326 | 0.000866 | — | 41.203125 | 0.004132 | 47.000000 | 31.905625 | 5968.000000 | 1083.232325 | 0.007506 | 0.000000 | 0.000000 | 0.000000 |
| random_win/mixed/decrease_first | 0.016990 | 0.199453 | 0.001123 | — | 41.828125 | 0.004132 | 52.000000 | 31.889012 | 5968.000000 | 1057.862900 | 0.008781 | 0.000000 | 0.000000 | 0.000000 |
| random_win/steep/steep | 0.003348 | — | 0.003348 | 0.031536 | — | 0.000590 | 44.000000 | 31.906112 | 5968.000000 | 1567.788700 | 0.007400 | 0.000000 | 0.000000 | 0.000000 |
| random_win/shallow/shallow | 0.002527 | — | 0.002527 | 0.003186 | — | 0.000502 | 47.000000 | 31.901037 | 5968.000000 | 582.520900 | 0.007800 | 0.000000 | 0.000000 | 0.000000 |
| random_win/noisy/noisy | 0.010358 | — | 0.010358 | 0.024447 | — | 0.001619 | 44.000000 | 31.911188 | 5968.000000 | 972.260300 | 0.007000 | 0.000000 | 0.000000 | 0.000000 |
| oracle_nofallback/core/quiet | 0.000080 | — | 0.000080 | — | — | 0.057075 | 0.000000 | 32.000000 | 5968.000000 | — | — | — | — | — |
| oracle_nofallback/core/noisy | 0.031364 | — | 0.031364 | — | — | 0.057075 | 0.000000 | 32.000000 | 5968.000000 | — | — | — | — | — |
| oracle_nofallback/core/switch_quiet | 0.005322 | 0.065637 | 0.000078 | — | 27.218750 | 0.057075 | 64.000000 | 31.837600 | 5968.000000 | — | — | — | — | — |
| oracle_nofallback/core/switch_noisy | 0.038694 | 0.115250 | 0.032037 | — | 32.078125 | 0.057075 | 64.000000 | 31.837600 | 5968.000000 | — | — | — | — | — |
| oracle_nofallback/mixed/increase_first | 0.017978 | 0.085061 | 0.012145 | — | 27.328125 | 0.036932 | 64.000000 | 31.837600 | 5968.000000 | — | — | — | — | — |
| oracle_nofallback/mixed/decrease_first | 0.024687 | 0.086059 | 0.019351 | — | 27.906250 | 0.036932 | 64.000000 | 31.837600 | 5968.000000 | — | — | — | — | — |
| oracle_nofallback/steep/steep | 0.000506 | — | 0.000506 | 0.004346 | — | 0.002154 | 64.000000 | 31.837600 | 5968.000000 | — | — | — | — | — |
| oracle_nofallback/shallow/shallow | 0.000256 | — | 0.000256 | 0.000304 | — | 0.002022 | 64.000000 | 31.881594 | 5984.750000 | — | — | — | — | — |
| oracle_nofallback/noisy/noisy | 0.007925 | — | 0.007925 | 0.008166 | — | 0.018061 | 64.000000 | 31.837600 | 5968.000000 | — | — | — | — | — |

Width counts retained observations, not physical storage. SGD uses exponential weights and has no literal window. Win mean averages the estimator window over in-regime post-burn steps. Target, drift-boundary and random requests are distinguished by provenance in every record and never mix.


## Measured execution time

| Stage | Family | Seconds |
| --- | --- | ---: |
| tuning | win | 14.70 |
| tuning | window | 0.51 |
| tuning | sgd | 0.01 |
| tuning | adwin | 3.43 |
| confirmation | win | 5.82 |
| confirmation | window | 0.32 |
| confirmation | sgd | 0.05 |
| confirmation | adwin | 1.39 |
| confirmation | reference | 4.83 |
| confirmation | random_win | 4.61 |
| confirmation | oracle_nofallback | 0.18 |

Configuration budgets are equal, not CPU costs. Times exclude archive writes and share cached fixtures.

## Scope and reproduction

ADWIN2 is independently implemented from the paper: practical Eq.(3.1), five buckets per size, minimum subwindow5. Gaussian observations violate the bounded-input premise; no corresponding formal guarantee or library-release parity is claimed. All policies see unchanged raw observations.

Granted timing is privileged. No schedule outcome overrides candidate performance. Candidate success requires all75 comparisons. All outcomes close this registration.

Intervals resample whole seeds10000 times with seed195000. Finite menus and synthetic fixtures do not establish global optimizer superiority, population guarantees or general neural-memory utility. Every reached row and source is archived; prior studies remain intact.

`python check_v3_slopewin.py --evidence results/v3-slopewin --reproduce` regenerates every reached row and scientific manifest/summary at rtol1e-11/atol1e-13. `python report_v3_slopewin.py --check` verifies both generated reports.
