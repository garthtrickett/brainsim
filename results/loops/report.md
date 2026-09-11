# Parallel loops: per-action modulation vs the global loop

Disposition: **adopt-loops-loops-full**.

| Stage | Rows |
| --- | ---: |
| confirmation | 48 |

## volatile-4/loops-LR: fail

| Arm mean | Frozen mean | Delta | 95% interval |
| ---: | ---: | ---: | --- |
| 0.316750 | 0.371500 | -0.054750 | [-0.189250, +0.100375] |

## volatile-4/loops-full: fail

| Arm mean | Frozen mean | Delta | 95% interval |
| ---: | ---: | ---: | --- |
| 0.308625 | 0.371500 | -0.062875 | [-0.186000, +0.054750] |

## lock-10/loops-LR: fail

| Arm mean | Frozen mean | Delta | 95% interval |
| ---: | ---: | ---: | --- |
| 409.625000 | 415.125000 | -5.500000 | [-39.750000, +23.875000] |

## lock-10/loops-full: pass

| Arm mean | Frozen mean | Delta | 95% interval |
| ---: | ---: | ---: | --- |
| 445.750000 | 415.125000 | +30.625000 | [+20.875000, +40.875000] |

## nway-8/loops-LR: pass

| Arm mean | Frozen mean | Delta | 95% interval |
| ---: | ---: | ---: | --- |
| 0.966250 | 0.978250 | -0.012000 | [-0.051875, +0.012750] |

## nway-8/loops-full: pass

| Arm mean | Frozen mean | Delta | 95% interval |
| ---: | ---: | ---: | --- |
| 0.961125 | 0.978250 | -0.017125 | [-0.050753, +0.005625] |

## Absolute scores by arm

| Task / arm | Mean | 95% interval |
| --- | ---: | --- |
| volatile-4/loops-LR | 0.316750 | [0.230497, 0.414625] |
| volatile-4/loops-full | 0.308625 | [0.244000, 0.373250] |
| lock-10/loops-LR | 409.625000 | [317.000000, 524.000000] |
| lock-10/loops-full | 445.750000 | [361.500000, 547.750000] |
| nway-8/loops-LR | 0.966250 | [0.927250, 0.987750] |
| nway-8/loops-full | 0.961125 | [0.929872, 0.981628] |

Candidate (highest paired delta among clearers): **loops-full on lock-10**.


## Scope and reproduction

Same-seed paired design against the frozen reference instrument; the shipped global arm is the frozen column itself (check_reference.py green is the proof), not a re-measurement. Lock-10 total reward is high-variance, reported whole. Eight seeds cannot establish population guarantees.

`python check_loops.py --evidence results/loops --reproduce` regenerates every row at rtol1e-11/atol1e-13. `python report_loops.py --check` verifies both generated reports.
