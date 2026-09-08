"""Step 7b gate: the port must be BIT-EXACT against brainsim.py.

`port-keeps-the-reference-number`: twice in this project a reimplementation
returned a plausible WRONG number, and both times the original's result was the
only thing that caught it. An approximate port is worse than no port, because a
5% drift looks like a seed. So the gate is equality, not closeness.
"""
import time, numpy as np
from brainsim import BrainSim
from fastsim import FastBrainSim
from tasks import NWay, Lock, Volatile, Conjunctive, TMaze, run

CASES = [("nway-4", lambda s: NWay(4, seed=s), 4, 400),
         ("nway-8", lambda s: NWay(8, seed=s), 8, 400),
         ("lock-10", lambda s: Lock(10, seed=s), 2, 400),
         ("volatile-4", lambda s: Volatile(4, seed=s), 4, 400),
         ("xor-2", lambda s: Conjunctive(seed=s), 2, 400),
         ("tmaze-2", lambda s: TMaze(2, seed=s), 2, 400)]

ok = True
for name, mk, nm, dec in CASES:
    for seed in (0, 1):
        t0 = time.time(); a = BrainSim(n_motor=nm, seed=seed)
        h1 = run(a, mk(seed), dec, seed=seed); t1 = time.time()
        b = FastBrainSim(n_motor=nm, seed=seed)
        h2 = run(b, mk(seed), dec, seed=seed); t2 = time.time()
        same = np.array_equal(h1, h2)
        ok &= same
        print(f"  {name:11s} seed{seed}  ref={h1.mean():.4f} port={h2.mean():.4f}"
              f"  {'EXACT' if same else '*** DIVERGED ***'}"
              f"   {t1-t0:.1f}s -> {t2-t1:.1f}s ({(t1-t0)/max(t2-t1,1e-9):.1f}x)",
              flush=True)
print("\nGATE:", "PASS -- port is bit-exact" if ok else "FAIL -- do not use the port")
if not ok:
    raise SystemExit(1)
