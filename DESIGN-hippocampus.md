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
pair; `ADAPTIVE` cancelling `V(s)`).

I suspected the sleep gradient was already doing harm here. **It is not.**

At n=3 it looked damaging (ON 2.67 vs OFF 5.33) and I hypothesised that step 2
would partly be SUBTRACTION. At 6 seeds and the correct 12000-decision horizon
the result reverses:

```
  gradient ON (shipped)        [4, 8, 7, 8, 10, 20]   mean 9.50  median 8.0
  gradient OFF (replay only)   [1, 13, 3, 6, 5, 16]   mean 7.33  median 5.5
  no sleep at all              [10, 13, 5, 3, 7, 9]   mean 7.83  median 8.0
```

ON beats OFF in **5 of 6 seeds**. The n=3 signal was one seed's 13. Fourth time
in this project a small-n result pointed the wrong way -- and this one would have
had me delete a working mechanism.

(My probe printed "gradient-off beats gradient-on in 5/6", which is inverted: the
counter compares `on > off`. The label was wrong, the number right. Read the
means, not the summary line you wrote at 6am.)

**"Below floor" was also a horizon artifact.** At 12000 decisions the agent finds
~9.5 rewards = 0.0008, essentially its 0.0010 floor. The 0.0000 at 4000 decisions
was simply most seeds not having reached the goal yet. The agent is AT chance on
the lock, not below it — there is nothing to subtract, and step 2 is pure
addition after all.

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
| 5 | 4000 decisions is enough | 1 seed in 5 finds nothing | WRONG — use 12000 |
| 6 | sleep gradient harms here | ON beats OFF 5/6 seeds | WRONG — it helps |

## Experimental design, forced by assumption 1

A seed that never reaches the goal cannot be helped by replay, and averaging it
in would hide whatever effect exists. So the ablation table reports **per seed**
and conditions on `rewards_found >= 1`. Seeds finding zero reward are reported
separately as an EXPLORATION failure, not a replay failure — they are evidence
for a different module.

MEASURED horizon: at 4000 decisions 1 seed in 5 finds nothing; at **12000 every
seed finds reward** (first at 4338, 423, 1088, 255, 2254; 4-10 rewards each).
So the ablation runs at 12000 decisions, where every seed has >=4 episodes to
replay. Below that the task measures exploration, not memory.

## Open problem this surfaced

`ADAPTIVE` (volatility-driven noise) was shelved in step 1 for not helping
`volatile-4`. Sparse reward is a different case: raising exploration when reward
has not been seen for a long time is exactly what would fix seed 0. Worth
retesting HERE, on the task it might actually suit — but as a separate arm, since
step 1 also showed it cancelling `V(s)` when both are active.


---

# RESULT: the borrowed biology held, the invented mechanism did not

`lock-10`: **9.50 -> 333.50 rewards** (12000 decisions, 6 seeds). From 0.7% of
ceiling to 25%. The sparse-reward wall is broken.

```
  no replay (baseline)          9.50
  rev, no trace, TD           333.50   <- SHIPPED
  fwd, no trace, TD             4.17   <- direction matters 80x
  rev, no trace, NO TD          2.83   <- bootstrapping is essential
  rev, compressed trace, TD   115.50   <- the trace COSTS 3x
  rev, uncompressed trace, TD 133.00   <- compression costs on top of that
```

| component | source | verdict |
|---|---|---|
| reverse ordering | Foster & Wilson 2006 | **essential**, 80x |
| TD bootstrapping | standard RL | **essential**, 118x |
| eligibility trace across steps | MY design | **harmful**, costs 3x |
| time compression | MY design (headline claim) | **harmful** |
| prioritisation | design | untestable here -- the store only ever holds rewarded episodes |
| DG sparse coding | design | never built; rationale refuted before coding |

Reverse ordering works for the standard reason: updating backwards means each
state's successor is already fresh, so credit crosses the whole episode in ONE
pass. Forward order moves it one step per pass.

## Why the refinement loop missed this

Six assumption-probes before building caught five wrong assumptions -- and missed
the biggest one. They probed the PREMISES (is reward ever found, how long are
episodes, do the codes overlap, does the arithmetic hold) and never probed the
MECHANISM CLAIM. The arithmetic I verified most carefully (trace 0.222
uncompressed vs 0.860 compressed) was correct and entirely beside the point,
because the trace should not have been there at all.

**Probe the claim, not just its premises.**

## One regression, caught before shipping

With replay ungated, three tasks got worse: nway-4 0.961->0.890, xor-2
0.722->0.518, volatile-4 0.472->0.305. All three are SINGLE-STEP episodes, so
each decision became a 1-step "episode" -- reverse replay has no sequence to work
on, it merely duplicates the online update, and on a volatile task it reinstates
contingencies that have since changed.

Gating replay on `len(episode) >= 2` removes every regression at zero cost:
all five tasks now identical with replay on or off, lock unchanged at 333.5.

Fourth time a module validated on its target broke something else (k-WTA retiring
three mechanisms; ADAPTIVE cancelling V(s); the sleep gradient under sparse
reward). First time the regression suite caught it before it shipped -- which is
what step 0 was built for.
