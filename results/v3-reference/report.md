# V3 separate-reference experiment

Disposition: **learning_negative**.

| Stage | Rows |
| --- | ---: |
| calibration | 48 |
| diagnostics | 96 |
| performance | 224 |

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

## Independent performance: all 90 required contrasts

| Contrast | Control | Separate | Difference | 95% interval | Pass |
| --- | ---: | ---: | ---: | --- | --- |
| coupled/primary | 0.350430 | 0.304365 | -0.046064 | [-0.061334, -0.030153] | True |
| coupled/quiet | 0.046966 | 0.000330 | -0.046636 | [-0.048919, -0.044452] | True |
| coupled/noisy | 0.014555 | 0.022847 | 0.008292 | [0.007197, 0.009376] | False |
| coupled/switch_quiet | 0.512758 | 0.252896 | -0.259862 | [-0.303217, -0.212379] | True |
| coupled/switch_noisy | 0.293390 | 0.341557 | 0.048167 | [0.037360, 0.058487] | False |
| coupled/noise_jump | 0.014791 | 0.015048 | 0.000257 | [-0.002626, 0.002889] | False |
| coupled/drift | 0.046792 | 0.001053 | -0.045739 | [-0.048447, -0.043066] | True |
| coupled/exactly_quiet | 0.000000 | 0.000000 | 0.000000 | [0.000000, 0.000000] | True |
| coupled/noise_jump/noise_increase | 0.062884 | 0.066437 | 0.003553 | [-0.022573, 0.022317] | False |
| coupled/noise_jump/noise_decrease | 0.001843 | 0.003746 | 0.001904 | [0.000511, 0.003598] | False |
| coupled/drift/drift | 0.051803 | 0.002081 | -0.049722 | [-0.057197, -0.042093] | True |
| coupled/mixed/increase_first/post_mse | 0.325236 | 0.322582 | -0.002655 | [-0.035381, 0.026440] | True |
| coupled/mixed/increase_first/stable_mse | 0.012631 | 0.013250 | 0.000619 | [-0.002068, 0.003084] | False |
| coupled/mixed/decrease_first/post_mse | 0.270336 | 0.300427 | 0.030091 | [0.019961, 0.038840] | False |
| coupled/mixed/decrease_first/stable_mse | 0.009782 | 0.015448 | 0.005665 | [0.004577, 0.006845] | False |
| watch_adam/primary | 1.669829 | 0.304365 | -1.365463 | [-1.376733, -1.353771] | True |
| watch_adam/quiet | 0.000060 | 0.000330 | 0.000270 | [0.000256, 0.000284] | True |
| watch_adam/noisy | 0.001691 | 0.022847 | 0.021156 | [0.019482, 0.022800] | False |
| watch_adam/switch_quiet | 0.958427 | 0.252896 | -0.705531 | [-0.708774, -0.702334] | True |
| watch_adam/switch_noisy | 2.236579 | 0.341557 | -1.895022 | [-1.929638, -1.859756] | True |
| watch_adam/noise_jump | 0.001262 | 0.015048 | 0.013786 | [0.012050, 0.015545] | False |
| watch_adam/drift | 0.000301 | 0.001053 | 0.000752 | [0.000722, 0.000781] | True |
| watch_adam/exactly_quiet | 0.000000 | 0.000000 | 0.000000 | [0.000000, 0.000000] | True |
| watch_adam/noise_jump/noise_increase | 0.006683 | 0.066437 | 0.059754 | [0.045730, 0.074724] | False |
| watch_adam/noise_jump/noise_decrease | 0.000912 | 0.003746 | 0.002834 | [0.001166, 0.004928] | False |
| watch_adam/drift/drift | 0.000650 | 0.002081 | 0.001431 | [0.001356, 0.001501] | True |
| watch_adam/mixed/increase_first/post_mse | 1.622444 | 0.322582 | -1.299863 | [-1.321590, -1.278289] | True |
| watch_adam/mixed/increase_first/stable_mse | 0.027875 | 0.013250 | -0.014625 | [-0.016206, -0.012938] | True |
| watch_adam/mixed/decrease_first/post_mse | 1.861865 | 0.300427 | -1.561438 | [-1.586395, -1.536178] | True |
| watch_adam/mixed/decrease_first/stable_mse | 0.035814 | 0.015448 | -0.020366 | [-0.022035, -0.018594] | True |
| adam/primary | 0.300031 | 0.304365 | 0.004335 | [-0.002513, 0.011755] | False |
| adam/quiet | 0.000514 | 0.000330 | -0.000184 | [-0.000199, -0.000170] | True |
| adam/noisy | 0.015314 | 0.022847 | 0.007533 | [0.006296, 0.008723] | False |
| adam/switch_quiet | 0.130679 | 0.252896 | 0.122217 | [0.118550, 0.125612] | False |
| adam/switch_noisy | 0.428602 | 0.341557 | -0.087045 | [-0.107212, -0.065653] | True |
| adam/noise_jump | 0.013060 | 0.015048 | 0.001988 | [0.000715, 0.003307] | False |
| adam/drift | 0.000513 | 0.001053 | 0.000540 | [0.000514, 0.000565] | True |
| adam/exactly_quiet | 0.000000 | 0.000000 | 0.000000 | [0.000000, 0.000000] | True |
| adam/noise_jump/noise_increase | 0.071315 | 0.066437 | -0.004878 | [-0.013907, 0.004805] | True |
| adam/noise_jump/noise_decrease | 0.001563 | 0.003746 | 0.002184 | [0.000598, 0.004124] | False |
| adam/drift/drift | 0.000506 | 0.002081 | 0.001575 | [0.001498, 0.001645] | True |
| adam/mixed/increase_first/post_mse | 0.265398 | 0.322582 | 0.057184 | [0.045593, 0.069470] | False |
| adam/mixed/increase_first/stable_mse | 0.011048 | 0.013250 | 0.002202 | [0.000974, 0.003547] | False |
| adam/mixed/decrease_first/post_mse | 0.375445 | 0.300427 | -0.075017 | [-0.090779, -0.058513] | True |
| adam/mixed/decrease_first/stable_mse | 0.010753 | 0.015448 | 0.004695 | [0.003490, 0.005960] | False |
| sgd/primary | 0.294674 | 0.304365 | 0.009691 | [0.002494, 0.017412] | False |
| sgd/quiet | 0.000044 | 0.000330 | 0.000286 | [0.000270, 0.000301] | True |
| sgd/noisy | 0.017647 | 0.022847 | 0.005199 | [0.003970, 0.006395] | False |
| sgd/switch_quiet | 0.284503 | 0.252896 | -0.031607 | [-0.035537, -0.027948] | True |
| sgd/switch_noisy | 0.301805 | 0.341557 | 0.039752 | [0.020380, 0.060175] | False |
| sgd/noise_jump | 0.007446 | 0.015048 | 0.007602 | [0.006080, 0.009169] | False |
| sgd/drift | 0.000352 | 0.001053 | 0.000701 | [0.000670, 0.000730] | True |
| sgd/exactly_quiet | 0.000000 | 0.000000 | 0.000000 | [0.000000, 0.000000] | True |
| sgd/noise_jump/noise_increase | 0.019015 | 0.066437 | 0.047422 | [0.034759, 0.061174] | False |
| sgd/noise_jump/noise_decrease | 0.000871 | 0.003746 | 0.002876 | [0.001296, 0.004888] | False |
| sgd/drift/drift | 0.000804 | 0.002081 | 0.001277 | [0.001207, 0.001341] | True |
| sgd/mixed/increase_first/post_mse | 0.293549 | 0.322582 | 0.029032 | [0.013041, 0.044608] | False |
| sgd/mixed/increase_first/stable_mse | 0.007416 | 0.013250 | 0.005834 | [0.004423, 0.007368] | False |
| sgd/mixed/decrease_first/post_mse | 0.298840 | 0.300427 | 0.001588 | [-0.014781, 0.018006] | True |
| sgd/mixed/decrease_first/stable_mse | 0.010486 | 0.015448 | 0.004961 | [0.003748, 0.006252] | False |
| single/primary | 0.379332 | 0.304365 | -0.074967 | [-0.082333, -0.066979] | True |
| single/quiet | 0.000308 | 0.000330 | 0.000022 | [0.000011, 0.000033] | True |
| single/noisy | 0.011184 | 0.022847 | 0.011663 | [0.010342, 0.012974] | False |
| single/switch_quiet | 0.161158 | 0.252896 | 0.091738 | [0.088182, 0.095076] | False |
| single/switch_noisy | 0.519663 | 0.341557 | -0.178106 | [-0.200851, -0.153950] | True |
| single/noise_jump | 0.007314 | 0.015048 | 0.007733 | [0.006334, 0.009185] | False |
| single/drift | 0.000315 | 0.001053 | 0.000738 | [0.000712, 0.000762] | True |
| single/exactly_quiet | 0.000000 | 0.000000 | 0.000000 | [0.000000, 0.000000] | True |
| single/noise_jump/noise_increase | 0.041969 | 0.066437 | 0.024468 | [0.014988, 0.034618] | False |
| single/noise_jump/noise_decrease | 0.001613 | 0.003746 | 0.002133 | [0.000576, 0.004081] | False |
| single/drift/drift | 0.000324 | 0.002081 | 0.001757 | [0.001682, 0.001826] | True |
| single/mixed/increase_first/post_mse | 0.389639 | 0.322582 | -0.067057 | [-0.081537, -0.051931] | True |
| single/mixed/increase_first/stable_mse | 0.006235 | 0.013250 | 0.007015 | [0.005591, 0.008590] | False |
| single/mixed/decrease_first/post_mse | 0.446869 | 0.300427 | -0.146442 | [-0.162526, -0.129620] | True |
| single/mixed/decrease_first/stable_mse | 0.007784 | 0.015448 | 0.007664 | [0.006404, 0.008991] | False |
| constant/primary | 0.479283 | 0.304365 | -0.174918 | [-0.183278, -0.165844] | True |
| constant/quiet | 0.000211 | 0.000330 | 0.000119 | [0.000108, 0.000131] | True |
| constant/noisy | 0.005461 | 0.022847 | 0.017386 | [0.015882, 0.018870] | False |
| constant/switch_quiet | 0.159864 | 0.252896 | 0.093032 | [0.089475, 0.096385] | False |
| constant/switch_noisy | 0.709471 | 0.341557 | -0.367914 | [-0.392777, -0.342335] | True |
| constant/noise_jump | 0.004950 | 0.015048 | 0.010097 | [0.008603, 0.011645] | False |
| constant/drift | 0.000312 | 0.001053 | 0.000741 | [0.000716, 0.000765] | True |
| constant/exactly_quiet | 0.000000 | 0.000000 | 0.000000 | [0.000000, 0.000000] | True |
| constant/noise_jump/noise_increase | 0.029531 | 0.066437 | 0.036906 | [0.026314, 0.048387] | False |
| constant/noise_jump/noise_decrease | 0.001149 | 0.003746 | 0.002598 | [0.001009, 0.004616] | False |
| constant/drift/drift | 0.000320 | 0.002081 | 0.001761 | [0.001686, 0.001830] | True |
| constant/mixed/increase_first/post_mse | 0.480585 | 0.322582 | -0.158003 | [-0.173862, -0.141965] | True |
| constant/mixed/increase_first/stable_mse | 0.004192 | 0.013250 | 0.009057 | [0.007524, 0.010744] | False |
| constant/mixed/decrease_first/post_mse | 0.567212 | 0.300427 | -0.266785 | [-0.284819, -0.247841] | True |
| constant/mixed/decrease_first/stable_mse | 0.005256 | 0.015448 | 0.010192 | [0.008866, 0.011608] | False |

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

## Absolute learning metrics: performance

| Setup/mode/fixture/coordinate | Finite seeds | Excess MSE | Post-200 MSE | Stable MSE | Adaptation latency | Mean update norm | Settled q |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| adam/closed/core/quiet | 32 | 0.000514 | — | 0.000514 | — | 0.012190 | 0.000000 |
| adam/closed/core/noisy | 32 | 0.015314 | — | 0.015314 | — | 0.012190 | 0.000000 |
| adam/closed/core/switch_quiet | 32 | 0.010773 | 0.130679 | 0.000347 | 33.796875 | 0.012190 | 0.000000 |
| adam/closed/core/switch_noisy | 32 | 0.048782 | 0.428602 | 0.015754 | 61.359375 | 0.012190 | 0.000000 |
| adam/closed/noise_jump/noise_jump | 32 | 0.013060 | — | 0.013060 | — | 0.005031 | 0.000000 |
| adam/closed/drift/drift | 32 | 0.000513 | — | 0.000513 | — | 0.003632 | 0.000000 |
| adam/closed/exactly_quiet/exactly_quiet | 32 | 0.000000 | — | 0.000000 | — | 0.000187 | 0.000000 |
| adam/closed/mixed/increase_first | 32 | 0.031396 | 0.265398 | 0.011048 | 46.500000 | 0.009470 | 0.000000 |
| adam/closed/mixed/decrease_first | 32 | 0.039928 | 0.375445 | 0.010753 | 52.109375 | 0.009470 | 0.000000 |
| constant/closed/core/quiet | 32 | 0.000211 | — | 0.000211 | — | 0.006442 | 0.029411 |
| constant/closed/core/noisy | 32 | 0.005461 | — | 0.005461 | — | 0.006442 | 0.031171 |
| constant/closed/core/switch_quiet | 32 | 0.013027 | 0.159864 | 0.000258 | 41.953125 | 0.006442 | 0.073326 |
| constant/closed/core/switch_noisy | 32 | 0.064581 | 0.709471 | 0.008504 | 132.390625 | 0.006442 | 0.051495 |
| constant/closed/noise_jump/noise_jump | 32 | 0.004950 | — | 0.004950 | — | 0.002099 | 0.046351 |
| constant/closed/drift/drift | 32 | 0.000312 | — | 0.000312 | — | 0.002196 | 0.046351 |
| constant/closed/exactly_quiet/exactly_quiet | 32 | 0.000000 | — | 0.000000 | — | 0.000167 | 0.046351 |
| constant/closed/mixed/increase_first | 32 | 0.042304 | 0.480585 | 0.004192 | 80.109375 | 0.004646 | 0.046351 |
| constant/closed/mixed/decrease_first | 32 | 0.050212 | 0.567212 | 0.005256 | 98.312500 | 0.004646 | 0.046351 |
| coupled/closed/core/quiet | 32 | 0.046966 | — | 0.046966 | — | 0.023864 | 0.083213 |
| coupled/closed/core/noisy | 32 | 0.014555 | — | 0.014555 | — | 0.023864 | 0.034622 |
| coupled/closed/core/switch_quiet | 32 | 0.055753 | 0.512758 | 0.016014 | 128.046875 | 0.023864 | 0.078838 |
| coupled/closed/core/switch_noisy | 32 | 0.037595 | 0.293390 | 0.015352 | 51.406250 | 0.023864 | 0.038982 |
| coupled/closed/noise_jump/noise_jump | 32 | 0.014791 | — | 0.014791 | — | 0.003672 | 0.044660 |
| coupled/closed/drift/drift | 32 | 0.046792 | — | 0.046792 | — | 0.011172 | 0.089105 |
| coupled/closed/exactly_quiet/exactly_quiet | 32 | 0.000000 | — | 0.000000 | — | 0.000426 | 0.000000 |
| coupled/closed/mixed/increase_first | 32 | 0.037639 | 0.325236 | 0.012631 | 61.359375 | 0.008078 | 0.055555 |
| coupled/closed/mixed/decrease_first | 32 | 0.030627 | 0.270336 | 0.009782 | 45.687500 | 0.008078 | 0.045160 |
| separate/closed/core/quiet | 32 | 0.000330 | — | 0.000330 | — | 0.010843 | 0.031103 |
| separate/closed/core/noisy | 32 | 0.022847 | — | 0.022847 | — | 0.010843 | 0.031466 |
| separate/closed/core/switch_quiet | 32 | 0.020479 | 0.252896 | 0.000269 | 54.250000 | 0.010843 | 0.072954 |
| separate/closed/core/switch_noisy | 32 | 0.048380 | 0.341557 | 0.022886 | 61.593750 | 0.010843 | 0.051375 |
| separate/closed/noise_jump/noise_jump | 32 | 0.015048 | — | 0.015048 | — | 0.002102 | 0.031658 |
| separate/closed/drift/drift | 32 | 0.001053 | — | 0.001053 | — | 0.006142 | 0.255416 |
| separate/closed/exactly_quiet/exactly_quiet | 32 | 0.000000 | — | 0.000000 | — | 0.000167 | 0.000000 |
| separate/closed/mixed/increase_first | 32 | 0.037996 | 0.322582 | 0.013250 | 67.593750 | 0.007906 | 0.061629 |
| separate/closed/mixed/decrease_first | 32 | 0.038246 | 0.300427 | 0.015448 | 62.890625 | 0.007906 | 0.060319 |
| sgd/closed/core/quiet | 32 | 0.000044 | — | 0.000044 | — | 0.045827 | 0.000000 |
| sgd/closed/core/noisy | 32 | 0.017647 | — | 0.017647 | — | 0.045827 | 0.000000 |
| sgd/closed/core/switch_quiet | 32 | 0.022803 | 0.284503 | 0.000046 | 63.703125 | 0.045827 | 0.000000 |
| sgd/closed/core/switch_noisy | 32 | 0.041004 | 0.301805 | 0.018325 | 67.031250 | 0.045827 | 0.000000 |
| sgd/closed/noise_jump/noise_jump | 32 | 0.007446 | — | 0.007446 | — | 0.010837 | 0.000000 |
| sgd/closed/drift/drift | 32 | 0.000352 | — | 0.000352 | — | 0.001648 | 0.000000 |
| sgd/closed/exactly_quiet/exactly_quiet | 32 | 0.000000 | — | 0.000000 | — | 0.000167 | 0.000000 |
| sgd/closed/mixed/increase_first | 32 | 0.030307 | 0.293549 | 0.007416 | 67.828125 | 0.029451 | 0.000000 |
| sgd/closed/mixed/decrease_first | 32 | 0.033554 | 0.298840 | 0.010486 | 69.546875 | 0.029451 | 0.000000 |
| single/closed/core/quiet | 32 | 0.000308 | — | 0.000308 | — | 0.008674 | 0.002681 |
| single/closed/core/noisy | 32 | 0.011184 | — | 0.011184 | — | 0.008674 | 0.477294 |
| single/closed/core/switch_quiet | 32 | 0.013054 | 0.161158 | 0.000175 | 42.203125 | 0.008674 | 0.007193 |
| single/closed/core/switch_noisy | 32 | 0.052337 | 0.519663 | 0.011700 | 87.187500 | 0.008674 | 0.479567 |
| single/closed/noise_jump/noise_jump | 32 | 0.007314 | — | 0.007314 | — | 0.002826 | 0.196579 |
| single/closed/drift/drift | 32 | 0.000315 | — | 0.000315 | — | 0.002222 | 0.002670 |
| single/closed/exactly_quiet/exactly_quiet | 32 | 0.000000 | — | 0.000000 | — | 0.000167 | 0.000000 |
| single/closed/mixed/increase_first | 32 | 0.036908 | 0.389639 | 0.006235 | 78.500000 | 0.006410 | 0.199237 |
| single/closed/mixed/decrease_first | 32 | 0.042911 | 0.446869 | 0.007784 | 79.953125 | 0.006410 | 0.287402 |
| watch_adam/closed/core/quiet | 32 | 0.000060 | — | 0.000060 | — | 0.002241 | 0.033191 |
| watch_adam/closed/core/noisy | 32 | 0.001691 | — | 0.001691 | — | 0.002241 | 0.032544 |
| watch_adam/closed/core/switch_quiet | 32 | 0.078019 | 0.958427 | 0.001461 | 226.031250 | 0.002241 | 0.152140 |
| watch_adam/closed/core/switch_noisy | 32 | 0.240817 | 2.236579 | 0.067273 | 670.500000 | 0.002241 | 0.052425 |
| watch_adam/closed/noise_jump/noise_jump | 32 | 0.001262 | — | 0.001262 | — | 0.000599 | 0.033864 |
| watch_adam/closed/drift/drift | 32 | 0.000301 | — | 0.000301 | — | 0.000745 | 0.035812 |
| watch_adam/closed/exactly_quiet/exactly_quiet | 32 | 0.000000 | — | 0.000000 | — | 0.000167 | 0.000141 |
| watch_adam/closed/mixed/increase_first | 32 | 0.155440 | 1.622444 | 0.027875 | 450.562500 | 0.001759 | 0.149957 |
| watch_adam/closed/mixed/decrease_first | 32 | 0.181898 | 1.861865 | 0.035814 | 508.000000 | 0.001759 | 0.152209 |

Update norms are for the fixture vector, repeated across its coordinates for context. Finite-seed counts expose failed trajectories; missing required performance rows cannot pass.

## Limits

Separate observes a fixed zero reference. Its fixed/active gate sequences are identical by construction; their two sets of cells are not independent replications. The toy exposes supervised observations; this does not establish an efficient reference-gradient mechanism for a general neural model.

Native detector criteria remain >=80% target detection and <=5% false alarms in every registered cell, including mixed changes. All 90 performance contrasts must pass for positive. Settings are fixed/transferred, not globally optimized; matching mean q does not match realized update norms. A common-threshold improvement cannot repair the native decision. Diagnostic prediction metrics cannot substitute for the independent performance partition.

Intervals use 10,000 whole-seed bootstrap resamples, seed 65000. Point screens and degenerate zero/one-rate bootstrap intervals are not population guarantees. No agent/default integration follows. Every old experiment remains intact.

Reproduce every reached row and summary with `python check_v3_reference.py --evidence results/v3-reference --reproduce`; check this report with `python report_v3_reference.py --check`. Numerical tolerance is rtol 1e-11/atol 1e-13, excluding only timing and regenerated input hashes.
