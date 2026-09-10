# V6 margin-directed exploration

Disposition: **learning_negative**.

| Task | Usable | Confirmation rows |
| --- | --- | ---: |
| volatile | True | 96 |
| noisy | True | 96 |
| lock | True | 96 |

## Task usability (remeasured baseline vs frozen bounds)

| Task | Floor | Ceiling | Baseline | Position | Verdict |
| --- | ---: | ---: | ---: | ---: | ---: |
| volatile | 0.251 | 1.0 | 0.331190 | 0.11 | learning_negative |
| noisy | 0.2495 | 1.0 | 0.315952 | 0.09 | no_verdict |
| lock | 12.5 | 1333.0 | 474.750000 | 0.35 | learning_negative |

## Task volatile: learning_negative

Gain = explorer minus baseline (paired); headroom = oracle minus explorer (paired). A pass needs both intervals strictly above zero.

| Explorer | Gain Δ | 95% interval | Headroom Δ | 95% interval | Pass |
| --- | ---: | --- | ---: | --- | --- |
| exploreA | -0.0626 | [-0.0986, -0.0238] | 0.1590 | [0.1128, 0.1995] | False |
| exploreB | -0.0745 | [-0.1124, -0.0293] | 0.1710 | [0.1286, 0.2107] | False |

## Task noisy: no verdict (baseline outside 10–90% band)


## Task lock: learning_negative

Gain = explorer minus baseline (paired); headroom = oracle minus explorer (paired). A pass needs both intervals strictly above zero.

| Explorer | Gain Δ | 95% interval | Headroom Δ | 95% interval | Pass |
| --- | ---: | --- | ---: | --- | --- |
| exploreA | -340.3750 | [-405.6281, -274.2500] | 449.1250 | [375.2469, 514.3750] | False |
| exploreB | -462.8750 | [-549.1250, -390.6250] | 571.6250 | [499.0000, 647.8750] | False |

## Scope and reproduction

Paired seed design; intervals resample whole seeds10000 times with seed215000. Eight seeds and three tasks cannot establish population guarantees, exploration in general, or superiority over deep learning. The oracle is a privileged bound, never a deployable arm. Every reached row and source is archived; prior studies remain intact.

`python check_v6.py --evidence results/v6 --reproduce` regenerates every reached row and scientific manifest/summary at rtol1e-11/atol1e-13. `python report_v6.py --check` verifies both generated reports.
