import numpy as np, sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import tasks
from brainsim import BrainSim
# Round 2 hinted the sleep gradient HURTS on sparse reward (2.67 vs 5.33) but
# n=3 with a 13-vs-1 spread is not evidence -- the same shape that made
# prioritised replay look like +0.20 before 12 seeds cut it to +0.03.
# 6 seeds at the horizon where every seed finds reward (12000 decisions).
DEC=12000
CFG=[("gradient ON (shipped)", {}),
     ("gradient OFF (replay only)", dict(SLEEP_ETA=0.0)),
     ("no sleep at all", dict(SLEEP_ETA=0.0, SLEEP_EVERY=10**9))]
print(f"lock-10, {DEC} decisions, 6 seeds. total rewards found.\n")
out={}
for lab,over in CFG:
    res=[]
    for seed in range(6):
        t=tasks.Lock(10,seed=0); a=BrainSim(n_motor=2,seed=seed)
        for k,v in over.items(): setattr(a,k,v)
        res.append(float(tasks.run(a,t,DEC,seed=seed).sum()))
    out[lab]=res
    print(f"  {lab:<28} {[int(x) for x in res]}  mean={np.mean(res):5.2f}  median={np.median(res):5.1f}")
on=out["gradient ON (shipped)"]; off=out["gradient OFF (replay only)"]
better=sum(1 for a,b in zip(off,on) if b>a)   # b is ON, a is OFF
print(f"\n  gradient-ON beats gradient-off in {better}/6 seeds")
print(f"  medians: on={np.median(on):.1f} off={np.median(off):.1f}")
