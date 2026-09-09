# V3 bounded burst-controller experiment

Disposition: **learning_negative**.

| Stage | Rows |
| --- | ---: |
| tuning | 480 |
| confirmation | 224 |

Frozen strict detector threshold: 0.4690234346011377.

## Finite-menu tuning

All searched families: 12 configurations × 8 seeds × 5 fixtures. Objective: half primary post-switch MSE plus half mean of 14 retention metrics.

| Family | Index | Configuration | Tuning objective | Menu endpoint fields |
| --- | ---: | --- | ---: | --- |
| burst | 8 | `{"lr": 0.032, "factor": 2.0, "duration": 16, "beta2": 0.999}` | 0.176564 | lr, factor, duration |
| oracle | 10 | `{"lr": 0.032, "factor": 8.0, "duration": 16, "beta2": 0.999}` | 0.094467 | lr, factor, duration |
| continuous | 9 | `{"lr": 0.032, "gain": 8.0, "beta2": 0.999}` | 0.182309 | lr |
| adam | 10 | `{"lr": 0.128, "beta2": 0.999}` | 0.138365 | lr, beta2 |
| sgd | 8 | `{"lr": 0.128}` | 0.085671 | none |

Endpoints are reported, not expanded: these are fixed menus, not global optima. oracle_matched and random use burst settings exactly, with no additional tuning.

Frozen random opportunity probability: **0.000401142**, from 167 candidate starts / 421488 tuning coordinate-updates. Expected pooled frequency is matched; realized per-condition counts and movement are not.

## Independent primary performance

| Policy | Finite seeds | Primary MSE | 95% interval |
| --- | ---: | ---: | --- |
| burst | 32 | 0.261323 | [0.25682690830806404, 0.2662180741139454] |
| oracle | 32 | 0.146911 | [0.14140958940055454, 0.15282939683064387] |
| continuous | 32 | 0.277312 | [0.2707410306878521, 0.28387481098297607] |
| adam | 32 | 0.194492 | [0.18874852589670046, 0.2002032172729102] |
| sgd | 32 | 0.119910 | [0.11720413774038466, 0.12272957060077358] |
| oracle_matched | 32 | 0.218205 | [0.2137616507090037, 0.22312282576460327] |
| random | 32 | 0.297185 | [0.29117167181799647, 0.30356198274940677] |

## burst: learning_negative

All 60 candidate comparisons are required; no selected success overrides a failed cell.

| Contrast | Control | Policy | Delta | 95% interval | Pass |
| --- | ---: | ---: | ---: | --- | --- |
| adam/primary | 0.194492 | 0.261323 | 0.066831 | [0.062226, 0.071490] | False |
| adam/quiet | 0.002380 | 0.000646 | -0.001734 | [-0.001778, -0.001691] | True |
| adam/noisy | 0.060836 | 0.015464 | -0.045372 | [-0.046744, -0.044019] | True |
| adam/switch_quiet | 0.098946 | 0.158330 | 0.059385 | [0.057859, 0.061031] | False |
| adam/switch_noisy | 0.233594 | 0.338489 | 0.104896 | [0.093313, 0.116757] | False |
| adam/noise_jump | 0.039163 | 0.010452 | -0.028710 | [-0.030049, -0.027426] | True |
| adam/drift | 0.002372 | 0.000682 | -0.001690 | [-0.001728, -0.001652] | True |
| adam/exactly_quiet | 0.000000 | 0.000000 | 0.000000 | [0.000000, 0.000000] | True |
| adam/noise_jump/noise_increase | 0.204258 | 0.051143 | -0.153115 | [-0.176404, -0.132080] | True |
| adam/noise_jump/noise_decrease | 0.005318 | 0.003366 | -0.001951 | [-0.003335, -0.000650] | True |
| adam/drift/drift | 0.002406 | 0.000707 | -0.001699 | [-0.001758, -0.001643] | True |
| adam/mixed/increase_first/post_mse | 0.225226 | 0.255441 | 0.030216 | [0.019591, 0.041078] | False |
| adam/mixed/increase_first/stable_mse | 0.032145 | 0.008006 | -0.024139 | [-0.025468, -0.022805] | True |
| adam/mixed/decrease_first/post_mse | 0.220201 | 0.293030 | 0.072829 | [0.063233, 0.082287] | False |
| adam/mixed/decrease_first/stable_mse | 0.043130 | 0.010618 | -0.032512 | [-0.033688, -0.031385] | True |
| sgd/primary | 0.119910 | 0.261323 | 0.141413 | [0.137831, 0.145210] | False |
| sgd/quiet | 0.000170 | 0.000646 | 0.000476 | [0.000464, 0.000489] | True |
| sgd/noisy | 0.067354 | 0.015464 | -0.051890 | [-0.052679, -0.051111] | True |
| sgd/switch_quiet | 0.083470 | 0.158330 | 0.074861 | [0.073857, 0.075861] | False |
| sgd/switch_noisy | 0.151504 | 0.338489 | 0.186985 | [0.174304, 0.199833] | False |
| sgd/noise_jump | 0.028948 | 0.010452 | -0.018495 | [-0.019371, -0.017641] | True |
| sgd/drift | 0.000200 | 0.000682 | 0.000482 | [0.000469, 0.000495] | True |
| sgd/exactly_quiet | 0.000000 | 0.000000 | -0.000000 | [-0.000000, -0.000000] | True |
| sgd/noise_jump/noise_increase | 0.067688 | 0.051143 | -0.016545 | [-0.019657, -0.013625] | True |
| sgd/noise_jump/noise_decrease | 0.002358 | 0.003366 | 0.001008 | [-0.000105, 0.002364] | False |
| sgd/drift/drift | 0.000235 | 0.000707 | 0.000472 | [0.000449, 0.000496] | True |
| sgd/mixed/increase_first/post_mse | 0.123904 | 0.255441 | 0.131537 | [0.123608, 0.139685] | False |
| sgd/mixed/increase_first/stable_mse | 0.027700 | 0.008006 | -0.019694 | [-0.020506, -0.018854] | True |
| sgd/mixed/decrease_first/post_mse | 0.120763 | 0.293030 | 0.172267 | [0.165359, 0.178895] | False |
| sgd/mixed/decrease_first/stable_mse | 0.040601 | 0.010618 | -0.029983 | [-0.030804, -0.029161] | True |
| continuous/primary | 0.277312 | 0.261323 | -0.015989 | [-0.020962, -0.010850] | False |
| continuous/quiet | 0.000718 | 0.000646 | -0.000072 | [-0.000080, -0.000064] | True |
| continuous/noisy | 0.030672 | 0.015464 | -0.015208 | [-0.016202, -0.014197] | True |
| continuous/switch_quiet | 0.200704 | 0.158330 | -0.042374 | [-0.045364, -0.039046] | True |
| continuous/switch_noisy | 0.307798 | 0.338489 | 0.030691 | [0.015927, 0.044413] | False |
| continuous/noise_jump | 0.020018 | 0.010452 | -0.009566 | [-0.010638, -0.008597] | True |
| continuous/drift | 0.001715 | 0.000682 | -0.001033 | [-0.001065, -0.001001] | True |
| continuous/exactly_quiet | 0.000000 | 0.000000 | 0.000000 | [0.000000, 0.000000] | True |
| continuous/noise_jump/noise_increase | 0.085701 | 0.051143 | -0.034558 | [-0.047663, -0.024166] | True |
| continuous/noise_jump/noise_decrease | 0.004573 | 0.003366 | -0.001207 | [-0.002192, -0.000414] | True |
| continuous/drift/drift | 0.003145 | 0.000707 | -0.002438 | [-0.002543, -0.002332] | True |
| continuous/mixed/increase_first/post_mse | 0.300819 | 0.255441 | -0.045378 | [-0.055143, -0.034743] | True |
| continuous/mixed/increase_first/stable_mse | 0.015958 | 0.008006 | -0.007952 | [-0.008780, -0.007151] | True |
| continuous/mixed/decrease_first/post_mse | 0.299925 | 0.293030 | -0.006895 | [-0.018663, 0.004063] | True |
| continuous/mixed/decrease_first/stable_mse | 0.021027 | 0.010618 | -0.010409 | [-0.011303, -0.009637] | True |
| random/primary | 0.297185 | 0.261323 | -0.035862 | [-0.038527, -0.032953] | True |
| random/quiet | 0.000650 | 0.000646 | -0.000004 | [-0.000006, -0.000002] | True |
| random/noisy | 0.015487 | 0.015464 | -0.000023 | [-0.000148, 0.000110] | True |
| random/switch_quiet | 0.134337 | 0.158330 | 0.023993 | [0.023246, 0.024474] | False |
| random/switch_noisy | 0.428427 | 0.338489 | -0.089937 | [-0.096684, -0.082093] | True |
| random/noise_jump | 0.010416 | 0.010452 | 0.000037 | [-0.000051, 0.000140] | True |
| random/drift | 0.000667 | 0.000682 | 0.000015 | [0.000009, 0.000021] | True |
| random/exactly_quiet | 0.000000 | 0.000000 | -0.000000 | [-0.000000, 0.000000] | True |
| random/noise_jump/noise_increase | 0.051606 | 0.051143 | -0.000464 | [-0.001253, 0.000017] | True |
| random/noise_jump/noise_decrease | 0.003347 | 0.003366 | 0.000019 | [-0.000002, 0.000049] | True |
| random/drift/drift | 0.000670 | 0.000707 | 0.000038 | [0.000026, 0.000050] | True |
| random/mixed/increase_first/post_mse | 0.288719 | 0.255441 | -0.033277 | [-0.037437, -0.028154] | True |
| random/mixed/increase_first/stable_mse | 0.008085 | 0.008006 | -0.000079 | [-0.000166, -0.000016] | True |
| random/mixed/decrease_first/post_mse | 0.337256 | 0.293030 | -0.044227 | [-0.050717, -0.037014] | True |
| random/mixed/decrease_first/stable_mse | 0.010602 | 0.010618 | 0.000016 | [-0.000086, 0.000129] | True |

## oracle: oracle_negative

Candidate alone decides advancement. Both oracle arms are privileged diagnostics.

| Contrast | Control | Policy | Delta | 95% interval | Pass |
| --- | ---: | ---: | ---: | --- | --- |
| adam/primary | 0.194492 | 0.146911 | -0.047581 | [-0.053509, -0.041694] | True |
| adam/quiet | 0.002380 | 0.000646 | -0.001734 | [-0.001778, -0.001691] | True |
| adam/noisy | 0.060836 | 0.015364 | -0.045471 | [-0.046846, -0.044106] | True |
| adam/switch_quiet | 0.098946 | 0.085408 | -0.013537 | [-0.015094, -0.011978] | True |
| adam/switch_noisy | 0.233594 | 0.179078 | -0.054516 | [-0.068853, -0.039593] | True |
| adam/noise_jump | 0.039163 | 0.010351 | -0.028811 | [-0.030172, -0.027519] | True |
| adam/drift | 0.002372 | 0.000663 | -0.001709 | [-0.001747, -0.001670] | True |
| adam/exactly_quiet | 0.000000 | 0.000000 | 0.000000 | [0.000000, 0.000000] | True |
| adam/noise_jump/noise_increase | 0.204258 | 0.051143 | -0.153115 | [-0.176404, -0.132080] | True |
| adam/noise_jump/noise_decrease | 0.005318 | 0.003366 | -0.001951 | [-0.003335, -0.000650] | True |
| adam/drift/drift | 0.002406 | 0.000665 | -0.001741 | [-0.001803, -0.001683] | True |
| adam/mixed/increase_first/post_mse | 0.225226 | 0.171450 | -0.053776 | [-0.068905, -0.036784] | True |
| adam/mixed/increase_first/stable_mse | 0.032145 | 0.008018 | -0.024127 | [-0.025460, -0.022793] | True |
| adam/mixed/decrease_first/post_mse | 0.220201 | 0.151707 | -0.068495 | [-0.077431, -0.060273] | True |
| adam/mixed/decrease_first/stable_mse | 0.043130 | 0.010595 | -0.032535 | [-0.033736, -0.031383] | True |
| sgd/primary | 0.119910 | 0.146911 | 0.027000 | [0.021134, 0.033082] | False |
| sgd/quiet | 0.000170 | 0.000646 | 0.000476 | [0.000465, 0.000488] | True |
| sgd/noisy | 0.067354 | 0.015364 | -0.051989 | [-0.052782, -0.051214] | True |
| sgd/switch_quiet | 0.083470 | 0.085408 | 0.001938 | [0.000731, 0.003085] | True |
| sgd/switch_noisy | 0.151504 | 0.179078 | 0.027574 | [0.013776, 0.042338] | False |
| sgd/noise_jump | 0.028948 | 0.010351 | -0.018597 | [-0.019494, -0.017730] | True |
| sgd/drift | 0.000200 | 0.000663 | 0.000463 | [0.000450, 0.000476] | True |
| sgd/exactly_quiet | 0.000000 | 0.000000 | -0.000000 | [-0.000000, -0.000000] | True |
| sgd/noise_jump/noise_increase | 0.067688 | 0.051143 | -0.016545 | [-0.019657, -0.013625] | True |
| sgd/noise_jump/noise_decrease | 0.002358 | 0.003366 | 0.001008 | [-0.000105, 0.002364] | False |
| sgd/drift/drift | 0.000235 | 0.000665 | 0.000430 | [0.000410, 0.000450] | True |
| sgd/mixed/increase_first/post_mse | 0.123904 | 0.171450 | 0.047546 | [0.030987, 0.068127] | False |
| sgd/mixed/increase_first/stable_mse | 0.027700 | 0.008018 | -0.019682 | [-0.020497, -0.018840] | True |
| sgd/mixed/decrease_first/post_mse | 0.120763 | 0.151707 | 0.030943 | [0.022786, 0.039893] | False |
| sgd/mixed/decrease_first/stable_mse | 0.040601 | 0.010595 | -0.030006 | [-0.030840, -0.029167] | True |

## oracle_matched: oracle_negative

Candidate alone decides advancement. Both oracle arms are privileged diagnostics.

| Contrast | Control | Policy | Delta | 95% interval | Pass |
| --- | ---: | ---: | ---: | --- | --- |
| adam/primary | 0.194492 | 0.218205 | 0.023713 | [0.019658, 0.027978] | False |
| adam/quiet | 0.002380 | 0.000646 | -0.001734 | [-0.001778, -0.001691] | True |
| adam/noisy | 0.060836 | 0.015364 | -0.045471 | [-0.046846, -0.044106] | True |
| adam/switch_quiet | 0.098946 | 0.111368 | 0.012423 | [0.011054, 0.013893] | False |
| adam/switch_noisy | 0.233594 | 0.304619 | 0.071026 | [0.060041, 0.082336] | False |
| adam/noise_jump | 0.039163 | 0.010351 | -0.028811 | [-0.030172, -0.027519] | True |
| adam/drift | 0.002372 | 0.000663 | -0.001709 | [-0.001747, -0.001670] | True |
| adam/exactly_quiet | 0.000000 | 0.000000 | 0.000000 | [0.000000, 0.000000] | True |
| adam/noise_jump/noise_increase | 0.204258 | 0.051143 | -0.153115 | [-0.176404, -0.132080] | True |
| adam/noise_jump/noise_decrease | 0.005318 | 0.003366 | -0.001951 | [-0.003335, -0.000650] | True |
| adam/drift/drift | 0.002406 | 0.000665 | -0.001741 | [-0.001803, -0.001683] | True |
| adam/mixed/increase_first/post_mse | 0.225226 | 0.217981 | -0.007245 | [-0.016400, 0.002088] | True |
| adam/mixed/increase_first/stable_mse | 0.032145 | 0.008029 | -0.024116 | [-0.025449, -0.022781] | True |
| adam/mixed/decrease_first/post_mse | 0.220201 | 0.238850 | 0.018648 | [0.010238, 0.027009] | False |
| adam/mixed/decrease_first/stable_mse | 0.043130 | 0.010571 | -0.032559 | [-0.033761, -0.031405] | True |
| sgd/primary | 0.119910 | 0.218205 | 0.098294 | [0.094967, 0.101727] | False |
| sgd/quiet | 0.000170 | 0.000646 | 0.000476 | [0.000465, 0.000488] | True |
| sgd/noisy | 0.067354 | 0.015364 | -0.051989 | [-0.052782, -0.051214] | True |
| sgd/switch_quiet | 0.083470 | 0.111368 | 0.027898 | [0.027035, 0.028724] | False |
| sgd/switch_noisy | 0.151504 | 0.304619 | 0.153115 | [0.141290, 0.165389] | False |
| sgd/noise_jump | 0.028948 | 0.010351 | -0.018597 | [-0.019494, -0.017730] | True |
| sgd/drift | 0.000200 | 0.000663 | 0.000463 | [0.000450, 0.000476] | True |
| sgd/exactly_quiet | 0.000000 | 0.000000 | -0.000000 | [-0.000000, -0.000000] | True |
| sgd/noise_jump/noise_increase | 0.067688 | 0.051143 | -0.016545 | [-0.019657, -0.013625] | True |
| sgd/noise_jump/noise_decrease | 0.002358 | 0.003366 | 0.001008 | [-0.000105, 0.002364] | False |
| sgd/drift/drift | 0.000235 | 0.000665 | 0.000430 | [0.000410, 0.000450] | True |
| sgd/mixed/increase_first/post_mse | 0.123904 | 0.217981 | 0.094077 | [0.087002, 0.101230] | False |
| sgd/mixed/increase_first/stable_mse | 0.027700 | 0.008029 | -0.019671 | [-0.020482, -0.018828] | True |
| sgd/mixed/decrease_first/post_mse | 0.120763 | 0.238850 | 0.118086 | [0.112265, 0.123947] | False |
| sgd/mixed/decrease_first/stable_mse | 0.040601 | 0.010571 | -0.030030 | [-0.030865, -0.029190] | True |

## Raw detector diagnostic: detector_pass

Twelve cells, one signal. These diagnostics do not veto or establish learning performance.

| Cell | Count/total | Rate | Censored latency | Pass |
| --- | --- | ---: | ---: | --- |
| core/quiet/blocks | 13/1600 | 0.008125 | — | True |
| core/noisy/blocks | 8/1600 | 0.005000 | — | True |
| core/switch_quiet/target_down | 32/32 | 1.000000 | 10.031250 | True |
| core/switch_quiet/target_up | 32/32 | 1.000000 | 10.125000 | True |
| core/switch_noisy/target_down | 32/32 | 1.000000 | 12.093750 | True |
| core/switch_noisy/target_up | 32/32 | 1.000000 | 12.843750 | True |
| mixed/increase_first/target_down | 32/32 | 1.000000 | 12.187500 | True |
| mixed/increase_first/target_up | 32/32 | 1.000000 | 12.312500 | True |
| mixed/decrease_first/target_down | 32/32 | 1.000000 | 11.281250 | True |
| mixed/decrease_first/target_up | 32/32 | 1.000000 | 12.218750 | True |
| noise_jump/noise_jump/noise_increase | 0/32 | 0.000000 | 100.000000 | True |
| noise_jump/noise_jump/noise_decrease | 0/32 | 0.000000 | 100.000000 | True |

## Absolute errors and actual activity

| Policy/fixture/coordinate | Excess MSE | Post MSE | Stable MSE | Recovery latency | Mean vector update norm | Total starts | Mean active updates | Duty |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| burst/core/quiet | 0.000646 | — | 0.000646 | — | 0.012958 | 14.000000 | 7.000000 | 0.001196 |
| burst/core/noisy | 0.015464 | — | 0.015464 | — | 0.012958 | 10.000000 | 5.000000 | 0.000854 |
| burst/core/switch_quiet | 0.013007 | 0.158330 | 0.000371 | 30.109375 | 0.012958 | 78.000000 | 39.000000 | 0.006662 |
| burst/core/switch_noisy | 0.041525 | 0.338489 | 0.015702 | 42.578125 | 0.012958 | 96.000000 | 47.937500 | 0.008189 |
| burst/noise_jump/noise_jump | 0.010452 | — | 0.010452 | — | 0.004326 | 15.000000 | 7.500000 | 0.001281 |
| burst/drift/drift | 0.000682 | — | 0.000682 | — | 0.004587 | 346.000000 | 173.000000 | 0.029552 |
| burst/exactly_quiet/exactly_quiet | 0.000000 | — | 0.000000 | — | 0.000187 | 0.000000 | 0.000000 | 0.000000 |
| burst/mixed/increase_first | 0.027801 | 0.255441 | 0.008006 | 38.937500 | 0.009019 | 84.000000 | 42.000000 | 0.007175 |
| burst/mixed/decrease_first | 0.033211 | 0.293030 | 0.010618 | 46.375000 | 0.009019 | 86.000000 | 43.000000 | 0.007345 |
| oracle/core/quiet | 0.000646 | — | 0.000646 | — | 0.014113 | 0.000000 | 0.000000 | 0.000000 |
| oracle/core/noisy | 0.015364 | — | 0.015364 | — | 0.014113 | 0.000000 | 0.000000 | 0.000000 |
| oracle/core/switch_quiet | 0.007230 | 0.085408 | 0.000432 | 19.109375 | 0.014113 | 64.000000 | 32.000000 | 0.005466 |
| oracle/core/switch_noisy | 0.028718 | 0.179078 | 0.015643 | 57.484375 | 0.014113 | 64.000000 | 32.000000 | 0.005466 |
| oracle/noise_jump/noise_jump | 0.010351 | — | 0.010351 | — | 0.004316 | 0.000000 | 0.000000 | 0.000000 |
| oracle/drift/drift | 0.000663 | — | 0.000663 | — | 0.004468 | 0.000000 | 0.000000 | 0.000000 |
| oracle/exactly_quiet/exactly_quiet | 0.000000 | — | 0.000000 | — | 0.000187 | 0.000000 | 0.000000 | 0.000000 |
| oracle/mixed/increase_first | 0.021092 | 0.171450 | 0.008018 | 47.968750 | 0.009993 | 64.000000 | 32.000000 | 0.005466 |
| oracle/mixed/decrease_first | 0.021884 | 0.151707 | 0.010595 | 43.343750 | 0.009993 | 64.000000 | 32.000000 | 0.005466 |
| continuous/core/quiet | 0.000718 | — | 0.000718 | — | 0.019957 | 0.000000 | 0.000000 | 0.000000 |
| continuous/core/noisy | 0.030672 | — | 0.030672 | — | 0.019957 | 0.000000 | 0.000000 | 0.000000 |
| continuous/core/switch_quiet | 0.016427 | 0.200704 | 0.000402 | 52.640625 | 0.019957 | 0.000000 | 0.000000 | 0.000000 |
| continuous/core/switch_noisy | 0.054587 | 0.307798 | 0.032569 | 62.187500 | 0.019957 | 0.000000 | 0.000000 | 0.000000 |
| continuous/noise_jump/noise_jump | 0.020018 | — | 0.020018 | — | 0.005780 | 0.000000 | 0.000000 | 0.000000 |
| continuous/drift/drift | 0.001715 | — | 0.001715 | — | 0.010985 | 0.000000 | 0.000000 | 0.000000 |
| continuous/exactly_quiet/exactly_quiet | 0.000000 | — | 0.000000 | — | 0.000187 | 0.000000 | 0.000000 | 0.000000 |
| continuous/mixed/increase_first | 0.038747 | 0.300819 | 0.015958 | 70.234375 | 0.014846 | 0.000000 | 0.000000 | 0.000000 |
| continuous/mixed/decrease_first | 0.043339 | 0.299925 | 0.021027 | 71.000000 | 0.014846 | 0.000000 | 0.000000 | 0.000000 |
| adam/core/quiet | 0.002380 | — | 0.002380 | — | 0.046478 | 0.000000 | 0.000000 | 0.000000 |
| adam/core/noisy | 0.060836 | — | 0.060836 | — | 0.046478 | 0.000000 | 0.000000 | 0.000000 |
| adam/core/switch_quiet | 0.009498 | 0.098946 | 0.001720 | 39.750000 | 0.046478 | 0.000000 | 0.000000 | 0.000000 |
| adam/core/switch_noisy | 0.075707 | 0.233594 | 0.061978 | 48.734375 | 0.046478 | 0.000000 | 0.000000 | 0.000000 |
| adam/noise_jump/noise_jump | 0.039163 | — | 0.039163 | — | 0.016843 | 0.000000 | 0.000000 | 0.000000 |
| adam/drift/drift | 0.002372 | — | 0.002372 | — | 0.016187 | 0.000000 | 0.000000 | 0.000000 |
| adam/exactly_quiet/exactly_quiet | 0.000000 | — | 0.000000 | — | 0.000362 | 0.000000 | 0.000000 | 0.000000 |
| adam/mixed/increase_first | 0.047591 | 0.225226 | 0.032145 | 71.156250 | 0.032255 | 0.000000 | 0.000000 | 0.000000 |
| adam/mixed/decrease_first | 0.057296 | 0.220201 | 0.043130 | 59.859375 | 0.032255 | 0.000000 | 0.000000 | 0.000000 |
| sgd/core/quiet | 0.000170 | — | 0.000170 | — | 0.166883 | 0.000000 | 0.000000 | 0.000000 |
| sgd/core/noisy | 0.067354 | — | 0.067354 | — | 0.166883 | 0.000000 | 0.000000 | 0.000000 |
| sgd/core/switch_quiet | 0.006834 | 0.083470 | 0.000170 | 17.359375 | 0.166883 | 0.000000 | 0.000000 | 0.000000 |
| sgd/core/switch_noisy | 0.075313 | 0.151504 | 0.068687 | 71.156250 | 0.166883 | 0.000000 | 0.000000 | 0.000000 |
| sgd/noise_jump/noise_jump | 0.028948 | — | 0.028948 | — | 0.040000 | 0.000000 | 0.000000 | 0.000000 |
| sgd/drift/drift | 0.000200 | — | 0.000200 | — | 0.005439 | 0.000000 | 0.000000 | 0.000000 |
| sgd/exactly_quiet/exactly_quiet | 0.000000 | — | 0.000000 | — | 0.000167 | 0.000000 | 0.000000 | 0.000000 |
| sgd/mixed/increase_first | 0.035396 | 0.123904 | 0.027700 | 40.718750 | 0.106924 | 0.000000 | 0.000000 | 0.000000 |
| sgd/mixed/decrease_first | 0.047014 | 0.120763 | 0.040601 | 44.968750 | 0.106924 | 0.000000 | 0.000000 | 0.000000 |
| oracle_matched/core/quiet | 0.000646 | — | 0.000646 | — | 0.012971 | 0.000000 | 0.000000 | 0.000000 |
| oracle_matched/core/noisy | 0.015364 | — | 0.015364 | — | 0.012971 | 0.000000 | 0.000000 | 0.000000 |
| oracle_matched/core/switch_quiet | 0.009282 | 0.111368 | 0.000405 | 40.875000 | 0.012971 | 64.000000 | 32.000000 | 0.005466 |
| oracle_matched/core/switch_noisy | 0.038700 | 0.304619 | 0.015577 | 54.593750 | 0.012971 | 64.000000 | 32.000000 | 0.005466 |
| oracle_matched/noise_jump/noise_jump | 0.010351 | — | 0.010351 | — | 0.004316 | 0.000000 | 0.000000 | 0.000000 |
| oracle_matched/drift/drift | 0.000663 | — | 0.000663 | — | 0.004468 | 0.000000 | 0.000000 | 0.000000 |
| oracle_matched/exactly_quiet/exactly_quiet | 0.000000 | — | 0.000000 | — | 0.000187 | 0.000000 | 0.000000 | 0.000000 |
| oracle_matched/mixed/increase_first | 0.024825 | 0.217981 | 0.008029 | 45.078125 | 0.008975 | 64.000000 | 32.000000 | 0.005466 |
| oracle_matched/mixed/decrease_first | 0.028833 | 0.238850 | 0.010571 | 44.312500 | 0.008975 | 64.000000 | 32.000000 | 0.005466 |
| random/core/quiet | 0.000650 | — | 0.000650 | — | 0.012706 | 80.000000 | 40.000000 | 0.006833 |
| random/core/noisy | 0.015487 | — | 0.015487 | — | 0.012706 | 79.000000 | 39.062500 | 0.006673 |
| random/core/switch_quiet | 0.011105 | 0.134337 | 0.000389 | 34.359375 | 0.012706 | 71.000000 | 35.500000 | 0.006064 |
| random/core/switch_noisy | 0.048635 | 0.428427 | 0.015609 | 65.625000 | 0.012706 | 70.000000 | 35.000000 | 0.005979 |
| random/noise_jump/noise_jump | 0.010416 | — | 0.010416 | — | 0.004341 | 73.000000 | 36.500000 | 0.006235 |
| random/drift/drift | 0.000667 | — | 0.000667 | — | 0.004495 | 74.000000 | 37.000000 | 0.006320 |
| random/exactly_quiet/exactly_quiet | 0.000000 | — | 0.000000 | — | 0.000187 | 60.000000 | 30.000000 | 0.005125 |
| random/mixed/increase_first | 0.030536 | 0.288719 | 0.008085 | 45.437500 | 0.008798 | 71.000000 | 35.500000 | 0.006064 |
| random/mixed/decrease_first | 0.036734 | 0.337256 | 0.010602 | 48.265625 | 0.008798 | 83.000000 | 41.500000 | 0.007089 |

Vector update norm is repeated across coordinates of its fixture. Zero burst activity for continuous/Adam/SGD does not mean zero learning. Duty excludes the fixed startup period.

## Actual burst starts near events

| Policy/fixture/coordinate/event | Hits/finite seeds | Censored start latency |
| --- | --- | ---: |
| burst/core/switch_quiet/target_down | 32/32 | 10.031250 |
| burst/core/switch_quiet/target_up | 32/32 | 10.125000 |
| burst/core/switch_noisy/target_down | 32/32 | 12.093750 |
| burst/core/switch_noisy/target_up | 32/32 | 12.843750 |
| burst/noise_jump/noise_jump/noise_increase | 0/32 | 100.000000 |
| burst/noise_jump/noise_jump/noise_decrease | 0/32 | 100.000000 |
| burst/drift/drift/drift_start | 29/32 | 65.218750 |
| burst/drift/drift/drift_end | 11/32 | 77.593750 |
| burst/mixed/increase_first/target_down | 32/32 | 12.187500 |
| burst/mixed/increase_first/target_up | 32/32 | 12.312500 |
| burst/mixed/decrease_first/target_down | 32/32 | 11.281250 |
| burst/mixed/decrease_first/target_up | 32/32 | 12.218750 |
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
| random/core/switch_quiet/target_down | 0/32 | 100.000000 |
| random/core/switch_quiet/target_up | 1/32 | 97.218750 |
| random/core/switch_noisy/target_down | 1/32 | 97.062500 |
| random/core/switch_noisy/target_up | 1/32 | 97.125000 |
| random/noise_jump/noise_jump/noise_increase | 2/32 | 95.562500 |
| random/noise_jump/noise_jump/noise_decrease | 3/32 | 93.062500 |
| random/drift/drift/drift_start | 3/32 | 93.187500 |
| random/drift/drift/drift_end | 1/32 | 99.093750 |
| random/mixed/increase_first/target_down | 1/32 | 99.625000 |
| random/mixed/increase_first/target_up | 1/32 | 96.875000 |
| random/mixed/decrease_first/target_down | 2/32 | 95.218750 |
| random/mixed/decrease_first/target_up | 0/32 | 100.000000 |

## Measured row execution time

| Stage | Family | Seconds |
| --- | --- | ---: |
| tuning | burst | 5.76 |
| tuning | oracle | 3.69 |
| tuning | continuous | 4.09 |
| tuning | adam | 3.48 |
| tuning | sgd | 1.29 |
| confirmation | burst | 7.27 |
| confirmation | oracle | 1.16 |
| confirmation | continuous | 0.93 |
| confirmation | adam | 1.26 |
| confirmation | sgd | 0.46 |
| confirmation | oracle_matched | 0.85 |
| confirmation | random | 1.00 |

Each searched family executes 5,184,000 learner coordinate-updates. Times exclude archive writes and share a causal signal cache: the first family pays cache initialization. These are observed times, not equal CPU-cost claims.

## Scope and evidence

Rate caps do not cap realized Adam update norms. Perfect timing is privileged and is not a mathematical upper bound. The separately tuned oracle tests this finite controller menu; the matched oracle holds candidate parameters fixed. Random scheduling matches expected pooled frequency only, so actual activity and per-condition differences remain visible.

Candidate advancement requires >=10% primary improvement over Adam, SGD, continuous and random with paired upper delta <0, plus every retention upper delta <=max(.002,.1*control). No oracle or alarm score overrides that decision. A positive result would warrant only a separately authorized broader supervised benchmark; all outcomes close this registration.

Whole-seed intervals: 10,000 resamples, seed75000. The archive retains every reached row, tuning score, source snapshot, event start and candidate event-error/recovery record. Small synthetic fixtures and finite menus do not establish global optimizer superiority or a scalable reference-gradient mechanism. Every earlier study remains unchanged.

`python check_v3_burst.py --evidence results/v3-burst --reproduce` regenerates every reached row and manifest/summary at rtol1e-11/atol1e-13. `python report_v3_burst.py --check` checks both generated reports.
