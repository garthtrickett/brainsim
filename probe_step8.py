"""Step 8 probe: plasticity gating.

TWO questions, in order, because step 6 probed only the PREMISE and the
hippocampus shipped a headline that was actively harmful:

  1. PREMISE  -- does the gap exist, and does it SCALE with the number of
                 unrewarded decisions? A control at delay=0 (no irrelevant
                 decisions) must show no gap, or the instrument is measuring
                 something else.
  2. CEILING  -- does a PERFECT gate close it? `oracle` is privileged: it uses
                 `done` as a scored/unscored signal the agent cannot know. If a
                 perfect gate does not help, no real gate will, and step 8 dies
                 here for the cost of one run.

The premise was measured BEFORE the decide() tie-break bug was fixed, which
invalidated every multi-action result. It is re-measured, not assumed.
"""
import numpy as np, json
from fastsim import FastBrainSim
import tasks

SEEDS, DEC = 5, 6000
DELAYS = [0, 1, 2, 3, 5]
MODES = ["off", "oracle", "oracle_carry"]

def score(h, tail=1500): return float(h[-tail:].mean())

def run_mode(delay, mode, seed):
    a = FastBrainSim(n_motor=2, seed=seed)
    a.PGATE = mode
    return score(tasks.run(a, tasks.TMaze(2, delay, seed=seed), DEC, seed=seed))

print(f"step 8 premise + gate ceiling | {SEEDS} seeds, {DEC} decisions\n", flush=True)
print(f"{'delay':>6} {'floor':>7} {'ceil':>7} | " +
      " ".join(f"{m:>13}" for m in MODES) + "   frac-of-ceiling", flush=True)

out = {}
for d in DELAYS:
    fl = np.mean([score(tasks.random_policy(tasks.TMaze(2, d, seed=s), DEC, seed=s))
                  for s in range(SEEDS)])
    ce = np.mean([score(tasks.oracle(tasks.TMaze(2, d, seed=s), DEC, seed=s))
                  for s in range(SEEDS)])
    row = {}
    for m in MODES:
        row[m] = float(np.mean([run_mode(d, m, s) for s in range(SEEDS)]))
    fr = {m: (row[m] - fl) / (ce - fl) if ce > fl else float("nan") for m in MODES}
    out[d] = {"floor": float(fl), "ceiling": float(ce), **row,
              "frac": {k: float(v) for k, v in fr.items()}}
    print(f"{d:>6} {fl:>7.3f} {ce:>7.3f} | " +
          " ".join(f"{row[m]:>13.3f}" for m in MODES) +
          "   " + " ".join(f"{m}={fr[m]:.2f}" for m in MODES), flush=True)

json.dump(out, open("probe_step8.json", "w"), indent=1)
print("\nGATE 1 (premise): does frac-of-ceiling for 'off' FALL as delay grows?")
f0, f5 = out[0]["frac"]["off"], out[DELAYS[-1]]["frac"]["off"]
print(f"  delay=0 {f0:.2f} -> delay={DELAYS[-1]} {f5:.2f}  "
      f"{'PASS -- premise holds' if f5 < f0 - 0.10 else 'FAIL -- no scaling gap, step 8 premise is dead'}")
print("\nGATE 2 (mechanism ceiling): does a PERFECT gate beat 'off' at delay>0?")
best = max(MODES[1:], key=lambda m: np.mean([out[d]['frac'][m] for d in DELAYS[1:]]))
bo = np.mean([out[d]['frac']['off'] for d in DELAYS[1:]])
bb = np.mean([out[d]['frac'][best] for d in DELAYS[1:]])
print(f"  off={bo:.3f}  best({best})={bb:.3f}  "
      f"{'PASS -- worth building a real gate' if bb > bo + 0.05 else 'FAIL -- even a perfect gate does not help; step 8 dies here'}")
