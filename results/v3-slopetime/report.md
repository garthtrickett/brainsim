# V3 observable-gated slope

Disposition: **learning_negative** (slope_adwin arm).

| Stage | Rows |
| --- | ---: |
| tuning | 384 |
| confirmation | 224 |

## Finite-menu tuning

Each searched family: 12 configurations ×8 seeds ×5 fixtures. Same objective: half primary post-switch MSE plus half mean of14 retention metrics. Only the slope horizon is searched; estimator and base are frozen.

| Family | Index | Configuration | Tuning objective | Menu endpoint fields |
| --- | ---: | --- | ---: | --- |
| slope_adwin | 0 | `{"Hs": 16}` | 0.073513 | Hs |
| window | 3 | `{"window": 8}` | 0.100463 | none |
| sgd | 8 | `{"lr": 0.128}` | 0.086124 | none |
| adwin | 9 | `{"delta": 0.1, "clock": 1}` | 0.126906 | delta, clock |

Endpoint choices remain in the registered finite menu; no extension or global-optimum claim. Reference, random_slope and oracle_nofallback are matched diagnostics run in confirmation only.

Frozen random p=0.002735039431, from 1132 alarm-driven requests / 432000 tuning coordinate-updates, 16-update suppression, opportunities from t0. Expected pooled frequency is matched, not actual counts or memory age.


## Independent primary performance

| Policy | Finite seeds | Primary MSE | 95% interval |
| --- | ---: | ---: | --- |
| slope_adwin | 32 | 0.108994 | [0.10576473668443619, 0.1122294278969106] |
| window | 32 | 0.127588 | [0.12446422672624648, 0.13073038893245756] |
| sgd | 32 | 0.118972 | [0.11542707656520308, 0.1225431337537935] |
| adwin | 32 | 0.196737 | [0.19129771524598693, 0.20253296788004832] |
| reference | 32 | 0.084769 | [0.08061236264233887, 0.08887342598824419] |
| random_slope | 32 | 0.195218 | [0.1892962272415713, 0.20124556318656076] |
| oracle_nofallback | 32 | 0.103576 | [0.09997850765989506, 0.10705814967047132] |

## slope_adwin: learning_negative

The deployable arm faces45 comparisons against window/SGD/ADWIN. All45 must pass for learning_positive; a positive justifies only a separately authorized broader benchmark, never agent integration.

| Contrast | Control | Policy | Delta | 95% interval | Pass |
| --- | ---: | ---: | ---: | --- | --- |
| window/primary | 0.127588 | 0.108994 | -0.018593 | [-0.021767, -0.015360] | True |
| window/quiet | 0.000310 | 0.000001 | -0.000309 | [-0.000315, -0.000304] | True |
| window/noisy | 0.124982 | 0.001602 | -0.123380 | [-0.124960, -0.121785] | True |
| window/switch_quiet | 0.064181 | 0.053825 | -0.010357 | [-0.011990, -0.008703] | True |
| window/switch_noisy | 0.190475 | 0.165746 | -0.024730 | [-0.034486, -0.014847] | True |
| window/noise_jump | 0.051442 | 0.003769 | -0.047672 | [-0.049279, -0.046056] | True |
| window/drift | 0.000322 | 0.000522 | 0.000200 | [0.000186, 0.000215] | True |
| window/exactly_quiet | 0.000000 | 0.000000 | 0.000000 | [0.000000, 0.000000] | True |
| window/noise_jump/noise_increase | 0.121821 | 0.050165 | -0.071657 | [-0.079953, -0.063312] | True |
| window/noise_jump/noise_decrease | 0.003153 | 0.000983 | -0.002170 | [-0.003596, -0.000722] | True |
| window/drift/drift | 0.000338 | 0.001183 | 0.000845 | [0.000795, 0.000896] | True |
| window/mixed/increase_first/post_mse | 0.127863 | 0.109054 | -0.018809 | [-0.025224, -0.012878] | True |
| window/mixed/increase_first/stable_mse | 0.049601 | 0.001598 | -0.048003 | [-0.050092, -0.045925] | True |
| window/mixed/decrease_first/post_mse | 0.127832 | 0.107353 | -0.020479 | [-0.026699, -0.014798] | True |
| window/mixed/decrease_first/stable_mse | 0.076045 | 0.001795 | -0.074250 | [-0.076501, -0.071891] | True |
| sgd/primary | 0.118972 | 0.108994 | -0.009978 | [-0.013720, -0.006264] | False |
| sgd/quiet | 0.000169 | 0.000001 | -0.000169 | [-0.000172, -0.000165] | True |
| sgd/noisy | 0.068121 | 0.001602 | -0.066519 | [-0.067405, -0.065596] | True |
| sgd/switch_quiet | 0.083805 | 0.053825 | -0.029980 | [-0.031622, -0.028326] | True |
| sgd/switch_noisy | 0.152965 | 0.165746 | 0.012780 | [0.003655, 0.021687] | False |
| sgd/noise_jump | 0.028367 | 0.003769 | -0.024597 | [-0.025648, -0.023588] | True |
| sgd/drift | 0.000197 | 0.000522 | 0.000325 | [0.000311, 0.000339] | True |
| sgd/exactly_quiet | 0.000000 | 0.000000 | -0.000000 | [-0.000000, -0.000000] | True |
| sgd/noise_jump/noise_increase | 0.066536 | 0.050165 | -0.016371 | [-0.022487, -0.009922] | True |
| sgd/noise_jump/noise_decrease | 0.001843 | 0.000983 | -0.000860 | [-0.001952, 0.000293] | True |
| sgd/drift/drift | 0.000238 | 0.001183 | 0.000945 | [0.000897, 0.000992] | True |
| sgd/mixed/increase_first/post_mse | 0.120772 | 0.109054 | -0.011718 | [-0.018444, -0.005053] | True |
| sgd/mixed/increase_first/stable_mse | 0.027104 | 0.001598 | -0.025507 | [-0.026757, -0.024224] | True |
| sgd/mixed/decrease_first/post_mse | 0.118347 | 0.107353 | -0.010994 | [-0.016925, -0.005507] | True |
| sgd/mixed/decrease_first/stable_mse | 0.041555 | 0.001795 | -0.039760 | [-0.041064, -0.038404] | True |
| adwin/primary | 0.196737 | 0.108994 | -0.087742 | [-0.092084, -0.083296] | True |
| adwin/quiet | 0.000001 | 0.000001 | 0.000000 | [0.000000, 0.000000] | True |
| adwin/noisy | 0.000794 | 0.001602 | 0.000808 | [0.000446, 0.001229] | True |
| adwin/switch_quiet | 0.149701 | 0.053825 | -0.095876 | [-0.098827, -0.092907] | True |
| adwin/switch_noisy | 0.244430 | 0.165746 | -0.078684 | [-0.089542, -0.068174] | True |
| adwin/noise_jump | 0.000790 | 0.003769 | 0.002979 | [0.002351, 0.003680] | False |
| adwin/drift | 0.003169 | 0.000522 | -0.002647 | [-0.002681, -0.002613] | True |
| adwin/exactly_quiet | 0.000000 | 0.000000 | 0.000000 | [0.000000, 0.000000] | True |
| adwin/noise_jump/noise_increase | 0.003083 | 0.050165 | 0.047081 | [0.038344, 0.055859] | False |
| adwin/noise_jump/noise_decrease | 0.000983 | 0.000983 | 0.000000 | [0.000000, 0.000000] | True |
| adwin/drift/drift | 0.007677 | 0.001183 | -0.006495 | [-0.006705, -0.006290] | True |
| adwin/mixed/increase_first/post_mse | 0.199356 | 0.109054 | -0.090302 | [-0.099771, -0.080438] | True |
| adwin/mixed/increase_first/stable_mse | 0.000822 | 0.001598 | 0.000776 | [0.000367, 0.001283] | True |
| adwin/mixed/decrease_first/post_mse | 0.193460 | 0.107353 | -0.086107 | [-0.093962, -0.078146] | True |
| adwin/mixed/decrease_first/stable_mse | 0.001164 | 0.001795 | 0.000631 | [0.000330, 0.000970] | True |

## reference: learning_negative (41/45, diagnostic)


## random_slope: learning_negative (25/45, diagnostic)


## oracle_nofallback: learning_negative (39/45, diagnostic)


## Absolute errors and memory

| Policy/fixture/coordinate | Excess MSE | Post MSE | Stable MSE | Recovery latency | Mean vector update norm | Total requests | Fast mean width | Fast discarded | ADWIN mean width | Fast share | Slope share | Slope mean |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| slope_adwin/core/quiet | 0.000001 | — | 0.000001 | — | 0.006196 | 0.000000 | 32.000000 | 5968.000000 | 3500.500000 | 0.000000 | 0.000000 | 0.000000 |
| slope_adwin/core/noisy | 0.001602 | — | 0.001602 | — | 0.006196 | 70.000000 | 31.912463 | 5969.312500 | 2778.400550 | 0.006331 | 0.000000 | 0.000000 |
| slope_adwin/core/switch_quiet | 0.004328 | 0.053825 | 0.000024 | 4.000000 | 0.006196 | 452.000000 | 31.647644 | 5968.000000 | 1106.342525 | 0.022581 | 0.000000 | 0.000000 |
| slope_adwin/core/switch_noisy | 0.016648 | 0.165746 | 0.003683 | 35.140625 | 0.006196 | 453.000000 | 31.548325 | 5968.000000 | 1023.756725 | 0.029369 | 0.000000 | 0.000000 |
| slope_adwin/noise_jump/noise_jump | 0.003769 | — | 0.003769 | — | 0.001861 | 192.000000 | 31.732856 | 5968.000000 | 1755.438100 | 0.018269 | 0.000000 | 0.000000 |
| slope_adwin/drift/drift | 0.000522 | — | 0.000522 | — | 0.001400 | 2361.000000 | 26.795850 | 5968.000000 | 842.853200 | 0.369362 | 0.000000 | 0.000000 |
| slope_adwin/exactly_quiet/exactly_quiet | 0.000000 | — | 0.000000 | — | 0.000167 | 0.000000 | 32.000000 | 5968.000000 | 3500.500000 | 0.000000 | 0.000000 | 0.000000 |
| slope_adwin/mixed/increase_first | 0.010194 | 0.109054 | 0.001598 | 26.265625 | 0.004779 | 457.000000 | 31.584481 | 5968.000000 | 1073.593550 | 0.026706 | 0.000000 | 0.000000 |
| slope_adwin/mixed/decrease_first | 0.010240 | 0.107353 | 0.001795 | 25.109375 | 0.004779 | 472.000000 | 31.598438 | 5968.000000 | 1054.475000 | 0.025444 | 0.000000 | 0.000000 |
| window/core/quiet | 0.000310 | — | 0.000310 | — | 0.222856 | 0.000000 | 8.000000 | 5992.000000 | — | — | — | — |
| window/core/noisy | 0.124982 | — | 0.124982 | — | 0.222856 | 0.000000 | 8.000000 | 5992.000000 | — | — | — | — |
| window/core/switch_quiet | 0.005423 | 0.064181 | 0.000313 | 8.000000 | 0.222856 | 0.000000 | 8.000000 | 5992.000000 | — | — | — | — |
| window/core/switch_noisy | 0.132117 | 0.190475 | 0.127042 | 203.484375 | 0.222856 | 0.000000 | 8.000000 | 5992.000000 | — | — | — | — |
| window/noise_jump/noise_jump | 0.051442 | — | 0.051442 | — | 0.052114 | 0.000000 | 8.000000 | 5992.000000 | — | — | — | — |
| window/drift/drift | 0.000322 | — | 0.000322 | — | 0.007216 | 0.000000 | 8.000000 | 5992.000000 | — | — | — | — |
| window/exactly_quiet/exactly_quiet | 0.000000 | — | 0.000000 | — | 0.000167 | 0.000000 | 8.000000 | 5992.000000 | — | — | — | — |
| window/mixed/increase_first | 0.055862 | 0.127863 | 0.049601 | 104.218750 | 0.142602 | 0.000000 | 8.000000 | 5992.000000 | — | — | — | — |
| window/mixed/decrease_first | 0.080188 | 0.127832 | 0.076045 | 119.812500 | 0.142602 | 0.000000 | 8.000000 | 5992.000000 | — | — | — | — |
| sgd/core/quiet | 0.000169 | — | 0.000169 | — | 0.166519 | 0.000000 | — | — | — | — | — | — |
| sgd/core/noisy | 0.068121 | — | 0.068121 | — | 0.166519 | 0.000000 | — | — | — | — | — | — |
| sgd/core/switch_quiet | 0.006862 | 0.083805 | 0.000172 | 17.390625 | 0.166519 | 0.000000 | — | — | — | — | — | — |
| sgd/core/switch_noisy | 0.076705 | 0.152965 | 0.070074 | 65.562500 | 0.166519 | 0.000000 | — | — | — | — | — | — |
| sgd/noise_jump/noise_jump | 0.028367 | — | 0.028367 | — | 0.039091 | 0.000000 | — | — | — | — | — | — |
| sgd/drift/drift | 0.000197 | — | 0.000197 | — | 0.005422 | 0.000000 | — | — | — | — | — | — |
| sgd/exactly_quiet/exactly_quiet | 0.000000 | — | 0.000000 | — | 0.000167 | 0.000000 | — | — | — | — | — | — |
| sgd/mixed/increase_first | 0.034598 | 0.120772 | 0.027104 | 44.437500 | 0.106794 | 0.000000 | — | — | — | — | — | — |
| sgd/mixed/decrease_first | 0.047698 | 0.118347 | 0.041555 | 39.171875 | 0.106794 | 0.000000 | — | — | — | — | — | — |
| adwin/core/quiet | 0.000001 | — | 0.000001 | — | 0.004573 | 0.000000 | 3500.500000 | 0.000000 | — | — | — | — |
| adwin/core/noisy | 0.000794 | — | 0.000794 | — | 0.004573 | 70.000000 | 2778.400550 | 1766.625000 | — | — | — | — |
| adwin/core/switch_quiet | 0.011998 | 0.149701 | 0.000024 | 28.921875 | 0.004573 | 452.000000 | 1106.342525 | 4015.500000 | — | — | — | — |
| adwin/core/switch_noisy | 0.021433 | 0.244430 | 0.002042 | 51.265625 | 0.004573 | 453.000000 | 1023.756725 | 4162.500000 | — | — | — | — |
| adwin/noise_jump/noise_jump | 0.000790 | — | 0.000790 | — | 0.000687 | 192.000000 | 1755.438100 | 2372.750000 | — | — | — | — |
| adwin/drift/drift | 0.003169 | — | 0.003169 | — | 0.000567 | 2361.000000 | 842.853200 | 3939.000000 | — | — | — | — |
| adwin/exactly_quiet/exactly_quiet | 0.000000 | — | 0.000000 | — | 0.000167 | 0.000000 | 3500.500000 | 0.000000 | — | — | — | — |
| adwin/mixed/increase_first | 0.016704 | 0.199356 | 0.000822 | 43.000000 | 0.003592 | 457.000000 | 1073.593550 | 4014.562500 | — | — | — | — |
| adwin/mixed/decrease_first | 0.016548 | 0.193460 | 0.001164 | 42.609375 | 0.003592 | 472.000000 | 1054.475000 | 4189.875000 | — | — | — | — |
| reference/core/quiet | 0.000001 | — | 0.000001 | — | 0.004463 | 0.000000 | 32.000000 | 5968.000000 | — | — | — | — |
| reference/core/noisy | 0.000794 | — | 0.000794 | — | 0.004463 | 0.000000 | 32.000000 | 5968.000000 | — | — | — | — |
| reference/core/switch_quiet | 0.005486 | 0.068298 | 0.000024 | 30.984375 | 0.004463 | 64.000000 | 31.837600 | 5968.000000 | — | — | — | — |
| reference/core/switch_noisy | 0.010068 | 0.102359 | 0.002042 | 42.750000 | 0.004463 | 64.000000 | 31.837600 | 5968.000000 | — | — | — | — |
| reference/noise_jump/noise_jump | 0.000790 | — | 0.000790 | — | 0.000687 | 0.000000 | 32.000000 | 5968.000000 | — | — | — | — |
| reference/drift/drift | 0.003133 | — | 0.003133 | — | 0.000592 | 64.000000 | 31.837600 | 5968.000000 | — | — | — | — |
| reference/exactly_quiet/exactly_quiet | 0.000000 | — | 0.000000 | — | 0.000167 | 0.000000 | 32.000000 | 5968.000000 | — | — | — | — |
| reference/mixed/increase_first | 0.007551 | 0.084939 | 0.000822 | 36.156250 | 0.003480 | 64.000000 | 31.837600 | 5968.000000 | — | — | — | — |
| reference/mixed/decrease_first | 0.007749 | 0.083479 | 0.001164 | 38.656250 | 0.003480 | 64.000000 | 31.837600 | 5968.000000 | — | — | — | — |
| random_slope/core/quiet | 0.000017 | — | 0.000017 | — | 0.013821 | 523.000000 | 30.885088 | 5968.906250 | 3500.500000 | 0.087225 | 0.000000 | 0.000000 |
| random_slope/core/noisy | 0.007861 | — | 0.007861 | — | 0.013821 | 539.000000 | 30.886106 | 5969.156250 | 2778.400550 | 0.087031 | 0.000000 | 0.000000 |
| random_slope/core/switch_quiet | 0.011859 | 0.147795 | 0.000038 | 28.375000 | 0.013821 | 531.000000 | 30.879362 | 5969.781250 | 1106.342525 | 0.087331 | 0.000000 | 0.000000 |
| random_slope/core/switch_noisy | 0.026431 | 0.239465 | 0.007906 | 51.812500 | 0.013821 | 481.000000 | 31.003256 | 5969.375000 | 1023.756725 | 0.077781 | 0.000000 | 0.000000 |
| random_slope/noise_jump/noise_jump | 0.003238 | — | 0.003238 | — | 0.002425 | 515.000000 | 30.909669 | 5968.000000 | 1755.438100 | 0.085169 | 0.000000 | 0.000000 |
| random_slope/drift/drift | 0.002912 | — | 0.002912 | — | 0.000775 | 511.000000 | 30.908019 | 5968.437500 | 842.853200 | 0.085506 | 0.000000 | 0.000000 |
| random_slope/exactly_quiet/exactly_quiet | 0.000000 | — | 0.000000 | — | 0.000167 | 512.000000 | 30.895569 | 5968.125000 | 3500.500000 | 0.086044 | 0.000000 | 0.000000 |
| random_slope/mixed/increase_first | 0.018467 | 0.197426 | 0.002906 | 40.468750 | 0.008014 | 492.000000 | 30.967025 | 5968.281250 | 1073.593550 | 0.081025 | 0.000000 | 0.000000 |
| random_slope/mixed/decrease_first | 0.020142 | 0.196186 | 0.004833 | 43.234375 | 0.008014 | 494.000000 | 30.961062 | 5968.343750 | 1054.475000 | 0.081331 | 0.000000 | 0.000000 |
| oracle_nofallback/core/quiet | 0.000077 | — | 0.000077 | — | 0.058402 | 0.000000 | 32.000000 | 5968.000000 | — | — | — | — |
| oracle_nofallback/core/noisy | 0.030950 | — | 0.030950 | — | 0.058402 | 41.000000 | 31.921225 | 5969.218750 | — | — | — | — |
| oracle_nofallback/core/switch_quiet | 0.004875 | 0.060030 | 0.000078 | 14.718750 | 0.058402 | 98.000000 | 31.751325 | 5968.000000 | — | — | — | — |
| oracle_nofallback/core/switch_noisy | 0.042720 | 0.149749 | 0.033413 | 26.984375 | 0.058402 | 144.000000 | 31.643362 | 5968.000000 | — | — | — | — |
| oracle_nofallback/noise_jump/noise_jump | 0.014772 | — | 0.014772 | — | 0.013999 | 88.000000 | 31.779606 | 5968.000000 | — | — | — | — |
| oracle_nofallback/drift/drift | 0.000175 | — | 0.000175 | — | 0.002556 | 2030.000000 | 26.911956 | 5968.000000 | — | — | — | — |
| oracle_nofallback/exactly_quiet/exactly_quiet | 0.000000 | — | 0.000000 | — | 0.000167 | 0.000000 | 32.000000 | 5968.000000 | — | — | — | — |
| oracle_nofallback/mixed/increase_first | 0.020109 | 0.103972 | 0.012817 | 22.328125 | 0.037795 | 131.000000 | 31.672356 | 5968.000000 | — | — | — | — |
| oracle_nofallback/mixed/decrease_first | 0.025845 | 0.100552 | 0.019349 | 14.593750 | 0.037795 | 127.000000 | 31.691719 | 5968.000000 | — | — | — | — |

Width counts retained observations, not physical storage. SGD uses exponential weights and has no literal window. Observed alarms, granted times and random requests are distinguished by provenance in every record and never mix.


## Measured execution time

| Stage | Family | Seconds |
| --- | --- | ---: |
| tuning | slope_adwin | 10.56 |
| tuning | window | 0.09 |
| tuning | sgd | 0.07 |
| tuning | adwin | 3.11 |
| confirmation | slope_adwin | 3.94 |
| confirmation | window | 0.02 |
| confirmation | sgd | 0.02 |
| confirmation | adwin | 1.28 |
| confirmation | reference | 1.40 |
| confirmation | random_slope | 2.42 |
| confirmation | oracle_nofallback | 1.38 |

Configuration budgets are equal, not CPU costs. Times exclude archive writes and share cached fixtures.

## Scope and reproduction

ADWIN2 is independently implemented from the paper: practical Eq.(3.1), five buckets per size, minimum subwindow5. Gaussian observations violate the bounded-input premise; no corresponding formal guarantee or library-release parity is claimed. All policies see unchanged raw observations.

Observed alarms are deployable timing; granted times and random requests are diagnostic. No schedule outcome overrides the advancement gate. All outcomes close this registration.

Intervals resample whole seeds10000 times with seed145000. Finite menus and synthetic fixtures do not establish global optimizer superiority, population guarantees or general neural-memory utility. Every reached row and source is archived; prior studies remain intact.

`python check_v3_slopetime.py --evidence results/v3-slopetime --reproduce` regenerates every reached row and scientific manifest/summary at rtol1e-11/atol1e-13. `python report_v3_slopetime.py --check` verifies both generated reports.
