# Step 4: cerebellum — consolidation, not capability

The plan called this "naming the sleep gradient as the third learning system".
That is descriptive work, and descriptive work cannot be wrong, which makes it
useless as a step. The sharp question is different:

**Does the sleep gradient still earn its place?**

It was validated in Part 3: +0.06 over MATCHED local replay, 5/5 seeds. That was
measured before `V(s)`, before the hippocampus, and before the `decide()` fix.
Three regime changes since. Three conclusions have already flipped when their
regime moved (the sleep gradient itself at n=3 vs n=6; `V(s)`; `ADAPTIVE`).

A mechanism validated in a regime that no longer exists is not validated.

## What the cerebellum actually offers, beyond a label

| feature | do we have it | substantive? |
|---|---|---|
| sparse random expansion (granule layer) | YES -- k-WTA 6/80 from 40 in | already there, and measured GOOD at conjunctions (xor-2 0.721 on a fixed random encoder) |
| error-driven supervised learning | YES -- the sleep gradient | this is the thing to re-validate |
| explicit teaching signal (climbing fibre) | partly -- targets come from reward | a separate teacher would be new |
| **forward model** (predict sensory consequences of action) | **built and ORPHANED** | the world model from Part 1 has no consumer |
| precise timing | no | out of scope |

The one genuinely substantive thread: **we built a world model (prediction error
0.275 -> 0.190, surprise spikes correctly on a rule change) and then cut its only
consumer when curiosity failed.** The cerebellum is the natural consumer -- a
forward model that predicts the consequences of actions. That is capability, not
naming.

## Probes, before building anything

1. **Does the sleep gradient still contribute?** SLEEP_ETA on/off across every
   task, current defaults, 6 seeds. If it contributes nothing now, the honest
   move is to REMOVE it, not rename it.
2. **Does replay subsume it?** The hippocampus replays the same buffer. If
   removing the gradient costs nothing while replay is on, they are redundant.
3. Only if (1) survives: is a forward-model teaching signal worth building?

## Prediction, written first

I expect the sleep gradient to have been **subsumed by hippocampal replay** --
both learn offline from the same buffer, and replay is the stronger mechanism
(it broke the lock 35x). If so, step 4 is a DELETION and the cerebellum reduces
to the granule-layer expansion we already have.
