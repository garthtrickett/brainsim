"""Brain-plausible replacements for the non-local ACTION_GATED fix.

An earlier version of this test used a SUBCLASS that reimplemented step() and
silently dropped synaptic scaling, degrading every row including the reference
(ACTION_GATED read 0.792/0.632 instead of its true 0.959/0.900). The mechanisms
now live in BrainSim itself and are toggled by attribute -- one implementation,
nothing to drift. The reference is measured in THIS run for the same reason.

Mechanisms:
  PERSIST  recurrent self-excitation + pooled lateral inhibition. Amplifies an
           early noise-driven lead and sustains it to reward, so credit and the
           decision coincide in TIME.
  TAGGATE  a synapse tags only if its cell clears THETA x (pooled max), i.e.
           winner-take-all on CREDIT over the trial.

Measured motor traces are [9.53 9.48 9.53 9.48] -- 0.5% apart -- so any THETA
below ~0.99 admits every cell and gates nothing. THETA=1.0 (exact max) is the
real local WTA, and is the biologically implementable form of action-gating.
"""
import numpy as np, sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from brainsim import BrainSim
TICKS = 30
def run(seed, ncls, trials=3000, dens=0.30, **over):
    rng = np.random.default_rng(seed)
    pats = [(rng.random(40) < dens).astype(float) for _ in range(ncls)]
    b = BrainSim(n_motor=ncls, seed=seed); b.ACTION_GATED = False
    for k, v in over.items(): setattr(b, k, v)
    h = []
    for i in range(trials):
        c = i % ncls
        for _ in range(TICKS): b.step(pats[c])
        a = b.decide(); r = 1.0 if a == c else 0.0
        b.reward(r, action=a); h.append(r)
    return np.array(h)[-300:].mean()
CFG = [
    ("local baseline",            {}),
    ("taggate THETA=0.99",        dict(TAGGATE=True, THETA=0.99)),
    ("taggate THETA=1.0 (WTA)",   dict(TAGGATE=True, THETA=1.0)),
    ("persist + THETA=1.0",       dict(TAGGATE=True, THETA=1.0, PERSIST=True)),
    ("persist only",              dict(PERSIST=True)),
    ("ACTION_GATED (non-local)",  dict(ACTION_GATED=True)),
]
for ncls in (4, 8, 2):
    print(f"\n  === {ncls} classes (chance {1/ncls:.3f}) ===")
    for lab, over in CFG:
        a = [run(s, ncls, **over) for s in (0, 1, 2)]
        print(f"    {lab:<26} {np.mean(a):.3f}   seeds: {' '.join(f'{x:.2f}' for x in a)}")
