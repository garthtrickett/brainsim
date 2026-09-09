# brainsim

The simplest AI I could design that works the way a brain works rather than the
way an LLM works — then implemented, ablated, and corrected until each part
earned its place or was cut.

One loop that never stops. Learning happens *inside* it. Every learning signal a
synapse uses is local: two neurons and one broadcast scalar. No backprop.

**This file is what the design IS.** For how it got here — including five
mechanisms that were validated and later turned harmful, three verdicts that
reversed, and two designs shelved unbuilt — see [HISTORY.md](HISTORY.md). That
half is the more useful one.

## Run it

```sh
pip install numpy
python3 demo.py                                   # end-to-end validation
python3 experiments/23_calibrate_tasks.py         # task floors and ceilings
```

## Where it stands

The frozen reference uses eight agent seeds on task seed zero. Baselines and
individual scores are in `reference.json`; remaining-v1 experiments and their
different seed protocol are documented in [V1-RESULTS.md](V1-RESULTS.md).

| task | measured floor | baseline | measured ceiling |
| --- | ---: | ---: | ---: |
| `nway-4` | 0.251 | 0.997 | 1.000 |
| `nway-8` | 0.126 | 0.978 | 1.000 |
| `xor-2` | 0.504 | 0.825 | 1.000 |
| `volatile-4` | 0.251 | 0.371 | 1.000 |
| `tmaze-within-30` | 0.504 | 0.999 | 1.000 |
| `tmaze-within-60` | 0.504 | 0.998 | 1.000 |
| `lock-10` | 12.500 | 415.125 | 1333.000 |

Lock scores count total rewards over 12,000 decisions; other scores are tail
accuracy. These small synthetic-task comparisons do not establish superiority
over deep learning generally.

Validation: `python check_v1.py` and `python check_reference.py --out results/local-reference.json`.
Install the existing pinned experiment dependencies with `pip install -r requirements.txt`.

V3's first standalone optimizer test is complete: the two-timescale candidate
improves on Adam but fails the simpler-control, noisy-switch and retention
criteria. It is not integrated. See [V3-RESULTS.md](V3-RESULTS.md). Reproduce it
with `python check_v3_gate.py --evidence results/v3 --reproduce`.

The mean-disagreement successor completed its bounded tuning search and stopped
as inconclusive at the gain limit. Confirmation remains unrun; see
[V3-SLICE-1-RESULTS.md](V3-SLICE-1-RESULTS.md). Reproduce its reached evidence
with `python check_v3_slice1.py --evidence results/v3-slice1 --reproduce`.

A separately registered wider search resolved that gain boundary, but independent
detection failed: the mean-disagreement gate also reacted to increases in noise.
Performance confirmation was therefore not run. See
[V3-GAIN-FOLLOWUP-RESULTS.md](V3-GAIN-FOLLOWUP-RESULTS.md), or reproduce all 3,984
reached rows with `python check_v3_gain.py --evidence results/v3-gain-followup --reproduce`.

## Architecture

```
  sensory 40 ──W_in──▶ hidden 80 ──W_out──▶ motor n ──▶ argmax(votes)
                (fixed)   k-WTA k=6   (plastic)
                            │                  ▲
                            ├──▶ wm (PFC) ──W_wm┘   residual only
                            └──▶ V(s) critic
```

**Per tick.** Leaky integrate-and-fire. `k-WTA` keeps the 6 best-driven hidden
units and silences the rest. Motor cells read the *previous* tick's hidden spikes
(one-tick axonal delay) plus exploration noise.

**Per decision (~30 ticks).** `argmax` over accumulated votes. Reward arrives;
`NM = r − V(s)` is the neuromodulator — reward *minus what was expected*.
Eligibility is credited via `TAGGATE`: a synapse tags only if its own cell leads
the pool, a threshold supplied by pooled inhibition. The tag is then consumed.

**Offline (every 50 decisions).** Hippocampal replay: episodes are replayed in
**reverse** with TD bootstrapping, so credit crosses a whole episode in one pass.

## Defaults, and what each is worth

| constant | value | why |
|---|---|---|
| `LEAK` / `TRACE_D` | 0.85 / 0.80 | membrane ~20ms, spike trace ~50ms |
| `ELIG_D` | 0.995 | τ≈200 ticks; τ≈10 collapses to chance once anything fills the gap |
| `NOISE` | 0.35 | the only source of exploration; remove it and learning stops |
| `TAGGATE` / `THETA` | on / 1.0 | WTA on *credit*. Traces sit 0.5% apart, so any threshold below ~0.99 gates nothing |
| `TRM_D` | 0.97 | gate window: alignment vs exploration. The optimum inverts with action count |
| `VALUE_STATE` | on | striatal V(s). Essential for the lock (330 vs 66) |
| `ADAPTIVE` | on | volatility from reward-rate change → LR and noise |
| `HIPPO` | on | reverse replay + TD. Lock 9.5 → 419 |
| `HIPPO_REVERSE` | on | reverse beats forward **80×** |
| `HIPPO_TRACE` | **off** | trace-spanning is *harmful*: 115 vs 333 without |
| `WM` | on | working memory via a residual pathway; two tasks 0.51 → 0.999 |
| `SLEEP_REPLAY` | **0** | local replay + gradient, both now harmful |
| `DOWNSCALE` | **1.0** | shrank exactly the weights replay had strengthened |
| `ETA_TH` | **0.0** | threshold homeostasis causes *more* silence than it prevents under k-WTA |
| `ACTION_GATED` | off | the one non-local option; `TAGGATE` matches it locally |

## Deliberately not built

- **Basal ganglia** — its target gap (0.100 at nway-8) turned out to be a
  five-line tie-breaker bug in `decide()`. Now 0.018. See `DESIGN-basal-ganglia.md`.
- **Predictive-coding hierarchy** — twice measured that representation is *not*
  the bottleneck. A fixed random projection with k-WTA is *good* at conjunctions.
- **Curiosity / intrinsic reward** — no effect survived a control check.
- **Pretrained encoder** — subsumed by the sleep gradient, then by replay.

## Known limits

- **Cannot absorb decisions that do not matter.** An unrewarded arbitrary action
  draws a negative RPE into a policy sharing hidden units with the step that counts.
- **One global NM scalar and one global k-WTA pool by default.** Local-pool
  instruments now exist, but did not earn a default at the tested scale. Larger
  networks and parallel loops still need their own evidence.
- **No body.** The Part 1 design specified homeostatic set-points; the
  implementation takes reward from a task. Embodiment was dropped at first
  contact with code and never returned.

## Where this is going

- **`PLAN.md`** — roadmap, steps 0–13, and the v2/v3 forks.
- **`V2.md`** — substrate PRD: continuous time, event-driven, local pools.
- **`V3.md`** — the fluctuation thesis. Two timescales of variance separate
  noise from change; one estimator cannot, which is what Adam does. Orthogonal
  to v2 and testable in v1.
- **`HISTORY.md`** — the more valuable half of the documentation.
- **`V1-RESULTS.md`** — remaining-v1 investigations, exact commands, results and
  explicit deferrals. Experimental knobs remain off by default.
- **`V3-NEXT.md`** — why the next experiment can precede the continuous-time fork.
