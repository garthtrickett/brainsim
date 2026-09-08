"""Step 9: local competitive pools.

PREMISE (measured in step 6): capacity collapses as stimulus combinations grow,
with 80 units and one global k-WTA --
    4 combos 0.946 | 9 combos 0.644 | 16 combos 0.385
Step 7 then showed brainsim losing xor-2 and volatile-4 to tabular-Q, the ONE
baseline with a separate entry per state and therefore zero interference. Two
independent measurements pointing at the same thing.

POOLS>1 keeps total sparsity IDENTICAL (P pools x k/P winners = k) and changes
only whether competition is global or local. So a difference cannot be a
sparsity difference -- that confound killed earlier ablations here.

Runs on plain BrainSim: the numba kernel does not implement pools, and a port
that silently ignored the option would return a plausible wrong number.
"""
import numpy as np, json
import tasks
from brainsim import BrainSim

SEEDS = 5
POOLS = [1, 2, 4, 8]

def score(h, tail): return float(h[-tail:].mean())

def run(mk, nact, dec, tail, pools, seed, runner="run"):
    a = BrainSim(n_motor=nact, seed=seed); a.POOLS = pools
    r = tasks.run(a, mk(seed), dec, seed=seed)
    return score(r, tail)

CASES = []
c = tasks.Compositional(4, 4, seed=0, held_out=0)
CASES.append(("compositional-4x4", lambda s: tasks.Compositional(4,4,seed=s,held_out=0),
              c.n_actions, 4000, 1000))
CASES.append(("xor-2",      lambda s: tasks.Conjunctive(seed=s),      2, 4000, 1000))
CASES.append(("volatile-4", lambda s: tasks.Volatile(4,300,seed=s),   4, 4000, 1000))
CASES.append(("nway-8",     lambda s: tasks.NWay(8,seed=s),           8, 4000, 1000))

print(f"step 9: local pools | {SEEDS} seeds | total sparsity held constant\n", flush=True)
print(f"{'task':<20} {'floor':>7} {'ceil':>7} | " +
      " ".join(f"{'P='+str(p):>8}" for p in POOLS), flush=True)
out = {}
for name, mk, nact, dec, tail in CASES:
    fl = np.mean([score(tasks.random_policy(mk(s), dec, seed=s), tail) for s in range(SEEDS)])
    ce = np.mean([score(tasks.oracle(mk(s), dec, seed=s), tail) for s in range(SEEDS)])
    row = {}
    for p in POOLS:
        row[p] = float(np.mean([run(mk, nact, dec, tail, p, s) for s in range(SEEDS)]))
    out[name] = {"floor": float(fl), "ceiling": float(ce),
                 **{str(k): v for k, v in row.items()}}
    print(f"{name:<20} {fl:>7.3f} {ce:>7.3f} | " +
          " ".join(f"{row[p]:>8.3f}" for p in POOLS), flush=True)

json.dump(out, open("probe_step9.json", "w"), indent=1)
print("\nGATE: does any P>1 beat P=1 on the INTERFERENCE tasks "
      "(compositional, xor-2, volatile-4) without breaking nway-8?")
for name in ("compositional-4x4", "xor-2", "volatile-4"):
    b1 = out[name]["1"]
    best = max(POOLS[1:], key=lambda p: out[name][str(p)])
    print(f"  {name:<20} P=1 {b1:.3f} -> best P={best} {out[name][str(best)]:.3f}"
          f"  delta={out[name][str(best)]-b1:+.3f}")
n1 = out["nway-8"]["1"]
print(f"  nway-8 regression      P=1 {n1:.3f} -> " +
      " ".join(f"P={p} {out['nway-8'][str(p)]:.3f}" for p in POOLS[1:]))
