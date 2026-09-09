# Decision after the v1 investigations

**Update, 2026-09-09:** the standalone test below is complete. The two-timescale
candidate fails its registered detection, control-comparison and retention
criteria. Do not integrate it into brainsim; see [V3-RESULTS.md](V3-RESULTS.md).
The text below records the experiment-order decision that preceded the result.

The successor plan in [V3-SLICE-1-PLAN.md](V3-SLICE-1-PLAN.md) has now been
executed to its registered stop: the mean-disagreement candidate selected the
highest gain, so tuning is inconclusive and confirmation was not opened. See
[V3-SLICE-1-RESULTS.md](V3-SLICE-1-RESULTS.md). Further search requires a new
registration; no agent integration follows.

That separately registered follow-up is now complete: gain 64 won inside the wider
range, but the detector falsely signaled on noise increases. Independent performance
was not opened. See [V3-GAIN-FOLLOWUP-RESULTS.md](V3-GAIN-FOLLOWUP-RESULTS.md).
The bounded follow-up is closed, with no further search or integration activated.

The separately registered persistent detector now also has a result: all passive
observer cells pass, but six learning-coupled detector cells fail. Performance was
not opened. See [V3-PERSISTENT-RESULTS.md](V3-PERSISTENT-RESULTS.md). This experiment
is closed; its observer result does not establish a learning rule.

The separately authorized reference-detector test now separates detection from
learning: detection passed, but independent learning did not beat the strong
controls while preserving retention. See [V3-REFERENCE-RESULTS.md](V3-REFERENCE-RESULTS.md).
It also showed that missed alarms can coexist with timely prediction recovery.
This experiment is closed; no automatic follow-up is activated.

The bounded-burst follow-up then tested how to use the signal: detected bursts
failed independent learning advancement, and even the tuned perfect-timing oracle
failed the full comparison against SGD. See [V3-BURST-RESULTS.md](V3-BURST-RESULTS.md).
Its 704 reached rows are archived; this finite-menu experiment is closed.

The change-triggered forgetting follow-up is now complete: matched-control gains
and a strong oracle adaptation benefit did not satisfy the full learning/retention
criteria. See [V3-FORGETTING-RESULTS.md](V3-FORGETTING-RESULTS.md). All 736 reached
rows are archived; the finite-menu experiment is closed without integration.

The interference-as-discovery follow-up is now complete: the §11.1 candidate
failed its ground-truth localisation gate (candidate AUC* 0.626, shuffled
0.626) and the full learning gate (57/90; conditioning loses to pooled
prediction). True-context oracles adapted far better but still failed full
retention. See [V3-DISCOVERY-RESULTS.md](V3-DISCOVERY-RESULTS.md). All 768
reached rows are archived; the finite-menu experiment is closed without
integration.

The oracle-schedule retention follow-up is now complete: the fast-window/ADWIN2
candidate held the adaptation/stability tradeoff (primary 0.083 against every
control, every stable/noise cell against ADWIN passed) but closed
learning-negative on drift, which neither component tracks, plus a strict-veto
tie on a 0-vs-0 noiseless cell. See
[V3-RETENTION-RESULTS.md](V3-RETENTION-RESULTS.md). All 576 reached rows are
archived; the finite-menu experiment is closed without integration.

The timing-tolerance follow-up is now complete: the primary win survives ±2
steps of schedule jitter and is dead by ±8 — far tighter than ADWIN's own
error profile — and the deployable ADWIN-scheduled arm failed retention on
noise-driven false alarms while holding primary. See
[V3-TOLERANCE-RESULTS.md](V3-TOLERANCE-RESULTS.md). All 736 reached rows are
archived; the detector line closes with that number, without integration.

The drift-boundary follow-up is now complete: the frozen candidate on an
enriched target-plus-ramp schedule failed the same six drift cells at
unchanged values with the treatment fully engaged — perfect drift timing buys
nothing, so the wall is the mechanism. See
[V3-DRIFT-RESULTS.md](V3-DRIFT-RESULTS.md). All 480 reached rows are
archived; the finite-menu experiment is closed without integration.

The slope-state follow-up is now complete: a trend regime gated on granted
drift boundaries passed all 75 comparisons, beating SGD on the ramp with
everything else preserved — the first full V3 positive. See
[V3-SLOPE-RESULTS.md](V3-SLOPE-RESULTS.md). All 576 reached rows are
archived; no default change or agent integration follows.

The slope-timing follow-up is now complete: that trend regime gated by
observed ADWIN alarms closed learning-negative — false alarms on noise
destroyed stability and the primary win missed its 10% rule — while the
granted reference replicated its predecessors. See
[V3-SLOPETIME-RESULTS.md](V3-SLOPETIME-RESULTS.md). All 608 reached rows are
archived; the finite-menu experiment is closed without integration.

The slope broader benchmark is now complete: steep and noisy ramps pass
strictly, but the shallow ramp loses to the plain fast window — kink-smearing
beats trend signal where it is weakest — closing 74/75 learning-negative. See
[V3-SLOPEBENCH-RESULTS.md](V3-SLOPEBENCH-RESULTS.md). All 480 reached rows are
archived; the finite-menu experiment is closed without integration.

The kink-guarded slope follow-up is now complete: guard horizon J=96 narrows
the shallow-ramp gap threefold (0.000960 to 0.000313) without closing it —
the same strict cell fails, everything else passes. See
[V3-SLOPEGUARD-RESULTS.md](V3-SLOPEGUARD-RESULTS.md). All 608 reached rows are
archived; the finite-menu experiment is closed without integration.

The slope-state follow-up is now complete: a trend regime gated on granted
drift boundaries passed all 75 comparisons, beating SGD on the ramp with
everything else preserved — the first full V3 positive. See
[V3-SLOPE-RESULTS.md](V3-SLOPE-RESULTS.md). All 576 reached rows are
archived; no default change or agent integration follows.

**Defer the v2 rewrite and test v3's first hypothesis directly on the existing
v1 infrastructure.** This is a decision about experiment order, not acceptance
of v3's thesis or abandonment of continuous time.

The fast baseline and frozen evidence are sufficient for the next learning-rule
question. Local pools did not earn a default at the tested scale. Continuous
time would simultaneously change decision boundaries, eligibility consumption,
replay episodes and the task interface, making attribution harder. Its eventual
purpose remains embodiment and scaling; neither is demonstrated by these v1 runs.

The next implementation should be only V3 §9's standalone non-stationary
supervised toy: Adam versus a precisely specified two-timescale modulation.
No spiking-network rewrite, no hierarchy, and none of the speculative §10/§11
queue should precede that result. At this decision point no v3 optimiser had been implemented; the standalone
instrument is now archived with its negative advancement result.

Before running it, correct four instrument issues in the thesis:

1. **Stable noise does not imply a zero rectified gate.** With finite-window
   estimators, fast-minus-slow fluctuates on stationary noise. Clipping negative
   differences to zero leaves a positive average whenever positive excursions
   occur. Calibrate the stationary false-positive distribution; do not test the
   claim by expecting the gate to become literally zero.
2. **Variance and raw second moment differ.** Adam's second moment includes
   gradient mean as well as variance. Specify the statistic being compared and
   measure whether it responds to known switches rather than ordinary movement
   of the mean gradient. The Kalman-gain analogy is not an established derivation.
3. **An unlearnable state needs equal action payoffs.** T1's `p=0.5` description
   must mean reward probability 0.5 for every action in that state. A correct
   action paying half the time while wrong actions never pay remains learnable.
4. **Use equal tuning and compute budgets.** Include fixed-rate and single-
   timescale controls, stationary noisy/quiet controls, paired seeds and an
   independent confirmation set. Specify how the gate changes Adam before seeing
   results. A gain over a poorly tuned comparator is not the desired finding.

Measure switch detection and stationary false alarms separately from prediction
loss and adaptation time. Preserve negative results. If the gate cannot separate
the known conditions, stop that hypothesis before integrating it into brainsim.
If it succeeds, add the noisy-volatile task before making claims about the agent;
the existing deterministic suite cannot test the intended noise/change contrast.

The repository has not established novelty or advantages over modern optimisers
generally. A literature check is required before making those claims. The outcome
of v1 is a clearer, cheaper next experiment, not evidence of a breakthrough.
