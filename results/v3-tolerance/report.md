# V3 timing tolerance

Disposition: **learning_negative** (ADWIN-schedule arm).

| Stage | Rows |
| --- | ---: |
| tuning | 288 |
| confirmation | 448 |

## Finite-menu tuning

Each searched family: 12 configurations ×8 seeds ×5 fixtures. Same objective: half primary post-switch MSE plus half mean of14 retention metrics. The candidate configuration is frozen from the retention manifest; perturbed and ADWIN-schedule arms are schedule variants run in confirmation only.

| Family | Index | Configuration | Tuning objective | Menu endpoint fields |
| --- | ---: | --- | ---: | --- |
| window | 3 | `{"window": 8}` | 0.097026 | none |
| sgd | 8 | `{"lr": 0.128}` | 0.084688 | none |
| adwin | 9 | `{"delta": 0.1, "clock": 1}` | 0.125870 | delta, clock |

Endpoint choices remain in the registered finite menu; no extension or global-optimum claim.


## Tolerance measurement (diagnostic families)

Per-level 45-comparison instrument against window/SGD/ADWIN. The tolerance point is the largest jitter passing all45. This disposition authorizes nothing.

| Arm | Primary MSE | Cells passed /45 | Status |
| --- | ---: | ---: | --- |
| reference | 0.081348 | 41/45 | learning_negative |
| jitter_2 | 0.089387 | 40/45 | learning_negative |
| jitter_8 | 0.123764 | 36/45 | learning_negative |
| jitter_16 | 0.159616 | 32/45 | learning_negative |
| jitter_32 | 0.172438 | 31/45 | learning_negative |
| jitter_128 | 0.193027 | 30/45 | learning_negative |
| drop_10 | 0.089122 | 40/45 | learning_negative |
| drop_50 | 0.134296 | 32/45 | learning_negative |
| add_0005 | 0.194667 | 29/45 | learning_negative |
| add_0020 | 0.193165 | 25/45 | learning_negative |

Tolerance point: **None**.

## adwin_schedule: learning_negative

The deployable arm faces the same45 comparisons. All45 must pass for learning_positive; a positive justifies only a separately authorized broader benchmark, never agent integration.

| Contrast | Control | Policy | Delta | 95% interval | Pass |
| --- | ---: | ---: | ---: | --- | --- |
| window/primary | 0.125197 | 0.104354 | -0.020843 | [-0.024430, -0.017379] | True |
| window/quiet | 0.000311 | 0.000001 | -0.000310 | [-0.000315, -0.000306] | True |
| window/noisy | 0.122507 | 0.002130 | -0.120378 | [-0.122092, -0.118653] | True |
| window/switch_quiet | 0.063926 | 0.054302 | -0.009624 | [-0.011262, -0.008016] | True |
| window/switch_noisy | 0.187573 | 0.154381 | -0.033192 | [-0.042040, -0.024011] | True |
| window/noise_jump | 0.050250 | 0.004367 | -0.045884 | [-0.047917, -0.043949] | True |
| window/drift | 0.000322 | 0.000502 | 0.000180 | [0.000164, 0.000197] | True |
| window/exactly_quiet | 0.000000 | 0.000000 | 0.000000 | [0.000000, 0.000000] | True |
| window/noise_jump/noise_increase | 0.116142 | 0.054374 | -0.061768 | [-0.072276, -0.051157] | True |
| window/noise_jump/noise_decrease | 0.004374 | 0.000838 | -0.003536 | [-0.004781, -0.002457] | True |
| window/drift/drift | 0.000333 | 0.001153 | 0.000820 | [0.000787, 0.000856] | True |
| window/mixed/increase_first/post_mse | 0.121281 | 0.103298 | -0.017982 | [-0.024418, -0.011978] | True |
| window/mixed/increase_first/stable_mse | 0.049795 | 0.001391 | -0.048404 | [-0.050420, -0.046432] | True |
| window/mixed/decrease_first/post_mse | 0.128010 | 0.105435 | -0.022575 | [-0.029222, -0.016279] | True |
| window/mixed/decrease_first/stable_mse | 0.076370 | 0.001902 | -0.074469 | [-0.076257, -0.072636] | True |
| sgd/primary | 0.116510 | 0.104354 | -0.012156 | [-0.015236, -0.009237] | True |
| sgd/quiet | 0.000171 | 0.000001 | -0.000170 | [-0.000172, -0.000167] | True |
| sgd/noisy | 0.067250 | 0.002130 | -0.065120 | [-0.066138, -0.064121] | True |
| sgd/switch_quiet | 0.083467 | 0.054302 | -0.029165 | [-0.030805, -0.027524] | True |
| sgd/switch_noisy | 0.146897 | 0.154381 | 0.007484 | [0.000394, 0.014881] | False |
| sgd/noise_jump | 0.027578 | 0.004367 | -0.023211 | [-0.024453, -0.022024] | True |
| sgd/drift | 0.000195 | 0.000502 | 0.000307 | [0.000291, 0.000323] | True |
| sgd/exactly_quiet | 0.000000 | 0.000000 | -0.000000 | [-0.000000, -0.000000] | True |
| sgd/noise_jump/noise_increase | 0.062471 | 0.054374 | -0.008096 | [-0.016676, 0.001406] | True |
| sgd/noise_jump/noise_decrease | 0.001855 | 0.000838 | -0.001017 | [-0.001620, -0.000479] | True |
| sgd/drift/drift | 0.000230 | 0.001153 | 0.000923 | [0.000891, 0.000957] | True |
| sgd/mixed/increase_first/post_mse | 0.115281 | 0.103298 | -0.011982 | [-0.017899, -0.006815] | True |
| sgd/mixed/increase_first/stable_mse | 0.027418 | 0.001391 | -0.026027 | [-0.027203, -0.024886] | True |
| sgd/mixed/decrease_first/post_mse | 0.120397 | 0.105435 | -0.014962 | [-0.020755, -0.009419] | True |
| sgd/mixed/decrease_first/stable_mse | 0.042059 | 0.001902 | -0.040157 | [-0.041433, -0.038889] | True |
| adwin/primary | 0.194754 | 0.104354 | -0.090400 | [-0.094575, -0.086488] | True |
| adwin/quiet | 0.000001 | 0.000001 | 0.000000 | [0.000000, 0.000000] | True |
| adwin/noisy | 0.000985 | 0.002130 | 0.001145 | [0.000805, 0.001500] | True |
| adwin/switch_quiet | 0.150687 | 0.054302 | -0.096386 | [-0.099601, -0.093212] | True |
| adwin/switch_noisy | 0.228309 | 0.154381 | -0.073928 | [-0.083913, -0.064170] | True |
| adwin/noise_jump | 0.001038 | 0.004367 | 0.003329 | [0.002807, 0.003884] | False |
| adwin/drift | 0.003142 | 0.000502 | -0.002640 | [-0.002667, -0.002612] | True |
| adwin/exactly_quiet | 0.000000 | 0.000000 | 0.000000 | [0.000000, 0.000000] | True |
| adwin/noise_jump/noise_increase | 0.002520 | 0.054374 | 0.051855 | [0.041731, 0.062979] | False |
| adwin/noise_jump/noise_decrease | 0.000838 | 0.000838 | 0.000000 | [0.000000, 0.000000] | True |
| adwin/drift/drift | 0.007698 | 0.001153 | -0.006545 | [-0.006743, -0.006351] | True |
| adwin/mixed/increase_first/post_mse | 0.195975 | 0.103298 | -0.092677 | [-0.102199, -0.083309] | True |
| adwin/mixed/increase_first/stable_mse | 0.000761 | 0.001391 | 0.000631 | [0.000310, 0.000993] | True |
| adwin/mixed/decrease_first/post_mse | 0.204044 | 0.105435 | -0.098609 | [-0.106131, -0.091853] | True |
| adwin/mixed/decrease_first/stable_mse | 0.001096 | 0.001902 | 0.000806 | [0.000430, 0.001238] | True |

## reference (unperturbed schedule, diagnostic)

| Contrast | Control | Policy | Delta | 95% interval | Pass |
| --- | ---: | ---: | ---: | --- | --- |
| window/primary | 0.125197 | 0.081348 | -0.043849 | [-0.047371, -0.040265] | True |
| window/quiet | 0.000311 | 0.000001 | -0.000310 | [-0.000315, -0.000306] | True |
| window/noisy | 0.122507 | 0.000985 | -0.121522 | [-0.123260, -0.119760] | True |
| window/switch_quiet | 0.063926 | 0.067645 | 0.003719 | [0.003211, 0.004249] | True |
| window/switch_noisy | 0.187573 | 0.088731 | -0.098841 | [-0.109518, -0.087846] | True |
| window/noise_jump | 0.050250 | 0.001038 | -0.049212 | [-0.051310, -0.047288] | True |
| window/drift | 0.000322 | 0.003142 | 0.002820 | [0.002793, 0.002850] | False |
| window/exactly_quiet | 0.000000 | 0.000000 | 0.000000 | [0.000000, 0.000000] | True |
| window/noise_jump/noise_increase | 0.116142 | 0.002520 | -0.113622 | [-0.124377, -0.104134] | True |
| window/noise_jump/noise_decrease | 0.004374 | 0.000838 | -0.003536 | [-0.004781, -0.002457] | True |
| window/drift/drift | 0.000333 | 0.007698 | 0.007365 | [0.007157, 0.007573] | False |
| window/mixed/increase_first/post_mse | 0.121281 | 0.079737 | -0.041544 | [-0.048651, -0.034618] | True |
| window/mixed/increase_first/stable_mse | 0.049795 | 0.000761 | -0.049035 | [-0.051102, -0.047042] | True |
| window/mixed/decrease_first/post_mse | 0.128010 | 0.089281 | -0.038729 | [-0.044451, -0.033322] | True |
| window/mixed/decrease_first/stable_mse | 0.076370 | 0.001096 | -0.075275 | [-0.077090, -0.073418] | True |
| sgd/primary | 0.116510 | 0.081348 | -0.035162 | [-0.038104, -0.032234] | True |
| sgd/quiet | 0.000171 | 0.000001 | -0.000170 | [-0.000172, -0.000167] | True |
| sgd/noisy | 0.067250 | 0.000985 | -0.066265 | [-0.067331, -0.065176] | True |
| sgd/switch_quiet | 0.083467 | 0.067645 | -0.015822 | [-0.016303, -0.015324] | True |
| sgd/switch_noisy | 0.146897 | 0.088731 | -0.058166 | [-0.067216, -0.048719] | True |
| sgd/noise_jump | 0.027578 | 0.001038 | -0.026539 | [-0.027805, -0.025372] | True |
| sgd/drift | 0.000195 | 0.003142 | 0.002947 | [0.002920, 0.002975] | False |
| sgd/exactly_quiet | 0.000000 | 0.000000 | -0.000000 | [-0.000000, -0.000000] | True |
| sgd/noise_jump/noise_increase | 0.062471 | 0.002520 | -0.059951 | [-0.066761, -0.054208] | True |
| sgd/noise_jump/noise_decrease | 0.001855 | 0.000838 | -0.001017 | [-0.001620, -0.000479] | True |
| sgd/drift/drift | 0.000230 | 0.007698 | 0.007468 | [0.007264, 0.007672] | False |
| sgd/mixed/increase_first/post_mse | 0.115281 | 0.079737 | -0.035544 | [-0.040922, -0.030251] | True |
| sgd/mixed/increase_first/stable_mse | 0.027418 | 0.000761 | -0.026657 | [-0.027887, -0.025489] | True |
| sgd/mixed/decrease_first/post_mse | 0.120397 | 0.089281 | -0.031116 | [-0.035376, -0.026824] | True |
| sgd/mixed/decrease_first/stable_mse | 0.042059 | 0.001096 | -0.040963 | [-0.042192, -0.039730] | True |
| adwin/primary | 0.194754 | 0.081348 | -0.113405 | [-0.117065, -0.109813] | True |
| adwin/quiet | 0.000001 | 0.000001 | 0.000000 | [0.000000, 0.000000] | True |
| adwin/noisy | 0.000985 | 0.000985 | 0.000000 | [0.000000, 0.000000] | True |
| adwin/switch_quiet | 0.150687 | 0.067645 | -0.083043 | [-0.085347, -0.080798] | True |
| adwin/switch_noisy | 0.228309 | 0.088731 | -0.139578 | [-0.148105, -0.131489] | True |
| adwin/noise_jump | 0.001038 | 0.001038 | 0.000000 | [0.000000, 0.000000] | True |
| adwin/drift | 0.003142 | 0.003142 | 0.000000 | [0.000000, 0.000000] | True |
| adwin/exactly_quiet | 0.000000 | 0.000000 | 0.000000 | [0.000000, 0.000000] | True |
| adwin/noise_jump/noise_increase | 0.002520 | 0.002520 | 0.000000 | [0.000000, 0.000000] | True |
| adwin/noise_jump/noise_decrease | 0.000838 | 0.000838 | 0.000000 | [0.000000, 0.000000] | True |
| adwin/drift/drift | 0.007698 | 0.007698 | 0.000000 | [0.000000, 0.000000] | True |
| adwin/mixed/increase_first/post_mse | 0.195975 | 0.079737 | -0.116238 | [-0.122062, -0.110101] | True |
| adwin/mixed/increase_first/stable_mse | 0.000761 | 0.000761 | 0.000000 | [0.000000, 0.000000] | True |
| adwin/mixed/decrease_first/post_mse | 0.204044 | 0.089281 | -0.114763 | [-0.122120, -0.107563] | True |
| adwin/mixed/decrease_first/stable_mse | 0.001096 | 0.001096 | 0.000000 | [0.000000, 0.000000] | True |

## Absolute errors and memory

| Policy/fixture/coordinate | Excess MSE | Post MSE | Stable MSE | Recovery latency | Mean vector update norm | Total requests | Fast mean width | Fast discarded | ADWIN mean width | Fast share |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| window/core/quiet | 0.000311 | — | 0.000311 | — | 0.222986 | 0.000000 | 8.000000 | 5992.000000 | — | — |
| window/core/noisy | 0.122507 | — | 0.122507 | — | 0.222986 | 0.000000 | 8.000000 | 5992.000000 | — | — |
| window/core/switch_quiet | 0.005400 | 0.063926 | 0.000310 | 7.984375 | 0.222986 | 0.000000 | 8.000000 | 5992.000000 | — | — |
| window/core/switch_noisy | 0.130504 | 0.187573 | 0.125541 | 212.140625 | 0.222986 | 0.000000 | 8.000000 | 5992.000000 | — | — |
| window/noise_jump/noise_jump | 0.050250 | — | 0.050250 | — | 0.051937 | 0.000000 | 8.000000 | 5992.000000 | — | — |
| window/drift/drift | 0.000322 | — | 0.000322 | — | 0.007244 | 0.000000 | 8.000000 | 5992.000000 | — | — |
| window/exactly_quiet/exactly_quiet | 0.000000 | — | 0.000000 | — | 0.000167 | 0.000000 | 8.000000 | 5992.000000 | — | — |
| window/mixed/increase_first | 0.055514 | 0.121281 | 0.049795 | 81.625000 | 0.142912 | 0.000000 | 8.000000 | 5992.000000 | — | — |
| window/mixed/decrease_first | 0.080502 | 0.128010 | 0.076370 | 105.109375 | 0.142912 | 0.000000 | 8.000000 | 5992.000000 | — | — |
| sgd/core/quiet | 0.000171 | — | 0.000171 | — | 0.166693 | 0.000000 | — | — | — | — |
| sgd/core/noisy | 0.067250 | — | 0.067250 | — | 0.166693 | 0.000000 | — | — | — | — |
| sgd/core/switch_quiet | 0.006834 | 0.083467 | 0.000170 | 17.312500 | 0.166693 | 0.000000 | — | — | — | — |
| sgd/core/switch_noisy | 0.074578 | 0.146897 | 0.068290 | 67.593750 | 0.166693 | 0.000000 | — | — | — | — |
| sgd/noise_jump/noise_jump | 0.027578 | — | 0.027578 | — | 0.038836 | 0.000000 | — | — | — | — |
| sgd/drift/drift | 0.000195 | — | 0.000195 | — | 0.005442 | 0.000000 | — | — | — | — |
| sgd/exactly_quiet/exactly_quiet | 0.000000 | — | 0.000000 | — | 0.000167 | 0.000000 | — | — | — | — |
| sgd/mixed/increase_first | 0.034447 | 0.115281 | 0.027418 | 35.984375 | 0.106635 | 0.000000 | — | — | — | — |
| sgd/mixed/decrease_first | 0.048326 | 0.120397 | 0.042059 | 38.531250 | 0.106635 | 0.000000 | — | — | — | — |
| adwin/core/quiet | 0.000001 | — | 0.000001 | — | 0.004570 | 0.000000 | 3500.500000 | 0.000000 | — | — |
| adwin/core/noisy | 0.000985 | — | 0.000985 | — | 0.004570 | 67.000000 | 2522.842650 | 2406.250000 | — | — |
| adwin/core/switch_quiet | 0.012080 | 0.150687 | 0.000027 | 28.453125 | 0.004570 | 455.000000 | 1107.425550 | 3993.875000 | — | — |
| adwin/core/switch_noisy | 0.019687 | 0.228309 | 0.001546 | 46.140625 | 0.004570 | 444.000000 | 1027.551025 | 4214.625000 | — | — |
| adwin/noise_jump/noise_jump | 0.001038 | — | 0.001038 | — | 0.000724 | 206.000000 | 1719.845200 | 2401.125000 | — | — |
| adwin/drift/drift | 0.003142 | — | 0.003142 | — | 0.000569 | 2326.000000 | 848.558400 | 3913.000000 | — | — |
| adwin/exactly_quiet/exactly_quiet | 0.000000 | — | 0.000000 | — | 0.000167 | 0.000000 | 3500.500000 | 0.000000 | — | — |
| adwin/mixed/increase_first | 0.016378 | 0.195975 | 0.000761 | 40.031250 | 0.003674 | 442.000000 | 1073.040250 | 3992.625000 | — | — |
| adwin/mixed/decrease_first | 0.017332 | 0.204044 | 0.001096 | 43.531250 | 0.003674 | 492.000000 | 1049.340150 | 4199.375000 | — | — |
| reference/core/quiet | 0.000001 | — | 0.000001 | — | 0.004431 | 0.000000 | 32.000000 | 5968.000000 | 3500.500000 | 0.000000 |
| reference/core/noisy | 0.000985 | — | 0.000985 | — | 0.004431 | 0.000000 | 32.000000 | 5968.000000 | 2522.842650 | 0.000000 |
| reference/core/switch_quiet | 0.005436 | 0.067645 | 0.000027 | 30.015625 | 0.004431 | 64.000000 | 31.837600 | 5968.000000 | 1107.425550 | 0.012800 |
| reference/core/switch_noisy | 0.008520 | 0.088731 | 0.001546 | 36.515625 | 0.004431 | 64.000000 | 31.837600 | 5968.000000 | 1027.551025 | 0.012800 |
| reference/noise_jump/noise_jump | 0.001038 | — | 0.001038 | — | 0.000724 | 0.000000 | 32.000000 | 5968.000000 | 1719.845200 | 0.000000 |
| reference/drift/drift | 0.003142 | — | 0.003142 | — | 0.000569 | 0.000000 | 32.000000 | 5968.000000 | 848.558400 | 0.000000 |
| reference/exactly_quiet/exactly_quiet | 0.000000 | — | 0.000000 | — | 0.000167 | 0.000000 | 32.000000 | 5968.000000 | 3500.500000 | 0.000000 |
| reference/mixed/increase_first | 0.007079 | 0.079737 | 0.000761 | 34.921875 | 0.003546 | 64.000000 | 31.837600 | 5968.000000 | 1073.040250 | 0.012800 |
| reference/mixed/decrease_first | 0.008151 | 0.089281 | 0.001096 | 40.000000 | 0.003546 | 64.000000 | 31.837600 | 5968.000000 | 1049.340150 | 0.012800 |
| jitter_2/core/quiet | 0.000001 | — | 0.000001 | — | 0.004464 | 0.000000 | 32.000000 | 5968.000000 | 3500.500000 | 0.000000 |
| jitter_2/core/noisy | 0.000985 | — | 0.000985 | — | 0.004464 | 0.000000 | 32.000000 | 5968.000000 | 2522.842650 | 0.000000 |
| jitter_2/core/switch_quiet | 0.006242 | 0.077717 | 0.000027 | 25.125000 | 0.004464 | 64.000000 | 31.837600 | 5968.000000 | 1107.425550 | 0.012800 |
| jitter_2/core/switch_noisy | 0.008826 | 0.092316 | 0.001566 | 34.140625 | 0.004464 | 64.000000 | 31.837600 | 5968.000000 | 1027.551025 | 0.012800 |
| jitter_2/noise_jump/noise_jump | 0.001038 | — | 0.001038 | — | 0.000724 | 0.000000 | 32.000000 | 5968.000000 | 1719.845200 | 0.000000 |
| jitter_2/drift/drift | 0.003142 | — | 0.003142 | — | 0.000569 | 0.000000 | 32.000000 | 5968.000000 | 848.558400 | 0.000000 |
| jitter_2/exactly_quiet/exactly_quiet | 0.000000 | — | 0.000000 | — | 0.000167 | 0.000000 | 32.000000 | 5968.000000 | 3500.500000 | 0.000000 |
| jitter_2/mixed/increase_first | 0.007683 | 0.087238 | 0.000765 | 29.515625 | 0.003553 | 64.000000 | 31.837600 | 5968.000000 | 1073.040250 | 0.012800 |
| jitter_2/mixed/decrease_first | 0.009050 | 0.100276 | 0.001117 | 34.921875 | 0.003553 | 64.000000 | 31.837600 | 5968.000000 | 1049.340150 | 0.012800 |
| jitter_8/core/quiet | 0.000001 | — | 0.000001 | — | 0.004461 | 0.000000 | 32.000000 | 5968.000000 | 3500.500000 | 0.000000 |
| jitter_8/core/noisy | 0.000985 | — | 0.000985 | — | 0.004461 | 0.000000 | 32.000000 | 5968.000000 | 2522.842650 | 0.000000 |
| jitter_8/core/switch_quiet | 0.008904 | 0.110989 | 0.000027 | 16.687500 | 0.004461 | 64.000000 | 31.837600 | 5968.000000 | 1107.425550 | 0.012800 |
| jitter_8/core/switch_noisy | 0.012762 | 0.139941 | 0.001702 | 36.296875 | 0.004461 | 64.000000 | 31.837600 | 5968.000000 | 1027.551025 | 0.012800 |
| jitter_8/noise_jump/noise_jump | 0.001038 | — | 0.001038 | — | 0.000724 | 0.000000 | 32.000000 | 5968.000000 | 1719.845200 | 0.000000 |
| jitter_8/drift/drift | 0.003142 | — | 0.003142 | — | 0.000569 | 0.000000 | 32.000000 | 5968.000000 | 848.558400 | 0.000000 |
| jitter_8/exactly_quiet/exactly_quiet | 0.000000 | — | 0.000000 | — | 0.000167 | 0.000000 | 32.000000 | 5968.000000 | 3500.500000 | 0.000000 |
| jitter_8/mixed/increase_first | 0.010083 | 0.116664 | 0.000815 | 27.140625 | 0.003569 | 64.000000 | 31.837600 | 5968.000000 | 1073.040250 | 0.012800 |
| jitter_8/mixed/decrease_first | 0.011231 | 0.127460 | 0.001124 | 33.984375 | 0.003569 | 64.000000 | 31.837600 | 5968.000000 | 1049.340150 | 0.012800 |
| jitter_16/core/quiet | 0.000001 | — | 0.000001 | — | 0.004580 | 0.000000 | 32.000000 | 5968.000000 | 3500.500000 | 0.000000 |
| jitter_16/core/noisy | 0.000985 | — | 0.000985 | — | 0.004580 | 0.000000 | 32.000000 | 5968.000000 | 2522.842650 | 0.000000 |
| jitter_16/core/switch_quiet | 0.010846 | 0.135265 | 0.000027 | 20.500000 | 0.004580 | 64.000000 | 31.837600 | 5968.000000 | 1107.425550 | 0.012800 |
| jitter_16/core/switch_noisy | 0.015535 | 0.174164 | 0.001741 | 36.468750 | 0.004580 | 64.000000 | 31.837600 | 5968.000000 | 1027.551025 | 0.012800 |
| jitter_16/noise_jump/noise_jump | 0.001038 | — | 0.001038 | — | 0.000724 | 0.000000 | 32.000000 | 5968.000000 | 1719.845200 | 0.000000 |
| jitter_16/drift/drift | 0.003142 | — | 0.003142 | — | 0.000569 | 0.000000 | 32.000000 | 5968.000000 | 848.558400 | 0.000000 |
| jitter_16/exactly_quiet/exactly_quiet | 0.000000 | — | 0.000000 | — | 0.000167 | 0.000000 | 32.000000 | 5968.000000 | 3500.500000 | 0.000000 |
| jitter_16/mixed/increase_first | 0.014000 | 0.165316 | 0.000842 | 31.703125 | 0.003681 | 64.000000 | 31.837600 | 5968.000000 | 1073.040250 | 0.012800 |
| jitter_16/mixed/decrease_first | 0.014200 | 0.163717 | 0.001198 | 36.515625 | 0.003681 | 64.000000 | 31.837600 | 5968.000000 | 1049.340150 | 0.012800 |
| jitter_32/core/quiet | 0.000001 | — | 0.000001 | — | 0.004774 | 0.000000 | 32.000000 | 5968.000000 | 3500.500000 | 0.000000 |
| jitter_32/core/noisy | 0.000985 | — | 0.000985 | — | 0.004774 | 0.000000 | 32.000000 | 5968.000000 | 2522.842650 | 0.000000 |
| jitter_32/core/switch_quiet | 0.011608 | 0.144779 | 0.000028 | 22.828125 | 0.004774 | 64.000000 | 31.837600 | 5968.000000 | 1107.425550 | 0.012800 |
| jitter_32/core/switch_noisy | 0.017191 | 0.194777 | 0.001749 | 37.671875 | 0.004774 | 64.000000 | 31.837600 | 5968.000000 | 1027.551025 | 0.012800 |
| jitter_32/noise_jump/noise_jump | 0.001038 | — | 0.001038 | — | 0.000724 | 0.000000 | 32.000000 | 5968.000000 | 1719.845200 | 0.000000 |
| jitter_32/drift/drift | 0.003142 | — | 0.003142 | — | 0.000569 | 0.000000 | 32.000000 | 5968.000000 | 848.558400 | 0.000000 |
| jitter_32/exactly_quiet/exactly_quiet | 0.000000 | — | 0.000000 | — | 0.000167 | 0.000000 | 32.000000 | 5968.000000 | 3500.500000 | 0.000000 |
| jitter_32/mixed/increase_first | 0.014635 | 0.172873 | 0.000875 | 32.171875 | 0.003896 | 64.000000 | 31.837600 | 5968.000000 | 1073.040250 | 0.012800 |
| jitter_32/mixed/decrease_first | 0.015359 | 0.177323 | 0.001275 | 38.656250 | 0.003896 | 64.000000 | 31.837600 | 5968.000000 | 1049.340150 | 0.012800 |
| jitter_128/core/quiet | 0.000001 | — | 0.000001 | — | 0.005027 | 0.000000 | 32.000000 | 5968.000000 | 3500.500000 | 0.000000 |
| jitter_128/core/noisy | 0.000985 | — | 0.000985 | — | 0.005027 | 0.000000 | 32.000000 | 5968.000000 | 2522.842650 | 0.000000 |
| jitter_128/core/switch_quiet | 0.011992 | 0.149573 | 0.000028 | 27.312500 | 0.005027 | 64.000000 | 31.837600 | 5968.000000 | 1107.425550 | 0.012800 |
| jitter_128/core/switch_noisy | 0.020005 | 0.227806 | 0.001936 | 44.156250 | 0.005027 | 64.000000 | 31.837600 | 5968.000000 | 1027.551025 | 0.012800 |
| jitter_128/noise_jump/noise_jump | 0.001038 | — | 0.001038 | — | 0.000724 | 0.000000 | 32.000000 | 5968.000000 | 1719.845200 | 0.000000 |
| jitter_128/drift/drift | 0.003142 | — | 0.003142 | — | 0.000569 | 0.000000 | 32.000000 | 5968.000000 | 848.558400 | 0.000000 |
| jitter_128/exactly_quiet/exactly_quiet | 0.000000 | — | 0.000000 | — | 0.000167 | 0.000000 | 32.000000 | 5968.000000 | 3500.500000 | 0.000000 |
| jitter_128/mixed/increase_first | 0.016687 | 0.196054 | 0.001090 | 39.359375 | 0.004123 | 64.000000 | 31.837600 | 5968.000000 | 1073.040250 | 0.012800 |
| jitter_128/mixed/decrease_first | 0.017110 | 0.198673 | 0.001322 | 42.546875 | 0.004123 | 64.000000 | 31.837600 | 5968.000000 | 1049.340150 | 0.012800 |
| drop_10/core/quiet | 0.000001 | — | 0.000001 | — | 0.004448 | 0.000000 | 32.000000 | 5968.000000 | 3500.500000 | 0.000000 |
| drop_10/core/noisy | 0.000985 | — | 0.000985 | — | 0.004448 | 0.000000 | 32.000000 | 5968.000000 | 2522.842650 | 0.000000 |
| drop_10/core/switch_quiet | 0.005949 | 0.074054 | 0.000027 | 29.875000 | 0.004448 | 59.000000 | 31.850287 | 5968.000000 | 1107.425550 | 0.011800 |
| drop_10/core/switch_noisy | 0.009450 | 0.100349 | 0.001546 | 37.687500 | 0.004448 | 58.000000 | 31.852825 | 5968.000000 | 1027.551025 | 0.011600 |
| drop_10/noise_jump/noise_jump | 0.001038 | — | 0.001038 | — | 0.000724 | 0.000000 | 32.000000 | 5968.000000 | 1719.845200 | 0.000000 |
| drop_10/drift/drift | 0.003142 | — | 0.003142 | — | 0.000569 | 0.000000 | 32.000000 | 5968.000000 | 848.558400 | 0.000000 |
| drop_10/exactly_quiet/exactly_quiet | 0.000000 | — | 0.000000 | — | 0.000167 | 0.000000 | 32.000000 | 5968.000000 | 3500.500000 | 0.000000 |
| drop_10/mixed/increase_first | 0.007539 | 0.085486 | 0.000761 | 34.796875 | 0.003551 | 60.000000 | 31.847750 | 5968.000000 | 1073.040250 | 0.012000 |
| drop_10/mixed/decrease_first | 0.008736 | 0.096599 | 0.001096 | 40.000000 | 0.003551 | 60.000000 | 31.847750 | 5968.000000 | 1049.340150 | 0.012000 |
| drop_50/core/quiet | 0.000001 | — | 0.000001 | — | 0.004551 | 0.000000 | 32.000000 | 5968.000000 | 3500.500000 | 0.000000 |
| drop_50/core/noisy | 0.000985 | — | 0.000985 | — | 0.004551 | 0.000000 | 32.000000 | 5968.000000 | 2522.842650 | 0.000000 |
| drop_50/core/switch_quiet | 0.009079 | 0.113175 | 0.000027 | 29.078125 | 0.004551 | 29.000000 | 31.926413 | 5968.000000 | 1107.425550 | 0.005800 |
| drop_50/core/switch_noisy | 0.013403 | 0.149765 | 0.001546 | 43.812500 | 0.004551 | 36.000000 | 31.908650 | 5968.000000 | 1027.551025 | 0.007200 |
| drop_50/noise_jump/noise_jump | 0.001038 | — | 0.001038 | — | 0.000724 | 0.000000 | 32.000000 | 5968.000000 | 1719.845200 | 0.000000 |
| drop_50/drift/drift | 0.003142 | — | 0.003142 | — | 0.000569 | 0.000000 | 32.000000 | 5968.000000 | 848.558400 | 0.000000 |
| drop_50/exactly_quiet/exactly_quiet | 0.000000 | — | 0.000000 | — | 0.000167 | 0.000000 | 32.000000 | 5968.000000 | 3500.500000 | 0.000000 |
| drop_50/mixed/increase_first | 0.011730 | 0.137879 | 0.000761 | 37.281250 | 0.003632 | 32.000000 | 31.918800 | 5968.000000 | 1073.040250 | 0.006400 |
| drop_50/mixed/decrease_first | 0.011918 | 0.136367 | 0.001096 | 40.828125 | 0.003632 | 38.000000 | 31.903575 | 5968.000000 | 1049.340150 | 0.007600 |
| add_0005/core/quiet | 0.000004 | — | 0.000004 | — | 0.006110 | 96.000000 | 31.783650 | 5968.781250 | 3500.500000 | 0.017019 |
| add_0005/core/noisy | 0.001796 | — | 0.001796 | — | 0.006110 | 87.000000 | 31.841988 | 5968.000000 | 2522.842650 | 0.012438 |
| add_0005/core/switch_quiet | 0.012070 | 0.150535 | 0.000029 | 28.218750 | 0.006110 | 113.000000 | 31.744375 | 5968.000000 | 1107.425550 | 0.020213 |
| add_0005/core/switch_noisy | 0.020501 | 0.227190 | 0.002528 | 46.140625 | 0.006110 | 78.000000 | 31.819837 | 5968.000000 | 1027.551025 | 0.014200 |
| add_0005/noise_jump/noise_jump | 0.001376 | — | 0.001376 | — | 0.001021 | 89.000000 | 31.809762 | 5968.000000 | 1719.845200 | 0.014912 |
| add_0005/drift/drift | 0.003098 | — | 0.003098 | — | 0.000604 | 88.000000 | 31.809687 | 5968.000000 | 848.558400 | 0.015000 |
| add_0005/exactly_quiet/exactly_quiet | 0.000000 | — | 0.000000 | — | 0.000167 | 106.000000 | 31.786850 | 5968.000000 | 3500.500000 | 0.016787 |
| add_0005/mixed/increase_first | 0.016843 | 0.196383 | 0.001231 | 39.609375 | 0.004683 | 96.000000 | 31.789088 | 5968.000000 | 1073.040250 | 0.016413 |
| add_0005/mixed/decrease_first | 0.018263 | 0.204559 | 0.002063 | 43.531250 | 0.004683 | 101.000000 | 31.789475 | 5968.000000 | 1049.340150 | 0.016506 |
| add_0020/core/quiet | 0.000013 | — | 0.000013 | — | 0.011686 | 394.000000 | 31.167094 | 5969.250000 | 3500.500000 | 0.064812 |
| add_0020/core/noisy | 0.006068 | — | 0.006068 | — | 0.011686 | 403.000000 | 31.183625 | 5969.937500 | 2522.842650 | 0.063000 |
| add_0020/core/switch_quiet | 0.011873 | 0.147988 | 0.000037 | 26.828125 | 0.011686 | 402.000000 | 31.155894 | 5968.562500 | 1107.425550 | 0.065525 |
| add_0020/core/switch_noisy | 0.023625 | 0.226259 | 0.006004 | 46.812500 | 0.011686 | 383.000000 | 31.201406 | 5969.625000 | 1027.551025 | 0.061738 |
| add_0020/noise_jump/noise_jump | 0.002755 | — | 0.002755 | — | 0.002000 | 377.000000 | 31.229825 | 5968.000000 | 1719.845200 | 0.060044 |
| add_0020/drift/drift | 0.002948 | — | 0.002948 | — | 0.000717 | 369.000000 | 31.251887 | 5968.812500 | 848.558400 | 0.058156 |
| add_0020/exactly_quiet/exactly_quiet | 0.000000 | — | 0.000000 | — | 0.000167 | 381.000000 | 31.203775 | 5968.000000 | 3500.500000 | 0.062294 |
| add_0020/mixed/increase_first | 0.018270 | 0.194924 | 0.002909 | 39.593750 | 0.007121 | 412.000000 | 31.118094 | 5968.125000 | 1073.040250 | 0.068800 |
| add_0020/mixed/decrease_first | 0.019889 | 0.203491 | 0.003924 | 41.328125 | 0.007121 | 368.000000 | 31.236469 | 5969.125000 | 1049.340150 | 0.059306 |
| adwin_schedule/core/quiet | 0.000001 | — | 0.000001 | — | 0.006149 | 0.000000 | 32.000000 | 5968.000000 | 3500.500000 | 0.000000 |
| adwin_schedule/core/noisy | 0.002130 | — | 0.002130 | — | 0.006149 | 67.000000 | 31.891006 | 5968.687500 | 2522.842650 | 0.008156 |
| adwin_schedule/core/switch_quiet | 0.004369 | 0.054302 | 0.000027 | 4.000000 | 0.006149 | 455.000000 | 31.650931 | 5968.000000 | 1107.425550 | 0.021981 |
| adwin_schedule/core/switch_noisy | 0.014711 | 0.154381 | 0.002566 | 36.312500 | 0.006149 | 444.000000 | 31.567381 | 5968.000000 | 1027.551025 | 0.027881 |
| adwin_schedule/noise_jump/noise_jump | 0.004367 | — | 0.004367 | — | 0.001931 | 206.000000 | 31.725069 | 5968.000000 | 1719.845200 | 0.019162 |
| adwin_schedule/drift/drift | 0.000502 | — | 0.000502 | — | 0.001390 | 2326.000000 | 26.837962 | 5968.000000 | 848.558400 | 0.366838 |
| adwin_schedule/exactly_quiet/exactly_quiet | 0.000000 | — | 0.000000 | — | 0.000167 | 0.000000 | 32.000000 | 5968.000000 | 3500.500000 | 0.000000 |
| adwin_schedule/mixed/increase_first | 0.009544 | 0.103298 | 0.001391 | 17.812500 | 0.004781 | 442.000000 | 31.606019 | 5968.000000 | 1073.040250 | 0.024706 |
| adwin_schedule/mixed/decrease_first | 0.010184 | 0.105435 | 0.001902 | 25.921875 | 0.004781 | 492.000000 | 31.574481 | 5968.000000 | 1049.340150 | 0.027119 |

Width counts retained observations, not physical storage. SGD uses exponential weights and has no literal window. True, jittered, dropped, added and observed schedules are distinguished by provenance in every record and never mix. Fast share is the post-burn fraction of predictions taken from the fast window.


## Measured execution time

| Stage | Family | Seconds |
| --- | --- | ---: |
| tuning | window | 0.73 |
| tuning | sgd | 0.89 |
| tuning | adwin | 4.49 |
| confirmation | window | 1.82 |
| confirmation | sgd | 0.48 |
| confirmation | adwin | 3.59 |
| confirmation | reference | 4.12 |
| confirmation | jitter_2 | 3.79 |
| confirmation | jitter_8 | 3.72 |
| confirmation | jitter_16 | 2.87 |
| confirmation | jitter_32 | 4.13 |
| confirmation | jitter_128 | 3.36 |
| confirmation | drop_10 | 3.93 |
| confirmation | drop_50 | 5.67 |
| confirmation | add_0005 | 4.15 |
| confirmation | add_0020 | 2.19 |
| confirmation | adwin_schedule | 3.20 |

Configuration budgets are equal, not CPU costs. Times exclude archive writes and share cached fixtures.

## Scope and reproduction

ADWIN2 is independently implemented from the paper: practical Eq.(3.1), five buckets per size, minimum subwindow5. Gaussian observations violate the bounded-input premise; no corresponding formal guarantee or library-release parity is claimed. All policies see unchanged raw observations.

Perturbed schedules are diagnostic: jittered/dropped/added times are evaluator-built from true times, not observable-derived. Only the ADWIN-schedule arm is deployable. No schedule outcome overrides the advancement gate. The tolerance curve authorizes no follow-up; the reading rules in the registration decide what follows.

Intervals resample whole seeds10000 times with seed115000. Finite menus and synthetic fixtures do not establish global optimizer superiority, population guarantees or general neural-memory utility. Every reached row and source is archived; prior studies remain intact.

`python check_v3_tolerance.py --evidence results/v3-tolerance --reproduce` regenerates every reached row and scientific manifest/summary at rtol1e-11/atol1e-13. `python report_v3_tolerance.py --check` verifies both generated reports.
