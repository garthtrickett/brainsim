# Step 2: hippocampus — episodic store + time-compressed reverse replay

Target: `lock-10`. Measured floor 0.0010, current agent **0.0000**, ceiling 0.1110.
The agent scores *below* random because it learns the wrong thing from near-zero
signal.

## Two separate failures

**Reward density.** MEASURED, not assumed: the current agent finds the goal
**0, 3 and 1 times** across three seeds in 4000 decisions. One seed finds NONE.

That is worse than the floor estimate suggested and it changes the design:
replay is *multiplicative* on reward found. Zero times anything is zero, so a
seed that never reaches the goal stays at 0.000 however good the replay is.
**Exploration is a co-equal blocker, not a solved precondition.**

**Credit does not propagate backwards.** Eligibility is consumed and zeroed at
every decision. When reward finally arrives only the LAST decision is credited;
the 9 correct actions that led there get nothing. A successful episode teaches
"at state 9, do X" — and state 9 is almost never reached.

## Why compression is the mechanism, not decoration

`ELIG_D = 0.995` → τ ≈ 200 ticks.

```
  10 steps x 30 ticks = 300 ticks -> trace at episode start = 0.222   (verified)
  10 steps x  3 ticks =  30 ticks -> trace at episode start = 0.860   (verified)
```

Compression is what lets ONE eligibility trace span a whole episode.

**But it only matters for the RARE episodes.** Measured run lengths: mean 1.9,
p95 = 4-5. The typical run is 2 steps = 60 ticks, where the trace is already
0.74 — compression buys nothing. It matters only for the 9-10 step runs that
actually reach reward, which are 0-3 per 4000 decisions.

Consequence: **prioritisation is load-bearing, not a refinement.** The buffer
will hold ~2000 runs of 2-step junk and one or two that matter. Uniform sampling
would almost never touch the useful one.

## Structure

**Episodes, not decisions.** The buffer currently holds flat
`(z, de, nm, action, r)` tuples. It becomes a list of sequences
`[(z_t, a_t, r_t), ...]` from episode start to termination. Without sequence
structure there is nothing to replay backwards.

**Reverse replay after reward.** After reward, place-cell sequences replay
backwards from the goal (Foster & Wilson 2006). Mechanically that is backward
credit propagation. Forward replay is the CONTROL: if forward and reverse are
equal, direction is irrelevant and this is an oversampled buffer wearing
hippocampal language.

**Prioritised selection**, biased to rewarded and surprising episodes. With ~4
rewards in 4000 decisions, uniform sampling would almost never replay the one
episode worth replaying.

**Sparse storage code (DG-style)** — DEMOTED to speculative. My rationale was
interference between adjacent lock states. Measured, adjacent states overlap
**0.409** and random pairs **0.447**: adjacent states are if anything LESS
similar, so there is no adjacent-state interference to separate. Overall overlap
is high (0.447, max 0.706), so sparsening might still help generally — but not
for the reason given, so it goes in as a low-priority ablation arm, not a
component.

## `V(s)` is a prerequisite, shipped by accident

Reverse replay plus a state value function IS a TD backup along the sequence.
`V(s)` shipped in step 1 for an unrelated reason (`volatile-4`), and it is
exactly what this needs. Luck, not planning — but it means step 2 builds on
something already validated.

## Ablations, designed in

| arm | tests |
|---|---|
| no replay (current) | baseline, 0.0000 |
| forward, uncompressed | does replay alone help? |
| reverse, uncompressed | does DIRECTION matter? |
| forward, compressed | does COMPRESSION matter? |
| **reverse, compressed** | the full design |
| uniform vs prioritised | does prioritisation matter at 4 rewards? |
| sparse vs standard code | does pattern separation matter? |

Decisive comparison: **compressed-forward vs compressed-reverse**.

## Risks

**Three writers on `W_out`** — online learning, the sleep gradient, and now
replay. Two controllers on one variable has bitten twice (Part 3b's homeostatic
pair; `ADAPTIVE` cancelling `V(s)`). The sleep gradient ALREADY replays from this
buffer, so the two must be coordinated, not both firing blind.

**The lock is unusually kind to replay.** It has exactly one correct path, so
overfitting to a single replayed trajectory is *correct* here. That will not
generalise to tasks with many solutions and must not be claimed to.

**Timescales**, stated up front: storage one-shot; replay at sleep (every 50
decisions) and immediately post-reward; compression 10x; eligibility τ≈200 ticks
unchanged, now spanning a 30-tick compressed episode.

## Assumptions, verified (`26_hippocampus_probes.py`)

| # | assumption | measured | verdict |
|---|---|---|---|
| 1 | agent finds reward a few times | **0, 3, 1** across seeds | WRONG — can be zero |
| 2 | episodes are ~10 steps | mean **1.9**, p95 **4-5** | WRONG — only rare ones are long |
| 3 | adjacent states interfere | adjacent **0.409** vs all-pairs **0.447** | WRONG — no special interference |
| 4 | trace 0.22 vs 0.86 | 0.222 / 0.860 | correct |

## Experimental design, forced by assumption 1

A seed that never reaches the goal cannot be helped by replay, and averaging it
in would hide whatever effect exists. So the ablation table reports **per seed**
and conditions on `rewards_found >= 1`. Seeds finding zero reward are reported
separately as an EXPLORATION failure, not a replay failure — they are evidence
for a different module.

If most seeds find zero reward at 4000 decisions, lengthen the run until they do
rather than averaging a wall of zeros. The gate is: at least 2 of 3 seeds must
find reward at all, or the task is measuring exploration and not memory.

## Open problem this surfaced

`ADAPTIVE` (volatility-driven noise) was shelved in step 1 for not helping
`volatile-4`. Sparse reward is a different case: raising exploration when reward
has not been seen for a long time is exactly what would fix seed 0. Worth
retesting HERE, on the task it might actually suit — but as a separate arm, since
step 1 also showed it cancelling `V(s)` when both are active.
