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
