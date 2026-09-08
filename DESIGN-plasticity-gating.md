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

---

# Result (2026-09-08). Verdict: measured, ship nothing.

```
tmaze delay sweep, 5 seeds, fraction of measured ceiling

 delay |   off    oracle  oracle_carry |  hold  gate+hold
     0 |  1.00      1.00          1.00 |     -          -     <- control: no gap
     1 |  0.03      0.64          0.65 |  0.02       0.20
     2 |  0.02     -0.00         -0.00 |  0.02       0.13
     3 | -0.01     -0.07         -0.03 | -0.00      -0.01
     5 | -0.01      0.00         -0.01 |  0.01       0.00
```

## Gate 1 — premise: PASS, cleanly

`delay=0` sits exactly at ceiling and the gap appears the moment one unrewarded
decision is added. The control could have moved and did not, which is the check
three of four earlier ablations failed.

## Gate 2 — printed PASS. Not accepted as printed.

The whole of Gate 2 is **one row**. At `delay=1` a perfect gate takes 3% of
ceiling to 65%, which is large and real. At `delay>=2` a *perfect* gate does
**nothing**, and at `delay>=3` nothing works at all.

Four wrong conclusions in this project came from a single data point. The
supported claim is not "gating works" but *"gating works for exactly one
unrewarded step."* No real gate can beat the oracle, since the oracle is handed
the answer — so the honest ceiling on step 8 is a mechanism that helps in one
narrow case.

## The memory hypothesis was wrong

`reward()` clears WM on every call, so the cue cannot cross a decision boundary.
That looked like the obvious cause of the `delay>=2` floor. It is not:

- **`WM_HOLD` alone does nothing** — `hold` tracks `off` at every delay.
- `gate+hold` gives 0.13 at `delay=2`, the only thing that moves there, but it
  **halves the `delay=1` result** (0.65 -> 0.20). It trades one case for another.
- The automated verdict line printed "MEMORY was the limit" on a 0.043 vs 0.038
  threshold squeak. It is wrong and is recorded here as wrong.

**And it is not WM decay either.** `WM_DECAY=0.999` is tau=999 ticks; at
`delay=5` the cue must survive 150 ticks and 86% of it does. The signal is
present.

The remaining hypothesis, **unmeasured**: `wm` is a running integrator
(`wm = wm*DECAY + WM_LR*g*fh`), so the cue is not lost to decay but **diluted**
by 30 more ticks of accumulated input per added delay. At `delay=1` the cue is a
large share of WM contents; by `delay=3` it is a quarter. Recorded as a
hypothesis, not a finding.

## Decision

**Ship nothing.** `PGATE` and `WM_HOLD` stay in the source, default off, as
instruments. Step 8 joins the basal ganglia, predictive coding (twice), the
cerebellum and curiosity: measured, and the answer was do not build it.

Regression clean — with both options off, `nway-8`, `volatile-4` and `xor-2`
reproduce `reference.json` per-seed exactly.
