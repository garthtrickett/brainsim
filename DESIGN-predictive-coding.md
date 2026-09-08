# Step 6: predictive-coding hierarchy

**Prior evidence says do not build this.** Twice measured that representation is
not the bottleneck:

- hidden codes were MORE separable at 4/8 classes (0.549) than at the 2-class
  case that worked (0.622);
- `xor-2`, built specifically so a fixed random encoder should fail, is solved at
  **0.839**. Sparse random projection + k-WTA is *good* at conjunctions -- the
  winning set depends on the input COMBINATION. That is why random feature
  expansions make XOR separable, and it is the cerebellar granule-layer
  architecture, which exists to build conjunctive codes.

## What every previous attempt got wrong

Both failed tasks tested **discrimination of patterns the encoder had already
seen**. A random expansion is excellent at that: with 80 units and k=6 there are
C(80,6) ~ 3e8 possible codes, so almost any set of seen patterns gets distinct
representations. Discrimination was never going to bind.

Representation learning should matter for **generalisation to combinations never
seen during training**. A random code for `A1+B2` tells you nothing about
`A1+B3` unless the code factorises into an A-part and a B-part -- which is
exactly what a learned representation buys and a random one does not.

That needs a **train/test split**, which `tasks.run` does not have. Building it
is most of the work of this step.

## The task: compositional generalisation

Stimuli are `shape_i + colour_j` (two feature groups, 4x4 = 16 combinations).
The label is a function of BOTH factors. Train on 12 combinations, hold out 4.

- A **factorised** representation generalises: having seen `A1B1`, `A1B2`,
  `A2B1`, it can place `A2B2`.
- A **conjunctive/random** representation cannot: the held-out combination has a
  code it has never seen and no structure relating it to what it has.

GATE, in order:
1. **Train accuracy must be high.** If the design cannot even fit 12 seen
   combinations, the task is too hard and the held-out number is noise.
2. **Held-out accuracy must be at chance for the FIXED encoder.** If a random
   encoder already generalises, representation is genuinely not the bottleneck
   and step 6 is shelved on evidence rather than on my say-so.
3. Only if 1 and 2 both hold is there a gap for predictive coding to close.

## Prediction, written first

I expect gate 1 to pass and gate 2 to **fail** -- i.e. the random encoder will
generalise better than the compositional story predicts, because overlapping
sparse codes do carry partial factor information (`A2B2` shares active units with
both `A2B1` and `A1B2`). If so, step 6 is shelved for the third time, and the
finding is that this architecture does not need representation learning at the
scale it operates at.
