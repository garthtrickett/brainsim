# V3 change-triggered forgetting

Disposition: **learning_negative**.

| Stage | Rows |
| --- | ---: |
| tuning | 480 |
| confirmation | 256 |

Frozen strict detector threshold: 0.4690234346011377.

## Finite-menu tuning

Each searched family: 12 configurations ×8 seeds ×5 fixtures. Same objective: half primary post-switch MSE plus half mean of14 retention metrics.

| Family | Index | Configuration | Tuning objective | Menu endpoint fields |
| --- | ---: | --- | ---: | --- |
| forget | 4 | `{"keep": 4, "window": 32}` | 0.127751 | window |
| oracle | 1 | `{"keep": 1, "window": 128}` | 0.024315 | keep |
| window | 3 | `{"window": 8}` | 0.096777 | none |
| sgd | 8 | `{"lr": 0.128}` | 0.085129 | none |
| adwin | 9 | `{"delta": 0.1, "clock": 1}` | 0.127719 | delta, clock |

Endpoint choices remain in the registered finite menu; no extension or global-optimum claim. Matched oracle/random use candidate K/W. Noreset_matched uses its exact W without resets.

Frozen random p=0.000480548543, from 201 requests / 421488 tuning coordinate-updates, corrected for16-update cooldown. Expected pooled frequency is matched, not actual counts or memory age.


## Independent primary performance

| Policy | Finite seeds | Primary MSE | 95% interval |
| --- | ---: | ---: | --- |
| forget | 32 | 0.191012 | [0.18739108067596535, 0.1946574008669737] |
| oracle | 32 | 0.034957 | [0.03319446951704507, 0.03684757936645999] |
| window | 32 | 0.124435 | [0.12141366248538463, 0.12754519964088315] |
| sgd | 32 | 0.116201 | [0.11374932126737777, 0.11851363471954975] |
| adwin | 32 | 0.195223 | [0.19048878016685564, 0.20007081911026323] |
| oracle_matched | 32 | 0.083220 | [0.08055876594437679, 0.08569853817514257] |
| random | 32 | 0.236991 | [0.2333134250550971, 0.24042160592339276] |
| noreset_matched | 32 | 0.237095 | [0.23334828068237248, 0.24056885119347135] |

## forget: learning_negative

All75 candidate comparisons are required, including the matched no-reset control.

| Contrast | Control | Policy | Delta | 95% interval | Pass |
| --- | ---: | ---: | ---: | --- | --- |
| window/primary | 0.124435 | 0.191012 | 0.066577 | [0.063882, 0.069347] | False |
| window/quiet | 0.000311 | 0.000078 | -0.000233 | [-0.000237, -0.000229] | True |
| window/noisy | 0.122770 | 0.030309 | -0.092461 | [-0.093961, -0.091075] | True |
| window/switch_quiet | 0.064244 | 0.159639 | 0.095395 | [0.094924, 0.095906] | False |
| window/switch_noisy | 0.187394 | 0.228658 | 0.041264 | [0.032950, 0.049962] | False |
| window/noise_jump | 0.051482 | 0.012838 | -0.038644 | [-0.040344, -0.036980] | True |
| window/drift | 0.000321 | 0.000176 | -0.000146 | [-0.000153, -0.000138] | True |
| window/exactly_quiet | 0.000000 | 0.000000 | 0.000000 | [0.000000, 0.000000] | True |
| window/noise_jump/noise_increase | 0.120311 | 0.027212 | -0.093099 | [-0.102229, -0.084696] | True |
| window/noise_jump/noise_decrease | 0.003409 | 0.002117 | -0.001292 | [-0.002255, -0.000384] | True |
| window/drift/drift | 0.000336 | 0.000326 | -0.000010 | [-0.000032, 0.000013] | True |
| window/mixed/increase_first/post_mse | 0.122696 | 0.184919 | 0.062223 | [0.054966, 0.068927] | False |
| window/mixed/increase_first/stable_mse | 0.049071 | 0.011964 | -0.037107 | [-0.038749, -0.035475] | True |
| window/mixed/decrease_first/post_mse | 0.123405 | 0.190832 | 0.067428 | [0.061111, 0.073675] | False |
| window/mixed/decrease_first/stable_mse | 0.075287 | 0.018790 | -0.056496 | [-0.057950, -0.055033] | True |
| sgd/primary | 0.116201 | 0.191012 | 0.074811 | [0.072612, 0.077225] | False |
| sgd/quiet | 0.000170 | 0.000078 | -0.000092 | [-0.000094, -0.000091] | True |
| sgd/noisy | 0.066940 | 0.030309 | -0.036630 | [-0.037235, -0.036060] | True |
| sgd/switch_quiet | 0.083870 | 0.159639 | 0.075769 | [0.075290, 0.076286] | False |
| sgd/switch_noisy | 0.153912 | 0.228658 | 0.074746 | [0.068339, 0.081338] | False |
| sgd/noise_jump | 0.028146 | 0.012838 | -0.015308 | [-0.015982, -0.014651] | True |
| sgd/drift | 0.000194 | 0.000176 | -0.000019 | [-0.000024, -0.000013] | True |
| sgd/exactly_quiet | 0.000000 | 0.000000 | -0.000000 | [-0.000000, -0.000000] | True |
| sgd/noise_jump/noise_increase | 0.065560 | 0.027212 | -0.038347 | [-0.042001, -0.035043] | True |
| sgd/noise_jump/noise_decrease | 0.001678 | 0.002117 | 0.000439 | [0.000057, 0.000840] | True |
| sgd/drift/drift | 0.000232 | 0.000326 | 0.000094 | [0.000076, 0.000112] | True |
| sgd/mixed/increase_first/post_mse | 0.112549 | 0.184919 | 0.072370 | [0.067664, 0.076999] | False |
| sgd/mixed/increase_first/stable_mse | 0.026647 | 0.011964 | -0.014682 | [-0.015346, -0.014020] | True |
| sgd/mixed/decrease_first/post_mse | 0.114474 | 0.190832 | 0.076358 | [0.071771, 0.081050] | False |
| sgd/mixed/decrease_first/stable_mse | 0.041215 | 0.018790 | -0.022425 | [-0.023014, -0.021836] | True |
| adwin/primary | 0.195223 | 0.191012 | -0.004211 | [-0.010073, 0.001481] | False |
| adwin/quiet | 0.000001 | 0.000078 | 0.000077 | [0.000075, 0.000080] | True |
| adwin/noisy | 0.001224 | 0.030309 | 0.029085 | [0.028055, 0.030140] | False |
| adwin/switch_quiet | 0.152183 | 0.159639 | 0.007456 | [0.005476, 0.009402] | True |
| adwin/switch_noisy | 0.245127 | 0.228658 | -0.016469 | [-0.032231, -0.001883] | True |
| adwin/noise_jump | 0.000782 | 0.012838 | 0.012056 | [0.011349, 0.012777] | False |
| adwin/drift | 0.003150 | 0.000176 | -0.002975 | [-0.003004, -0.002947] | True |
| adwin/exactly_quiet | 0.000000 | 0.000000 | 0.000000 | [0.000000, 0.000000] | True |
| adwin/noise_jump/noise_increase | 0.003259 | 0.027212 | 0.023953 | [0.020729, 0.027600] | False |
| adwin/noise_jump/noise_decrease | 0.000798 | 0.002117 | 0.001319 | [0.000555, 0.002112] | False |
| adwin/drift/drift | 0.007628 | 0.000326 | -0.007302 | [-0.007535, -0.007080] | True |
| adwin/mixed/increase_first/post_mse | 0.190538 | 0.184919 | -0.005619 | [-0.014251, 0.002668] | True |
| adwin/mixed/increase_first/stable_mse | 0.000618 | 0.011964 | 0.011346 | [0.010722, 0.011962] | False |
| adwin/mixed/decrease_first/post_mse | 0.193044 | 0.190832 | -0.002212 | [-0.011601, 0.007491] | True |
| adwin/mixed/decrease_first/stable_mse | 0.000979 | 0.018790 | 0.017811 | [0.017035, 0.018564] | False |
| random/primary | 0.236991 | 0.191012 | -0.045978 | [-0.047700, -0.044194] | True |
| random/quiet | 0.000080 | 0.000078 | -0.000001 | [-0.000002, -0.000001] | True |
| random/noisy | 0.030818 | 0.030309 | -0.000509 | [-0.000737, -0.000280] | True |
| random/switch_quiet | 0.223882 | 0.159639 | -0.064242 | [-0.064730, -0.063721] | True |
| random/switch_noisy | 0.261902 | 0.228658 | -0.033244 | [-0.037129, -0.029555] | True |
| random/noise_jump | 0.013118 | 0.012838 | -0.000280 | [-0.000419, -0.000159] | True |
| random/drift | 0.000186 | 0.000176 | -0.000010 | [-0.000012, -0.000008] | True |
| random/exactly_quiet | 0.000000 | 0.000000 | 0.000000 | [0.000000, 0.000000] | True |
| random/noise_jump/noise_increase | 0.027238 | 0.027212 | -0.000026 | [-0.000066, 0.000000] | True |
| random/noise_jump/noise_decrease | 0.002069 | 0.002117 | 0.000048 | [-0.000001, 0.000147] | True |
| random/drift/drift | 0.000347 | 0.000326 | -0.000021 | [-0.000025, -0.000017] | True |
| random/mixed/increase_first/post_mse | 0.228813 | 0.184919 | -0.043894 | [-0.046975, -0.040754] | True |
| random/mixed/increase_first/stable_mse | 0.012137 | 0.011964 | -0.000173 | [-0.000341, -0.000032] | True |
| random/mixed/decrease_first/post_mse | 0.233366 | 0.190832 | -0.042533 | [-0.046679, -0.038096] | True |
| random/mixed/decrease_first/stable_mse | 0.019149 | 0.018790 | -0.000359 | [-0.000570, -0.000182] | True |
| noreset_matched/primary | 0.237095 | 0.191012 | -0.046083 | [-0.047887, -0.044239] | True |
| noreset_matched/quiet | 0.000078 | 0.000078 | -0.000000 | [-0.000000, 0.000000] | True |
| noreset_matched/noisy | 0.030225 | 0.030309 | 0.000084 | [-0.000027, 0.000214] | True |
| noreset_matched/switch_quiet | 0.223881 | 0.159639 | -0.064242 | [-0.064730, -0.063721] | True |
| noreset_matched/switch_noisy | 0.261818 | 0.228658 | -0.033160 | [-0.037143, -0.029397] | True |
| noreset_matched/noise_jump | 0.012856 | 0.012838 | -0.000018 | [-0.000076, 0.000042] | True |
| noreset_matched/drift | 0.000184 | 0.000176 | -0.000009 | [-0.000010, -0.000007] | True |
| noreset_matched/exactly_quiet | 0.000000 | 0.000000 | 0.000000 | [0.000000, 0.000000] | True |
| noreset_matched/noise_jump/noise_increase | 0.027212 | 0.027212 | 0.000000 | [0.000000, 0.000000] | True |
| noreset_matched/noise_jump/noise_decrease | 0.002117 | 0.002117 | 0.000000 | [-0.000000, 0.000000] | True |
| noreset_matched/drift/drift | 0.000347 | 0.000326 | -0.000022 | [-0.000025, -0.000018] | True |
| noreset_matched/mixed/increase_first/post_mse | 0.228836 | 0.184919 | -0.043917 | [-0.047012, -0.040766] | True |
| noreset_matched/mixed/increase_first/stable_mse | 0.011970 | 0.011964 | -0.000006 | [-0.000044, 0.000036] | True |
| noreset_matched/mixed/decrease_first/post_mse | 0.233845 | 0.190832 | -0.043012 | [-0.047268, -0.038497] | True |
| noreset_matched/mixed/decrease_first/stable_mse | 0.018870 | 0.018790 | -0.000080 | [-0.000147, -0.000026] | True |

## oracle: oracle_negative

Privileged diagnostic: cannot authorize candidate advancement.

| Contrast | Control | Policy | Delta | 95% interval | Pass |
| --- | ---: | ---: | ---: | --- | --- |
| window/primary | 0.124435 | 0.034957 | -0.089478 | [-0.093063, -0.086007] | True |
| window/quiet | 0.000311 | 0.000019 | -0.000292 | [-0.000296, -0.000288] | True |
| window/noisy | 0.122770 | 0.007796 | -0.114974 | [-0.116956, -0.113105] | True |
| window/switch_quiet | 0.064244 | 0.020076 | -0.044168 | [-0.044516, -0.043830] | True |
| window/switch_noisy | 0.187394 | 0.050455 | -0.136939 | [-0.147164, -0.126462] | True |
| window/noise_jump | 0.051482 | 0.003400 | -0.048083 | [-0.050260, -0.045981] | True |
| window/drift | 0.000321 | 0.001645 | 0.001324 | [0.001266, 0.001384] | True |
| window/exactly_quiet | 0.000000 | 0.000000 | 0.000000 | [0.000000, 0.000000] | True |
| window/noise_jump/noise_increase | 0.120311 | 0.005499 | -0.114812 | [-0.125064, -0.104983] | True |
| window/noise_jump/noise_decrease | 0.003409 | 0.001774 | -0.001635 | [-0.002930, -0.000449] | True |
| window/drift/drift | 0.000336 | 0.004052 | 0.003716 | [0.003450, 0.003995] | False |
| window/mixed/increase_first/post_mse | 0.122696 | 0.033809 | -0.088888 | [-0.095244, -0.082442] | True |
| window/mixed/increase_first/stable_mse | 0.049071 | 0.002988 | -0.046083 | [-0.048075, -0.044126] | True |
| window/mixed/decrease_first/post_mse | 0.123405 | 0.035488 | -0.087917 | [-0.095265, -0.080547] | True |
| window/mixed/decrease_first/stable_mse | 0.075287 | 0.004728 | -0.070559 | [-0.072460, -0.068619] | True |
| sgd/primary | 0.116201 | 0.034957 | -0.081244 | [-0.084023, -0.078391] | True |
| sgd/quiet | 0.000170 | 0.000019 | -0.000151 | [-0.000154, -0.000149] | True |
| sgd/noisy | 0.066940 | 0.007796 | -0.059144 | [-0.060358, -0.057958] | True |
| sgd/switch_quiet | 0.083870 | 0.020076 | -0.063794 | [-0.064161, -0.063423] | True |
| sgd/switch_noisy | 0.153912 | 0.050455 | -0.103457 | [-0.112399, -0.094264] | True |
| sgd/noise_jump | 0.028146 | 0.003400 | -0.024747 | [-0.025933, -0.023580] | True |
| sgd/drift | 0.000194 | 0.001645 | 0.001450 | [0.001394, 0.001509] | True |
| sgd/exactly_quiet | 0.000000 | 0.000000 | -0.000000 | [-0.000000, -0.000000] | True |
| sgd/noise_jump/noise_increase | 0.065560 | 0.005499 | -0.060060 | [-0.065608, -0.054761] | True |
| sgd/noise_jump/noise_decrease | 0.001678 | 0.001774 | 0.000096 | [-0.000644, 0.000860] | True |
| sgd/drift/drift | 0.000232 | 0.004052 | 0.003820 | [0.003556, 0.004097] | False |
| sgd/mixed/increase_first/post_mse | 0.112549 | 0.033809 | -0.078741 | [-0.083924, -0.073252] | True |
| sgd/mixed/increase_first/stable_mse | 0.026647 | 0.002988 | -0.023659 | [-0.024704, -0.022636] | True |
| sgd/mixed/decrease_first/post_mse | 0.114474 | 0.035488 | -0.078986 | [-0.084764, -0.073148] | True |
| sgd/mixed/decrease_first/stable_mse | 0.041215 | 0.004728 | -0.036487 | [-0.037584, -0.035330] | True |
| adwin/primary | 0.195223 | 0.034957 | -0.160266 | [-0.165142, -0.155358] | True |
| adwin/quiet | 0.000001 | 0.000019 | 0.000019 | [0.000017, 0.000020] | True |
| adwin/noisy | 0.001224 | 0.007796 | 0.006572 | [0.006153, 0.007024] | False |
| adwin/switch_quiet | 0.152183 | 0.020076 | -0.132107 | [-0.134090, -0.130220] | True |
| adwin/switch_noisy | 0.245127 | 0.050455 | -0.194672 | [-0.211686, -0.177779] | True |
| adwin/noise_jump | 0.000782 | 0.003400 | 0.002617 | [0.002337, 0.002913] | False |
| adwin/drift | 0.003150 | 0.001645 | -0.001506 | [-0.001563, -0.001447] | True |
| adwin/exactly_quiet | 0.000000 | 0.000000 | 0.000000 | [0.000000, 0.000000] | True |
| adwin/noise_jump/noise_increase | 0.003259 | 0.005499 | 0.002240 | [0.001096, 0.003438] | False |
| adwin/noise_jump/noise_decrease | 0.000798 | 0.001774 | 0.000976 | [0.000234, 0.001684] | True |
| adwin/drift/drift | 0.007628 | 0.004052 | -0.003576 | [-0.003621, -0.003530] | True |
| adwin/mixed/increase_first/post_mse | 0.190538 | 0.033809 | -0.156730 | [-0.163562, -0.150176] | True |
| adwin/mixed/increase_first/stable_mse | 0.000618 | 0.002988 | 0.002370 | [0.002100, 0.002648] | False |
| adwin/mixed/decrease_first/post_mse | 0.193044 | 0.035488 | -0.157556 | [-0.166340, -0.148960] | True |
| adwin/mixed/decrease_first/stable_mse | 0.000979 | 0.004728 | 0.003749 | [0.003415, 0.004081] | False |

## oracle_matched: oracle_negative

Privileged diagnostic: cannot authorize candidate advancement.

| Contrast | Control | Policy | Delta | 95% interval | Pass |
| --- | ---: | ---: | ---: | --- | --- |
| window/primary | 0.124435 | 0.083220 | -0.041214 | [-0.043947, -0.038463] | True |
| window/quiet | 0.000311 | 0.000078 | -0.000233 | [-0.000237, -0.000229] | True |
| window/noisy | 0.122770 | 0.030225 | -0.092545 | [-0.094020, -0.091201] | True |
| window/switch_quiet | 0.064244 | 0.065772 | 0.001528 | [0.001212, 0.001840] | True |
| window/switch_noisy | 0.187394 | 0.104963 | -0.082430 | [-0.090714, -0.073671] | True |
| window/noise_jump | 0.051482 | 0.012856 | -0.038626 | [-0.040345, -0.036968] | True |
| window/drift | 0.000321 | 0.000184 | -0.000137 | [-0.000143, -0.000130] | True |
| window/exactly_quiet | 0.000000 | 0.000000 | 0.000000 | [0.000000, 0.000000] | True |
| window/noise_jump/noise_increase | 0.120311 | 0.027212 | -0.093099 | [-0.102229, -0.084696] | True |
| window/noise_jump/noise_decrease | 0.003409 | 0.002117 | -0.001292 | [-0.002255, -0.000384] | True |
| window/drift/drift | 0.000336 | 0.000347 | 0.000012 | [-0.000009, 0.000033] | True |
| window/mixed/increase_first/post_mse | 0.122696 | 0.080321 | -0.042375 | [-0.047948, -0.037027] | True |
| window/mixed/increase_first/stable_mse | 0.049071 | 0.011970 | -0.037101 | [-0.038748, -0.035465] | True |
| window/mixed/decrease_first/post_mse | 0.123405 | 0.081825 | -0.041580 | [-0.046693, -0.036298] | True |
| window/mixed/decrease_first/stable_mse | 0.075287 | 0.018870 | -0.056417 | [-0.057891, -0.054938] | True |
| sgd/primary | 0.116201 | 0.083220 | -0.032981 | [-0.034924, -0.031029] | True |
| sgd/quiet | 0.000170 | 0.000078 | -0.000092 | [-0.000094, -0.000091] | True |
| sgd/noisy | 0.066940 | 0.030225 | -0.036714 | [-0.037280, -0.036195] | True |
| sgd/switch_quiet | 0.083870 | 0.065772 | -0.018098 | [-0.018329, -0.017864] | True |
| sgd/switch_noisy | 0.153912 | 0.104963 | -0.048948 | [-0.055594, -0.042033] | True |
| sgd/noise_jump | 0.028146 | 0.012856 | -0.015290 | [-0.015967, -0.014637] | True |
| sgd/drift | 0.000194 | 0.000184 | -0.000010 | [-0.000014, -0.000005] | True |
| sgd/exactly_quiet | 0.000000 | 0.000000 | -0.000000 | [-0.000000, -0.000000] | True |
| sgd/noise_jump/noise_increase | 0.065560 | 0.027212 | -0.038347 | [-0.042001, -0.035043] | True |
| sgd/noise_jump/noise_decrease | 0.001678 | 0.002117 | 0.000439 | [0.000057, 0.000840] | True |
| sgd/drift/drift | 0.000232 | 0.000347 | 0.000115 | [0.000099, 0.000133] | True |
| sgd/mixed/increase_first/post_mse | 0.112549 | 0.080321 | -0.032228 | [-0.035575, -0.028911] | True |
| sgd/mixed/increase_first/stable_mse | 0.026647 | 0.011970 | -0.014677 | [-0.015346, -0.014008] | True |
| sgd/mixed/decrease_first/post_mse | 0.114474 | 0.081825 | -0.032649 | [-0.036287, -0.028377] | True |
| sgd/mixed/decrease_first/stable_mse | 0.041215 | 0.018870 | -0.022345 | [-0.022946, -0.021748] | True |
| adwin/primary | 0.195223 | 0.083220 | -0.112003 | [-0.116395, -0.107803] | True |
| adwin/quiet | 0.000001 | 0.000078 | 0.000077 | [0.000075, 0.000080] | True |
| adwin/noisy | 0.001224 | 0.030225 | 0.029001 | [0.027982, 0.030051] | False |
| adwin/switch_quiet | 0.152183 | 0.065772 | -0.086411 | [-0.088381, -0.084537] | True |
| adwin/switch_noisy | 0.245127 | 0.104963 | -0.140164 | [-0.154528, -0.127185] | True |
| adwin/noise_jump | 0.000782 | 0.012856 | 0.012074 | [0.011374, 0.012779] | False |
| adwin/drift | 0.003150 | 0.000184 | -0.002966 | [-0.002995, -0.002939] | True |
| adwin/exactly_quiet | 0.000000 | 0.000000 | 0.000000 | [0.000000, 0.000000] | True |
| adwin/noise_jump/noise_increase | 0.003259 | 0.027212 | 0.023953 | [0.020729, 0.027600] | False |
| adwin/noise_jump/noise_decrease | 0.000798 | 0.002117 | 0.001319 | [0.000555, 0.002112] | False |
| adwin/drift/drift | 0.007628 | 0.000347 | -0.007281 | [-0.007515, -0.007056] | True |
| adwin/mixed/increase_first/post_mse | 0.190538 | 0.080321 | -0.110217 | [-0.116087, -0.104593] | True |
| adwin/mixed/increase_first/stable_mse | 0.000618 | 0.011970 | 0.011352 | [0.010734, 0.011969] | False |
| adwin/mixed/decrease_first/post_mse | 0.193044 | 0.081825 | -0.111220 | [-0.118976, -0.103003] | True |
| adwin/mixed/decrease_first/stable_mse | 0.000979 | 0.018870 | 0.017891 | [0.017112, 0.018654] | False |

## Raw detector diagnostic: detector_pass

One fixed signal; diagnostic only.

| Cell | Count/total | Rate | Latency | Pass |
| --- | --- | ---: | ---: | --- |
| core/quiet/blocks | 9/1600 | 0.005625 | — | True |
| core/noisy/blocks | 11/1600 | 0.006875 | — | True |
| core/switch_quiet/target_down | 32/32 | 1.000000 | 10.031250 | True |
| core/switch_quiet/target_up | 32/32 | 1.000000 | 10.125000 | True |
| core/switch_noisy/target_down | 32/32 | 1.000000 | 13.593750 | True |
| core/switch_noisy/target_up | 32/32 | 1.000000 | 13.281250 | True |
| mixed/increase_first/target_down | 32/32 | 1.000000 | 12.125000 | True |
| mixed/increase_first/target_up | 32/32 | 1.000000 | 10.937500 | True |
| mixed/decrease_first/target_down | 32/32 | 1.000000 | 11.312500 | True |
| mixed/decrease_first/target_up | 32/32 | 1.000000 | 12.281250 | True |
| noise_jump/noise_jump/noise_increase | 0/32 | 0.000000 | 100.000000 | True |
| noise_jump/noise_jump/noise_decrease | 0/32 | 0.000000 | 100.000000 | True |

## Absolute errors and memory

| Policy/fixture/coordinate | Excess MSE | Post MSE | Stable MSE | Recovery latency | Mean vector update norm | Total resets/shrinks | Mean width | Final width mean | Discarded mean |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| forget/core/quiet | 0.000078 | — | 0.000078 | — | 0.057740 | 11.000000 | 31.977162 | 32.000000 | 5968.000000 |
| forget/core/noisy | 0.030309 | — | 0.030309 | — | 0.057740 | 12.000000 | 31.972088 | 32.000000 | 5968.000000 |
| forget/core/switch_quiet | 0.012844 | 0.159639 | 0.000079 | 11.078125 | 0.057740 | 79.000000 | 31.809781 | 31.812500 | 5968.187500 |
| forget/core/switch_noisy | 0.046674 | 0.228658 | 0.030849 | 33.484375 | 0.057740 | 105.000000 | 31.745594 | 32.000000 | 5968.000000 |
| forget/noise_jump/noise_jump | 0.012838 | — | 0.012838 | — | 0.013320 | 12.000000 | 31.969550 | 32.000000 | 5968.000000 |
| forget/drift/drift | 0.000176 | — | 0.000176 | — | 0.002096 | 327.000000 | 31.178906 | 32.000000 | 5968.000000 |
| forget/exactly_quiet/exactly_quiet | 0.000000 | — | 0.000000 | — | 0.000167 | 0.000000 | 32.000000 | 32.000000 | 5968.000000 |
| forget/mixed/increase_first | 0.025801 | 0.184919 | 0.011964 | 23.265625 | 0.037448 | 92.000000 | 31.776700 | 32.000000 | 5968.000000 |
| forget/mixed/decrease_first | 0.032554 | 0.190832 | 0.018790 | 22.187500 | 0.037448 | 90.000000 | 31.781775 | 32.000000 | 5968.000000 |
| oracle/core/quiet | 0.000019 | — | 0.000019 | — | 0.016777 | 0.000000 | 128.000000 | 128.000000 | 5872.000000 |
| oracle/core/noisy | 0.007796 | — | 0.007796 | — | 0.016777 | 0.000000 | 128.000000 | 128.000000 | 5872.000000 |
| oracle/core/switch_quiet | 0.001625 | 0.020076 | 0.000021 | 1.000000 | 0.016777 | 64.000000 | 124.748800 | 128.000000 | 5872.000000 |
| oracle/core/switch_noisy | 0.011170 | 0.050455 | 0.007754 | 25.234375 | 0.016777 | 64.000000 | 124.748800 | 128.000000 | 5872.000000 |
| oracle/noise_jump/noise_jump | 0.003400 | — | 0.003400 | — | 0.003533 | 0.000000 | 128.000000 | 128.000000 | 5872.000000 |
| oracle/drift/drift | 0.001645 | — | 0.001645 | — | 0.000818 | 0.000000 | 128.000000 | 128.000000 | 5872.000000 |
| oracle/exactly_quiet/exactly_quiet | 0.000000 | — | 0.000000 | — | 0.000167 | 0.000000 | 128.000000 | 128.000000 | 5872.000000 |
| oracle/mixed/increase_first | 0.005454 | 0.033809 | 0.002988 | 10.250000 | 0.011576 | 64.000000 | 124.748800 | 128.000000 | 5872.000000 |
| oracle/mixed/decrease_first | 0.007189 | 0.035488 | 0.004728 | 14.593750 | 0.011576 | 64.000000 | 124.748800 | 128.000000 | 5872.000000 |
| window/core/quiet | 0.000311 | — | 0.000311 | — | 0.222931 | 0.000000 | 8.000000 | 8.000000 | 5992.000000 |
| window/core/noisy | 0.122770 | — | 0.122770 | — | 0.222931 | 0.000000 | 8.000000 | 8.000000 | 5992.000000 |
| window/core/switch_quiet | 0.005430 | 0.064244 | 0.000315 | 8.000000 | 0.222931 | 0.000000 | 8.000000 | 8.000000 | 5992.000000 |
| window/core/switch_noisy | 0.129318 | 0.187394 | 0.124268 | 232.609375 | 0.222931 | 0.000000 | 8.000000 | 8.000000 | 5992.000000 |
| window/noise_jump/noise_jump | 0.051482 | — | 0.051482 | — | 0.052655 | 0.000000 | 8.000000 | 8.000000 | 5992.000000 |
| window/drift/drift | 0.000321 | — | 0.000321 | — | 0.007257 | 0.000000 | 8.000000 | 8.000000 | 5992.000000 |
| window/exactly_quiet/exactly_quiet | 0.000000 | — | 0.000000 | — | 0.000167 | 0.000000 | 8.000000 | 8.000000 | 5992.000000 |
| window/mixed/increase_first | 0.054961 | 0.122696 | 0.049071 | 109.687500 | 0.142674 | 0.000000 | 8.000000 | 8.000000 | 5992.000000 |
| window/mixed/decrease_first | 0.079136 | 0.123405 | 0.075287 | 153.953125 | 0.142674 | 0.000000 | 8.000000 | 8.000000 | 5992.000000 |
| sgd/core/quiet | 0.000170 | — | 0.000170 | — | 0.166555 | 0.000000 | — | — | — |
| sgd/core/noisy | 0.066940 | — | 0.066940 | — | 0.166555 | 0.000000 | — | — | — |
| sgd/core/switch_quiet | 0.006868 | 0.083870 | 0.000172 | 17.312500 | 0.166555 | 0.000000 | — | — | — |
| sgd/core/switch_noisy | 0.074711 | 0.153912 | 0.067824 | 63.718750 | 0.166555 | 0.000000 | — | — | — |
| sgd/noise_jump/noise_jump | 0.028146 | — | 0.028146 | — | 0.039340 | 0.000000 | — | — | — |
| sgd/drift/drift | 0.000194 | — | 0.000194 | — | 0.005454 | 0.000000 | — | — | — |
| sgd/exactly_quiet/exactly_quiet | 0.000000 | — | 0.000000 | — | 0.000167 | 0.000000 | — | — | — |
| sgd/mixed/increase_first | 0.033519 | 0.112549 | 0.026647 | 52.156250 | 0.106693 | 0.000000 | — | — | — |
| sgd/mixed/decrease_first | 0.047076 | 0.114474 | 0.041215 | 49.265625 | 0.106693 | 0.000000 | — | — | — |
| adwin/core/quiet | 0.000001 | — | 0.000001 | — | 0.004483 | 0.000000 | 3500.500000 | 6000.000000 | 0.000000 |
| adwin/core/noisy | 0.001224 | — | 0.001224 | — | 0.004483 | 88.000000 | 2366.734775 | 3460.375000 | 2539.625000 |
| adwin/core/switch_quiet | 0.012197 | 0.152183 | 0.000024 | 30.093750 | 0.004483 | 457.000000 | 1107.122275 | 2013.500000 | 3986.500000 |
| adwin/core/switch_noisy | 0.021197 | 0.245127 | 0.001725 | 52.109375 | 0.004483 | 447.000000 | 1042.230625 | 1793.250000 | 4206.750000 |
| adwin/noise_jump/noise_jump | 0.000782 | — | 0.000782 | — | 0.000657 | 201.000000 | 1847.964650 | 3848.750000 | 2151.250000 |
| adwin/drift/drift | 0.003150 | — | 0.003150 | — | 0.000567 | 2370.000000 | 837.336000 | 2089.000000 | 3911.000000 |
| adwin/exactly_quiet/exactly_quiet | 0.000000 | — | 0.000000 | — | 0.000167 | 0.000000 | 3500.500000 | 6000.000000 | 0.000000 |
| adwin/mixed/increase_first | 0.015812 | 0.190538 | 0.000618 | 40.250000 | 0.003619 | 444.000000 | 1091.664675 | 2014.125000 | 3985.875000 |
| adwin/mixed/decrease_first | 0.016344 | 0.193044 | 0.000979 | 38.609375 | 0.003619 | 458.000000 | 1050.163625 | 1835.625000 | 4164.375000 |
| oracle_matched/core/quiet | 0.000078 | — | 0.000078 | — | 0.057094 | 0.000000 | 32.000000 | 32.000000 | 5968.000000 |
| oracle_matched/core/noisy | 0.030225 | — | 0.030225 | — | 0.057094 | 0.000000 | 32.000000 | 32.000000 | 5968.000000 |
| oracle_matched/core/switch_quiet | 0.005334 | 0.065772 | 0.000079 | 27.781250 | 0.057094 | 64.000000 | 31.837600 | 32.000000 | 5968.000000 |
| oracle_matched/core/switch_noisy | 0.036817 | 0.104963 | 0.030891 | 31.546875 | 0.057094 | 64.000000 | 31.837600 | 32.000000 | 5968.000000 |
| oracle_matched/noise_jump/noise_jump | 0.012856 | — | 0.012856 | — | 0.013289 | 0.000000 | 32.000000 | 32.000000 | 5968.000000 |
| oracle_matched/drift/drift | 0.000184 | — | 0.000184 | — | 0.002005 | 0.000000 | 32.000000 | 32.000000 | 5968.000000 |
| oracle_matched/exactly_quiet/exactly_quiet | 0.000000 | — | 0.000000 | — | 0.000167 | 0.000000 | 32.000000 | 32.000000 | 5968.000000 |
| oracle_matched/mixed/increase_first | 0.017438 | 0.080321 | 0.011970 | 27.281250 | 0.036826 | 64.000000 | 31.837600 | 32.000000 | 5968.000000 |
| oracle_matched/mixed/decrease_first | 0.023906 | 0.081825 | 0.018870 | 27.687500 | 0.036826 | 64.000000 | 31.837600 | 32.000000 | 5968.000000 |
| random/core/quiet | 0.000080 | — | 0.000080 | — | 0.057707 | 84.000000 | 31.819969 | 31.781250 | 5968.218750 |
| random/core/noisy | 0.030818 | — | 0.030818 | — | 0.057707 | 90.000000 | 31.822919 | 31.531250 | 5968.468750 |
| random/core/switch_quiet | 0.017985 | 0.223882 | 0.000081 | 29.156250 | 0.057707 | 83.000000 | 31.818138 | 32.000000 | 5968.000000 |
| random/core/switch_noisy | 0.049844 | 0.261902 | 0.031404 | 40.453125 | 0.057707 | 89.000000 | 31.815044 | 31.687500 | 5968.312500 |
| random/noise_jump/noise_jump | 0.013118 | — | 0.013118 | — | 0.013508 | 91.000000 | 31.817475 | 31.750000 | 5968.250000 |
| random/drift/drift | 0.000186 | — | 0.000186 | — | 0.002031 | 96.000000 | 31.797038 | 31.875000 | 5968.125000 |
| random/exactly_quiet/exactly_quiet | 0.000000 | — | 0.000000 | — | 0.000167 | 80.000000 | 31.826494 | 31.281250 | 5968.718750 |
| random/mixed/increase_first | 0.029471 | 0.228813 | 0.012137 | 35.062500 | 0.036994 | 99.000000 | 31.787263 | 31.375000 | 5968.625000 |
| random/mixed/decrease_first | 0.036286 | 0.233366 | 0.019149 | 34.468750 | 0.036994 | 90.000000 | 31.808750 | 32.000000 | 5968.000000 |
| noreset_matched/core/quiet | 0.000078 | — | 0.000078 | — | 0.056807 | 0.000000 | 32.000000 | 32.000000 | 5968.000000 |
| noreset_matched/core/noisy | 0.030225 | — | 0.030225 | — | 0.056807 | 0.000000 | 32.000000 | 32.000000 | 5968.000000 |
| noreset_matched/core/switch_quiet | 0.017983 | 0.223881 | 0.000079 | 29.156250 | 0.056807 | 0.000000 | 32.000000 | 32.000000 | 5968.000000 |
| noreset_matched/core/switch_noisy | 0.049366 | 0.261818 | 0.030891 | 40.453125 | 0.056807 | 0.000000 | 32.000000 | 32.000000 | 5968.000000 |
| noreset_matched/noise_jump/noise_jump | 0.012856 | — | 0.012856 | — | 0.013289 | 0.000000 | 32.000000 | 32.000000 | 5968.000000 |
| noreset_matched/drift/drift | 0.000184 | — | 0.000184 | — | 0.002005 | 0.000000 | 32.000000 | 32.000000 | 5968.000000 |
| noreset_matched/exactly_quiet/exactly_quiet | 0.000000 | — | 0.000000 | — | 0.000167 | 0.000000 | 32.000000 | 32.000000 | 5968.000000 |
| noreset_matched/mixed/increase_first | 0.029320 | 0.228836 | 0.011970 | 35.062500 | 0.036592 | 0.000000 | 32.000000 | 32.000000 | 5968.000000 |
| noreset_matched/mixed/decrease_first | 0.036068 | 0.233845 | 0.018870 | 34.468750 | 0.036592 | 0.000000 | 32.000000 | 32.000000 | 5968.000000 |

Width counts retained observations, not physical storage. SGD uses exponential weights and has no literal window. Fixed windows evict routinely without reset flags; ADWIN flags window shrinkage. Discarded totals include routine cap evictions. Vector norms repeat per fixture.

## Actual reset/shrink timing

| Policy/fixture/coordinate/event | Hits/finite seeds | Censored latency |
| --- | --- | ---: |
| forget/core/switch_quiet/target_down | 32/32 | 10.031250 |
| forget/core/switch_quiet/target_up | 32/32 | 10.125000 |
| forget/core/switch_noisy/target_down | 32/32 | 13.593750 |
| forget/core/switch_noisy/target_up | 32/32 | 13.281250 |
| forget/noise_jump/noise_jump/noise_increase | 0/32 | 100.000000 |
| forget/noise_jump/noise_jump/noise_decrease | 0/32 | 100.000000 |
| forget/drift/drift/drift_start | 31/32 | 66.093750 |
| forget/drift/drift/drift_end | 10/32 | 80.187500 |
| forget/mixed/increase_first/target_down | 32/32 | 12.125000 |
| forget/mixed/increase_first/target_up | 32/32 | 10.937500 |
| forget/mixed/decrease_first/target_down | 32/32 | 11.312500 |
| forget/mixed/decrease_first/target_up | 32/32 | 12.281250 |
| oracle/core/switch_quiet/target_down | 32/32 | 0.000000 |
| oracle/core/switch_quiet/target_up | 32/32 | 0.000000 |
| oracle/core/switch_noisy/target_down | 32/32 | 0.000000 |
| oracle/core/switch_noisy/target_up | 32/32 | 0.000000 |
| oracle/noise_jump/noise_jump/noise_increase | 0/32 | 100.000000 |
| oracle/noise_jump/noise_jump/noise_decrease | 0/32 | 100.000000 |
| oracle/drift/drift/drift_start | 0/32 | 100.000000 |
| oracle/drift/drift/drift_end | 0/32 | 100.000000 |
| oracle/mixed/increase_first/target_down | 32/32 | 0.000000 |
| oracle/mixed/increase_first/target_up | 32/32 | 0.000000 |
| oracle/mixed/decrease_first/target_down | 32/32 | 0.000000 |
| oracle/mixed/decrease_first/target_up | 32/32 | 0.000000 |
| adwin/core/switch_quiet/target_down | 32/32 | 1.375000 |
| adwin/core/switch_quiet/target_up | 32/32 | 1.625000 |
| adwin/core/switch_noisy/target_down | 32/32 | 5.281250 |
| adwin/core/switch_noisy/target_up | 32/32 | 4.937500 |
| adwin/noise_jump/noise_jump/noise_increase | 32/32 | 16.906250 |
| adwin/noise_jump/noise_jump/noise_decrease | 0/32 | 100.000000 |
| adwin/drift/drift/drift_start | 13/32 | 97.437500 |
| adwin/drift/drift/drift_end | 32/32 | 21.250000 |
| adwin/mixed/increase_first/target_down | 32/32 | 1.500000 |
| adwin/mixed/increase_first/target_up | 32/32 | 4.906250 |
| adwin/mixed/decrease_first/target_down | 32/32 | 4.906250 |
| adwin/mixed/decrease_first/target_up | 32/32 | 1.500000 |
| oracle_matched/core/switch_quiet/target_down | 32/32 | 0.000000 |
| oracle_matched/core/switch_quiet/target_up | 32/32 | 0.000000 |
| oracle_matched/core/switch_noisy/target_down | 32/32 | 0.000000 |
| oracle_matched/core/switch_noisy/target_up | 32/32 | 0.000000 |
| oracle_matched/noise_jump/noise_jump/noise_increase | 0/32 | 100.000000 |
| oracle_matched/noise_jump/noise_jump/noise_decrease | 0/32 | 100.000000 |
| oracle_matched/drift/drift/drift_start | 0/32 | 100.000000 |
| oracle_matched/drift/drift/drift_end | 0/32 | 100.000000 |
| oracle_matched/mixed/increase_first/target_down | 32/32 | 0.000000 |
| oracle_matched/mixed/increase_first/target_up | 32/32 | 0.000000 |
| oracle_matched/mixed/decrease_first/target_down | 32/32 | 0.000000 |
| oracle_matched/mixed/decrease_first/target_up | 32/32 | 0.000000 |
| random/core/switch_quiet/target_down | 2/32 | 96.781250 |
| random/core/switch_quiet/target_up | 1/32 | 98.375000 |
| random/core/switch_noisy/target_down | 0/32 | 100.000000 |
| random/core/switch_noisy/target_up | 2/32 | 98.625000 |
| random/noise_jump/noise_jump/noise_increase | 1/32 | 99.093750 |
| random/noise_jump/noise_jump/noise_decrease | 3/32 | 94.218750 |
| random/drift/drift/drift_start | 3/32 | 95.500000 |
| random/drift/drift/drift_end | 2/32 | 97.437500 |
| random/mixed/increase_first/target_down | 0/32 | 100.000000 |
| random/mixed/increase_first/target_up | 0/32 | 100.000000 |
| random/mixed/decrease_first/target_down | 1/32 | 99.343750 |
| random/mixed/decrease_first/target_up | 2/32 | 96.500000 |

## Measured execution time

| Stage | Family | Seconds |
| --- | --- | ---: |
| tuning | forget | 3.47 |
| tuning | oracle | 2.17 |
| tuning | window | 1.15 |
| tuning | sgd | 0.89 |
| tuning | adwin | 9.68 |
| confirmation | forget | 4.60 |
| confirmation | oracle | 0.37 |
| confirmation | window | 0.44 |
| confirmation | sgd | 0.41 |
| confirmation | adwin | 8.32 |
| confirmation | oracle_matched | 1.65 |
| confirmation | random | 0.85 |
| confirmation | noreset_matched | 0.69 |

Each searched family consumes 5,184,000 coordinate observations. Times exclude archive writes and share cached gates; the first family pays cache initialization. Configuration budgets are equal, not CPU costs.

## Scope and reproduction

ADWIN2 is independently implemented from the paper: practical Eq.(3.1), five buckets per size, minimum subwindow5. Gaussian observations violate the bounded-input premise; no corresponding formal guarantee or library-release parity is claimed. All policies see unchanged raw observations.

Perfect timing is privileged, not perfect segmentation: retaining K>1 at the true event may retain old-regime data. No oracle or detector outcome overrides candidate performance. Candidate success requires all75 comparisons, including >=10% primary improvement and every retention bound. Oracle arms each have45 comparisons. All outcomes close this registration.

Intervals resample whole seeds10000 times with seed85000. Finite menus and synthetic fixtures do not establish global optimizer superiority, population guarantees or general neural-memory utility. Every reached row and source is archived; prior studies remain intact.

`python check_v3_forgetting.py --evidence results/v3-forgetting --reproduce` regenerates every reached row and scientific manifest/summary at rtol1e-11/atol1e-13. `python report_v3_forgetting.py --check` verifies both generated reports.
