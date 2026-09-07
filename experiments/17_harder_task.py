"""Do Part 3b's retirements survive a task with actual capacity pressure?

Everything so far is validated on ONE two-class discrimination that the mainline
now solves at 1.00 -- a ceiling that cannot separate good from great. Three
mechanisms were retired for being redundant under k-WTA (refractory period,
TARGET_RATE=0.01, threshold homeostasis). That conclusion is only trustworthy if
it holds where the representation is actually strained.

Harder task: 8 classes instead of 2, denser patterns (more overlap between
classes), same 80 hidden cells and same k=6. Chance = 0.125.

GATE: the mainline must beat chance clearly, or the task is too hard and the
ablations below are all noise.
"""
import numpy as np, sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from brainsim import BrainSim

TICKS, NCLASS, DENSITY = 30, 8, 0.45      # denser => classes overlap more
def run(seed, trials=4000, **over):
    rng = np.random.default_rng(seed)
    pats = [(rng.random(40) < DENSITY).astype(float) for _ in range(NCLASS)]
    b = BrainSim(n_motor=NCLASS, seed=seed)
    for k, v in over.items(): setattr(b, k, v)
    h = []
    for i in range(trials):
        c = i % NCLASS
        for _ in range(TICKS): b.step(pats[c])
        a = b.decide(); r = 1.0 if a == c else 0.0
        b.reward(r, action=a); h.append(r)
    hh = np.array(h)
    return hh[:400].mean(), hh[-400:].mean()

CFG = [
    ("mainline (ETA_TH=0)",        {}),
    ("  ETA_TH=0.02 back ON",      dict(ETA_TH=0.02)),
    ("  no sleep gradient",        dict(SLEEP_ETA=0.0)),
    ("  no synaptic scaling",      dict(SCALE_EVERY=10**9)),
    ("  weaker competition k=20",  dict(k=20)),
    ("  stronger competition k=3", dict(k=3)),
]
SEEDS = range(4)
print(f"{NCLASS} classes, density {DENSITY}, 80 hidden, k=6. chance = {1/NCLASS:.3f}\n")
res = {}
for name, over in CFG:
    out = [run(s, **over) for s in SEEDS]
    early = np.mean([o[0] for o in out]); late = np.mean([o[1] for o in out])
    res[name] = late
    print(f"  {name:<28} early={early:.3f}  late={late:.3f}   "
          f"(seeds: {' '.join(f'{o[1]:.2f}' for o in out)})")

base = res["mainline (ETA_TH=0)"]
print(f"\n  GATE: mainline {base:.3f} vs chance {1/NCLASS:.3f}", end="  ")
print("-> task is learnable, ablations interpretable"
      if base > 1/NCLASS + 0.15 else "-> TOO HARD, ablations are noise")
eta = res["  ETA_TH=0.02 back ON"]
print(f"  does the threshold-homeostasis retirement hold? {base >= eta - 0.02} "
      f"(off={base:.3f} vs on={eta:.3f})")
