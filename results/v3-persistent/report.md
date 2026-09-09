# V3 persistent detector experiment

Disposition: **detector_negative**.

Four fixed detector policies; no hyperparameter selection. Calibration precedes fresh confirmation. All 24 candidate cells must pass before independent performance.

| Stage | Rows |
| --- | ---: |
| calibration | 64 |
| diagnostics | 128 |
| performance | 0 |

## Fixed policies and thresholds

| Policy | Configuration | Fixed threshold | Closed threshold |
| --- | --- | ---: | ---: |
| current | `{"lr": 0.004, "gain": 64.0, "beta2": 0.999}` | 0.21194271589472133 | 0.19560052134623715 |
| persistence | `{"lr": 0.004, "gain": 64.0, "beta2": 0.999}` | 0.15631722071536694 | 0.1519824470480801 |
| candidate | `{"lr": 0.004, "gain": 64.0, "beta2": 0.999}` | 0.4682240285231746 | 0.8161801210201912 |
| cusum | `{"lr": 0.004, "gain": 64.0, "beta2": 0.999}` | 0.32808257365743465 | 0.3014929352662185 |
| sgd | `{"lr": 0.035743040182210514}` | — | — |
| adam | `{"lr": 0.032, "beta2": 0.9999}` | — | — |
| single | `{"lr": 0.016, "gain": 1.0}` | — | — |
| constant | `{"lr": 0.004, "gain": 64.0, "beta2": 0.999}` | — | — |

## Detector: current — detector_negative

| Cell | Count/total | Rate | Seed-bootstrap 95% interval | Censored latency | Pass |
| --- | --- | ---: | --- | ---: | --- |
| fixed/quiet/blocks | 16/1600 | 0.01000 | [0.00500, 0.01625] | — | True |
| fixed/noisy/blocks | 13/1600 | 0.00813 | [0.00438, 0.01188] | — | True |
| fixed/switch_quiet/target_down | 32/32 | 1.00000 | [1.00000, 1.00000] | 2.969 | True |
| fixed/switch_quiet/target_up | 32/32 | 1.00000 | [1.00000, 1.00000] | 2.906 | True |
| fixed/switch_noisy/target_down | 32/32 | 1.00000 | [1.00000, 1.00000] | 6.375 | True |
| fixed/switch_noisy/target_up | 32/32 | 1.00000 | [1.00000, 1.00000] | 6.781 | True |
| fixed/noise_jump/noise_increase | 5/32 | 0.15625 | [0.03125, 0.28125] | 86.125 | False |
| fixed/noise_jump/noise_decrease | 0/32 | 0.00000 | [0.00000, 0.00000] | 100.000 | True |
| fixed/increase_first/target_down | 32/32 | 1.00000 | [1.00000, 1.00000] | 3.344 | True |
| fixed/increase_first/target_up | 32/32 | 1.00000 | [1.00000, 1.00000] | 5.719 | True |
| fixed/decrease_first/target_down | 32/32 | 1.00000 | [1.00000, 1.00000] | 5.562 | True |
| fixed/decrease_first/target_up | 32/32 | 1.00000 | [1.00000, 1.00000] | 3.719 | True |
| closed/quiet/blocks | 1/1600 | 0.00063 | [0.00000, 0.00187] | — | True |
| closed/noisy/blocks | 22/1600 | 0.01375 | [0.00750, 0.02063] | — | True |
| closed/switch_quiet/target_down | 32/32 | 1.00000 | [1.00000, 1.00000] | 2.219 | True |
| closed/switch_quiet/target_up | 32/32 | 1.00000 | [1.00000, 1.00000] | 2.125 | True |
| closed/switch_noisy/target_down | 32/32 | 1.00000 | [1.00000, 1.00000] | 5.844 | True |
| closed/switch_noisy/target_up | 32/32 | 1.00000 | [1.00000, 1.00000] | 6.500 | True |
| closed/noise_jump/noise_increase | 5/32 | 0.15625 | [0.03125, 0.28125] | 89.438 | False |
| closed/noise_jump/noise_decrease | 0/32 | 0.00000 | [0.00000, 0.00000] | 100.000 | True |
| closed/increase_first/target_down | 32/32 | 1.00000 | [1.00000, 1.00000] | 3.219 | True |
| closed/increase_first/target_up | 32/32 | 1.00000 | [1.00000, 1.00000] | 5.344 | True |
| closed/decrease_first/target_down | 32/32 | 1.00000 | [1.00000, 1.00000] | 5.250 | True |
| closed/decrease_first/target_up | 32/32 | 1.00000 | [1.00000, 1.00000] | 3.406 | True |

## Detector: persistence — detector_negative

| Cell | Count/total | Rate | Seed-bootstrap 95% interval | Censored latency | Pass |
| --- | --- | ---: | --- | ---: | --- |
| fixed/quiet/blocks | 13/1600 | 0.00813 | [0.00438, 0.01250] | — | True |
| fixed/noisy/blocks | 18/1600 | 0.01125 | [0.00625, 0.01688] | — | True |
| fixed/switch_quiet/target_down | 32/32 | 1.00000 | [1.00000, 1.00000] | 5.000 | True |
| fixed/switch_quiet/target_up | 32/32 | 1.00000 | [1.00000, 1.00000] | 5.000 | True |
| fixed/switch_noisy/target_down | 32/32 | 1.00000 | [1.00000, 1.00000] | 7.531 | True |
| fixed/switch_noisy/target_up | 32/32 | 1.00000 | [1.00000, 1.00000] | 8.031 | True |
| fixed/noise_jump/noise_increase | 4/32 | 0.12500 | [0.03125, 0.25000] | 89.094 | False |
| fixed/noise_jump/noise_decrease | 0/32 | 0.00000 | [0.00000, 0.00000] | 100.000 | True |
| fixed/increase_first/target_down | 32/32 | 1.00000 | [1.00000, 1.00000] | 5.312 | True |
| fixed/increase_first/target_up | 32/32 | 1.00000 | [1.00000, 1.00000] | 7.344 | True |
| fixed/decrease_first/target_down | 32/32 | 1.00000 | [1.00000, 1.00000] | 7.219 | True |
| fixed/decrease_first/target_up | 32/32 | 1.00000 | [1.00000, 1.00000] | 5.469 | True |
| closed/quiet/blocks | 13/1600 | 0.00813 | [0.00438, 0.01250] | — | True |
| closed/noisy/blocks | 21/1600 | 0.01313 | [0.00750, 0.01875] | — | True |
| closed/switch_quiet/target_down | 32/32 | 1.00000 | [1.00000, 1.00000] | 4.938 | True |
| closed/switch_quiet/target_up | 32/32 | 1.00000 | [1.00000, 1.00000] | 4.844 | True |
| closed/switch_noisy/target_down | 32/32 | 1.00000 | [1.00000, 1.00000] | 7.688 | True |
| closed/switch_noisy/target_up | 32/32 | 1.00000 | [1.00000, 1.00000] | 8.031 | True |
| closed/noise_jump/noise_increase | 4/32 | 0.12500 | [0.03125, 0.25000] | 89.094 | False |
| closed/noise_jump/noise_decrease | 0/32 | 0.00000 | [0.00000, 0.00000] | 100.000 | True |
| closed/increase_first/target_down | 32/32 | 1.00000 | [1.00000, 1.00000] | 5.281 | True |
| closed/increase_first/target_up | 32/32 | 1.00000 | [1.00000, 1.00000] | 7.188 | True |
| closed/decrease_first/target_down | 32/32 | 1.00000 | [1.00000, 1.00000] | 7.188 | True |
| closed/decrease_first/target_up | 32/32 | 1.00000 | [1.00000, 1.00000] | 5.375 | True |

## Detector: candidate — detector_negative

| Cell | Count/total | Rate | Seed-bootstrap 95% interval | Censored latency | Pass |
| --- | --- | ---: | --- | ---: | --- |
| fixed/quiet/blocks | 8/1600 | 0.00500 | [0.00125, 0.01000] | — | True |
| fixed/noisy/blocks | 14/1600 | 0.00875 | [0.00438, 0.01375] | — | True |
| fixed/switch_quiet/target_down | 32/32 | 1.00000 | [1.00000, 1.00000] | 10.062 | True |
| fixed/switch_quiet/target_up | 32/32 | 1.00000 | [1.00000, 1.00000] | 10.094 | True |
| fixed/switch_noisy/target_down | 32/32 | 1.00000 | [1.00000, 1.00000] | 12.750 | True |
| fixed/switch_noisy/target_up | 32/32 | 1.00000 | [1.00000, 1.00000] | 13.406 | True |
| fixed/noise_jump/noise_increase | 0/32 | 0.00000 | [0.00000, 0.00000] | 100.000 | True |
| fixed/noise_jump/noise_decrease | 0/32 | 0.00000 | [0.00000, 0.00000] | 100.000 | True |
| fixed/increase_first/target_down | 32/32 | 1.00000 | [1.00000, 1.00000] | 12.062 | True |
| fixed/increase_first/target_up | 32/32 | 1.00000 | [1.00000, 1.00000] | 11.688 | True |
| fixed/decrease_first/target_down | 32/32 | 1.00000 | [1.00000, 1.00000] | 11.562 | True |
| fixed/decrease_first/target_up | 32/32 | 1.00000 | [1.00000, 1.00000] | 12.094 | True |
| closed/quiet/blocks | 21/1600 | 0.01313 | [0.00813, 0.01813] | — | True |
| closed/noisy/blocks | 0/1600 | 0.00000 | [0.00000, 0.00000] | — | True |
| closed/switch_quiet/target_down | 30/32 | 0.93750 | [0.84375, 1.00000] | 34.125 | True |
| closed/switch_quiet/target_up | 30/32 | 0.93750 | [0.84375, 1.00000] | 33.000 | True |
| closed/switch_noisy/target_down | 1/32 | 0.03125 | [0.00000, 0.09375] | 97.406 | False |
| closed/switch_noisy/target_up | 1/32 | 0.03125 | [0.00000, 0.09375] | 97.344 | False |
| closed/noise_jump/noise_increase | 0/32 | 0.00000 | [0.00000, 0.00000] | 100.000 | True |
| closed/noise_jump/noise_decrease | 0/32 | 0.00000 | [0.00000, 0.00000] | 100.000 | True |
| closed/increase_first/target_down | 1/32 | 0.03125 | [0.00000, 0.09375] | 96.906 | False |
| closed/increase_first/target_up | 16/32 | 0.50000 | [0.31250, 0.65625] | 58.781 | False |
| closed/decrease_first/target_down | 22/32 | 0.68750 | [0.53125, 0.84375] | 42.781 | False |
| closed/decrease_first/target_up | 0/32 | 0.00000 | [0.00000, 0.00000] | 100.000 | False |

## Detector: cusum — detector_negative

| Cell | Count/total | Rate | Seed-bootstrap 95% interval | Censored latency | Pass |
| --- | --- | ---: | --- | ---: | --- |
| fixed/quiet/blocks | 15/1600 | 0.00938 | [0.00438, 0.01500] | — | True |
| fixed/noisy/blocks | 19/1600 | 0.01188 | [0.00688, 0.01750] | — | True |
| fixed/switch_quiet/target_down | 32/32 | 1.00000 | [1.00000, 1.00000] | 2.188 | True |
| fixed/switch_quiet/target_up | 32/32 | 1.00000 | [1.00000, 1.00000] | 2.156 | True |
| fixed/switch_noisy/target_down | 32/32 | 1.00000 | [1.00000, 1.00000] | 6.562 | True |
| fixed/switch_noisy/target_up | 32/32 | 1.00000 | [1.00000, 1.00000] | 7.062 | True |
| fixed/noise_jump/noise_increase | 9/32 | 0.28125 | [0.12500, 0.43750] | 73.156 | False |
| fixed/noise_jump/noise_decrease | 0/32 | 0.00000 | [0.00000, 0.00000] | 100.000 | True |
| fixed/increase_first/target_down | 32/32 | 1.00000 | [1.00000, 1.00000] | 2.531 | True |
| fixed/increase_first/target_up | 32/32 | 1.00000 | [1.00000, 1.00000] | 6.188 | True |
| fixed/decrease_first/target_down | 32/32 | 1.00000 | [1.00000, 1.00000] | 5.562 | True |
| fixed/decrease_first/target_up | 32/32 | 1.00000 | [1.00000, 1.00000] | 3.031 | True |
| closed/quiet/blocks | 4/1600 | 0.00250 | [0.00063, 0.00500] | — | True |
| closed/noisy/blocks | 30/1600 | 0.01875 | [0.01312, 0.02500] | — | True |
| closed/switch_quiet/target_down | 32/32 | 1.00000 | [1.00000, 1.00000] | 1.906 | True |
| closed/switch_quiet/target_up | 32/32 | 1.00000 | [1.00000, 1.00000] | 1.594 | True |
| closed/switch_noisy/target_down | 32/32 | 1.00000 | [1.00000, 1.00000] | 6.094 | True |
| closed/switch_noisy/target_up | 32/32 | 1.00000 | [1.00000, 1.00000] | 6.375 | True |
| closed/noise_jump/noise_increase | 8/32 | 0.25000 | [0.12500, 0.40625] | 75.750 | False |
| closed/noise_jump/noise_decrease | 0/32 | 0.00000 | [0.00000, 0.00000] | 100.000 | True |
| closed/increase_first/target_down | 32/32 | 1.00000 | [1.00000, 1.00000] | 2.219 | True |
| closed/increase_first/target_up | 32/32 | 1.00000 | [1.00000, 1.00000] | 5.250 | True |
| closed/decrease_first/target_down | 32/32 | 1.00000 | [1.00000, 1.00000] | 5.031 | True |
| closed/decrease_first/target_up | 32/32 | 1.00000 | [1.00000, 1.00000] | 2.719 | True |

## All descriptive detector conditions

| Arm/mode/fixture/coordinate | Finite seeds | Startup gate | Settled gate | Point alarms | Block alarms |
| --- | ---: | ---: | ---: | ---: | ---: |
| current/fixed/core/quiet | 32 | 0.034970 | 0.019242 | 0.000131 | 0.010000 |
| current/fixed/core/noisy | 32 | 0.033277 | 0.019098 | 0.000156 | 0.008125 |
| current/fixed/core/switch_quiet | 32 | 0.034004 | 0.048972 | 0.060169 | 0.104375 |
| current/fixed/core/switch_noisy | 32 | 0.035958 | 0.032792 | 0.031481 | 0.086250 |
| current/fixed/noise_jump/noise_jump | 32 | 0.037614 | 0.017564 | 0.000325 | 0.013750 |
| current/fixed/drift/drift | 32 | 0.032458 | 0.156367 | 0.404094 | 0.440625 |
| current/fixed/exactly_quiet/exactly_quiet | 32 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| current/fixed/mixed/increase_first | 32 | 0.033231 | 0.038572 | 0.043112 | 0.090625 |
| current/fixed/mixed/decrease_first | 32 | 0.029745 | 0.038338 | 0.042862 | 0.090625 |
| current/closed/core/quiet | 32 | 0.092271 | 0.018350 | 0.000006 | 0.000625 |
| current/closed/core/noisy | 32 | 0.035395 | 0.019543 | 0.000225 | 0.013750 |
| current/closed/core/switch_quiet | 32 | 0.092040 | 0.018239 | 0.002737 | 0.043750 |
| current/closed/core/switch_noisy | 32 | 0.040031 | 0.021646 | 0.005750 | 0.056250 |
| current/closed/noise_jump/noise_jump | 32 | 0.092077 | 0.018132 | 0.000269 | 0.014375 |
| current/closed/drift/drift | 32 | 0.092672 | 0.018366 | 0.000006 | 0.000625 |
| current/closed/exactly_quiet/exactly_quiet | 32 | 0.086488 | 0.000001 | 0.000000 | 0.000000 |
| current/closed/mixed/increase_first | 32 | 0.091978 | 0.020463 | 0.004581 | 0.050625 |
| current/closed/mixed/decrease_first | 32 | 0.036337 | 0.020796 | 0.005856 | 0.053750 |
| persistence/fixed/core/quiet | 32 | 0.021390 | 0.008438 | 0.000181 | 0.008125 |
| persistence/fixed/core/noisy | 32 | 0.019660 | 0.008343 | 0.000237 | 0.011250 |
| persistence/fixed/core/switch_quiet | 32 | 0.020450 | 0.039889 | 0.071256 | 0.113750 |
| persistence/fixed/core/switch_noisy | 32 | 0.022460 | 0.020749 | 0.035013 | 0.091250 |
| persistence/fixed/noise_jump/noise_jump | 32 | 0.024189 | 0.007647 | 0.000487 | 0.013125 |
| persistence/fixed/drift/drift | 32 | 0.019011 | 0.141402 | 0.410206 | 0.445000 |
| persistence/fixed/exactly_quiet/exactly_quiet | 32 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| persistence/fixed/mixed/increase_first | 32 | 0.019961 | 0.028026 | 0.050688 | 0.099375 |
| persistence/fixed/mixed/decrease_first | 32 | 0.016930 | 0.027830 | 0.050469 | 0.100625 |
| persistence/closed/core/quiet | 32 | 0.084757 | 0.009235 | 0.000119 | 0.008125 |
| persistence/closed/core/noisy | 32 | 0.021584 | 0.008707 | 0.000313 | 0.013125 |
| persistence/closed/core/switch_quiet | 32 | 0.084637 | 0.009751 | 0.005338 | 0.058125 |
| persistence/closed/core/switch_noisy | 32 | 0.026387 | 0.010707 | 0.006644 | 0.054375 |
| persistence/closed/noise_jump/noise_jump | 32 | 0.084430 | 0.008300 | 0.000313 | 0.013750 |
| persistence/closed/drift/drift | 32 | 0.085026 | 0.009362 | 0.000069 | 0.005625 |
| persistence/closed/exactly_quiet/exactly_quiet | 32 | 0.085658 | 0.000001 | 0.000000 | 0.000000 |
| persistence/closed/mixed/increase_first | 32 | 0.084522 | 0.010775 | 0.005350 | 0.052500 |
| persistence/closed/mixed/decrease_first | 32 | 0.022125 | 0.010855 | 0.006112 | 0.054375 |
| candidate/fixed/core/quiet | 32 | 0.026604 | 0.031489 | 0.000106 | 0.005000 |
| candidate/fixed/core/noisy | 32 | 0.026708 | 0.031390 | 0.000213 | 0.008750 |
| candidate/fixed/core/switch_quiet | 32 | 0.027310 | 0.071923 | 0.048200 | 0.091875 |
| candidate/fixed/core/switch_noisy | 32 | 0.025305 | 0.050753 | 0.024606 | 0.073750 |
| candidate/fixed/noise_jump/noise_jump | 32 | 0.024624 | 0.031802 | 0.000250 | 0.008125 |
| candidate/fixed/drift/drift | 32 | 0.026287 | 0.255885 | 0.332156 | 0.430625 |
| candidate/fixed/exactly_quiet/exactly_quiet | 32 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| candidate/fixed/mixed/increase_first | 32 | 0.026732 | 0.060930 | 0.035638 | 0.082500 |
| candidate/fixed/mixed/decrease_first | 32 | 0.026396 | 0.060389 | 0.035394 | 0.083125 |
| candidate/closed/core/quiet | 32 | 0.124526 | 0.084709 | 0.000150 | 0.013125 |
| candidate/closed/core/noisy | 32 | 0.035232 | 0.034381 | 0.000000 | 0.000000 |
| candidate/closed/core/switch_quiet | 32 | 0.124340 | 0.074769 | 0.001131 | 0.051250 |
| candidate/closed/core/switch_noisy | 32 | 0.032624 | 0.038103 | 0.000019 | 0.001250 |
| candidate/closed/noise_jump/noise_jump | 32 | 0.122788 | 0.047392 | 0.000000 | 0.000000 |
| candidate/closed/drift/drift | 32 | 0.124489 | 0.090902 | 0.000188 | 0.016875 |
| candidate/closed/exactly_quiet/exactly_quiet | 32 | 0.109419 | 0.000000 | 0.000000 | 0.000000 |
| candidate/closed/mixed/increase_first | 32 | 0.124931 | 0.058040 | 0.000225 | 0.015000 |
| candidate/closed/mixed/decrease_first | 32 | 0.035615 | 0.045543 | 0.000237 | 0.013750 |
| cusum/fixed/core/quiet | 32 | 0.042447 | 0.050406 | 0.000287 | 0.009375 |
| cusum/fixed/core/noisy | 32 | 0.043230 | 0.050590 | 0.000500 | 0.011875 |
| cusum/fixed/core/switch_quiet | 32 | 0.043488 | 0.206206 | 0.200200 | 0.244375 |
| cusum/fixed/core/switch_noisy | 32 | 0.042585 | 0.110111 | 0.091194 | 0.134375 |
| cusum/fixed/noise_jump/noise_jump | 32 | 0.042112 | 0.049631 | 0.000700 | 0.016875 |
| cusum/fixed/drift/drift | 32 | 0.043049 | 0.777394 | 0.791688 | 0.804375 |
| cusum/fixed/exactly_quiet/exactly_quiet | 32 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| cusum/fixed/mixed/increase_first | 32 | 0.043384 | 0.125875 | 0.110200 | 0.153125 |
| cusum/fixed/mixed/decrease_first | 32 | 0.043407 | 0.124236 | 0.108144 | 0.148750 |
| cusum/closed/core/quiet | 32 | 0.333219 | 0.050151 | 0.000038 | 0.002500 |
| cusum/closed/core/noisy | 32 | 0.050368 | 0.050778 | 0.000606 | 0.018750 |
| cusum/closed/core/switch_quiet | 32 | 0.333850 | 0.051131 | 0.003700 | 0.045000 |
| cusum/closed/core/switch_noisy | 32 | 0.049843 | 0.054751 | 0.008875 | 0.058750 |
| cusum/closed/noise_jump/noise_jump | 32 | 0.332995 | 0.067217 | 0.026369 | 0.059375 |
| cusum/closed/drift/drift | 32 | 0.333949 | 0.050381 | 0.000019 | 0.001250 |
| cusum/closed/exactly_quiet/exactly_quiet | 32 | 0.317578 | 0.000000 | 0.000000 | 0.000000 |
| cusum/closed/mixed/increase_first | 32 | 0.332736 | 0.101429 | 0.072813 | 0.141250 |
| cusum/closed/mixed/decrease_first | 32 | 0.053821 | 0.103250 | 0.077100 | 0.141875 |

## Interpretation and limits

Only stationary core coordinates use block alarm rates as false alarms. Mixed increase_first pairs target-down with noise increase and target-up with noise decrease; decrease_first reverses that pairing. Each direction remains separate. Exactly quiet and drift are descriptive.

Intervals resample whole seeds (10,000 resamples, seed 55000). Rate thresholds are point screens, not population guarantees. Four overlapping signed scores are correlated, not four independent pieces of evidence. The standardized mean score is not a calibrated p-value. The CUSUM reference uses moving estimates and empirical calibration, not known-parameter textbook guarantees.

All settings are transferred or fixed before data. This tests specified finite policies, not globally optimal tuning or optimizer-wide superiority. Passing detection alone establishes no learning gain. A failure closes this experiment; a positive performance result warrants only a separately registered agent experiment. No existing result or default is changed.

Reproduce every reached row and decision with `python check_v3_persistent.py --evidence results/v3-persistent --reproduce`. Verify this report with `python report_v3_persistent.py --check`. Only timings and regenerated scientific-input hashes are excluded from numerical reproduction.
