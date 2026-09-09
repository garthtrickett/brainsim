# V3 interference-as-discovery

Disposition: **discovery_negative**.

| Stage | Rows |
| --- | ---: |
| tuning | 480 |
| confirmation | 288 |

## Finite-menu tuning

Each searched family: 12 configurations × 8 seeds × 5 fixtures. Same objective: half primary post-switch MSE plus half mean of 14 retention metrics.

| Family | Index | Configuration | Tuning objective | Menu endpoint fields |
| --- | ---: | --- | ---: | --- |
| discover | 9 | `{"tau": 0.5, "alpha": 0.01, "cue_lr": 0.01, "lr": 0.2}` | 0.103299 | tau, alpha, cue_lr, lr |
| oracle | 4 | `{"tau": 0.05, "alpha": 0.1, "cue_lr": 0.01, "lr": 0.05}` | 0.032826 | tau, alpha, cue_lr, lr |
| window | 3 | `{"window": 8}` | 0.095185 | window |
| sgd | 8 | `{"lr": 0.128}` | 0.084388 | none |
| adwin | 9 | `{"delta": 0.1, "clock": 1}` | 0.127667 | delta, clock |

Endpoint choices remain in the registered finite menu; no extension or global-optimum claim. Matched oracle/random/shuffled/nocontext use the discover configuration without extra search.


## Independent primary performance

| Policy | Finite seeds | Primary MSE | 95% interval |
| --- | ---: | ---: | --- |
| discover | 32 | 0.137288 | [0.1343756723827616, 0.1400920307181493] |
| oracle | 32 | 0.047243 | [0.04579501675440085, 0.04871562135799787] |
| window | 32 | 0.123465 | [0.1203744309186509, 0.1265218462816915] |
| sgd | 32 | 0.114924 | [0.11242362531836864, 0.11736924531274023] |
| adwin | 32 | 0.191803 | [0.18638254673694563, 0.19740320052562876] |
| oracle_matched | 32 | 0.086099 | [0.0839619972547058, 0.0881482926328965] |
| random | 32 | 0.136749 | [0.13387665185810144, 0.13954926867276402] |
| shuffled | 32 | 0.138018 | [0.1355689517101496, 0.14053068716952616] |
| nocontext_matched | 32 | 0.112036 | [0.10936477771215582, 0.11464658203601309] |

## discover: learning_negative

All 90 candidate comparisons plus the discovery gate are required.

| Contrast | Control | Policy | Delta | 95% interval | Pass |
| --- | ---: | ---: | ---: | --- | --- |
| window/primary | 0.123465 | 0.137288 | 0.013823 | [0.011210, 0.016271] | False |
| window/quiet | 0.000310 | 0.000275 | -0.000035 | [-0.000036, -0.000034] | True |
| window/noisy | 0.125112 | 0.111100 | -0.014013 | [-0.015032, -0.013073] | True |
| window/switch_quiet | 0.063994 | 0.059325 | -0.004669 | [-0.004767, -0.004567] | True |
| window/switch_noisy | 0.186861 | 0.224808 | 0.037947 | [0.030556, 0.044908] | False |
| window/noise_jump | 0.049474 | 0.043570 | -0.005904 | [-0.006573, -0.005210] | True |
| window/drift | 0.000319 | 0.000286 | -0.000033 | [-0.000035, -0.000032] | True |
| window/exactly_quiet | 0.000000 | 0.000000 | 0.000000 | [0.000000, 0.000000] | True |
| window/noise_jump/noise_increase | 0.117908 | 0.097620 | -0.020287 | [-0.025988, -0.014916] | True |
| window/noise_jump/noise_decrease | 0.002874 | 0.003963 | 0.001089 | [0.000165, 0.002064] | False |
| window/drift/drift | 0.000330 | 0.000300 | -0.000030 | [-0.000032, -0.000027] | True |
| window/mixed/increase_first/post_mse | 0.122445 | 0.132083 | 0.009638 | [0.004461, 0.015009] | False |
| window/mixed/increase_first/stable_mse | 0.047249 | 0.042669 | -0.004579 | [-0.005439, -0.003696] | True |
| window/mixed/decrease_first/post_mse | 0.120559 | 0.132937 | 0.012378 | [0.006544, 0.018124] | False |
| window/mixed/decrease_first/stable_mse | 0.078079 | 0.069599 | -0.008479 | [-0.009475, -0.007470] | True |
| sgd/primary | 0.114924 | 0.137288 | 0.022364 | [0.020440, 0.024283] | False |
| sgd/quiet | 0.000169 | 0.000275 | 0.000106 | [0.000105, 0.000107] | True |
| sgd/noisy | 0.068288 | 0.111100 | 0.042811 | [0.042092, 0.043483] | False |
| sgd/switch_quiet | 0.083600 | 0.059325 | -0.024276 | [-0.024372, -0.024182] | True |
| sgd/switch_noisy | 0.149266 | 0.224808 | 0.075542 | [0.070308, 0.080904] | False |
| sgd/noise_jump | 0.027172 | 0.043570 | 0.016398 | [0.015701, 0.017096] | False |
| sgd/drift | 0.000195 | 0.000286 | 0.000091 | [0.000089, 0.000093] | True |
| sgd/exactly_quiet | 0.000000 | 0.000000 | -0.000000 | [-0.000000, -0.000000] | True |
| sgd/noise_jump/noise_increase | 0.062503 | 0.097620 | 0.035118 | [0.031640, 0.038791] | False |
| sgd/noise_jump/noise_decrease | 0.001405 | 0.003963 | 0.002558 | [0.001850, 0.003327] | False |
| sgd/drift/drift | 0.000232 | 0.000300 | 0.000068 | [0.000064, 0.000072] | True |
| sgd/mixed/increase_first/post_mse | 0.113405 | 0.132083 | 0.018678 | [0.014065, 0.023384] | False |
| sgd/mixed/increase_first/stable_mse | 0.025785 | 0.042669 | 0.016884 | [0.016172, 0.017588] | False |
| sgd/mixed/decrease_first/post_mse | 0.113423 | 0.132937 | 0.019514 | [0.013694, 0.025187] | False |
| sgd/mixed/decrease_first/stable_mse | 0.042799 | 0.069599 | 0.026800 | [0.025782, 0.027802] | False |
| adwin/primary | 0.191803 | 0.137288 | -0.054515 | [-0.059720, -0.049506] | True |
| adwin/quiet | 0.000001 | 0.000275 | 0.000274 | [0.000270, 0.000277] | True |
| adwin/noisy | 0.000683 | 0.111100 | 0.110417 | [0.108904, 0.111901] | False |
| adwin/switch_quiet | 0.150170 | 0.059325 | -0.090846 | [-0.093142, -0.088588] | True |
| adwin/switch_noisy | 0.232495 | 0.224808 | -0.007687 | [-0.018928, 0.003335] | True |
| adwin/noise_jump | 0.000792 | 0.043570 | 0.042778 | [0.041272, 0.044324] | False |
| adwin/drift | 0.003155 | 0.000286 | -0.002870 | [-0.002899, -0.002840] | True |
| adwin/exactly_quiet | 0.000000 | 0.000000 | 0.000000 | [0.000000, 0.000000] | True |
| adwin/noise_jump/noise_increase | 0.003675 | 0.097620 | 0.093945 | [0.087656, 0.100491] | False |
| adwin/noise_jump/noise_decrease | 0.000904 | 0.003963 | 0.003059 | [0.001713, 0.004352] | False |
| adwin/drift/drift | 0.007856 | 0.000300 | -0.007556 | [-0.007746, -0.007364] | True |
| adwin/mixed/increase_first/post_mse | 0.189789 | 0.132083 | -0.057706 | [-0.067180, -0.048460] | True |
| adwin/mixed/increase_first/stable_mse | 0.000662 | 0.042669 | 0.042008 | [0.040712, 0.043408] | False |
| adwin/mixed/decrease_first/post_mse | 0.194757 | 0.132937 | -0.061820 | [-0.071686, -0.052097] | True |
| adwin/mixed/decrease_first/stable_mse | 0.001045 | 0.069599 | 0.068554 | [0.066594, 0.070656] | False |
| random/primary | 0.136749 | 0.137288 | 0.000539 | [-0.002041, 0.003136] | False |
| random/quiet | 0.000275 | 0.000275 | 0.000000 | [0.000000, 0.000000] | True |
| random/noisy | 0.111647 | 0.111100 | -0.000547 | [-0.001792, 0.000682] | True |
| random/switch_quiet | 0.059325 | 0.059325 | 0.000000 | [0.000000, 0.000000] | True |
| random/switch_noisy | 0.218643 | 0.224808 | 0.006165 | [0.000308, 0.012350] | True |
| random/noise_jump | 0.043266 | 0.043570 | 0.000304 | [-0.000616, 0.001165] | True |
| random/drift | 0.000286 | 0.000286 | 0.000000 | [0.000000, 0.000000] | True |
| random/exactly_quiet | 0.000000 | 0.000000 | 0.000000 | [0.000000, 0.000000] | True |
| random/noise_jump/noise_increase | 0.095873 | 0.097620 | 0.001748 | [-0.003960, 0.007427] | True |
| random/noise_jump/noise_decrease | 0.003577 | 0.003963 | 0.000386 | [-0.000850, 0.001562] | True |
| random/drift/drift | 0.000300 | 0.000300 | 0.000000 | [0.000000, 0.000000] | True |
| random/mixed/increase_first/post_mse | 0.136212 | 0.132083 | -0.004129 | [-0.010577, 0.001894] | True |
| random/mixed/increase_first/stable_mse | 0.042279 | 0.042669 | 0.000390 | [-0.000540, 0.001314] | True |
| random/mixed/decrease_first/post_mse | 0.132815 | 0.132937 | 0.000122 | [-0.006600, 0.006887] | True |
| random/mixed/decrease_first/stable_mse | 0.069815 | 0.069599 | -0.000216 | [-0.001508, 0.001095] | True |
| shuffled/primary | 0.138018 | 0.137288 | -0.000730 | [-0.003169, 0.001702] | False |
| shuffled/quiet | 0.000275 | 0.000275 | 0.000000 | [0.000000, 0.000000] | True |
| shuffled/noisy | 0.111666 | 0.111100 | -0.000566 | [-0.001767, 0.000659] | True |
| shuffled/switch_quiet | 0.059325 | 0.059325 | 0.000000 | [0.000000, 0.000000] | True |
| shuffled/switch_noisy | 0.221814 | 0.224808 | 0.002994 | [-0.002434, 0.008278] | True |
| shuffled/noise_jump | 0.044031 | 0.043570 | -0.000461 | [-0.001454, 0.000506] | True |
| shuffled/drift | 0.000286 | 0.000286 | 0.000000 | [0.000000, 0.000000] | True |
| shuffled/exactly_quiet | 0.000000 | 0.000000 | 0.000000 | [0.000000, 0.000000] | True |
| shuffled/noise_jump/noise_increase | 0.098207 | 0.097620 | -0.000586 | [-0.005886, 0.004891] | True |
| shuffled/noise_jump/noise_decrease | 0.003215 | 0.003963 | 0.000748 | [-0.000187, 0.001690] | True |
| shuffled/drift/drift | 0.000300 | 0.000300 | 0.000000 | [0.000000, 0.000000] | True |
| shuffled/mixed/increase_first/post_mse | 0.134849 | 0.132083 | -0.002766 | [-0.009233, 0.003873] | True |
| shuffled/mixed/increase_first/stable_mse | 0.042972 | 0.042669 | -0.000302 | [-0.001103, 0.000495] | True |
| shuffled/mixed/decrease_first/post_mse | 0.136083 | 0.132937 | -0.003146 | [-0.009146, 0.002513] | True |
| shuffled/mixed/decrease_first/stable_mse | 0.069062 | 0.069599 | 0.000537 | [-0.000775, 0.001931] | True |
| nocontext_matched/primary | 0.112036 | 0.137288 | 0.025253 | [0.023165, 0.027384] | False |
| nocontext_matched/quiet | 0.000275 | 0.000275 | 0.000000 | [0.000000, 0.000000] | True |
| nocontext_matched/noisy | 0.050735 | 0.111100 | 0.060365 | [0.059496, 0.061188] | False |
| nocontext_matched/switch_quiet | 0.059325 | 0.059325 | 0.000000 | [0.000000, 0.000000] | True |
| nocontext_matched/switch_noisy | 0.160839 | 0.224808 | 0.063969 | [0.058134, 0.069825] | False |
| nocontext_matched/noise_jump | 0.021111 | 0.043570 | 0.022458 | [0.021538, 0.023394] | False |
| nocontext_matched/drift | 0.000286 | 0.000286 | 0.000000 | [0.000000, 0.000000] | True |
| nocontext_matched/exactly_quiet | 0.000000 | 0.000000 | 0.000000 | [0.000000, 0.000000] | True |
| nocontext_matched/noise_jump/noise_increase | 0.062981 | 0.097620 | 0.034640 | [0.030826, 0.038520] | False |
| nocontext_matched/noise_jump/noise_decrease | 0.001306 | 0.003963 | 0.002657 | [0.001959, 0.003409] | False |
| nocontext_matched/drift/drift | 0.000300 | 0.000300 | 0.000000 | [0.000000, 0.000000] | True |
| nocontext_matched/mixed/increase_first/post_mse | 0.114331 | 0.132083 | 0.017752 | [0.012644, 0.022719] | False |
| nocontext_matched/mixed/increase_first/stable_mse | 0.019322 | 0.042669 | 0.023348 | [0.022516, 0.024212] | False |
| nocontext_matched/mixed/decrease_first/post_mse | 0.113648 | 0.132937 | 0.019289 | [0.013459, 0.024995] | False |
| nocontext_matched/mixed/decrease_first/stable_mse | 0.031938 | 0.069599 | 0.037662 | [0.036401, 0.038903] | False |

## oracle: oracle_negative

Privileged diagnostic: cannot authorize candidate advancement.

| Contrast | Control | Policy | Delta | 95% interval | Pass |
| --- | ---: | ---: | ---: | --- | --- |
| window/primary | 0.123465 | 0.047243 | -0.076222 | [-0.078985, -0.073516] | True |
| window/quiet | 0.000310 | 0.000063 | -0.000247 | [-0.000250, -0.000243] | True |
| window/noisy | 0.125112 | 0.025440 | -0.099673 | [-0.101166, -0.098259] | True |
| window/switch_quiet | 0.063994 | 0.043814 | -0.020180 | [-0.020468, -0.019910] | True |
| window/switch_noisy | 0.186861 | 0.050027 | -0.136834 | [-0.143468, -0.130162] | True |
| window/noise_jump | 0.049474 | 0.010179 | -0.039295 | [-0.040618, -0.037989] | True |
| window/drift | 0.000319 | 0.000227 | -0.000092 | [-0.000101, -0.000082] | True |
| window/exactly_quiet | 0.000000 | 0.000000 | 0.000000 | [0.000000, 0.000000] | True |
| window/noise_jump/noise_increase | 0.117908 | 0.021511 | -0.096397 | [-0.103910, -0.089378] | True |
| window/noise_jump/noise_decrease | 0.002874 | 0.001058 | -0.001816 | [-0.002561, -0.001123] | True |
| window/drift/drift | 0.000330 | 0.000483 | 0.000153 | [0.000127, 0.000180] | True |
| window/mixed/increase_first/post_mse | 0.122445 | 0.045592 | -0.076852 | [-0.082022, -0.071778] | True |
| window/mixed/increase_first/stable_mse | 0.047249 | 0.009678 | -0.037570 | [-0.038922, -0.036259] | True |
| window/mixed/decrease_first/post_mse | 0.120559 | 0.049537 | -0.071022 | [-0.075542, -0.066329] | True |
| window/mixed/decrease_first/stable_mse | 0.078079 | 0.016152 | -0.061927 | [-0.063710, -0.060208] | True |
| sgd/primary | 0.114924 | 0.047243 | -0.067681 | [-0.069559, -0.065745] | True |
| sgd/quiet | 0.000169 | 0.000063 | -0.000106 | [-0.000108, -0.000105] | True |
| sgd/noisy | 0.068288 | 0.025440 | -0.042849 | [-0.043507, -0.042237] | True |
| sgd/switch_quiet | 0.083600 | 0.043814 | -0.039787 | [-0.040052, -0.039532] | True |
| sgd/switch_noisy | 0.149266 | 0.050027 | -0.099239 | [-0.103283, -0.094915] | True |
| sgd/noise_jump | 0.027172 | 0.010179 | -0.016993 | [-0.017623, -0.016406] | True |
| sgd/drift | 0.000195 | 0.000227 | 0.000032 | [0.000026, 0.000039] | True |
| sgd/exactly_quiet | 0.000000 | 0.000000 | 0.000000 | [0.000000, 0.000000] | True |
| sgd/noise_jump/noise_increase | 0.062503 | 0.021511 | -0.040992 | [-0.044040, -0.038160] | True |
| sgd/noise_jump/noise_decrease | 0.001405 | 0.001058 | -0.000348 | [-0.000694, 0.000005] | True |
| sgd/drift/drift | 0.000232 | 0.000483 | 0.000251 | [0.000229, 0.000273] | True |
| sgd/mixed/increase_first/post_mse | 0.113405 | 0.045592 | -0.067813 | [-0.071739, -0.063961] | True |
| sgd/mixed/increase_first/stable_mse | 0.025785 | 0.009678 | -0.016107 | [-0.016670, -0.015571] | True |
| sgd/mixed/decrease_first/post_mse | 0.113423 | 0.049537 | -0.063886 | [-0.068391, -0.059143] | True |
| sgd/mixed/decrease_first/stable_mse | 0.042799 | 0.016152 | -0.026647 | [-0.027352, -0.025963] | True |
| adwin/primary | 0.191803 | 0.047243 | -0.144560 | [-0.149687, -0.139672] | True |
| adwin/quiet | 0.000001 | 0.000063 | 0.000062 | [0.000060, 0.000063] | True |
| adwin/noisy | 0.000683 | 0.025440 | 0.024757 | [0.024163, 0.025366] | False |
| adwin/switch_quiet | 0.150170 | 0.043814 | -0.106357 | [-0.108727, -0.104018] | True |
| adwin/switch_noisy | 0.232495 | 0.050027 | -0.182468 | [-0.193028, -0.172324] | True |
| adwin/noise_jump | 0.000792 | 0.010179 | 0.009387 | [0.008852, 0.009918] | False |
| adwin/drift | 0.003155 | 0.000227 | -0.002928 | [-0.002955, -0.002903] | True |
| adwin/exactly_quiet | 0.000000 | 0.000000 | 0.000000 | [0.000000, 0.000000] | True |
| adwin/noise_jump/noise_increase | 0.003675 | 0.021511 | 0.017836 | [0.015381, 0.020612] | False |
| adwin/noise_jump/noise_decrease | 0.000904 | 0.001058 | 0.000154 | [-0.000729, 0.000935] | True |
| adwin/drift/drift | 0.007856 | 0.000483 | -0.007373 | [-0.007538, -0.007206] | True |
| adwin/mixed/increase_first/post_mse | 0.189789 | 0.045592 | -0.144197 | [-0.152121, -0.136476] | True |
| adwin/mixed/increase_first/stable_mse | 0.000662 | 0.009678 | 0.009017 | [0.008457, 0.009597] | False |
| adwin/mixed/decrease_first/post_mse | 0.194757 | 0.049537 | -0.145219 | [-0.153712, -0.136900] | True |
| adwin/mixed/decrease_first/stable_mse | 0.001045 | 0.016152 | 0.015107 | [0.014401, 0.015848] | False |

## oracle_matched: oracle_negative

Privileged diagnostic: cannot authorize candidate advancement.

| Contrast | Control | Policy | Delta | 95% interval | Pass |
| --- | ---: | ---: | ---: | --- | --- |
| window/primary | 0.123465 | 0.086099 | -0.037366 | [-0.039478, -0.035388] | True |
| window/quiet | 0.000310 | 0.000275 | -0.000035 | [-0.000036, -0.000034] | True |
| window/noisy | 0.125112 | 0.111202 | -0.013910 | [-0.014393, -0.013443] | True |
| window/switch_quiet | 0.063994 | 0.059325 | -0.004669 | [-0.004767, -0.004567] | True |
| window/switch_noisy | 0.186861 | 0.117790 | -0.069071 | [-0.074275, -0.063769] | True |
| window/noise_jump | 0.049474 | 0.043760 | -0.005714 | [-0.006008, -0.005411] | True |
| window/drift | 0.000319 | 0.000286 | -0.000033 | [-0.000035, -0.000032] | True |
| window/exactly_quiet | 0.000000 | 0.000000 | 0.000000 | [0.000000, 0.000000] | True |
| window/noise_jump/noise_increase | 0.117908 | 0.097603 | -0.020305 | [-0.023748, -0.017258] | True |
| window/noise_jump/noise_decrease | 0.002874 | 0.001609 | -0.001265 | [-0.001704, -0.000890] | True |
| window/drift/drift | 0.000330 | 0.000300 | -0.000030 | [-0.000032, -0.000027] | True |
| window/mixed/increase_first/post_mse | 0.122445 | 0.080321 | -0.042123 | [-0.046516, -0.038155] | True |
| window/mixed/increase_first/stable_mse | 0.047249 | 0.042064 | -0.005185 | [-0.005535, -0.004829] | True |
| window/mixed/decrease_first/post_mse | 0.120559 | 0.086960 | -0.033599 | [-0.037422, -0.029710] | True |
| window/mixed/decrease_first/stable_mse | 0.078079 | 0.069434 | -0.008644 | [-0.009173, -0.008117] | True |
| sgd/primary | 0.114924 | 0.086099 | -0.028825 | [-0.030687, -0.026942] | True |
| sgd/quiet | 0.000169 | 0.000275 | 0.000106 | [0.000105, 0.000107] | True |
| sgd/noisy | 0.068288 | 0.111202 | 0.042914 | [0.042447, 0.043410] | False |
| sgd/switch_quiet | 0.083600 | 0.059325 | -0.024276 | [-0.024372, -0.024182] | True |
| sgd/switch_noisy | 0.149266 | 0.117790 | -0.031476 | [-0.037588, -0.024972] | True |
| sgd/noise_jump | 0.027172 | 0.043760 | 0.016588 | [0.016079, 0.017109] | False |
| sgd/drift | 0.000195 | 0.000286 | 0.000091 | [0.000089, 0.000093] | True |
| sgd/exactly_quiet | 0.000000 | 0.000000 | -0.000000 | [-0.000000, -0.000000] | True |
| sgd/noise_jump/noise_increase | 0.062503 | 0.097603 | 0.035100 | [0.032678, 0.037506] | False |
| sgd/noise_jump/noise_decrease | 0.001405 | 0.001609 | 0.000203 | [0.000030, 0.000367] | True |
| sgd/drift/drift | 0.000232 | 0.000300 | 0.000068 | [0.000064, 0.000072] | True |
| sgd/mixed/increase_first/post_mse | 0.113405 | 0.080321 | -0.033084 | [-0.037107, -0.029287] | True |
| sgd/mixed/increase_first/stable_mse | 0.025785 | 0.042064 | 0.016278 | [0.015743, 0.016843] | False |
| sgd/mixed/decrease_first/post_mse | 0.113423 | 0.086960 | -0.026463 | [-0.030257, -0.022734] | True |
| sgd/mixed/decrease_first/stable_mse | 0.042799 | 0.069434 | 0.026635 | [0.026002, 0.027300] | False |
| adwin/primary | 0.191803 | 0.086099 | -0.105704 | [-0.111118, -0.100468] | True |
| adwin/quiet | 0.000001 | 0.000275 | 0.000274 | [0.000270, 0.000277] | True |
| adwin/noisy | 0.000683 | 0.111202 | 0.110519 | [0.109107, 0.112016] | False |
| adwin/switch_quiet | 0.150170 | 0.059325 | -0.090846 | [-0.093142, -0.088588] | True |
| adwin/switch_noisy | 0.232495 | 0.117790 | -0.114705 | [-0.127376, -0.102462] | True |
| adwin/noise_jump | 0.000792 | 0.043760 | 0.042968 | [0.041451, 0.044549] | False |
| adwin/drift | 0.003155 | 0.000286 | -0.002870 | [-0.002899, -0.002840] | True |
| adwin/exactly_quiet | 0.000000 | 0.000000 | 0.000000 | [0.000000, 0.000000] | True |
| adwin/noise_jump/noise_increase | 0.003675 | 0.097603 | 0.093928 | [0.087769, 0.100091] | False |
| adwin/noise_jump/noise_decrease | 0.000904 | 0.001609 | 0.000705 | [-0.000272, 0.001666] | True |
| adwin/drift/drift | 0.007856 | 0.000300 | -0.007556 | [-0.007746, -0.007364] | True |
| adwin/mixed/increase_first/post_mse | 0.189789 | 0.080321 | -0.109468 | [-0.118632, -0.100715] | True |
| adwin/mixed/increase_first/stable_mse | 0.000662 | 0.042064 | 0.041402 | [0.039974, 0.042932] | False |
| adwin/mixed/decrease_first/post_mse | 0.194757 | 0.086960 | -0.107797 | [-0.115015, -0.100760] | True |
| adwin/mixed/decrease_first/stable_mse | 0.001045 | 0.069434 | 0.068389 | [0.066541, 0.070314] | False |

## Discovery gate (ground truth): discovery_negative

Polarity-invariant AUC* = max(AUC, 1-AUC) of pre-update cue score vs true hidden context, mean over four switching coordinates. MSE cannot pass this gate.

| Cell | Mean | 95% interval | Pass |
| --- | ---: | --- | --- |
| candidate_auc | 0.625520 | [0.612679, 0.638624] | False |
| shuffled_auc | 0.626177 | [0.613013, 0.640123] | False |
| delta | -0.000657 | [-0.009958, 0.008811] | False |

## Absolute errors and memory

| Policy/fixture/coordinate | Excess MSE | Post MSE | Stable MSE | Recovery latency | Mean update norm | Memory kind | Sigma/width mean |
| --- | ---: | ---: | ---: | ---: | ---: | --- | ---: |
| discover/core/quiet | 0.000275 | — | 0.000275 | — | 0.127926 | conditional | 0.002792 |
| discover/core/noisy | 0.111100 | — | 0.111100 | — | 0.127926 | conditional | 1.055279 |
| discover/core/switch_quiet | 0.005002 | 0.059325 | 0.000278 | 11.953125 | 0.127926 | conditional | 0.007498 |
| discover/core/switch_noisy | 0.120972 | 0.224808 | 0.111943 | 409.718750 | 0.127926 | conditional | 1.065094 |
| discover/noise_jump/noise_jump | 0.043570 | — | 0.043570 | — | 0.032592 | conditional | 0.415516 |
| discover/drift/drift | 0.000286 | — | 0.000286 | — | 0.008566 | conditional | 0.002801 |
| discover/exactly_quiet/exactly_quiet | 0.000000 | — | 0.000000 | — | 0.000167 | conditional | 0.000000 |
| discover/mixed/increase_first | 0.049822 | 0.132083 | 0.042669 | 132.484375 | 0.083808 | conditional | 0.421961 |
| discover/mixed/decrease_first | 0.074666 | 0.132937 | 0.069599 | 140.468750 | 0.083808 | conditional | 0.652387 |
| oracle/core/quiet | 0.000063 | — | 0.000063 | — | 0.030973 | conditional | 0.002575 |
| oracle/core/noisy | 0.025440 | — | 0.025440 | — | 0.030973 | conditional | 1.016285 |
| oracle/core/switch_quiet | 0.003566 | 0.043814 | 0.000066 | 16.406250 | 0.030973 | conditional | 0.041319 |
| oracle/core/switch_noisy | 0.027752 | 0.050027 | 0.025815 | 21.640625 | 0.030973 | conditional | 1.075782 |
| oracle/noise_jump/noise_jump | 0.010179 | — | 0.010179 | — | 0.007879 | conditional | 0.399567 |
| oracle/drift/drift | 0.000227 | — | 0.000227 | — | 0.002210 | conditional | 0.002738 |
| oracle/exactly_quiet/exactly_quiet | 0.000000 | — | 0.000000 | — | 0.000167 | conditional | 0.000000 |
| oracle/mixed/increase_first | 0.012551 | 0.045592 | 0.009678 | 21.250000 | 0.020181 | conditional | 0.447581 |
| oracle/mixed/decrease_first | 0.018823 | 0.049537 | 0.016152 | 22.515625 | 0.020181 | conditional | 0.668959 |
| window/core/quiet | 0.000310 | — | 0.000310 | — | 0.224044 | window | 8.000000 |
| window/core/noisy | 0.125112 | — | 0.125112 | — | 0.224044 | window | 8.000000 |
| window/core/switch_quiet | 0.005407 | 0.063994 | 0.000313 | 8.000000 | 0.224044 | window | 8.000000 |
| window/core/switch_noisy | 0.130101 | 0.186861 | 0.125166 | 304.906250 | 0.224044 | window | 8.000000 |
| window/noise_jump/noise_jump | 0.049474 | — | 0.049474 | — | 0.051055 | window | 8.000000 |
| window/drift/drift | 0.000319 | — | 0.000319 | — | 0.007272 | window | 8.000000 |
| window/exactly_quiet/exactly_quiet | 0.000000 | — | 0.000000 | — | 0.000167 | window | 8.000000 |
| window/mixed/increase_first | 0.053264 | 0.122445 | 0.047249 | 136.953125 | 0.143132 | window | 8.000000 |
| window/mixed/decrease_first | 0.081477 | 0.120559 | 0.078079 | 123.265625 | 0.143132 | window | 8.000000 |
| sgd/core/quiet | 0.000169 | — | 0.000169 | — | 0.167120 | exponential | — |
| sgd/core/noisy | 0.068288 | — | 0.068288 | — | 0.167120 | exponential | — |
| sgd/core/switch_quiet | 0.006847 | 0.083600 | 0.000173 | 17.406250 | 0.167120 | exponential | — |
| sgd/core/switch_noisy | 0.075120 | 0.149266 | 0.068673 | 82.187500 | 0.167120 | exponential | — |
| sgd/noise_jump/noise_jump | 0.027172 | — | 0.027172 | — | 0.038193 | exponential | — |
| sgd/drift/drift | 0.000195 | — | 0.000195 | — | 0.005457 | exponential | — |
| sgd/exactly_quiet/exactly_quiet | 0.000000 | — | 0.000000 | — | 0.000167 | exponential | — |
| sgd/mixed/increase_first | 0.032795 | 0.113405 | 0.025785 | 52.218750 | 0.106815 | exponential | — |
| sgd/mixed/decrease_first | 0.048449 | 0.113423 | 0.042799 | 44.000000 | 0.106815 | exponential | — |
| adwin/core/quiet | 0.000001 | — | 0.000001 | — | 0.004483 | adaptive | — |
| adwin/core/noisy | 0.000683 | — | 0.000683 | — | 0.004483 | adaptive | — |
| adwin/core/switch_quiet | 0.012038 | 0.150170 | 0.000026 | 27.828125 | 0.004483 | adaptive | — |
| adwin/core/switch_noisy | 0.019857 | 0.232495 | 0.001367 | 52.859375 | 0.004483 | adaptive | — |
| adwin/noise_jump/noise_jump | 0.000792 | — | 0.000792 | — | 0.000687 | adaptive | — |
| adwin/drift/drift | 0.003155 | — | 0.003155 | — | 0.000569 | adaptive | — |
| adwin/exactly_quiet/exactly_quiet | 0.000000 | — | 0.000000 | — | 0.000167 | adaptive | — |
| adwin/mixed/increase_first | 0.015792 | 0.189789 | 0.000662 | 45.593750 | 0.003675 | adaptive | — |
| adwin/mixed/decrease_first | 0.016542 | 0.194757 | 0.001045 | 40.718750 | 0.003675 | adaptive | — |
| oracle_matched/core/quiet | 0.000275 | — | 0.000275 | — | 0.127926 | conditional | 0.002792 |
| oracle_matched/core/noisy | 0.111202 | — | 0.111202 | — | 0.127926 | conditional | 1.055279 |
| oracle_matched/core/switch_quiet | 0.005002 | 0.059325 | 0.000278 | 11.953125 | 0.127926 | conditional | 0.007498 |
| oracle_matched/core/switch_noisy | 0.111966 | 0.117790 | 0.111460 | 311.968750 | 0.127926 | conditional | 1.065094 |
| oracle_matched/noise_jump/noise_jump | 0.043760 | — | 0.043760 | — | 0.032592 | conditional | 0.415516 |
| oracle_matched/drift/drift | 0.000286 | — | 0.000286 | — | 0.008566 | conditional | 0.002801 |
| oracle_matched/exactly_quiet/exactly_quiet | 0.000000 | — | 0.000000 | — | 0.000167 | conditional | 0.000000 |
| oracle_matched/mixed/increase_first | 0.045124 | 0.080321 | 0.042064 | 125.437500 | 0.083808 | conditional | 0.421961 |
| oracle_matched/mixed/decrease_first | 0.070836 | 0.086960 | 0.069434 | 132.921875 | 0.083808 | conditional | 0.652387 |
| random/core/quiet | 0.000275 | — | 0.000275 | — | 0.127926 | conditional | 0.002792 |
| random/core/noisy | 0.111647 | — | 0.111647 | — | 0.127926 | conditional | 1.055279 |
| random/core/switch_quiet | 0.005002 | 0.059325 | 0.000278 | 11.953125 | 0.127926 | conditional | 0.007498 |
| random/core/switch_noisy | 0.119436 | 0.218643 | 0.110809 | 478.046875 | 0.127926 | conditional | 1.065094 |
| random/noise_jump/noise_jump | 0.043266 | — | 0.043266 | — | 0.032592 | conditional | 0.415516 |
| random/drift/drift | 0.000286 | — | 0.000286 | — | 0.008566 | conditional | 0.002801 |
| random/exactly_quiet/exactly_quiet | 0.000000 | — | 0.000000 | — | 0.000167 | conditional | 0.000000 |
| random/mixed/increase_first | 0.049794 | 0.136212 | 0.042279 | 171.421875 | 0.083808 | conditional | 0.421961 |
| random/mixed/decrease_first | 0.074855 | 0.132815 | 0.069815 | 165.015625 | 0.083808 | conditional | 0.652387 |
| shuffled/core/quiet | 0.000275 | — | 0.000275 | — | 0.127926 | conditional | 0.002792 |
| shuffled/core/noisy | 0.111666 | — | 0.111666 | — | 0.127926 | conditional | 1.055279 |
| shuffled/core/switch_quiet | 0.005002 | 0.059325 | 0.000278 | 11.953125 | 0.127926 | conditional | 0.007498 |
| shuffled/core/switch_noisy | 0.120799 | 0.221814 | 0.112015 | 410.484375 | 0.127926 | conditional | 1.065094 |
| shuffled/noise_jump/noise_jump | 0.044031 | — | 0.044031 | — | 0.032592 | conditional | 0.415516 |
| shuffled/drift/drift | 0.000286 | — | 0.000286 | — | 0.008566 | conditional | 0.002801 |
| shuffled/exactly_quiet/exactly_quiet | 0.000000 | — | 0.000000 | — | 0.000167 | conditional | 0.000000 |
| shuffled/mixed/increase_first | 0.050322 | 0.134849 | 0.042972 | 174.078125 | 0.083808 | conditional | 0.421961 |
| shuffled/mixed/decrease_first | 0.074424 | 0.136083 | 0.069062 | 187.546875 | 0.083808 | conditional | 0.652387 |
| nocontext_matched/core/quiet | 0.000275 | — | 0.000275 | — | 0.127926 | conditional | 0.002792 |
| nocontext_matched/core/noisy | 0.050735 | — | 0.050735 | — | 0.127926 | conditional | 1.055279 |
| nocontext_matched/core/switch_quiet | 0.005002 | 0.059325 | 0.000278 | 11.953125 | 0.127926 | conditional | 0.007498 |
| nocontext_matched/core/switch_noisy | 0.059892 | 0.160839 | 0.051114 | 48.734375 | 0.127926 | conditional | 1.065094 |
| nocontext_matched/noise_jump/noise_jump | 0.021111 | — | 0.021111 | — | 0.032592 | conditional | 0.415516 |
| nocontext_matched/drift/drift | 0.000286 | — | 0.000286 | — | 0.008566 | conditional | 0.002801 |
| nocontext_matched/exactly_quiet/exactly_quiet | 0.000000 | — | 0.000000 | — | 0.000167 | conditional | 0.000000 |
| nocontext_matched/mixed/increase_first | 0.026923 | 0.114331 | 0.019322 | 50.828125 | 0.083808 | conditional | 0.421961 |
| nocontext_matched/mixed/decrease_first | 0.038474 | 0.113648 | 0.031938 | 47.187500 | 0.083808 | conditional | 0.652387 |

## Measured execution time

| Stage | Family | Seconds |
| --- | --- | ---: |
| tuning | discover | 1.58 |
| tuning | oracle | 0.48 |
| tuning | window | 0.81 |
| tuning | sgd | 0.41 |
| tuning | adwin | 4.92 |
| confirmation | discover | 3.11 |
| confirmation | oracle | 1.05 |
| confirmation | window | 0.31 |
| confirmation | sgd | 0.16 |
| confirmation | adwin | 1.82 |
| confirmation | oracle_matched | 0.81 |
| confirmation | random | 1.22 |
| confirmation | shuffled | 2.01 |
| confirmation | nocontext_matched | 1.72 |

Each searched family consumes 5,184,000 coordinate observations. Configuration budgets are equal, not CPU costs.

## Scope and reproduction

Cues are evaluator-generated noisy observations of the hidden context (SEP=0.5, unit cue noise; single-sample AUC ≈ 0.76). y bytes are identical to the forgetting fixtures at equal seeds. Perfect context is privileged, not perfect prediction: conditionals must still learn each regime mean. No oracle or discovery outcome overrides candidate learning performance; MSE cannot pass the discovery gate either. Candidate success requires the gate plus all 90 comparisons, including >= 10% primary improvement and every retention bound. Oracle arms each have 45 comparisons. All outcomes close this registration.

Intervals resample whole seeds 10000 times with seed 95000. Finite menus and synthetic fixtures do not establish global optimizer superiority, population guarantees or general neural-memory utility. Every reached row and source is archived; prior studies remain intact.

`python check_v3_discovery.py --evidence results/v3-discovery --reproduce` regenerates every reached row and scientific manifest/summary at rtol1e-11/atol1e-13. `python report_v3_discovery.py --check` verifies both generated reports.
