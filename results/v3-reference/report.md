# V3 separate-reference experiment

Disposition: **awaiting_performance**.

| Stage | Rows |
| --- | ---: |
| calibration | 48 |
| diagnostics | 96 |
| performance | 0 |

## Fixed configurations and native thresholds

| Policy | Configuration | Fixed threshold | Active threshold |
| --- | --- | ---: | ---: |
| coupled | `{"lr": 0.004, "gain": 64.0, "beta2": 0.999}` | 0.469023 | 0.813103 |
| watch_adam | `{"lr": 0.004, "gain": 0.0, "beta2": 0.999}` | 0.469023 | 0.456573 |
| separate | `{"lr": 0.004, "gain": 64.0, "beta2": 0.999}` | 0.469023 | 0.469023 |
| adam | `{"lr": 0.032, "beta2": 0.9999}` | — | — |
| sgd | `{"lr": 0.035743040182210514}` | — | — |
| single | `{"lr": 0.016, "gain": 1.0, "beta2": 0.999}` | — | — |
| constant | `{"lr": 0.004, "gain": 64.0, "beta2": 0.999}` | — | — |

## Native detector decisions: authoritative advancement gate

### coupled: detector_negative

| Cell | Count/total | Rate | 95% interval | Censored latency | Pass |
| --- | --- | ---: | --- | ---: | --- |
| fixed/quiet/blocks | 13/1600 | 0.00813 | [0.00438, 0.01188] | — | True |
| fixed/noisy/blocks | 15/1600 | 0.00938 | [0.00500, 0.01438] | — | True |
| fixed/switch_quiet/target_down | 32/32 | 1.00000 | [1.00000, 1.00000] | 10.031 | True |
| fixed/switch_quiet/target_up | 32/32 | 1.00000 | [1.00000, 1.00000] | 10.125 | True |
| fixed/switch_noisy/target_down | 32/32 | 1.00000 | [1.00000, 1.00000] | 13.156 | True |
| fixed/switch_noisy/target_up | 32/32 | 1.00000 | [1.00000, 1.00000] | 12.156 | True |
| fixed/noise_jump/noise_increase | 1/32 | 0.03125 | [0.00000, 0.09375] | 97.781 | True |
| fixed/noise_jump/noise_decrease | 0/32 | 0.00000 | [0.00000, 0.00000] | 100.000 | True |
| fixed/increase_first/target_down | 32/32 | 1.00000 | [1.00000, 1.00000] | 11.688 | True |
| fixed/increase_first/target_up | 32/32 | 1.00000 | [1.00000, 1.00000] | 11.500 | True |
| fixed/decrease_first/target_down | 32/32 | 1.00000 | [1.00000, 1.00000] | 11.375 | True |
| fixed/decrease_first/target_up | 32/32 | 1.00000 | [1.00000, 1.00000] | 12.094 | True |
| closed/quiet/blocks | 41/1600 | 0.02563 | [0.01937, 0.03250] | — | True |
| closed/noisy/blocks | 0/1600 | 0.00000 | [0.00000, 0.00000] | — | True |
| closed/switch_quiet/target_down | 30/32 | 0.93750 | [0.84375, 1.00000] | 32.875 | True |
| closed/switch_quiet/target_up | 31/32 | 0.96875 | [0.90625, 1.00000] | 33.312 | True |
| closed/switch_noisy/target_down | 0/32 | 0.00000 | [0.00000, 0.00000] | 100.000 | False |
| closed/switch_noisy/target_up | 0/32 | 0.00000 | [0.00000, 0.00000] | 100.000 | False |
| closed/noise_jump/noise_increase | 0/32 | 0.00000 | [0.00000, 0.00000] | 100.000 | True |
| closed/noise_jump/noise_decrease | 0/32 | 0.00000 | [0.00000, 0.00000] | 100.000 | True |
| closed/increase_first/target_down | 1/32 | 0.03125 | [0.00000, 0.09375] | 96.906 | False |
| closed/increase_first/target_up | 23/32 | 0.71875 | [0.56250, 0.87500] | 39.844 | False |
| closed/decrease_first/target_down | 21/32 | 0.65625 | [0.50000, 0.81250] | 45.188 | False |
| closed/decrease_first/target_up | 0/32 | 0.00000 | [0.00000, 0.00000] | 100.000 | False |

### watch_adam: detector_negative

| Cell | Count/total | Rate | 95% interval | Censored latency | Pass |
| --- | --- | ---: | --- | ---: | --- |
| fixed/quiet/blocks | 13/1600 | 0.00813 | [0.00438, 0.01188] | — | True |
| fixed/noisy/blocks | 15/1600 | 0.00938 | [0.00500, 0.01438] | — | True |
| fixed/switch_quiet/target_down | 32/32 | 1.00000 | [1.00000, 1.00000] | 10.031 | True |
| fixed/switch_quiet/target_up | 32/32 | 1.00000 | [1.00000, 1.00000] | 10.125 | True |
| fixed/switch_noisy/target_down | 32/32 | 1.00000 | [1.00000, 1.00000] | 13.156 | True |
| fixed/switch_noisy/target_up | 32/32 | 1.00000 | [1.00000, 1.00000] | 12.156 | True |
| fixed/noise_jump/noise_increase | 1/32 | 0.03125 | [0.00000, 0.09375] | 97.781 | True |
| fixed/noise_jump/noise_decrease | 0/32 | 0.00000 | [0.00000, 0.00000] | 100.000 | True |
| fixed/increase_first/target_down | 32/32 | 1.00000 | [1.00000, 1.00000] | 11.688 | True |
| fixed/increase_first/target_up | 32/32 | 1.00000 | [1.00000, 1.00000] | 11.500 | True |
| fixed/decrease_first/target_down | 32/32 | 1.00000 | [1.00000, 1.00000] | 11.375 | True |
| fixed/decrease_first/target_up | 32/32 | 1.00000 | [1.00000, 1.00000] | 12.094 | True |
| closed/quiet/blocks | 28/1600 | 0.01750 | [0.01188, 0.02312] | — | True |
| closed/noisy/blocks | 20/1600 | 0.01250 | [0.00750, 0.01812] | — | True |
| closed/switch_quiet/target_down | 32/32 | 1.00000 | [1.00000, 1.00000] | 10.000 | True |
| closed/switch_quiet/target_up | 32/32 | 1.00000 | [1.00000, 1.00000] | 10.000 | True |
| closed/switch_noisy/target_down | 32/32 | 1.00000 | [1.00000, 1.00000] | 12.969 | True |
| closed/switch_noisy/target_up | 32/32 | 1.00000 | [1.00000, 1.00000] | 11.969 | True |
| closed/noise_jump/noise_increase | 2/32 | 0.06250 | [0.00000, 0.15625] | 96.594 | False |
| closed/noise_jump/noise_decrease | 0/32 | 0.00000 | [0.00000, 0.00000] | 100.000 | True |
| closed/increase_first/target_down | 32/32 | 1.00000 | [1.00000, 1.00000] | 11.438 | True |
| closed/increase_first/target_up | 32/32 | 1.00000 | [1.00000, 1.00000] | 11.188 | True |
| closed/decrease_first/target_down | 32/32 | 1.00000 | [1.00000, 1.00000] | 11.156 | True |
| closed/decrease_first/target_up | 32/32 | 1.00000 | [1.00000, 1.00000] | 11.875 | True |

### separate: detector_pass

| Cell | Count/total | Rate | 95% interval | Censored latency | Pass |
| --- | --- | ---: | --- | ---: | --- |
| fixed/quiet/blocks | 13/1600 | 0.00813 | [0.00438, 0.01188] | — | True |
| fixed/noisy/blocks | 15/1600 | 0.00938 | [0.00500, 0.01438] | — | True |
| fixed/switch_quiet/target_down | 32/32 | 1.00000 | [1.00000, 1.00000] | 10.031 | True |
| fixed/switch_quiet/target_up | 32/32 | 1.00000 | [1.00000, 1.00000] | 10.125 | True |
| fixed/switch_noisy/target_down | 32/32 | 1.00000 | [1.00000, 1.00000] | 13.156 | True |
| fixed/switch_noisy/target_up | 32/32 | 1.00000 | [1.00000, 1.00000] | 12.156 | True |
| fixed/noise_jump/noise_increase | 1/32 | 0.03125 | [0.00000, 0.09375] | 97.781 | True |
| fixed/noise_jump/noise_decrease | 0/32 | 0.00000 | [0.00000, 0.00000] | 100.000 | True |
| fixed/increase_first/target_down | 32/32 | 1.00000 | [1.00000, 1.00000] | 11.688 | True |
| fixed/increase_first/target_up | 32/32 | 1.00000 | [1.00000, 1.00000] | 11.500 | True |
| fixed/decrease_first/target_down | 32/32 | 1.00000 | [1.00000, 1.00000] | 11.375 | True |
| fixed/decrease_first/target_up | 32/32 | 1.00000 | [1.00000, 1.00000] | 12.094 | True |
| closed/quiet/blocks | 13/1600 | 0.00813 | [0.00438, 0.01188] | — | True |
| closed/noisy/blocks | 15/1600 | 0.00938 | [0.00500, 0.01438] | — | True |
| closed/switch_quiet/target_down | 32/32 | 1.00000 | [1.00000, 1.00000] | 10.031 | True |
| closed/switch_quiet/target_up | 32/32 | 1.00000 | [1.00000, 1.00000] | 10.125 | True |
| closed/switch_noisy/target_down | 32/32 | 1.00000 | [1.00000, 1.00000] | 13.156 | True |
| closed/switch_noisy/target_up | 32/32 | 1.00000 | [1.00000, 1.00000] | 12.156 | True |
| closed/noise_jump/noise_increase | 1/32 | 0.03125 | [0.00000, 0.09375] | 97.781 | True |
| closed/noise_jump/noise_decrease | 0/32 | 0.00000 | [0.00000, 0.00000] | 100.000 | True |
| closed/increase_first/target_down | 32/32 | 1.00000 | [1.00000, 1.00000] | 11.688 | True |
| closed/increase_first/target_up | 32/32 | 1.00000 | [1.00000, 1.00000] | 11.500 | True |
| closed/decrease_first/target_down | 32/32 | 1.00000 | [1.00000, 1.00000] | 11.375 | True |
| closed/decrease_first/target_up | 32/32 | 1.00000 | [1.00000, 1.00000] | 12.094 | True |

## Common-threshold diagnostics: explanatory only

Every unchanged gate sequence is scored at separate/fixed calibration threshold. These cells do not select settings or permit advancement; stationary failures remain visible.

### coupled: detector_negative

| Cell | Count/total | Rate | 95% interval | Censored latency | Pass |
| --- | --- | ---: | --- | ---: | --- |
| fixed/quiet/blocks | 13/1600 | 0.00813 | [0.00438, 0.01188] | — | True |
| fixed/noisy/blocks | 15/1600 | 0.00938 | [0.00500, 0.01438] | — | True |
| fixed/switch_quiet/target_down | 32/32 | 1.00000 | [1.00000, 1.00000] | 10.031 | True |
| fixed/switch_quiet/target_up | 32/32 | 1.00000 | [1.00000, 1.00000] | 10.125 | True |
| fixed/switch_noisy/target_down | 32/32 | 1.00000 | [1.00000, 1.00000] | 13.156 | True |
| fixed/switch_noisy/target_up | 32/32 | 1.00000 | [1.00000, 1.00000] | 12.156 | True |
| fixed/noise_jump/noise_increase | 1/32 | 0.03125 | [0.00000, 0.09375] | 97.781 | True |
| fixed/noise_jump/noise_decrease | 0/32 | 0.00000 | [0.00000, 0.00000] | 100.000 | True |
| fixed/increase_first/target_down | 32/32 | 1.00000 | [1.00000, 1.00000] | 11.688 | True |
| fixed/increase_first/target_up | 32/32 | 1.00000 | [1.00000, 1.00000] | 11.500 | True |
| fixed/decrease_first/target_down | 32/32 | 1.00000 | [1.00000, 1.00000] | 11.375 | True |
| fixed/decrease_first/target_up | 32/32 | 1.00000 | [1.00000, 1.00000] | 12.094 | True |
| closed/quiet/blocks | 443/1600 | 0.27687 | [0.24938, 0.31000] | — | False |
| closed/noisy/blocks | 24/1600 | 0.01500 | [0.00875, 0.02188] | — | True |
| closed/switch_quiet/target_down | 32/32 | 1.00000 | [1.00000, 1.00000] | 11.844 | True |
| closed/switch_quiet/target_up | 32/32 | 1.00000 | [1.00000, 1.00000] | 11.188 | True |
| closed/switch_noisy/target_down | 32/32 | 1.00000 | [1.00000, 1.00000] | 13.344 | True |
| closed/switch_noisy/target_up | 31/32 | 0.96875 | [0.90625, 1.00000] | 14.969 | True |
| closed/noise_jump/noise_increase | 6/32 | 0.18750 | [0.06250, 0.34375] | 87.750 | False |
| closed/noise_jump/noise_decrease | 0/32 | 0.00000 | [0.00000, 0.00000] | 100.000 | True |
| closed/increase_first/target_down | 26/32 | 0.81250 | [0.65625, 0.93750] | 32.250 | True |
| closed/increase_first/target_up | 32/32 | 1.00000 | [1.00000, 1.00000] | 11.469 | True |
| closed/decrease_first/target_down | 32/32 | 1.00000 | [1.00000, 1.00000] | 11.438 | True |
| closed/decrease_first/target_up | 24/32 | 0.75000 | [0.59375, 0.87500] | 34.281 | False |

### watch_adam: detector_negative

| Cell | Count/total | Rate | 95% interval | Censored latency | Pass |
| --- | --- | ---: | --- | ---: | --- |
| fixed/quiet/blocks | 13/1600 | 0.00813 | [0.00438, 0.01188] | — | True |
| fixed/noisy/blocks | 15/1600 | 0.00938 | [0.00500, 0.01438] | — | True |
| fixed/switch_quiet/target_down | 32/32 | 1.00000 | [1.00000, 1.00000] | 10.031 | True |
| fixed/switch_quiet/target_up | 32/32 | 1.00000 | [1.00000, 1.00000] | 10.125 | True |
| fixed/switch_noisy/target_down | 32/32 | 1.00000 | [1.00000, 1.00000] | 13.156 | True |
| fixed/switch_noisy/target_up | 32/32 | 1.00000 | [1.00000, 1.00000] | 12.156 | True |
| fixed/noise_jump/noise_increase | 1/32 | 0.03125 | [0.00000, 0.09375] | 97.781 | True |
| fixed/noise_jump/noise_decrease | 0/32 | 0.00000 | [0.00000, 0.00000] | 100.000 | True |
| fixed/increase_first/target_down | 32/32 | 1.00000 | [1.00000, 1.00000] | 11.688 | True |
| fixed/increase_first/target_up | 32/32 | 1.00000 | [1.00000, 1.00000] | 11.500 | True |
| fixed/decrease_first/target_down | 32/32 | 1.00000 | [1.00000, 1.00000] | 11.375 | True |
| fixed/decrease_first/target_up | 32/32 | 1.00000 | [1.00000, 1.00000] | 12.094 | True |
| closed/quiet/blocks | 22/1600 | 0.01375 | [0.00875, 0.01875] | — | True |
| closed/noisy/blocks | 19/1600 | 0.01188 | [0.00750, 0.01688] | — | True |
| closed/switch_quiet/target_down | 32/32 | 1.00000 | [1.00000, 1.00000] | 10.031 | True |
| closed/switch_quiet/target_up | 32/32 | 1.00000 | [1.00000, 1.00000] | 10.094 | True |
| closed/switch_noisy/target_down | 32/32 | 1.00000 | [1.00000, 1.00000] | 13.219 | True |
| closed/switch_noisy/target_up | 32/32 | 1.00000 | [1.00000, 1.00000] | 12.094 | True |
| closed/noise_jump/noise_increase | 2/32 | 0.06250 | [0.00000, 0.15625] | 96.594 | False |
| closed/noise_jump/noise_decrease | 0/32 | 0.00000 | [0.00000, 0.00000] | 100.000 | True |
| closed/increase_first/target_down | 32/32 | 1.00000 | [1.00000, 1.00000] | 11.656 | True |
| closed/increase_first/target_up | 32/32 | 1.00000 | [1.00000, 1.00000] | 11.500 | True |
| closed/decrease_first/target_down | 32/32 | 1.00000 | [1.00000, 1.00000] | 11.375 | True |
| closed/decrease_first/target_up | 32/32 | 1.00000 | [1.00000, 1.00000] | 12.125 | True |

### separate: detector_pass

| Cell | Count/total | Rate | 95% interval | Censored latency | Pass |
| --- | --- | ---: | --- | ---: | --- |
| fixed/quiet/blocks | 13/1600 | 0.00813 | [0.00438, 0.01188] | — | True |
| fixed/noisy/blocks | 15/1600 | 0.00938 | [0.00500, 0.01438] | — | True |
| fixed/switch_quiet/target_down | 32/32 | 1.00000 | [1.00000, 1.00000] | 10.031 | True |
| fixed/switch_quiet/target_up | 32/32 | 1.00000 | [1.00000, 1.00000] | 10.125 | True |
| fixed/switch_noisy/target_down | 32/32 | 1.00000 | [1.00000, 1.00000] | 13.156 | True |
| fixed/switch_noisy/target_up | 32/32 | 1.00000 | [1.00000, 1.00000] | 12.156 | True |
| fixed/noise_jump/noise_increase | 1/32 | 0.03125 | [0.00000, 0.09375] | 97.781 | True |
| fixed/noise_jump/noise_decrease | 0/32 | 0.00000 | [0.00000, 0.00000] | 100.000 | True |
| fixed/increase_first/target_down | 32/32 | 1.00000 | [1.00000, 1.00000] | 11.688 | True |
| fixed/increase_first/target_up | 32/32 | 1.00000 | [1.00000, 1.00000] | 11.500 | True |
| fixed/decrease_first/target_down | 32/32 | 1.00000 | [1.00000, 1.00000] | 11.375 | True |
| fixed/decrease_first/target_up | 32/32 | 1.00000 | [1.00000, 1.00000] | 12.094 | True |
| closed/quiet/blocks | 13/1600 | 0.00813 | [0.00438, 0.01188] | — | True |
| closed/noisy/blocks | 15/1600 | 0.00938 | [0.00500, 0.01438] | — | True |
| closed/switch_quiet/target_down | 32/32 | 1.00000 | [1.00000, 1.00000] | 10.031 | True |
| closed/switch_quiet/target_up | 32/32 | 1.00000 | [1.00000, 1.00000] | 10.125 | True |
| closed/switch_noisy/target_down | 32/32 | 1.00000 | [1.00000, 1.00000] | 13.156 | True |
| closed/switch_noisy/target_up | 32/32 | 1.00000 | [1.00000, 1.00000] | 12.156 | True |
| closed/noise_jump/noise_increase | 1/32 | 0.03125 | [0.00000, 0.09375] | 97.781 | True |
| closed/noise_jump/noise_decrease | 0/32 | 0.00000 | [0.00000, 0.00000] | 100.000 | True |
| closed/increase_first/target_down | 32/32 | 1.00000 | [1.00000, 1.00000] | 11.688 | True |
| closed/increase_first/target_up | 32/32 | 1.00000 | [1.00000, 1.00000] | 11.500 | True |
| closed/decrease_first/target_down | 32/32 | 1.00000 | [1.00000, 1.00000] | 11.375 | True |
| closed/decrease_first/target_up | 32/32 | 1.00000 | [1.00000, 1.00000] | 12.094 | True |

## Missing alarms and prediction recovery: diagnostic data only

Recovery within 100 requires all ten consecutive predictions with absolute error <.2 to fit within the first 100 observations. Ratios condition on missed alarms only when that denominator is nonzero. These records do not establish independent learning gains.

| Setup/mode/fixture/coordinate/event | Seeds | Missed | Recovered | Both | Recovered/missed | Post-100 MSE | Post-200 MSE | Max q mean |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| coupled/fixed/core/switch_quiet/target_down | 32 | 0 | 0 | 0 | — | 1.000000 | 1.000000 | 0.996276 |
| coupled/fixed/core/switch_quiet/target_up | 32 | 0 | 0 | 0 | — | 1.000000 | 1.000000 | 0.996340 |
| coupled/fixed/core/switch_noisy/target_down | 32 | 0 | 0 | 0 | — | 1.000000 | 1.000000 | 0.807911 |
| coupled/fixed/core/switch_noisy/target_up | 32 | 0 | 0 | 0 | — | 1.000000 | 1.000000 | 0.802617 |
| coupled/fixed/mixed/increase_first/target_down | 32 | 0 | 0 | 0 | — | 1.000000 | 1.000000 | 0.838188 |
| coupled/fixed/mixed/increase_first/target_up | 32 | 0 | 0 | 0 | — | 1.000000 | 1.000000 | 0.964973 |
| coupled/fixed/mixed/decrease_first/target_down | 32 | 0 | 0 | 0 | — | 1.000000 | 1.000000 | 0.965119 |
| coupled/fixed/mixed/decrease_first/target_up | 32 | 0 | 0 | 0 | — | 1.000000 | 1.000000 | 0.843362 |
| coupled/closed/core/switch_quiet/target_down | 32 | 2 | 2 | 2 | 1.000000 | 1.012932 | 0.530999 | 0.848690 |
| coupled/closed/core/switch_quiet/target_up | 32 | 1 | 1 | 0 | 0.000000 | 1.000428 | 0.528468 | 0.852114 |
| coupled/closed/core/switch_noisy/target_down | 32 | 32 | 29 | 29 | 0.906250 | 0.551974 | 0.287091 | 0.640431 |
| coupled/closed/core/switch_noisy/target_up | 32 | 32 | 24 | 24 | 0.750000 | 0.529289 | 0.275320 | 0.646772 |
| coupled/closed/mixed/increase_first/target_down | 32 | 31 | 24 | 24 | 0.774194 | 0.733998 | 0.386028 | 0.587958 |
| coupled/closed/mixed/increase_first/target_up | 32 | 9 | 32 | 9 | 1.000000 | 0.536817 | 0.269462 | 0.826007 |
| coupled/closed/mixed/decrease_first/target_down | 32 | 11 | 32 | 11 | 1.000000 | 0.509550 | 0.255438 | 0.827212 |
| coupled/closed/mixed/decrease_first/target_up | 32 | 32 | 24 | 24 | 0.750000 | 0.626436 | 0.327433 | 0.562196 |
| watch_adam/fixed/core/switch_quiet/target_down | 32 | 0 | 0 | 0 | — | 1.000000 | 1.000000 | 0.996276 |
| watch_adam/fixed/core/switch_quiet/target_up | 32 | 0 | 0 | 0 | — | 1.000000 | 1.000000 | 0.996340 |
| watch_adam/fixed/core/switch_noisy/target_down | 32 | 0 | 0 | 0 | — | 1.000000 | 1.000000 | 0.807911 |
| watch_adam/fixed/core/switch_noisy/target_up | 32 | 0 | 0 | 0 | — | 1.000000 | 1.000000 | 0.802617 |
| watch_adam/fixed/mixed/increase_first/target_down | 32 | 0 | 0 | 0 | — | 1.000000 | 1.000000 | 0.838188 |
| watch_adam/fixed/mixed/increase_first/target_up | 32 | 0 | 0 | 0 | — | 1.000000 | 1.000000 | 0.964973 |
| watch_adam/fixed/mixed/decrease_first/target_down | 32 | 0 | 0 | 0 | — | 1.000000 | 1.000000 | 0.965119 |
| watch_adam/fixed/mixed/decrease_first/target_up | 32 | 0 | 0 | 0 | — | 1.000000 | 1.000000 | 0.843362 |
| watch_adam/closed/core/switch_quiet/target_down | 32 | 0 | 0 | 0 | — | 1.693810 | 0.953416 | 0.992951 |
| watch_adam/closed/core/switch_quiet/target_up | 32 | 0 | 0 | 0 | — | 1.725034 | 0.968173 | 0.993494 |
| watch_adam/closed/core/switch_noisy/target_down | 32 | 0 | 0 | 0 | — | 2.949119 | 2.199776 | 0.792759 |
| watch_adam/closed/core/switch_noisy/target_up | 32 | 0 | 0 | 0 | — | 3.000470 | 2.240773 | 0.786234 |
| watch_adam/closed/mixed/increase_first/target_down | 32 | 0 | 0 | 0 | — | 1.813995 | 1.077119 | 0.803842 |
| watch_adam/closed/mixed/increase_first/target_up | 32 | 0 | 0 | 0 | — | 2.907841 | 2.117482 | 0.963277 |
| watch_adam/closed/mixed/decrease_first/target_down | 32 | 0 | 0 | 0 | — | 2.934466 | 2.162919 | 0.963186 |
| watch_adam/closed/mixed/decrease_first/target_up | 32 | 0 | 0 | 0 | — | 2.362130 | 1.527103 | 0.817763 |
| separate/fixed/core/switch_quiet/target_down | 32 | 0 | 0 | 0 | — | 1.000000 | 1.000000 | 0.996276 |
| separate/fixed/core/switch_quiet/target_up | 32 | 0 | 0 | 0 | — | 1.000000 | 1.000000 | 0.996340 |
| separate/fixed/core/switch_noisy/target_down | 32 | 0 | 0 | 0 | — | 1.000000 | 1.000000 | 0.807911 |
| separate/fixed/core/switch_noisy/target_up | 32 | 0 | 0 | 0 | — | 1.000000 | 1.000000 | 0.802617 |
| separate/fixed/mixed/increase_first/target_down | 32 | 0 | 0 | 0 | — | 1.000000 | 1.000000 | 0.838188 |
| separate/fixed/mixed/increase_first/target_up | 32 | 0 | 0 | 0 | — | 1.000000 | 1.000000 | 0.964973 |
| separate/fixed/mixed/decrease_first/target_down | 32 | 0 | 0 | 0 | — | 1.000000 | 1.000000 | 0.965119 |
| separate/fixed/mixed/decrease_first/target_up | 32 | 0 | 0 | 0 | — | 1.000000 | 1.000000 | 0.843362 |
| separate/closed/core/switch_quiet/target_down | 32 | 0 | 32 | 0 | — | 0.507888 | 0.254198 | 0.996276 |
| separate/closed/core/switch_quiet/target_up | 32 | 0 | 32 | 0 | — | 0.520439 | 0.260498 | 0.996340 |
| separate/closed/core/switch_noisy/target_down | 32 | 0 | 24 | 0 | — | 0.659225 | 0.341550 | 0.807911 |
| separate/closed/core/switch_noisy/target_up | 32 | 0 | 28 | 0 | — | 0.600946 | 0.313077 | 0.802617 |
| separate/closed/mixed/increase_first/target_down | 32 | 0 | 19 | 0 | — | 0.692155 | 0.374046 | 0.838188 |
| separate/closed/mixed/increase_first/target_up | 32 | 0 | 32 | 0 | — | 0.594622 | 0.297387 | 0.964973 |
| separate/closed/mixed/decrease_first/target_down | 32 | 0 | 32 | 0 | — | 0.563665 | 0.281915 | 0.965119 |
| separate/closed/mixed/decrease_first/target_up | 32 | 0 | 20 | 0 | — | 0.648474 | 0.345089 | 0.843362 |

The summary JSON also includes seed-bootstrap intervals for miss, recovery and joint rates, q maxima, signed event error, pre-event MSE, post-20/100/200 MSE and censored recovery latency. The conditional recovered/missed ratio is descriptive; its denominator is shown explicitly.

## Absolute learning metrics: diagnostics

| Setup/mode/fixture/coordinate | Finite seeds | Excess MSE | Post-200 MSE | Stable MSE | Adaptation latency | Mean update norm | Settled q |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| coupled/fixed/core/quiet | 32 | 1.000000 | — | 1.000000 | — | 0.000000 | 0.030979 |
| coupled/fixed/core/noisy | 32 | 1.000000 | — | 1.000000 | — | 0.000000 | 0.031755 |
| coupled/fixed/core/switch_quiet | 32 | 1.000000 | 1.000000 | 1.000000 | 1000.000000 | 0.000000 | 0.071976 |
| coupled/fixed/core/switch_noisy | 32 | 1.000000 | 1.000000 | 1.000000 | 1000.000000 | 0.000000 | 0.051542 |
| coupled/fixed/noise_jump/noise_jump | 32 | 1.000000 | — | 1.000000 | — | 0.000000 | 0.031088 |
| coupled/fixed/drift/drift | 32 | 0.729379 | — | 0.729379 | — | 0.000000 | 0.255791 |
| coupled/fixed/exactly_quiet/exactly_quiet | 32 | 1.000000 | — | 1.000000 | — | 0.000000 | 0.000000 |
| coupled/fixed/mixed/increase_first | 32 | 1.000000 | 1.000000 | 1.000000 | 1000.000000 | 0.000000 | 0.060692 |
| coupled/fixed/mixed/decrease_first | 32 | 1.000000 | 1.000000 | 1.000000 | 1000.000000 | 0.000000 | 0.061061 |
| coupled/closed/core/quiet | 32 | 0.045402 | — | 0.045402 | — | 0.023524 | 0.083632 |
| coupled/closed/core/noisy | 32 | 0.015602 | — | 0.015602 | — | 0.023524 | 0.035230 |
| coupled/closed/core/switch_quiet | 32 | 0.055756 | 0.529733 | 0.014541 | 132.281250 | 0.023524 | 0.076251 |
| coupled/closed/core/switch_noisy | 32 | 0.036223 | 0.281206 | 0.014920 | 55.406250 | 0.023524 | 0.038980 |
| coupled/closed/noise_jump/noise_jump | 32 | 0.016673 | — | 0.016673 | — | 0.004332 | 0.047470 |
| coupled/closed/drift/drift | 32 | 0.046752 | — | 0.046752 | — | 0.010913 | 0.086434 |
| coupled/closed/exactly_quiet/exactly_quiet | 32 | 0.000000 | — | 0.000000 | — | 0.000426 | 0.000000 |
| coupled/closed/mixed/increase_first | 32 | 0.038041 | 0.327745 | 0.012850 | 56.812500 | 0.008340 | 0.055018 |
| coupled/closed/mixed/decrease_first | 32 | 0.032881 | 0.291435 | 0.010398 | 56.625000 | 0.008340 | 0.045196 |
| watch_adam/fixed/core/quiet | 32 | 1.000000 | — | 1.000000 | — | 0.000000 | 0.030979 |
| watch_adam/fixed/core/noisy | 32 | 1.000000 | — | 1.000000 | — | 0.000000 | 0.031755 |
| watch_adam/fixed/core/switch_quiet | 32 | 1.000000 | 1.000000 | 1.000000 | 1000.000000 | 0.000000 | 0.071976 |
| watch_adam/fixed/core/switch_noisy | 32 | 1.000000 | 1.000000 | 1.000000 | 1000.000000 | 0.000000 | 0.051542 |
| watch_adam/fixed/noise_jump/noise_jump | 32 | 1.000000 | — | 1.000000 | — | 0.000000 | 0.031088 |
| watch_adam/fixed/drift/drift | 32 | 0.729379 | — | 0.729379 | — | 0.000000 | 0.255791 |
| watch_adam/fixed/exactly_quiet/exactly_quiet | 32 | 1.000000 | — | 1.000000 | — | 0.000000 | 0.000000 |
| watch_adam/fixed/mixed/increase_first | 32 | 1.000000 | 1.000000 | 1.000000 | 1000.000000 | 0.000000 | 0.060692 |
| watch_adam/fixed/mixed/decrease_first | 32 | 1.000000 | 1.000000 | 1.000000 | 1000.000000 | 0.000000 | 0.061061 |
| watch_adam/closed/core/quiet | 32 | 0.000060 | — | 0.000060 | — | 0.002240 | 0.033575 |
| watch_adam/closed/core/noisy | 32 | 0.001997 | — | 0.001997 | — | 0.002240 | 0.032823 |
| watch_adam/closed/core/switch_quiet | 32 | 0.078211 | 0.960795 | 0.001464 | 226.171875 | 0.002240 | 0.151035 |
| watch_adam/closed/core/switch_noisy | 32 | 0.239272 | 2.220274 | 0.067010 | 675.359375 | 0.002240 | 0.052576 |
| watch_adam/closed/noise_jump/noise_jump | 32 | 0.001174 | — | 0.001174 | — | 0.000594 | 0.033249 |
| watch_adam/closed/drift/drift | 32 | 0.000302 | — | 0.000302 | — | 0.000744 | 0.034796 |
| watch_adam/closed/exactly_quiet/exactly_quiet | 32 | 0.000000 | — | 0.000000 | — | 0.000167 | 0.000141 |
| watch_adam/closed/mixed/increase_first | 32 | 0.152744 | 1.597301 | 0.027131 | 438.421875 | 0.001759 | 0.148913 |
| watch_adam/closed/mixed/decrease_first | 32 | 0.180410 | 1.845011 | 0.035662 | 509.921875 | 0.001759 | 0.153660 |
| separate/fixed/core/quiet | 32 | 1.000000 | — | 1.000000 | — | 0.000000 | 0.030979 |
| separate/fixed/core/noisy | 32 | 1.000000 | — | 1.000000 | — | 0.000000 | 0.031755 |
| separate/fixed/core/switch_quiet | 32 | 1.000000 | 1.000000 | 1.000000 | 1000.000000 | 0.000000 | 0.071976 |
| separate/fixed/core/switch_noisy | 32 | 1.000000 | 1.000000 | 1.000000 | 1000.000000 | 0.000000 | 0.051542 |
| separate/fixed/noise_jump/noise_jump | 32 | 1.000000 | — | 1.000000 | — | 0.000000 | 0.031088 |
| separate/fixed/drift/drift | 32 | 0.729379 | — | 0.729379 | — | 0.000000 | 0.255791 |
| separate/fixed/exactly_quiet/exactly_quiet | 32 | 1.000000 | — | 1.000000 | — | 0.000000 | 0.000000 |
| separate/fixed/mixed/increase_first | 32 | 1.000000 | 1.000000 | 1.000000 | 1000.000000 | 0.000000 | 0.060692 |
| separate/fixed/mixed/decrease_first | 32 | 1.000000 | 1.000000 | 1.000000 | 1000.000000 | 0.000000 | 0.061061 |
| separate/closed/core/quiet | 32 | 0.000324 | — | 0.000324 | — | 0.010928 | 0.030979 |
| separate/closed/core/noisy | 32 | 0.025039 | — | 0.025039 | — | 0.010928 | 0.031755 |
| separate/closed/core/switch_quiet | 32 | 0.020821 | 0.257348 | 0.000254 | 54.375000 | 0.010928 | 0.071976 |
| separate/closed/core/switch_noisy | 32 | 0.048322 | 0.327314 | 0.024062 | 68.046875 | 0.010928 | 0.051542 |
| separate/closed/noise_jump/noise_jump | 32 | 0.015562 | — | 0.015562 | — | 0.002091 | 0.031088 |
| separate/closed/drift/drift | 32 | 0.001074 | — | 0.001074 | — | 0.006180 | 0.255791 |
| separate/closed/exactly_quiet/exactly_quiet | 32 | 0.000000 | — | 0.000000 | — | 0.000167 | 0.000000 |
| separate/closed/mixed/increase_first | 32 | 0.038161 | 0.335716 | 0.012287 | 68.609375 | 0.008126 | 0.060692 |
| separate/closed/mixed/decrease_first | 32 | 0.040547 | 0.313502 | 0.016811 | 67.250000 | 0.008126 | 0.061061 |

Update norms are for the fixture vector, repeated across its coordinates for context. Finite-seed counts expose failed trajectories; missing required performance rows cannot pass.

## Limits

Separate observes a fixed zero reference. Its fixed/active gate sequences are identical by construction; their two sets of cells are not independent replications. The toy exposes supervised observations; this does not establish an efficient reference-gradient mechanism for a general neural model.

Native detector criteria remain >=80% target detection and <=5% false alarms in every registered cell, including mixed changes. All 90 performance contrasts must pass for positive. Settings are fixed/transferred, not globally optimized; matching mean q does not match realized update norms. A common-threshold improvement cannot repair the native decision. Diagnostic prediction metrics cannot substitute for the independent performance partition.

Intervals use 10,000 whole-seed bootstrap resamples, seed 65000. Point screens and degenerate zero/one-rate bootstrap intervals are not population guarantees. No agent/default integration follows. Every old experiment remains intact.

Reproduce every reached row and summary with `python check_v3_reference.py --evidence results/v3-reference --reproduce`; check this report with `python report_v3_reference.py --check`. Numerical tolerance is rtol 1e-11/atol 1e-13, excluding only timing and regenerated input hashes.
