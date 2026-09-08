# Step 8: plasticity gating — learn when NOT to update

**Prediction written before the probe returned.** `DESIGN-predictive-coding.md`
set the rule; it is the only thing that stops a result being reinterpreted after
the fact.

## The claimed gap

From step 5: *the design cannot absorb decisions that do not matter.* An
unrewarded arbitrary action draws a negative RPE into a policy sharing hidden
units with the step that counts. An **oracle** handed the cue still reached only
54% of ceiling on `tmaze-2d3`.

**That number predates the `decide()` tie-break fix**, which invalidated every
multi-action result in the project. It is re-measured here, not assumed.

## Two gates, in order

Step 6 probed the *premise* and never the *mechanism*, and the hippocampus
shipped a headline that turned out to be actively harmful. So both:

1. **Premise.** Does the gap scale with the number of unrewarded decisions?
   `delay=0` is the control — no irrelevant decisions, so no gap. If `delay=0`
   and `delay=5` look the same, the instrument is measuring something other than
   its name and the premise is dead.
2. **Mechanism ceiling.** Does a *perfect* gate close it? `oracle` is
   deliberately privileged — it uses `done` as a scored/unscored signal the
   agent cannot know. **If a perfect gate does not help, no real gate will**, and
   step 8 dies for the cost of one run rather than a week of building.

Two oracle variants, because the choice is not obvious:

- `oracle` — suppress the policy update on unscored decisions. Credit from the
  irrelevant step is discarded.
- `oracle_carry` — also skip eligibility consumption, so credit *carries* to the
  decision that is actually scored. This is tag-and-capture under delayed
  reward, and it is the variant I expect to win if either does.

The gate scales the **policy update only**. `V(s)`, the traces, replay and every
reset stay untouched — skipping `reward()` wholesale is a bug this project has
already made once, because it skipped the state resets too.

## Prediction

- Gate 1 **passes**: fraction-of-ceiling falls with delay. This is the one thing
  two independent measurements already agree on.
- Gate 2 **passes, but only for `oracle_carry`**. Plain `oracle` throws the
  credit away; the T-maze needs it *moved*, not deleted. If plain `oracle` wins
  instead, my model of the failure is wrong and the write-up must say so.
- On `lock-10` this should be **harmful** if applied there, since `done` fires
  only at the goal and the intermediate steps are exactly what replay needs.
  Not tested here; flagged so it is not shipped globally without checking.

## Relationship to step 7's finding

The reference table shows brainsim losing `xor-2` and `volatile-4` to tabular-Q,
the one baseline with zero interference. Step 8's diagnosis — *credit from an
irrelevant decision contaminating shared hidden units* — **is an interference
statement**. Step 8, step 9 (local pools) and `V3.md` §11.1 are three attacks on
one problem, and should be ablated against each other rather than shipped in
sequence.
