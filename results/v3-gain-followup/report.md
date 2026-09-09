# V3 bounded gain follow-up

Overall disposition: **detector_negative**.

Search disposition: **eligible**. Search limits and detector findings are separate.

## Frozen tuning choices

| Arm | Configuration | Added step amplitude (lr × gain) | Tuning excess MSE |
| --- | --- | ---: | ---: |
| sgd | `{"lr": 0.035743040182210514}` | — | 0.02050238 |
| adam | `{"lr": 0.032, "beta2": 0.9999}` | — | 0.01906885 |
| single | `{"lr": 0.016, "gain": 1.0}` | 0.016 | 0.01934858 |
| historical | `{"lr": 0.016, "gain": 8.0}` | 0.128 | 0.01877149 |
| candidate | `{"lr": 0.004, "gain": 64.0}` | 0.256 | 0.01230101 |

## Reached stages

| Stage | Rows | Status |
| --- | ---: | --- |
| tuning | 3840 | complete |
| calibration | 48 | complete |
| diagnostics | 96 | complete |
| performance | 0 | not run: prerequisite failed |

## Independent detector result

| Required cell | Count / total | Rate | 95% interval | Censored latency | Pass |
| --- | --- | ---: | --- | ---: | --- |
| fixed/quiet/blocks | 18/1600 | 0.0112 | [0.0069, 0.0156] | — | True |
| fixed/noisy/blocks | 17/1600 | 0.0106 | [0.0062, 0.0156] | — | True |
| fixed/switch_quiet/target_down | 32/32 | 1.0000 | [1.0000, 1.0000] | 2.81 | True |
| fixed/switch_quiet/target_up | 32/32 | 1.0000 | [1.0000, 1.0000] | 2.78 | True |
| fixed/switch_noisy/target_down | 32/32 | 1.0000 | [1.0000, 1.0000] | 6.12 | True |
| fixed/switch_noisy/target_up | 32/32 | 1.0000 | [1.0000, 1.0000] | 7.03 | True |
| fixed/noise_jump/noise_increase | 8/32 | 0.2500 | [0.1250, 0.4062] | 78.59 | False |
| fixed/noise_jump/noise_decrease | 0/32 | 0.0000 | [0.0000, 0.0000] | 100.00 | True |
| closed/quiet/blocks | 2/1600 | 0.0013 | [0.0000, 0.0031] | — | True |
| closed/noisy/blocks | 35/1600 | 0.0219 | [0.0144, 0.0300] | — | True |
| closed/switch_quiet/target_down | 32/32 | 1.0000 | [1.0000, 1.0000] | 2.06 | True |
| closed/switch_quiet/target_up | 32/32 | 1.0000 | [1.0000, 1.0000] | 2.16 | True |
| closed/switch_noisy/target_down | 32/32 | 1.0000 | [1.0000, 1.0000] | 5.66 | True |
| closed/switch_noisy/target_up | 32/32 | 1.0000 | [1.0000, 1.0000] | 6.78 | True |
| closed/noise_jump/noise_increase | 11/32 | 0.3438 | [0.1875, 0.5000] | 71.91 | False |
| closed/noise_jump/noise_decrease | 0/32 | 0.0000 | [0.0000, 0.0000] | 100.00 | True |

## Descriptive diagnostics: every control and condition

| Arm/mode/fixture/coordinate | Finite seeds | Initial gate | Settled gate | Point alarm rate | Block alarm rate |
| --- | ---: | ---: | ---: | ---: | ---: |
| single/fixed/core/quiet | 32 | 0.00236 | 0.00236 | 0.00000 | 0.00000 |
| single/fixed/core/noisy | 32 | 0.47047 | 0.47506 | 0.00036 | 0.01750 |
| single/fixed/core/switch_quiet | 32 | 0.00240 | 0.00706 | 0.00000 | 0.00000 |
| single/fixed/core/switch_noisy | 32 | 0.47582 | 0.47417 | 0.00071 | 0.02313 |
| single/fixed/noise_jump/noise_jump | 32 | 0.00235 | 0.18851 | 0.00008 | 0.00562 |
| single/fixed/drift/drift | 32 | 0.00235 | 0.00241 | 0.00000 | 0.00000 |
| single/fixed/exactly_quiet/exactly_quiet | 32 | 0.00000 | 0.00000 | 0.00000 | 0.00000 |
| single/closed/core/quiet | 32 | 0.00340 | 0.00267 | 0.00000 | 0.00000 |
| single/closed/core/noisy | 32 | 0.47359 | 0.47809 | 0.00034 | 0.01688 |
| single/closed/core/switch_quiet | 32 | 0.00342 | 0.00720 | 0.00000 | 0.00000 |
| single/closed/core/switch_noisy | 32 | 0.47892 | 0.47718 | 0.00061 | 0.02250 |
| single/closed/noise_jump/noise_jump | 32 | 0.00340 | 0.19040 | 0.00008 | 0.00562 |
| single/closed/drift/drift | 32 | 0.00336 | 0.00268 | 0.00000 | 0.00000 |
| single/closed/exactly_quiet/exactly_quiet | 32 | 0.00093 | 0.00000 | 0.00000 | 0.00000 |
| historical/fixed/core/quiet | 32 | 0.06818 | 0.03480 | 0.00013 | 0.01000 |
| historical/fixed/core/noisy | 32 | 0.06704 | 0.03459 | 0.00017 | 0.01000 |
| historical/fixed/core/switch_quiet | 32 | 0.06482 | 0.02468 | 0.00448 | 0.05188 |
| historical/fixed/core/switch_noisy | 32 | 0.06847 | 0.03053 | 0.00026 | 0.01500 |
| historical/fixed/noise_jump/noise_jump | 32 | 0.06989 | 0.03827 | 0.01121 | 0.04500 |
| historical/fixed/drift/drift | 32 | 0.06471 | 0.01863 | 0.00004 | 0.00313 |
| historical/fixed/exactly_quiet/exactly_quiet | 32 | 0.00000 | 0.00000 | 0.00000 | 0.00000 |
| historical/closed/core/quiet | 32 | 0.01870 | 0.03835 | 0.00036 | 0.01375 |
| historical/closed/core/noisy | 32 | 0.05490 | 0.03422 | 0.00008 | 0.00250 |
| historical/closed/core/switch_quiet | 32 | 0.01878 | 0.03398 | 0.00906 | 0.05813 |
| historical/closed/core/switch_noisy | 32 | 0.05705 | 0.03195 | 0.00009 | 0.00688 |
| historical/closed/noise_jump/noise_jump | 32 | 0.01779 | 0.03813 | 0.01010 | 0.03938 |
| historical/closed/drift/drift | 32 | 0.01899 | 0.03799 | 0.00051 | 0.01625 |
| historical/closed/exactly_quiet/exactly_quiet | 32 | 0.01136 | 0.00000 | 0.00000 | 0.00000 |
| candidate/fixed/core/quiet | 32 | 0.03310 | 0.01936 | 0.00016 | 0.01125 |
| candidate/fixed/core/noisy | 32 | 0.03310 | 0.01939 | 0.00013 | 0.01062 |
| candidate/fixed/core/switch_quiet | 32 | 0.03560 | 0.04888 | 0.06079 | 0.10625 |
| candidate/fixed/core/switch_noisy | 32 | 0.03211 | 0.03300 | 0.03148 | 0.09750 |
| candidate/fixed/noise_jump/noise_jump | 32 | 0.03217 | 0.01798 | 0.00036 | 0.01438 |
| candidate/fixed/drift/drift | 32 | 0.03454 | 0.15336 | 0.39021 | 0.42625 |
| candidate/fixed/exactly_quiet/exactly_quiet | 32 | 0.00000 | 0.00000 | 0.00000 | 0.00000 |
| candidate/closed/core/quiet | 32 | 0.09257 | 0.01841 | 0.00002 | 0.00125 |
| candidate/closed/core/noisy | 32 | 0.04108 | 0.01992 | 0.00034 | 0.02187 |
| candidate/closed/core/switch_quiet | 32 | 0.09249 | 0.01812 | 0.00275 | 0.04250 |
| candidate/closed/core/switch_noisy | 32 | 0.03943 | 0.02200 | 0.00631 | 0.06438 |
| candidate/closed/noise_jump/noise_jump | 32 | 0.09281 | 0.01849 | 0.00036 | 0.01937 |
| candidate/closed/drift/drift | 32 | 0.09208 | 0.01856 | 0.00000 | 0.00000 |
| candidate/closed/exactly_quiet/exactly_quiet | 32 | 0.08649 | 0.00000 | 0.00000 | 0.00000 |

Only stationary coordinates use block alarms as false alarms. Drift and noise changes are not successful target-switch detections. Intervals resample whole seeds, not independent events. Finite-seed counts expose any non-finite trajectories; raw event records are retained.

## Limits and decision

Five arms each receive 48 configurations × 16 tuning seeds × 6,000 four-coordinate observations: 3,840 trajectories, 92,160,000 coordinate updates. Tuning scores are selected training evidence, not independent performance results. The kernel, tasks and metrics are unchanged from slice1.

A wider-search boundary flag remains an unresolved search limit. This follow-up independently tests the detector at a specified finite configuration even with such a flag; it cannot run performance unless search adequacy AND every detector criterion pass. No existing experiment was reopened or its outcome changed. No automatic grid extension or agent integration follows.

A detector-negative result rejects the claimed detection behavior of this specified signal/policy on these fixtures, not all v3 ideas. A positive result would justify only a separately registered agent experiment. The synthetic separable coordinates do not test representation interference. Detector rate thresholds are point screens, not population-wide guarantees.

Reproduce with `python check_v3_gain.py --evidence results/v3-gain-followup --reproduce`; check this generated report with `python report_v3_gain.py --check`. Every reached scientific row, selection, calibrated threshold and decision is checked. Only timing and regenerated input hashes are excluded from numerical comparisons.
