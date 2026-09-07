# Step 3: basal ganglia — disinhibition + Go/NoGo opponent channels

Target: the `nway-8` gap. Local `TAGGATE` reaches **0.769**; the non-local
`ACTION_GATED` reference reaches **0.900**. At `nway-4` there is no gap (0.961 vs
0.959), so whatever is missing appears only as the action set grows.

## What the BG offers that we hand-rolled

**Disinhibition.** Default is everything BLOCKED by tonic inhibition (GPi/SNr);
the winning action is *released* when striatum inhibits the inhibitor. Selection
by removing a block, not by accumulating votes and taking an argmax.

**Go/NoGo opponent channels.** D1 (direct) promotes an action, D2 (indirect)
suppresses it, with opposite dopamine sensitivity: a burst strengthens Go, a dip
strengthens NoGo. Two populations per action instead of one signed weight.

**Dopamine-gated plasticity.** Only synapses on cells in an up-state change --
which is what `TAGGATE` already does crudely.

## Predictions, written before building

1. **BG should retire `TAGGATE`.** A real selection circuit subsumes a hand-rolled
   credit gate. This project's most repeated pattern is a new mechanism making an
   older one redundant while the old one keeps running and costing.
2. **It will probably break something else.** Four modules in a row have (k-WTA
   retired three mechanisms; ADAPTIVE cancelled V(s); replay damaged three tasks).
   The regression suite exists for this.

## Mechanism claims to probe BEFORE building

The hippocampus refinement loop checked five premises, missed the mechanism
claim, and shipped a headline that was worse than useless. **Probe the claim.**

| # | claim | probe |
|---|---|---|
| 1 | the readout cannot express negative evidence, and that binds at 8 actions | does `WMIN=-1` help at nway-8 NOW (at 0.769)? Tested at 0.152 before TAGGATE and found nothing -- different regime now |
| 2 | selection is the bottleneck | vote margin at nway-8 vs nway-4 |
| 3 | credit still lands on the wrong action | how often does the TAGGATE-tagged cell equal the chosen action? If they diverge at 8 and agree at 4, that IS the gap |
| 4 | TAGGATE is doing real work here | TAGGATE on/off at nway-8 in the current build |

If claim 1 fails, the Go/NoGo rationale is dead and only disinhibition remains.
If claim 3 shows agreement is already high, selection is not the problem and the
gap is elsewhere -- build nothing until that is understood.

## Prior evidence AGAINST this design

**A bound-based race already failed.** The `commitment` experiment (accumulate to
a bound, then lock) scored 0.350 vs 0.323 at 4 classes and went bimodal at 2
(0.50/1.00/0.50). Disinhibition is a close cousin: first action to break through
the block wins. The difference is that commitment LOCKED with no escape, while
disinhibition is graded and re-engageable -- but this is close enough that the
probe must distinguish them, not assume the difference matters.

## Risks

**Three writers on `W_out` already** -- online, sleep gradient, replay. BG adds a
fourth path shaping the same signal. Two controllers on one variable has bitten
twice (Part 3b's homeostatic pair; ADAPTIVE vs V(s)).

**`V(s)` and Go/NoGo both encode value.** The critic already learns V(s); a NoGo
channel is a second negative-value estimate. Check they do not fight.

**Timescales**, stated up front: tonic inhibition is instantaneous (per tick);
striatal plasticity rides the existing eligibility/NM path; no new slow variable
unless the probes demand one.
