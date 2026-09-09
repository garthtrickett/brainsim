# V3 first experiment: do not integrate this gate

The registered standalone test is complete. This centered-variance two-timescale
modulation improves on tuned Adam in the scalar switching task, but fails the
noise/change distinction and does not beat the simpler control. It has not earned
integration into brainsim. No default changes, v2 rewrite, or later v3 mechanism
are part of this experiment.

The protocol is [DESIGN-v3-gate.md](DESIGN-v3-gate.md); complete tables and paired
intervals are in [the generated report](results/v3/report.md). Sources, tuning,
calibration, frozen selection and all confirmation rows are in `results/v3/`.

## What happened

Each of four optimizers received 12 configurations and eight tuning seeds, then
one frozen configuration was tested on 32 independent seeds. Every seed contains
stationary and switching targets at low and high observation noise. All arms
consume the same samples, one gradient and one update per observation.

Mean excess squared prediction error in the first 200 samples after a switch:

| Optimizer | Post-switch error | Dual relative reduction |
| --- | ---: | ---: |
| Adam | 0.481997 | 43.9% |
| Constant-rate SGD | 0.324094 | 16.6% |
| Single-timescale gate | 0.251445 | -7.5% |
| Two-timescale gate | 0.270263 | — |

The dual-minus-single difference is +0.018818, paired bootstrap 95% interval
[+0.006871, +0.030963]. The simpler gate also adapts faster: 42.93 versus 70.20
samples to the registered sustained-error threshold, averaging noise regimes.
The Adam comparison alone would have overstated the finding.

The fixed-observer gate detects every low-noise switch but only **25%** of
high-noise switches, below the registered 80% criterion. Stationary block alarms
are **2.69%** in each noise regime, below the 5% limit. Its mean stationary gate
is about 0.034, confirming that rectification does not vanish on stable noise.
An increase in noise also triggers the gate despite no change in the target;
the two noise-change boundaries have an average hit rate of 50%. Smooth drift
produces no boundary detections. These results do not establish separation of
uncertainty about the target from observation noise.

The gate also increases stationary high-noise excess error from Adam's 0.007819
to 0.013539. The increase's upper interval endpoint, 0.006132, exceeds the
registered retention allowance of 0.002. All three advancement components fail:
detection, improvement against every control, and stationary retention.

## Implementation and limits

Adam uses bias-corrected first and raw second moments. The gate uses two
centered EMA variances (rates .1 and .01), not two raw second moments. It
multiplies Adam's step by `1 + gain * gate`, preserving a base update when the
gate is zero. The single-timescale arm uses a declared unit-scale variance gate.
The fixed observer receives observations alone, independently of optimizer motion;
its detection scores must not be read as closed-loop optimizer detection scores.

Equal budgets mean equal search trials and observations, not identical arithmetic
cost. Active optimizer state including the prediction is 1/3/5/7 scalars for
SGD/Adam/single/dual. Recorded timings are too coarsely rounded to resolve small
cost differences. No new dependencies were introduced.

The selected Adam second-moment decay and both gated gains reach search
boundaries; the single gate also selects the lowest searched rate. These are
finite-grid results, not proofs of optimal tuning. Timescales and centered
statistics were fixed before execution. The negative result bounds this
implementation on these streams; it does not refute all two-timescale rules,
all v3 ideas, or a future continuous-time design. Noise-stratified detector
thresholds use evaluator knowledge and are not deployable thresholds.

Adam and gradient-residual adaptive optimizers already exist; the protocol links
primary Adam and AdaBelief papers. No novelty, optimizer-wide advantage or Kalman
filter derivation is established here.

## Evidence and validation

Registration commit: `3879744`; implementation and instrument checks: `1795477`;
calibration/tuning and selection frozen before confirmation: `c50226b`.
These are original experiment commits retained in PR history; the publication
may be squash-merged. The registered files are also archived by content hash.

Evidence includes 8 calibration rows, 384 tuning rows, 32 diagnostic rows and
128 learning-confirmation rows. Tuning comprises 1,536 learning streams;
confirmation comprises 512 learning streams. Calibration has 16 fixed-observer
streams; confirmation has 192 fixed-observer streams. Both gates observe each
diagnostic stream. Total learning updates: 12,288,000; none are brainsim runs.

Commands run locally (all pass):

```sh
.venv/bin/python check_v3_gate.py
.venv/bin/python study_v3_gate.py prepare
# Commit frozen selection before the first confirmation run.
.venv/bin/python study_v3_gate.py confirm
.venv/bin/python report_v3_gate.py
.venv/bin/python check_v3_gate.py --evidence results/v3 --reproduce
.venv/bin/python report_v3_gate.py --check
.venv/bin/python check_evidence.py
.venv/bin/python check_v1.py
git diff --check
```

The new `V3 validation` workflow reproduces all 552 evidence rows, verifies
source hashes and frozen selection, and checks generated reports. Comparison
allows floating-point tolerances rtol 1e-11/atol 1e-13 and excludes elapsed time.
The existing `V1 validation` workflow retains its full frozen 56-score reference
gate. Passing implementation/reproduction checks does not mean the scientific
hypothesis passed; CI preserves this negative result.

Files added: `v3_gate.py` (instrument), `study_v3_gate.py` (staged runner),
`check_v3_gate.py` (scientific checks/reproduction), `report_v3_gate.py` (decision
and tables), protocol/results documents, archived evidence, and the v3 workflow.
`PLAN.md`, `V3.md`, `V3-NEXT.md` and `README.md` point to this disposition.
No v1 roadmap step is reopened and no capability registry exists for this toy.

## Disposition

Stop this candidate before agent integration, as registered. A follow-up would
need a new hypothesis, new registration and fresh confirmation seeds, addressing
the noisy-switch misses and the simpler control's advantage. Do not promote the
single gate automatically or extend the gain search against these same held-out
seeds. The speculative v3 queue and v2 rewrite remain separate decisions.
