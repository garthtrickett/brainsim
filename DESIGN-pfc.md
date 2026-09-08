# Step 5: PFC working memory

Target: `tmaze-2d3`. Floor 0.123, current **0.124**, ceiling 0.250.

Structure: cue at reset, two neutral steps, a "choose" pattern, then the 4th
decision is scored. The cue is **3 decisions gone** when the choice is made.

## Why nothing currently persists

`trh` decays at `TRACE_D=0.80`, so tau ~4.5 ticks. Three decisions is 90 ticks:
`0.8^90 = 1.6e-9`. Everything else (`trh_sum`, `trm`, `elig`) is explicitly reset
per decision. There is no state in this design that outlives a decision, so the
task is not merely hard -- it is **structurally impossible**, which is why it sits
exactly at floor rather than slightly above it.

## The gate problem, and an orphaned mechanism that fits

Persistent activity is easy; knowing WHEN TO WRITE is the hard part. Write always
and the cue is overwritten by the neutral and choice patterns. The standard answer
is a BG gate -- but step 3 is shelved, so it needs its own local signal.

**We have an orphaned world model.** Part 1 built it (prediction error
0.275 -> 0.190; surprise spikes correctly within 300 ticks of a rule change) and
then cut its only consumer when curiosity failed. A cue arriving at episode start
is unpredicted; the neutral pattern that follows is highly predictable. So
**surprise is a candidate write gate** -- and that finally gives the world model a
consumer, which the step 4 design flagged as the one substantive thread left.

## Mechanism claims to probe BEFORE building

The hippocampus loop probed premises and missed the mechanism claim, shipping a
headline that was worse than useless. Probe the CLAIM.

| # | claim | probe |
|---|---|---|
| 1 | memory is the ONLY missing piece | give the cue at decision time (superimpose cue on the choice pattern). If it still fails, the problem is not memory |
| 2 | nothing persists across decisions | measure `trh` similarity across a 3-decision gap; expect ~0 |
| 3 | **surprise distinguishes cue from delay** | measure prediction error at each step of the episode. If the cue is not more surprising than the neutral steps, the gate cannot work and the design is dead |
| 4 | a perfect memory suffices | oracle WM: append the true cue to the hidden state and measure the ceiling actually reachable |

Claim 3 is the load-bearing one. Claims 1 and 4 bound what is achievable.

## Prediction, written first

I expect claim 1 to hold (cue-at-decision solves it) and claim 3 to be the risk:
the world model may not separate cue from neutral, because both are just patterns
and the model was never trained to expect episode structure.

If claim 3 fails there is a fallback: gate on **change** (input differs from the
previous step) rather than on model surprise. Cruder, still local, no world model
needed. If that also fails, the honest outcome is that WM needs a gate this
design cannot supply locally, which is the same conclusion step 3 reached about
credit alignment before the bug fix rescued it.
