# V3 drift-timing tolerance

Disposition: reference **learning_positive**; tolerance **{'levels': {'jitter_32': {'status': 'learning_positive', 'passed': 45, 'cells': 45}, 'jitter_256': {'status': 'learning_positive', 'passed': 45, 'cells': 45}, 'jitter_1024': {'status': 'learning_negative', 'passed': 43, 'cells': 45}}, 'tolerance': 256}**.

| Stage | Rows |
| --- | ---: |
| tuning | 288 |
| confirmation | 288 |

## Finite-menu tuning

Each searched family: 12 configurations ×8 seeds ×5 fixtures. Same objective: half primary post-switch MSE plus half mean of14 retention metrics. The slope configuration is frozen from the slope manifest; perturbed arms run in confirmation only.

| Family | Index | Configuration | Tuning objective | Menu endpoint fields |
| --- | ---: | --- | ---: | --- |
| window | 3 | `{"window": 8}` | 0.095719 | none |
| sgd | 8 | `{"lr": 0.128}` | 0.084301 | none |
| adwin | 9 | `{"delta": 0.1, "clock": 1}` | 0.126928 | delta, clock |

Endpoint choices remain in the registered finite menu; no extension or global-optimum claim.


## Tolerance measurement (diagnostic arms)

Per-level 45-comparison instrument against window/SGD/ADWIN. The tolerance point is the largest jitter passing all45. This disposition authorizes nothing.

| Arm | Primary MSE | Cells passed /45 | Status |
| --- | ---: | ---: | --- |
| reference | 0.085204 | 45/45 | learning_positive |
| jitter_32 | 0.085204 | 45/45 | learning_positive |
| jitter_256 | 0.085204 | 45/45 | learning_positive |
| jitter_1024 | 0.085204 | 43/45 | learning_negative |
| drop_50 | 0.085204 | 43/45 | learning_negative |
| oracle_nofallback | 0.087734 | 39/45 | learning_negative |

Tolerance point: **256**.

## reference: learning_positive (unperturbed baseline, diagnostic)

| Contrast | Control | Policy | Delta | 95% interval | Pass |
| --- | ---: | ---: | ---: | --- | --- |
| window/primary | 0.127481 | 0.085204 | -0.042277 | [-0.045289, -0.038877] | True |
| window/quiet | 0.000317 | 0.000001 | -0.000316 | [-0.000321, -0.000311] | True |
| window/noisy | 0.124243 | 0.001068 | -0.123175 | [-0.124908, -0.121418] | True |
| window/switch_quiet | 0.064098 | 0.068478 | 0.004380 | [0.003896, 0.004881] | True |
| window/switch_noisy | 0.192164 | 0.105232 | -0.086932 | [-0.094735, -0.078656] | True |
| window/noise_jump | 0.050034 | 0.000904 | -0.049130 | [-0.050822, -0.047431] | True |
| window/drift | 0.000318 | 0.000095 | -0.000223 | [-0.000229, -0.000217] | True |
| window/exactly_quiet | 0.000000 | 0.000000 | 0.000000 | [0.000000, 0.000000] | True |
| window/noise_jump/noise_increase | 0.118741 | 0.004205 | -0.114537 | [-0.123257, -0.106310] | True |
| window/noise_jump/noise_decrease | 0.003570 | 0.000597 | -0.002973 | [-0.004038, -0.001973] | True |
| window/drift/drift | 0.000328 | 0.000087 | -0.000241 | [-0.000249, -0.000232] | True |
| window/mixed/increase_first/post_mse | 0.121785 | 0.080783 | -0.041002 | [-0.048464, -0.033139] | True |
| window/mixed/increase_first/stable_mse | 0.049780 | 0.000700 | -0.049079 | [-0.051065, -0.047129] | True |
| window/mixed/decrease_first/post_mse | 0.131878 | 0.086325 | -0.045553 | [-0.051176, -0.039831] | True |
| window/mixed/decrease_first/stable_mse | 0.074610 | 0.000716 | -0.073894 | [-0.076433, -0.071578] | True |
| sgd/primary | 0.119307 | 0.085204 | -0.034103 | [-0.036576, -0.031442] | True |
| sgd/quiet | 0.000174 | 0.000001 | -0.000173 | [-0.000176, -0.000169] | True |
| sgd/noisy | 0.067951 | 0.001068 | -0.066883 | [-0.067955, -0.065825] | True |
| sgd/switch_quiet | 0.083648 | 0.068478 | -0.015170 | [-0.015641, -0.014678] | True |
| sgd/switch_noisy | 0.157365 | 0.105232 | -0.052133 | [-0.058870, -0.045040] | True |
| sgd/noise_jump | 0.027346 | 0.000904 | -0.026442 | [-0.027301, -0.025570] | True |
| sgd/drift | 0.000194 | 0.000095 | -0.000099 | [-0.000104, -0.000095] | True |
| sgd/exactly_quiet | 0.000000 | 0.000000 | -0.000000 | [-0.000000, -0.000000] | True |
| sgd/noise_jump/noise_increase | 0.067079 | 0.004205 | -0.062875 | [-0.068991, -0.057233] | True |
| sgd/noise_jump/noise_decrease | 0.001692 | 0.000597 | -0.001096 | [-0.001798, -0.000407] | True |
| sgd/drift/drift | 0.000229 | 0.000087 | -0.000141 | [-0.000148, -0.000134] | True |
| sgd/mixed/increase_first/post_mse | 0.114311 | 0.080783 | -0.033528 | [-0.038731, -0.028035] | True |
| sgd/mixed/increase_first/stable_mse | 0.027106 | 0.000700 | -0.026405 | [-0.027626, -0.025219] | True |
| sgd/mixed/decrease_first/post_mse | 0.121905 | 0.086325 | -0.035580 | [-0.039948, -0.031042] | True |
| sgd/mixed/decrease_first/stable_mse | 0.040590 | 0.000716 | -0.039873 | [-0.041413, -0.038486] | True |
| adwin/primary | 0.198822 | 0.085204 | -0.113618 | [-0.116599, -0.110401] | True |
| adwin/quiet | 0.000001 | 0.000001 | 0.000000 | [0.000000, 0.000000] | True |
| adwin/noisy | 0.001068 | 0.001068 | 0.000000 | [0.000000, 0.000000] | True |
| adwin/switch_quiet | 0.148912 | 0.068478 | -0.080434 | [-0.082572, -0.078261] | True |
| adwin/switch_noisy | 0.253667 | 0.105232 | -0.148435 | [-0.159573, -0.136850] | True |
| adwin/noise_jump | 0.000904 | 0.000904 | 0.000000 | [0.000000, 0.000000] | True |
| adwin/drift | 0.003162 | 0.000095 | -0.003067 | [-0.003095, -0.003041] | True |
| adwin/exactly_quiet | 0.000000 | 0.000000 | 0.000000 | [0.000000, 0.000000] | True |
| adwin/noise_jump/noise_increase | 0.004205 | 0.004205 | 0.000000 | [0.000000, 0.000000] | True |
| adwin/noise_jump/noise_decrease | 0.000597 | 0.000597 | 0.000000 | [0.000000, 0.000000] | True |
| adwin/drift/drift | 0.007617 | 0.000087 | -0.007530 | [-0.007702, -0.007359] | True |
| adwin/mixed/increase_first/post_mse | 0.192793 | 0.080783 | -0.112010 | [-0.118365, -0.105634] | True |
| adwin/mixed/increase_first/stable_mse | 0.000700 | 0.000700 | 0.000000 | [0.000000, 0.000000] | True |
| adwin/mixed/decrease_first/post_mse | 0.199916 | 0.086325 | -0.113592 | [-0.119612, -0.107300] | True |
| adwin/mixed/decrease_first/stable_mse | 0.000716 | 0.000716 | 0.000000 | [0.000000, 0.000000] | True |

## Absolute errors and memory

| Policy/fixture/coordinate | Excess MSE | Post MSE | Stable MSE | Recovery latency | Mean vector update norm | Total requests | Fast mean width | Fast discarded | ADWIN mean width | Fast share |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| window/core/quiet | 0.000317 | — | 0.000317 | — | 0.222666 | 0.000000 | 8.000000 | 5992.000000 | — | — |
| window/core/noisy | 0.124243 | — | 0.124243 | — | 0.222666 | 0.000000 | 8.000000 | 5992.000000 | — | — |
| window/core/switch_quiet | 0.005411 | 0.064098 | 0.000308 | 8.000000 | 0.222666 | 0.000000 | 8.000000 | 5992.000000 | — | — |
| window/core/switch_noisy | 0.129579 | 0.192164 | 0.124137 | 209.781250 | 0.222666 | 0.000000 | 8.000000 | 5992.000000 | — | — |
| window/noise_jump/noise_jump | 0.050034 | — | 0.050034 | — | 0.052395 | 0.000000 | 8.000000 | 5992.000000 | — | — |
| window/drift/drift | 0.000318 | — | 0.000318 | — | 0.007228 | 0.000000 | 8.000000 | 5992.000000 | — | — |
| window/exactly_quiet/exactly_quiet | 0.000000 | — | 0.000000 | — | 0.000167 | 0.000000 | 8.000000 | 5992.000000 | — | — |
| window/mixed/increase_first | 0.055540 | 0.121785 | 0.049780 | 117.531250 | 0.142605 | 0.000000 | 8.000000 | 5992.000000 | — | — |
| window/mixed/decrease_first | 0.079191 | 0.131878 | 0.074610 | 139.437500 | 0.142605 | 0.000000 | 8.000000 | 5992.000000 | — | — |
| sgd/core/quiet | 0.000174 | — | 0.000174 | — | 0.166482 | 0.000000 | — | — | — | — |
| sgd/core/noisy | 0.067951 | — | 0.067951 | — | 0.166482 | 0.000000 | — | — | — | — |
| sgd/core/switch_quiet | 0.006847 | 0.083648 | 0.000168 | 17.265625 | 0.166482 | 0.000000 | — | — | — | — |
| sgd/core/switch_noisy | 0.075443 | 0.157365 | 0.068319 | 69.312500 | 0.166482 | 0.000000 | — | — | — | — |
| sgd/noise_jump/noise_jump | 0.027346 | — | 0.027346 | — | 0.039179 | 0.000000 | — | — | — | — |
| sgd/drift/drift | 0.000194 | — | 0.000194 | — | 0.005435 | 0.000000 | — | — | — | — |
| sgd/exactly_quiet/exactly_quiet | 0.000000 | — | 0.000000 | — | 0.000167 | 0.000000 | — | — | — | — |
| sgd/mixed/increase_first | 0.034082 | 0.114311 | 0.027106 | 43.765625 | 0.106620 | 0.000000 | — | — | — | — |
| sgd/mixed/decrease_first | 0.047095 | 0.121905 | 0.040590 | 41.359375 | 0.106620 | 0.000000 | — | — | — | — |
| adwin/core/quiet | 0.000001 | — | 0.000001 | — | 0.004541 | 0.000000 | 3500.500000 | 0.000000 | — | — |
| adwin/core/noisy | 0.001068 | — | 0.001068 | — | 0.004541 | 91.000000 | 2429.841600 | 2399.000000 | — | — |
| adwin/core/switch_quiet | 0.011942 | 0.148912 | 0.000031 | 27.656250 | 0.004541 | 439.000000 | 1105.916625 | 4016.875000 | — | — |
| adwin/core/switch_noisy | 0.021652 | 0.253667 | 0.001476 | 52.203125 | 0.004541 | 433.000000 | 1041.706075 | 4340.625000 | — | — |
| adwin/noise_jump/noise_jump | 0.000904 | — | 0.000904 | — | 0.000677 | 189.000000 | 1818.395750 | 2221.000000 | — | — |
| adwin/drift/drift | 0.003162 | — | 0.003162 | — | 0.000564 | 2364.000000 | 837.350600 | 3947.000000 | — | — |
| adwin/exactly_quiet/exactly_quiet | 0.000000 | — | 0.000000 | — | 0.000167 | 0.000000 | 3500.500000 | 0.000000 | — | — |
| adwin/mixed/increase_first | 0.016068 | 0.192793 | 0.000700 | 40.093750 | 0.003608 | 459.000000 | 1064.332550 | 4019.875000 | — | — |
| adwin/mixed/decrease_first | 0.016652 | 0.199916 | 0.000716 | 45.593750 | 0.003608 | 474.000000 | 1067.453575 | 4249.250000 | — | — |
| reference/core/quiet | 0.000001 | — | 0.000001 | — | 0.004427 | 0.000000 | 32.000000 | 5968.000000 | 3500.500000 | 0.000000 |
| reference/core/noisy | 0.001068 | — | 0.001068 | — | 0.004427 | 0.000000 | 32.000000 | 5968.000000 | 2429.841600 | 0.000000 |
| reference/core/switch_quiet | 0.005507 | 0.068478 | 0.000031 | 30.296875 | 0.004427 | 64.000000 | 31.837600 | 5968.000000 | 1105.916625 | 0.012800 |
| reference/core/switch_noisy | 0.009777 | 0.105232 | 0.001476 | 46.953125 | 0.004427 | 64.000000 | 31.837600 | 5968.000000 | 1041.706075 | 0.012800 |
| reference/noise_jump/noise_jump | 0.000904 | — | 0.000904 | — | 0.000677 | 0.000000 | 32.000000 | 5968.000000 | 1818.395750 | 0.000000 |
| reference/drift/drift | 0.000095 | — | 0.000095 | — | 0.000799 | 64.000000 | 31.837600 | 5968.000000 | 837.350600 | 0.006400 |
| reference/exactly_quiet/exactly_quiet | 0.000000 | — | 0.000000 | — | 0.000167 | 0.000000 | 32.000000 | 5968.000000 | 3500.500000 | 0.000000 |
| reference/mixed/increase_first | 0.007107 | 0.080783 | 0.000700 | 34.218750 | 0.003493 | 64.000000 | 31.837600 | 5968.000000 | 1064.332550 | 0.012800 |
| reference/mixed/decrease_first | 0.007565 | 0.086325 | 0.000716 | 40.281250 | 0.003493 | 64.000000 | 31.837600 | 5968.000000 | 1067.453575 | 0.012800 |
| jitter_32/core/quiet | 0.000001 | — | 0.000001 | — | 0.004427 | 0.000000 | 32.000000 | 5968.000000 | 3500.500000 | 0.000000 |
| jitter_32/core/noisy | 0.001068 | — | 0.001068 | — | 0.004427 | 0.000000 | 32.000000 | 5968.000000 | 2429.841600 | 0.000000 |
| jitter_32/core/switch_quiet | 0.005507 | 0.068478 | 0.000031 | 30.296875 | 0.004427 | 64.000000 | 31.837600 | 5968.000000 | 1105.916625 | 0.012800 |
| jitter_32/core/switch_noisy | 0.009777 | 0.105232 | 0.001476 | 46.953125 | 0.004427 | 64.000000 | 31.837600 | 5968.000000 | 1041.706075 | 0.012800 |
| jitter_32/noise_jump/noise_jump | 0.000904 | — | 0.000904 | — | 0.000677 | 0.000000 | 32.000000 | 5968.000000 | 1818.395750 | 0.000000 |
| jitter_32/drift/drift | 0.000101 | — | 0.000101 | — | 0.000798 | 64.000000 | 31.837600 | 5968.000000 | 837.350600 | 0.006400 |
| jitter_32/exactly_quiet/exactly_quiet | 0.000000 | — | 0.000000 | — | 0.000167 | 0.000000 | 32.000000 | 5968.000000 | 3500.500000 | 0.000000 |
| jitter_32/mixed/increase_first | 0.007107 | 0.080783 | 0.000700 | 34.218750 | 0.003493 | 64.000000 | 31.837600 | 5968.000000 | 1064.332550 | 0.012800 |
| jitter_32/mixed/decrease_first | 0.007565 | 0.086325 | 0.000716 | 40.281250 | 0.003493 | 64.000000 | 31.837600 | 5968.000000 | 1067.453575 | 0.012800 |
| jitter_256/core/quiet | 0.000001 | — | 0.000001 | — | 0.004427 | 0.000000 | 32.000000 | 5968.000000 | 3500.500000 | 0.000000 |
| jitter_256/core/noisy | 0.001068 | — | 0.001068 | — | 0.004427 | 0.000000 | 32.000000 | 5968.000000 | 2429.841600 | 0.000000 |
| jitter_256/core/switch_quiet | 0.005507 | 0.068478 | 0.000031 | 30.296875 | 0.004427 | 64.000000 | 31.837600 | 5968.000000 | 1105.916625 | 0.012800 |
| jitter_256/core/switch_noisy | 0.009777 | 0.105232 | 0.001476 | 46.953125 | 0.004427 | 64.000000 | 31.837600 | 5968.000000 | 1041.706075 | 0.012800 |
| jitter_256/noise_jump/noise_jump | 0.000904 | — | 0.000904 | — | 0.000677 | 0.000000 | 32.000000 | 5968.000000 | 1818.395750 | 0.000000 |
| jitter_256/drift/drift | 0.000194 | — | 0.000194 | — | 0.000819 | 64.000000 | 31.837600 | 5968.000000 | 837.350600 | 0.006400 |
| jitter_256/exactly_quiet/exactly_quiet | 0.000000 | — | 0.000000 | — | 0.000167 | 0.000000 | 32.000000 | 5968.000000 | 3500.500000 | 0.000000 |
| jitter_256/mixed/increase_first | 0.007107 | 0.080783 | 0.000700 | 34.218750 | 0.003493 | 64.000000 | 31.837600 | 5968.000000 | 1064.332550 | 0.012800 |
| jitter_256/mixed/decrease_first | 0.007565 | 0.086325 | 0.000716 | 40.281250 | 0.003493 | 64.000000 | 31.837600 | 5968.000000 | 1067.453575 | 0.012800 |
| jitter_1024/core/quiet | 0.000001 | — | 0.000001 | — | 0.004427 | 0.000000 | 32.000000 | 5968.000000 | 3500.500000 | 0.000000 |
| jitter_1024/core/noisy | 0.001068 | — | 0.001068 | — | 0.004427 | 0.000000 | 32.000000 | 5968.000000 | 2429.841600 | 0.000000 |
| jitter_1024/core/switch_quiet | 0.005507 | 0.068478 | 0.000031 | 30.296875 | 0.004427 | 64.000000 | 31.837600 | 5968.000000 | 1105.916625 | 0.012800 |
| jitter_1024/core/switch_noisy | 0.009777 | 0.105232 | 0.001476 | 46.953125 | 0.004427 | 64.000000 | 31.837600 | 5968.000000 | 1041.706075 | 0.012800 |
| jitter_1024/noise_jump/noise_jump | 0.000904 | — | 0.000904 | — | 0.000677 | 0.000000 | 32.000000 | 5968.000000 | 1818.395750 | 0.000000 |
| jitter_1024/drift/drift | 0.000847 | — | 0.000847 | — | 0.000833 | 64.000000 | 31.840137 | 5968.000000 | 837.350600 | 0.006400 |
| jitter_1024/exactly_quiet/exactly_quiet | 0.000000 | — | 0.000000 | — | 0.000167 | 0.000000 | 32.000000 | 5968.000000 | 3500.500000 | 0.000000 |
| jitter_1024/mixed/increase_first | 0.007107 | 0.080783 | 0.000700 | 34.218750 | 0.003493 | 64.000000 | 31.837600 | 5968.000000 | 1064.332550 | 0.012800 |
| jitter_1024/mixed/decrease_first | 0.007565 | 0.086325 | 0.000716 | 40.281250 | 0.003493 | 64.000000 | 31.837600 | 5968.000000 | 1067.453575 | 0.012800 |
| drop_50/core/quiet | 0.000001 | — | 0.000001 | — | 0.004427 | 0.000000 | 32.000000 | 5968.000000 | 3500.500000 | 0.000000 |
| drop_50/core/noisy | 0.001068 | — | 0.001068 | — | 0.004427 | 0.000000 | 32.000000 | 5968.000000 | 2429.841600 | 0.000000 |
| drop_50/core/switch_quiet | 0.005507 | 0.068478 | 0.000031 | 30.296875 | 0.004427 | 64.000000 | 31.837600 | 5968.000000 | 1105.916625 | 0.012800 |
| drop_50/core/switch_noisy | 0.009777 | 0.105232 | 0.001476 | 46.953125 | 0.004427 | 64.000000 | 31.837600 | 5968.000000 | 1041.706075 | 0.012800 |
| drop_50/noise_jump/noise_jump | 0.000904 | — | 0.000904 | — | 0.000677 | 0.000000 | 32.000000 | 5968.000000 | 1818.395750 | 0.000000 |
| drop_50/drift/drift | 0.001145 | — | 0.001145 | — | 0.000841 | 38.000000 | 31.903575 | 5968.000000 | 837.350600 | 0.003400 |
| drop_50/exactly_quiet/exactly_quiet | 0.000000 | — | 0.000000 | — | 0.000167 | 0.000000 | 32.000000 | 5968.000000 | 3500.500000 | 0.000000 |
| drop_50/mixed/increase_first | 0.007107 | 0.080783 | 0.000700 | 34.218750 | 0.003493 | 64.000000 | 31.837600 | 5968.000000 | 1064.332550 | 0.012800 |
| drop_50/mixed/decrease_first | 0.007565 | 0.086325 | 0.000716 | 40.281250 | 0.003493 | 64.000000 | 31.837600 | 5968.000000 | 1067.453575 | 0.012800 |
| oracle_nofallback/core/quiet | 0.000080 | — | 0.000080 | — | 0.057038 | 0.000000 | 32.000000 | 5968.000000 | — | — |
| oracle_nofallback/core/noisy | 0.031037 | — | 0.031037 | — | 0.057038 | 0.000000 | 32.000000 | 5968.000000 | — | — |
| oracle_nofallback/core/switch_quiet | 0.005357 | 0.066072 | 0.000077 | 27.609375 | 0.057038 | 64.000000 | 31.837600 | 5968.000000 | — | — |
| oracle_nofallback/core/switch_noisy | 0.038098 | 0.111538 | 0.031712 | 31.250000 | 0.057038 | 64.000000 | 31.837600 | 5968.000000 | — | — |
| oracle_nofallback/noise_jump/noise_jump | 0.012482 | — | 0.012482 | — | 0.013252 | 0.000000 | 32.000000 | 5968.000000 | — | — |
| oracle_nofallback/drift/drift | 0.000186 | — | 0.000186 | — | 0.002017 | 64.000000 | 31.837600 | 5968.000000 | — | — |
| oracle_nofallback/exactly_quiet/exactly_quiet | 0.000000 | — | 0.000000 | — | 0.000167 | 0.000000 | 32.000000 | 5968.000000 | — | — |
| oracle_nofallback/mixed/increase_first | 0.017947 | 0.083418 | 0.012254 | 27.312500 | 0.036736 | 64.000000 | 31.837600 | 5968.000000 | — | — |
| oracle_nofallback/mixed/decrease_first | 0.023924 | 0.089908 | 0.018187 | 28.609375 | 0.036736 | 64.000000 | 31.837600 | 5968.000000 | — | — |

Width counts retained observations, not physical storage. SGD uses exponential weights and has no literal window. Granted, perturbed and oracle schedules are distinguished by provenance in every record and never mix.


## Measured execution time

| Stage | Family | Seconds |
| --- | --- | ---: |
| tuning | window | 0.38 |
| tuning | sgd | 0.04 |
| tuning | adwin | 2.74 |
| confirmation | window | 0.68 |
| confirmation | sgd | 0.03 |
| confirmation | adwin | 1.33 |
| confirmation | reference | 2.21 |
| confirmation | jitter_32 | 2.19 |
| confirmation | jitter_256 | 2.67 |
| confirmation | jitter_1024 | 2.48 |
| confirmation | drop_50 | 2.34 |
| confirmation | oracle_nofallback | 0.18 |

Configuration budgets are equal, not CPU costs. Times exclude archive writes and share cached fixtures.

## Scope and reproduction

ADWIN2 is independently implemented from the paper: practical Eq.(3.1), five buckets per size, minimum subwindow5. Gaussian observations violate the bounded-input premise; no corresponding formal guarantee or library-release parity is claimed. All policies see unchanged raw observations.

Perturbed schedules are diagnostic: jittered/dropped times are evaluator-built from true boundaries, not observable-derived. The tolerance curve authorizes no follow-up; the reading rules in the registration decide what follows.

Intervals resample whole seeds10000 times with seed175000. Finite menus and synthetic fixtures do not establish global optimizer superiority, population guarantees or general neural-memory utility. Every reached row and source is archived; prior studies remain intact.

`python check_v3_drifttol.py --evidence results/v3-drifttol --reproduce` regenerates every reached row and scientific manifest/summary at rtol1e-11/atol1e-13. `python report_v3_drifttol.py --check` verifies both generated reports.
