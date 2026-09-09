# V4 robustness under frozen lies

Disposition: **learning_negative** (graded arm).

| Stage | Rows |
| --- | ---: |
| tuning | 384 |
| confirmation | 160 |

## Finite-menu tuning

Each searched family: 12 configurations ×8 seeds ×5 fixtures. Same objective: half primary post-switch MSE plus half mean of14 retention metrics.

| Family | Index | Configuration | Tuning objective | Menu endpoint fields |
| --- | ---: | --- | ---: | --- |
| graded | 3 | `{"gain": 2.0, "window": 8}` | 0.073850 | window |
| window | 3 | `{"window": 8}` | 0.098232 | none |
| sgd | 8 | `{"lr": 0.128}` | 0.083380 | none |
| adwin | 9 | `{"delta": 0.1, "clock": 1}` | 0.119778 | delta, clock |

Endpoint choices remain in the registered finite menu; no extension or global-optimum claim. The ADWIN-gated arm uses the selected graded config on observed alarms; it is diagnostic only.


## Independent primary performance

| Policy | Finite seeds | Primary MSE | 95% interval |
| --- | ---: | ---: | --- |
| graded | 32 | 0.103128 | [0.10063906895987759, 0.10573439551074587] |
| window | 32 | 0.123616 | [0.12032943593444737, 0.12698226113729003] |
| sgd | 32 | 0.115491 | [0.11259920954172804, 0.11850123792127538] |
| adwin | 32 | 0.191598 | [0.1867034680693096, 0.19662092137053985] |
| adwin_gated | 32 | 0.133386 | [0.12809979049120931, 0.13871589183222843] |

## graded: learning_negative

All45 comparisons against window/SGD/ADWIN are required for the graded arm; the ADWIN-gated arm is reported with the same instrument for comparison only.

| Contrast | Control | Policy | Delta | 95% interval | Pass |
| --- | ---: | ---: | ---: | --- | --- |
| window/primary | 0.123616 | 0.103128 | -0.020489 | [-0.022664, -0.018394] | True |
| window/quiet | 0.000316 | 0.000178 | -0.000138 | [-0.000140, -0.000135] | True |
| window/noisy | 0.124797 | 0.069985 | -0.054812 | [-0.055961, -0.053645] | True |
| window/switch_quiet | 0.064085 | 0.065940 | 0.001855 | [-0.001409, 0.005129] | True |
| window/switch_noisy | 0.183854 | 0.141820 | -0.042034 | [-0.048308, -0.035795] | True |
| window/noise_jump | 0.049606 | 0.027726 | -0.021880 | [-0.022725, -0.021056] | True |
| window/drift | 0.000320 | 0.000201 | -0.000120 | [-0.000122, -0.000117] | True |
| window/exactly_quiet | 0.000000 | 0.000000 | 0.000000 | [0.000000, 0.000000] | True |
| window/noise_jump/noise_increase | 0.122789 | 0.066762 | -0.056026 | [-0.060969, -0.051070] | True |
| window/noise_jump/noise_decrease | 0.002516 | 0.001394 | -0.001121 | [-0.001609, -0.000688] | True |
| window/drift/drift | 0.000330 | 0.000236 | -0.000094 | [-0.000100, -0.000088] | True |
| window/mixed/increase_first/post_mse | 0.124812 | 0.102277 | -0.022535 | [-0.027165, -0.017773] | True |
| window/mixed/increase_first/stable_mse | 0.049583 | 0.028246 | -0.021337 | [-0.022168, -0.020540] | True |
| window/mixed/decrease_first/post_mse | 0.121714 | 0.102473 | -0.019241 | [-0.023309, -0.015322] | True |
| window/mixed/decrease_first/stable_mse | 0.075299 | 0.042525 | -0.032773 | [-0.033664, -0.031899] | True |
| sgd/primary | 0.115491 | 0.103128 | -0.012363 | [-0.014186, -0.010632] | True |
| sgd/quiet | 0.000173 | 0.000178 | 0.000005 | [0.000004, 0.000006] | True |
| sgd/noisy | 0.068432 | 0.069985 | 0.001553 | [0.001251, 0.001870] | True |
| sgd/switch_quiet | 0.083594 | 0.065940 | -0.017654 | [-0.020914, -0.014429] | True |
| sgd/switch_noisy | 0.148868 | 0.141820 | -0.007048 | [-0.012227, -0.002121] | True |
| sgd/noise_jump | 0.027088 | 0.027726 | 0.000638 | [0.000469, 0.000816] | True |
| sgd/drift | 0.000195 | 0.000201 | 0.000005 | [0.000004, 0.000006] | True |
| sgd/exactly_quiet | 0.000000 | 0.000000 | -0.000000 | [-0.000000, -0.000000] | True |
| sgd/noise_jump/noise_increase | 0.065458 | 0.066762 | 0.001305 | [0.000404, 0.002377] | True |
| sgd/noise_jump/noise_decrease | 0.001389 | 0.001394 | 0.000006 | [0.000001, 0.000011] | True |
| sgd/drift/drift | 0.000231 | 0.000236 | 0.000005 | [0.000004, 0.000007] | True |
| sgd/mixed/increase_first/post_mse | 0.114802 | 0.102277 | -0.012525 | [-0.015966, -0.009328] | True |
| sgd/mixed/increase_first/stable_mse | 0.027341 | 0.028246 | 0.000905 | [0.000662, 0.001169] | True |
| sgd/mixed/decrease_first/post_mse | 0.114700 | 0.102473 | -0.012227 | [-0.015419, -0.009226] | True |
| sgd/mixed/decrease_first/stable_mse | 0.041433 | 0.042525 | 0.001093 | [0.000816, 0.001398] | True |
| adwin/primary | 0.191598 | 0.103128 | -0.088470 | [-0.092651, -0.084236] | True |
| adwin/quiet | 0.000001 | 0.000178 | 0.000177 | [0.000173, 0.000181] | True |
| adwin/noisy | 0.001029 | 0.069985 | 0.068956 | [0.067414, 0.070437] | False |
| adwin/switch_quiet | 0.151593 | 0.065940 | -0.085652 | [-0.089688, -0.081752] | True |
| adwin/switch_noisy | 0.235313 | 0.141820 | -0.093493 | [-0.106136, -0.081222] | True |
| adwin/noise_jump | 0.000717 | 0.027726 | 0.027009 | [0.025948, 0.028050] | False |
| adwin/drift | 0.003145 | 0.000201 | -0.002945 | [-0.002967, -0.002922] | True |
| adwin/exactly_quiet | 0.000000 | 0.000000 | 0.000000 | [0.000000, 0.000000] | True |
| adwin/noise_jump/noise_increase | 0.002346 | 0.066762 | 0.064416 | [0.060011, 0.068868] | False |
| adwin/noise_jump/noise_decrease | 0.000503 | 0.001394 | 0.000892 | [0.000326, 0.001554] | True |
| adwin/drift/drift | 0.007643 | 0.000236 | -0.007407 | [-0.007598, -0.007232] | True |
| adwin/mixed/increase_first/post_mse | 0.187416 | 0.102277 | -0.085139 | [-0.093100, -0.077451] | True |
| adwin/mixed/increase_first/stable_mse | 0.000591 | 0.028246 | 0.027654 | [0.026664, 0.028589] | False |
| adwin/mixed/decrease_first/post_mse | 0.192069 | 0.102473 | -0.089596 | [-0.096541, -0.083122] | True |
| adwin/mixed/decrease_first/stable_mse | 0.000934 | 0.042525 | 0.041592 | [0.040357, 0.042784] | False |

## adwin_gated: learning_negative (diagnostic; authorizes nothing)

All45 comparisons against window/SGD/ADWIN are required for the graded arm; the ADWIN-gated arm is reported with the same instrument for comparison only.

| Contrast | Control | Policy | Delta | 95% interval | Pass |
| --- | ---: | ---: | ---: | --- | --- |
| window/primary | 0.123616 | 0.133386 | 0.009770 | [0.005780, 0.014006] | False |
| window/quiet | 0.000316 | 0.000173 | -0.000142 | [-0.000144, -0.000140] | True |
| window/noisy | 0.124797 | 0.068711 | -0.056085 | [-0.057167, -0.054981] | True |
| window/switch_quiet | 0.064085 | 0.047911 | -0.016175 | [-0.017229, -0.015120] | True |
| window/switch_noisy | 0.183854 | 0.205953 | 0.022099 | [0.009848, 0.035114] | False |
| window/noise_jump | 0.049606 | 0.029710 | -0.019895 | [-0.020853, -0.018909] | True |
| window/drift | 0.000320 | 0.000254 | -0.000066 | [-0.000070, -0.000062] | True |
| window/exactly_quiet | 0.000000 | 0.000000 | 0.000000 | [0.000000, 0.000000] | True |
| window/noise_jump/noise_increase | 0.122789 | 0.125591 | 0.002802 | [-0.012964, 0.021639] | False |
| window/noise_jump/noise_decrease | 0.002516 | 0.001389 | -0.001127 | [-0.001615, -0.000694] | True |
| window/drift/drift | 0.000330 | 0.000369 | 0.000039 | [0.000032, 0.000047] | True |
| window/mixed/increase_first/post_mse | 0.124812 | 0.144649 | 0.019838 | [0.010291, 0.031323] | False |
| window/mixed/increase_first/stable_mse | 0.049583 | 0.027717 | -0.021866 | [-0.022669, -0.021077] | True |
| window/mixed/decrease_first/post_mse | 0.121714 | 0.135033 | 0.013319 | [0.006413, 0.021028] | False |
| window/mixed/decrease_first/stable_mse | 0.075299 | 0.041879 | -0.033420 | [-0.034327, -0.032484] | True |
| sgd/primary | 0.115491 | 0.133386 | 0.017895 | [0.013772, 0.022218] | False |
| sgd/quiet | 0.000173 | 0.000173 | 0.000000 | [0.000000, 0.000000] | True |
| sgd/noisy | 0.068432 | 0.068711 | 0.000280 | [0.000112, 0.000486] | True |
| sgd/switch_quiet | 0.083594 | 0.047911 | -0.035683 | [-0.036754, -0.034623] | True |
| sgd/switch_noisy | 0.148868 | 0.205953 | 0.057085 | [0.044962, 0.069642] | False |
| sgd/noise_jump | 0.027088 | 0.029710 | 0.002622 | [0.002013, 0.003342] | False |
| sgd/drift | 0.000195 | 0.000254 | 0.000059 | [0.000055, 0.000062] | True |
| sgd/exactly_quiet | 0.000000 | 0.000000 | 0.000000 | [0.000000, 0.000000] | True |
| sgd/noise_jump/noise_increase | 0.065458 | 0.125591 | 0.060133 | [0.044766, 0.078667] | False |
| sgd/noise_jump/noise_decrease | 0.001389 | 0.001389 | -0.000000 | [-0.000000, 0.000000] | True |
| sgd/drift/drift | 0.000231 | 0.000369 | 0.000138 | [0.000131, 0.000146] | True |
| sgd/mixed/increase_first/post_mse | 0.114802 | 0.144649 | 0.029848 | [0.020001, 0.041393] | False |
| sgd/mixed/increase_first/stable_mse | 0.027341 | 0.027717 | 0.000376 | [0.000141, 0.000660] | True |
| sgd/mixed/decrease_first/post_mse | 0.114700 | 0.135033 | 0.020333 | [0.013223, 0.028549] | False |
| sgd/mixed/decrease_first/stable_mse | 0.041433 | 0.041879 | 0.000446 | [0.000228, 0.000704] | True |
| adwin/primary | 0.191598 | 0.133386 | -0.058211 | [-0.063332, -0.053233] | True |
| adwin/quiet | 0.000001 | 0.000173 | 0.000172 | [0.000169, 0.000176] | True |
| adwin/noisy | 0.001029 | 0.068711 | 0.067682 | [0.066156, 0.069190] | False |
| adwin/switch_quiet | 0.151593 | 0.047911 | -0.103682 | [-0.106386, -0.100933] | True |
| adwin/switch_noisy | 0.235313 | 0.205953 | -0.029361 | [-0.040608, -0.017340] | True |
| adwin/noise_jump | 0.000717 | 0.029710 | 0.028994 | [0.027747, 0.030326] | False |
| adwin/drift | 0.003145 | 0.000254 | -0.002891 | [-0.002915, -0.002869] | True |
| adwin/exactly_quiet | 0.000000 | 0.000000 | 0.000000 | [0.000000, 0.000000] | True |
| adwin/noise_jump/noise_increase | 0.002346 | 0.125591 | 0.123245 | [0.106283, 0.142291] | False |
| adwin/noise_jump/noise_decrease | 0.000503 | 0.001389 | 0.000886 | [0.000319, 0.001551] | True |
| adwin/drift/drift | 0.007643 | 0.000369 | -0.007274 | [-0.007469, -0.007096] | True |
| adwin/mixed/increase_first/post_mse | 0.187416 | 0.144649 | -0.042766 | [-0.054518, -0.031397] | True |
| adwin/mixed/increase_first/stable_mse | 0.000591 | 0.027717 | 0.027125 | [0.026222, 0.027987] | False |
| adwin/mixed/decrease_first/post_mse | 0.192069 | 0.135033 | -0.057036 | [-0.067461, -0.046358] | True |
| adwin/mixed/decrease_first/stable_mse | 0.000934 | 0.041879 | 0.040945 | [0.039705, 0.042168] | False |

## Absolute errors and alarms

| Policy/fixture/coordinate | Excess MSE | Post MSE | Stable MSE | Recovery latency | Mean vector update norm | Total alarms | Mean width |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| graded/core/quiet | 0.000178 | — | 0.000178 | — | 0.170408 | 193.000000 | — |
| graded/core/noisy | 0.069985 | — | 0.069985 | — | 0.170408 | 167.000000 | — |
| graded/core/switch_quiet | 0.005435 | 0.065940 | 0.000174 | 9.437500 | 0.170408 | 245.000000 | — |
| graded/core/switch_noisy | 0.075031 | 0.141820 | 0.069223 | 62.015625 | 0.170408 | 242.000000 | — |
| graded/noise_jump/noise_jump | 0.027726 | — | 0.027726 | — | 0.039696 | 196.000000 | — |
| graded/drift/drift | 0.000201 | — | 0.000201 | — | 0.005553 | 235.000000 | — |
| graded/exactly_quiet/exactly_quiet | 0.000000 | — | 0.000000 | — | 0.000167 | 188.000000 | — |
| graded/mixed/increase_first | 0.034168 | 0.102277 | 0.028246 | 43.796875 | 0.109385 | 270.000000 | — |
| graded/mixed/decrease_first | 0.047321 | 0.102473 | 0.042525 | 38.515625 | 0.109385 | 242.000000 | — |
| window/core/quiet | 0.000316 | — | 0.000316 | — | 0.223069 | 0.000000 | 8.000000 |
| window/core/noisy | 0.124797 | — | 0.124797 | — | 0.223069 | 0.000000 | 8.000000 |
| window/core/switch_quiet | 0.005414 | 0.064085 | 0.000312 | 8.000000 | 0.223069 | 0.000000 | 8.000000 |
| window/core/switch_noisy | 0.129125 | 0.183854 | 0.124365 | 235.375000 | 0.223069 | 0.000000 | 8.000000 |
| window/noise_jump/noise_jump | 0.049606 | — | 0.049606 | — | 0.052108 | 0.000000 | 8.000000 |
| window/drift/drift | 0.000320 | — | 0.000320 | — | 0.007219 | 0.000000 | 8.000000 |
| window/exactly_quiet/exactly_quiet | 0.000000 | — | 0.000000 | — | 0.000167 | 0.000000 | 8.000000 |
| window/mixed/increase_first | 0.055601 | 0.124812 | 0.049583 | 126.140625 | 0.143022 | 0.000000 | 8.000000 |
| window/mixed/decrease_first | 0.079012 | 0.121714 | 0.075299 | 86.250000 | 0.143022 | 0.000000 | 8.000000 |
| sgd/core/quiet | 0.000173 | — | 0.000173 | — | 0.166799 | 0.000000 | — |
| sgd/core/noisy | 0.068432 | — | 0.068432 | — | 0.166799 | 0.000000 | — |
| sgd/core/switch_quiet | 0.006843 | 0.083594 | 0.000169 | 17.328125 | 0.166799 | 0.000000 | — |
| sgd/core/switch_noisy | 0.074142 | 0.148868 | 0.067644 | 61.968750 | 0.166799 | 0.000000 | — |
| sgd/noise_jump/noise_jump | 0.027088 | — | 0.027088 | — | 0.039025 | 0.000000 | — |
| sgd/drift/drift | 0.000195 | — | 0.000195 | — | 0.005438 | 0.000000 | — |
| sgd/exactly_quiet/exactly_quiet | 0.000000 | — | 0.000000 | — | 0.000167 | 0.000000 | — |
| sgd/mixed/increase_first | 0.034338 | 0.114802 | 0.027341 | 38.296875 | 0.106767 | 0.000000 | — |
| sgd/mixed/decrease_first | 0.047294 | 0.114700 | 0.041433 | 42.750000 | 0.106767 | 0.000000 | — |
| adwin/core/quiet | 0.000001 | — | 0.000001 | — | 0.004534 | 0.000000 | 3500.500000 |
| adwin/core/noisy | 0.001029 | — | 0.001029 | — | 0.004534 | 62.000000 | 2621.257500 |
| adwin/core/switch_quiet | 0.012160 | 0.151593 | 0.000035 | 28.343750 | 0.004534 | 450.000000 | 1106.194525 |
| adwin/core/switch_noisy | 0.020297 | 0.235313 | 0.001600 | 46.640625 | 0.004534 | 441.000000 | 1014.040700 |
| adwin/noise_jump/noise_jump | 0.000717 | — | 0.000717 | — | 0.000685 | 194.000000 | 1794.331400 |
| adwin/drift/drift | 0.003145 | — | 0.003145 | — | 0.000563 | 2336.000000 | 842.813600 |
| adwin/exactly_quiet/exactly_quiet | 0.000000 | — | 0.000000 | — | 0.000167 | 0.000000 | 3500.500000 |
| adwin/mixed/increase_first | 0.015537 | 0.187416 | 0.000591 | 37.671875 | 0.003719 | 453.000000 | 1072.909025 |
| adwin/mixed/decrease_first | 0.016224 | 0.192069 | 0.000934 | 34.781250 | 0.003719 | 479.000000 | 1040.491950 |
| adwin_gated/core/quiet | 0.000173 | — | 0.000173 | — | 0.172728 | 0.000000 | — |
| adwin_gated/core/noisy | 0.068711 | — | 0.068711 | — | 0.172728 | 62.000000 | — |
| adwin_gated/core/switch_quiet | 0.003989 | 0.047911 | 0.000169 | 4.796875 | 0.172728 | 450.000000 | — |
| adwin_gated/core/switch_noisy | 0.079090 | 0.205953 | 0.068058 | 83.640625 | 0.172728 | 441.000000 | — |
| adwin_gated/noise_jump/noise_jump | 0.029710 | — | 0.029710 | — | 0.041335 | 194.000000 | — |
| adwin_gated/drift/drift | 0.000254 | — | 0.000254 | — | 0.006621 | 2336.000000 | — |
| adwin_gated/exactly_quiet/exactly_quiet | 0.000000 | — | 0.000000 | — | 0.000167 | 0.000000 | — |
| adwin_gated/mixed/increase_first | 0.037071 | 0.144649 | 0.027717 | 52.671875 | 0.113708 | 453.000000 | — |
| adwin_gated/mixed/decrease_first | 0.049331 | 0.135033 | 0.041879 | 40.531250 | 0.113708 | 479.000000 | — |

Alarm counts include delayed true events and false alarms; their kinds are recorded per alarm in the raw evidence. SGD uses exponential weights and has no literal window.


## Measured execution time

| Stage | Family | Seconds |
| --- | --- | ---: |
| tuning | graded | 1.20 |
| tuning | window | 0.46 |
| tuning | sgd | 0.75 |
| tuning | adwin | 5.47 |
| confirmation | graded | 0.56 |
| confirmation | window | 0.25 |
| confirmation | sgd | 0.05 |
| confirmation | adwin | 1.45 |
| confirmation | adwin_gated | 1.75 |

Configuration budgets are equal, not CPU costs. Times exclude archive writes and share cached fixtures.

## Scope and reproduction

ADWIN2 is independently implemented from the paper: practical Eq.(3.1), five buckets per size, minimum subwindow5. Gaussian observations violate the bounded-input premise; no corresponding formal guarantee or library-release parity is claimed. All policies see unchanged raw observations.

The lie profile is frozen at registration and was never tuned. No schedule outcome overrides the advancement gate. All outcomes close this registration.

Intervals resample whole seeds10000 times with seed185000. Finite menus and synthetic fixtures do not establish global optimizer superiority, population guarantees or general neural-memory utility. Every reached row and source is archived; prior studies remain intact.

`python check_v4_robust.py --evidence results/v4-robust --reproduce` regenerates every reached row and scientific manifest/summary at rtol1e-11/atol1e-13. `python report_v4_robust.py --check` verifies both generated reports.
