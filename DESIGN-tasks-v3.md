# Task scope for v3

**§12 of `V3.md` framed the risk as scale: "80 units and 30 ticks, every v3
effect is about scale and time." Reading `tasks.py` shows that framing is mostly
wrong, and the real problem is cheaper to fix and worse to ignore.**

The suite is not primarily too *small*. `Volatile` already holds a mapping stable
for 300 trials before permuting, which is a real horizon. The suite is missing
specific *properties* that individual v3 mechanisms need in order to be
measurable at all.

Method: work backwards from each mechanism to the task property it requires, and
check whether the property exists.

---

## The blocking finding: our tasks contain no noise

`Volatile.step` is:

```python
return self.pats[self.c], float(a == self.map[self.c]), True
```

Reward is **deterministic**. So is `NWay`, `Conjunctive`, `TMaze`, `Lock`,
`Compositional`. Across the entire suite, a correct action always pays and an
incorrect one never does.

§9's whole claim is that **one variance estimator cannot separate "this is
noisy" from "this just changed."**

**In a suite with no noise, that confusion does not exist.** A two-timescale gate
would show no benefit over a one-timescale gate, and we would read that as *the
idea is wrong* when it means *the task cannot express the distinction*.

That is HISTORY.md's most-repeated failure — six instruments measuring something
other than their name — and it would have taken out the critical path. Caught
before running, which is the only cheap time to catch it.

---

## Requirements, per mechanism

| mechanism | property required | present? |
|---|---|---|
| §9 two-timescale gate | stochastic-but-stable states **coexisting with** deterministic-but-switching ones | **no — blocking** |
| 10.1 differencing pair | nothing new; refactor + ablation on the existing suite | yes |
| 10.2 reconsolidation | old states recur after a rule change; a no-replay control | partly (`Volatile` recurs) |
| 10.3 event boundaries | continuous stream, hidden boundaries, ground truth logged | **no** — only `Lock` is multi-step and its boundary is the goal |
| 11.1 interference → discovery | a ground-truth latent variable determining the mapping | **no** |
| 11.2 grown structure | capacity pressure **plus** a known correct size to grow toward | partly (`Compositional`) |
| 11.3 forgetting as default | an A → B → A phase sequence with matched-plasticity retention | **no** |

Only 10.1 is runnable on the suite as it stands.

---

## T1 — `noisy-volatile` — unblocks §9. Build first.

Four states. The mapping permutes every 300 trials as now, but payoff becomes
probabilistic and **heterogeneous across states**:

- 2 *reliable* states: correct action pays with p = 0.9
- 1 *marginal* state: p = 0.65
- 1 *unlearnable* state: p = 0.5 — genuinely random, no policy beats chance

A single-timescale estimator must keep plasticity high on the unlearnable state
forever, because it never stops looking surprising. A two-timescale gate must
drive it to zero there and spike only after a permutation.

**Measure the gate directly, not task accuracy.** Log gate value per state and
compare against the two ground truths we control (which state is noise, when the
switch happened). That is a mechanism test whose result does not depend on the
agent being any good, which makes it far stronger than an accuracy comparison
and immune to the confound that killed earlier ablations.

Floor and ceiling must be *measured*, not derived — the mixed-p oracle is not
1.0 and assuming it analytically is how `nway-8` went wrong.

---

## T2 — `context-bandit` — unblocks 11.1

A hidden binary context `c` flips every 200 trials and is **not in the
observation**. The correct action depends on `(state, c)`.

Without context discovery the agent is stuck near the mid-point between the two
mappings — that is the honest null and it must be measured first.

The test for 11.1 is not accuracy. It is: **does the direction discovered from
the contested weights correlate with `c`?** We know `c`, so this has a
constructible ground truth and a clean yes/no.

---

## T3 — `run_sequence` — unblocks 11.3, and 10.2's control

A runner, not a task: `run_sequence(agent, [A, B, A], decisions_each)`, returning
per-phase curves and retention on A.

It must report retention **at matched plasticity on B**, per §11.3's falsifier.
A method that forgets less because it learned less must be visibly disqualified
by the instrument itself, not by my judgement afterwards.

---

## T4 — `stream` — unblocks 10.3

Continuous, no `done` at all. Concatenated segments of varying length with no
boundary signal in the observation; true boundaries logged and withheld.

Test: do gate spikes coincide with true boundaries above chance? This also
supplies v2 the episode definition it currently lacks (PRD Q4).

---

## T5 — capacity ladder — for 11.2

`Compositional` at 2×2, 3×3, 4×4, 5×5 with `n_hidden` fixed at 80 — half of this
exists already (0.946 → 0.385 over 4 → 16 combinations).

What is missing is the **target**: hand-sweep `n_hidden` per rung to find the
size that suffices. Without it, "the network grew" is unfalsifiable — growth has
to be compared against a size somebody else would have chosen.

---

## What does *not* need to change

- **Network size.** 80 units with k = 6 stays fixed everywhere except T5. The
  temptation is to scale everything at once; that would change two variables and
  make every result unattributable.
- **Ticks per decision.** 30 stays. It is settling time, not horizon — horizon
  comes from the number of decisions, which T1/T3 already extend.
- **The existing seven tasks.** They stay as-is and stay in the frozen reference
  table. New tasks are additions; nothing is retuned.

---

## Cost

At the measured ~140 µs/tick: 3,000 decisions × 30 ticks ≈ 12.6 s per seed. Five
seeds × six conditions ≈ 6 minutes. T1, T2 and T4 are all affordable in plain
numpy.

T3 and T5 want roughly 10× that and are the first genuine use for `fastsim.py`
(step 7b) — which is unverified, and per `port-keeps-the-reference-number` must
reproduce the frozen table before it is trusted for anything.

---

## Order

1. **T1** — unblocks the critical path inside brainsim
2. **T3** — a runner, reused by two mechanisms
3. **T2** — the §11 swing with the cleanest falsifier
4. **T4**, then **T5**

None of this blocks §9's *first* experiment, which is Adam vs two-timescale Adam
on a non-stationary supervised toy and touches none of our tasks. That one stays
in front.
