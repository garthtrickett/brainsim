"""Why does the mainline's local rule reach 0.85 when 02_learning.py reaches 1.00?

I attributed the gap to the homeostatic machinery the mainline has and 02 does
not -- threshold adaptation, synaptic scaling, the sleep downscale, pruning --
but never tested that. This ablates each one.

Sleep GRADIENT is off throughout: the claim is about the LOCAL rule, and the
gradient masks the difference by reaching ceiling regardless.

GATE: with all four disabled, accuracy must approach 02's ~1.00. If it does not,
the gap is something else and the attribution is wrong.
"""
import numpy as np, sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from brainsim import BrainSim

TICKS = 30
def run(seed, trials=1200, **off):
    rng = np.random.default_rng(seed)
    pats = [(rng.random(40) < 0.35).astype(float) for _ in range(2)]
    b = BrainSim(seed=seed)
    b.SLEEP_ETA = 0.0                      # local rule only, no gradient
    for k, v in off.items(): setattr(b, k, v)
    h = []
    for i in range(trials):
        c = i % 2
        for _ in range(TICKS): b.step(pats[c])
        a = b.decide(); r = 1.0 if a == c else 0.0
        b.reward(r, action=a); h.append(r)
    return np.array(h)[-200:].mean()

CFG = [
    ("mainline as shipped",      {}),
    ("  - threshold homeostasis", dict(ETA_TH=0.0)),
    ("  - synaptic scaling",      dict(SCALE_EVERY=10**9)),
    ("  - sleep downscale",       dict(DOWNSCALE=1.0)),
    ("  - pruning",               dict(PRUNE_BELOW=0.0)),
    ("  - ALL FOUR (gate)",       dict(ETA_TH=0.0, SCALE_EVERY=10**9,
                                       DOWNSCALE=1.0, PRUNE_BELOW=0.0)),
]
SEEDS = range(5)
print("local rule only (sleep gradient off). chance=0.50, 02_learning.py=1.00\n")
res = {}
for name, off in CFG:
    a = [run(s, **off) for s in SEEDS]
    res[name] = np.mean(a)
    print(f"  {name:<28} {np.mean(a):.2f}   (seeds: {' '.join(f'{x:.2f}' for x in a)})")
base = res["mainline as shipped"]; allo = res["  - ALL FOUR (gate)"]
print(f"\n  gate: all four off reaches {allo:.2f}", end="  ")
print("-> attribution HOLDS" if allo > base + 0.08 else "-> attribution WRONG, gap is elsewhere")
