# V1 paired contrasts

Exploratory seed-paired bootstrap intervals; no multiple-comparison adjustment.
A positive delta is higher external task reward. These are screening results,
not automatic decisions to enable a feature.

| Study/task | Treatment vs control | Control | Treatment | Delta | 95% interval | Wins |
| --- | --- | ---: | ---: | ---: | --- | --- |
| pools/legacy-additive-4x4 | P2 vs P1 | 0.3627 | 0.3657 | +0.0030 | [-0.0355, +0.0400] | 4/6 |
| pools/legacy-additive-4x4 | P3 vs P1 | 0.3627 | 0.3633 | +0.0007 | [-0.0175, +0.0187] | 3/6 |
| pools/legacy-additive-4x4 | P6 vs P1 | 0.3627 | 0.3815 | +0.0188 | [-0.0135, +0.0568] | 4/6 |
| pools/shape-4x4 | P2 vs P1 | 0.9640 | 0.9633 | -0.0007 | [-0.0105, +0.0105] | 2/6 |
| pools/shape-4x4 | P3 vs P1 | 0.9640 | 0.9590 | -0.0050 | [-0.0130, +0.0022] | 2/6 |
| pools/shape-4x4 | P6 vs P1 | 0.9640 | 0.9637 | -0.0003 | [-0.0153, +0.0108] | 4/6 |
| pools/volatile-4 | P2 vs P1 | 0.3388 | 0.3143 | -0.0245 | [-0.0768, +0.0310] | 2/6 |
| pools/volatile-4 | P3 vs P1 | 0.3388 | 0.3688 | +0.0300 | [-0.0145, +0.0652] | 5/6 |
| pools/volatile-4 | P6 vs P1 | 0.3388 | 0.2697 | -0.0692 | [-0.1273, -0.0213] | 1/6 |
| pools/xor-2 | P2 vs P1 | 0.8927 | 0.8910 | -0.0017 | [-0.0070, +0.0032] | 3/6 |
| pools/xor-2 | P3 vs P1 | 0.8927 | 0.8720 | -0.0207 | [-0.0308, -0.0103] | 0/6 |
| pools/xor-2 | P6 vs P1 | 0.8927 | 0.8763 | -0.0163 | [-0.0247, -0.0065] | 1/6 |
| pools/nway-8 | P2 vs P1 | 0.9805 | 0.9725 | -0.0080 | [-0.0150, -0.0018] | 0/6 |
| pools/nway-8 | P3 vs P1 | 0.9805 | 0.9802 | -0.0003 | [-0.0082, +0.0073] | 2/6 |
| pools/nway-8 | P6 vs P1 | 0.9805 | 0.9790 | -0.0015 | [-0.0078, +0.0022] | 4/6 |
| curiosity/lock-10 | bonus-0.1 vs off | 551.6667 | 541.3333 | -10.3333 | [-146.6750, +102.3333] | 4/6 |
| curiosity/lock-10 | bonus-0.5 vs off | 551.6667 | 558.8333 | +7.1667 | [-157.3333, +201.3333] | 3/6 |
| replay/lock-10 | context vs off | 551.6667 | 535.5000 | -16.1667 | [-32.1667, +1.0000] | 1/6 |
| replay/lock-10 | shuffled vs off | 551.6667 | 539.8333 | -11.8333 | [-34.8333, +11.1667] | 2/6 |
| replay/lock-10 | context vs shuffled | 539.8333 | 535.5000 | -4.3333 | [-21.1667, +10.6667] | 3/6 |
| dyna/lock-10 | real vs off | 551.6667 | 596.1667 | +44.5000 | [+23.5000, +72.6667] | 6/6 |
| dyna/lock-10 | model vs off | 551.6667 | 580.0000 | +28.3333 | [+7.5000, +56.0000] | 5/6 |
| dyna/lock-10 | model vs real | 596.1667 | 580.0000 | -16.1667 | [-37.6667, +1.8333] | 2/6 |
| failure/lock-10 | fail-0.1 vs off | 551.6667 | 477.1667 | -74.5000 | [-334.0000, +200.5000] | 2/6 |
| failure/lock-10 | gain-0.9 vs off | 551.6667 | 427.0000 | -124.6667 | [-416.3333, +155.1667] | 3/6 |
| failure/lock-10 | fail-0.5 vs off | 551.6667 | 578.1667 | +26.5000 | [-153.0000, +213.3333] | 5/6 |
| failure/lock-10 | gain-0.5 vs off | 551.6667 | 510.3333 | -41.3333 | [-336.3333, +246.3333] | 4/6 |
| failure/lock-10 | fail-0.1 vs gain-0.9 | 427.0000 | 477.1667 | +50.1667 | [-264.0000, +349.3333] | 3/6 |
| failure/lock-10 | fail-0.5 vs gain-0.5 | 510.3333 | 578.1667 | +67.8333 | [-90.7417, +300.0000] | 2/6 |
| failure/volatile-4 | fail-0.1 vs off | 0.3388 | 0.3245 | -0.0143 | [-0.1008, +0.0708] | 2/6 |
| failure/volatile-4 | gain-0.9 vs off | 0.3388 | 0.3110 | -0.0278 | [-0.1600, +0.0823] | 3/6 |
| failure/volatile-4 | fail-0.5 vs off | 0.3388 | 0.3443 | +0.0055 | [-0.1123, +0.1183] | 3/6 |
| failure/volatile-4 | gain-0.5 vs off | 0.3388 | 0.3298 | -0.0090 | [-0.0548, +0.0218] | 4/6 |
| failure/volatile-4 | fail-0.1 vs gain-0.9 | 0.3110 | 0.3245 | +0.0135 | [-0.0918, +0.0883] | 5/6 |
| failure/volatile-4 | fail-0.5 vs gain-0.5 | 0.3298 | 0.3443 | +0.0145 | [-0.0695, +0.1035] | 3/6 |
| failure/xor-2 | fail-0.1 vs off | 0.8927 | 0.8818 | -0.0108 | [-0.0268, +0.0068] | 2/6 |
| failure/xor-2 | gain-0.9 vs off | 0.8927 | 0.8920 | -0.0007 | [-0.0113, +0.0088] | 4/6 |
| failure/xor-2 | fail-0.5 vs off | 0.8927 | 0.8490 | -0.0437 | [-0.0550, -0.0322] | 0/6 |
| failure/xor-2 | gain-0.5 vs off | 0.8927 | 0.8673 | -0.0253 | [-0.0395, -0.0110] | 1/6 |
| failure/xor-2 | fail-0.1 vs gain-0.9 | 0.8920 | 0.8818 | -0.0102 | [-0.0307, +0.0112] | 2/6 |
| failure/xor-2 | fail-0.5 vs gain-0.5 | 0.8673 | 0.8490 | -0.0183 | [-0.0245, -0.0113] | 0/6 |
| failure/nway-8 | fail-0.1 vs off | 0.9805 | 0.9850 | +0.0045 | [+0.0008, +0.0085] | 5/6 |
| failure/nway-8 | gain-0.9 vs off | 0.9805 | 0.9882 | +0.0077 | [-0.0003, +0.0160] | 4/6 |
| failure/nway-8 | fail-0.5 vs off | 0.9805 | 0.9837 | +0.0032 | [-0.0008, +0.0067] | 5/6 |
| failure/nway-8 | gain-0.5 vs off | 0.9805 | 0.9840 | +0.0035 | [-0.0070, +0.0097] | 5/6 |
| failure/nway-8 | fail-0.1 vs gain-0.9 | 0.9882 | 0.9850 | -0.0032 | [-0.0113, +0.0045] | 3/6 |
| failure/nway-8 | fail-0.5 vs gain-0.5 | 0.9840 | 0.9837 | -0.0003 | [-0.0083, +0.0123] | 1/6 |
| failure-capacity/legacy-additive-4x4 | fail-0.1 vs off | 0.3627 | 0.3775 | +0.0148 | [-0.0128, +0.0442] | 3/6 |
| failure-capacity/legacy-additive-4x4 | gain-0.9 vs off | 0.3627 | 0.3600 | -0.0027 | [-0.0410, +0.0280] | 4/6 |
| failure-capacity/legacy-additive-4x4 | fail-0.5 vs off | 0.3627 | 0.3802 | +0.0175 | [-0.0185, +0.0480] | 5/6 |
| failure-capacity/legacy-additive-4x4 | gain-0.5 vs off | 0.3627 | 0.3895 | +0.0268 | [-0.0152, +0.0695] | 4/6 |
| failure-capacity/legacy-additive-4x4 | fail-0.1 vs gain-0.9 | 0.3600 | 0.3775 | +0.0175 | [-0.0275, +0.0662] | 3/6 |
| failure-capacity/legacy-additive-4x4 | fail-0.5 vs gain-0.5 | 0.3895 | 0.3802 | -0.0093 | [-0.0320, +0.0230] | 1/6 |
