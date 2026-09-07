import numpy as np, sys; sys.path.insert(0,'/home/gust/code/brainsim')
import tasks
from brainsim import BrainSim
DEC=12000
def run(seed, **over):
    t=tasks.Lock(10,seed=0); a=BrainSim(n_motor=2,seed=seed)
    for k,v in over.items(): setattr(a,k,v)
    h=tasks.run(a,t,DEC,seed=seed)
    return float(h.sum()), len(a.episodes)
CFG=[("no replay (baseline)",   {}),
     ("hippo: fwd, uncompressed", dict(HIPPO=True, HIPPO_REVERSE=False, HIPPO_TICKS=30, HIPPO_BOOTSTRAP=False)),
     ("hippo: rev, uncompressed", dict(HIPPO=True, HIPPO_REVERSE=True,  HIPPO_TICKS=30, HIPPO_BOOTSTRAP=False)),
     ("hippo: fwd, compressed",   dict(HIPPO=True, HIPPO_REVERSE=False, HIPPO_TICKS=3,  HIPPO_BOOTSTRAP=False)),
     ("hippo: rev, compressed",   dict(HIPPO=True, HIPPO_REVERSE=True,  HIPPO_TICKS=3,  HIPPO_BOOTSTRAP=False)),
     ("hippo: rev, comp, TD",     dict(HIPPO=True, HIPPO_REVERSE=True,  HIPPO_TICKS=3,  HIPPO_BOOTSTRAP=True)),
     ("hippo: fwd, comp, TD",     dict(HIPPO=True, HIPPO_REVERSE=False, HIPPO_TICKS=3,  HIPPO_BOOTSTRAP=True))]
print(f"lock-10, {DEC} decisions, 6 seeds. floor~12 rewards, ceiling~1333.\n")
res={}
for lab,over in CFG:
    r=[run(s,**over) for s in range(6)]
    tot=[x[0] for x in r]; res[lab]=tot
    print(f"  {lab:<26} {[int(x) for x in tot]}  mean={np.mean(tot):6.2f}  median={np.median(tot):5.1f}")
b=res["no replay (baseline)"]
print("\n  vs baseline (per-seed wins):")
for lab in res:
    if lab==list(res)[0]: continue
    w=sum(1 for x,y in zip(res[lab],b) if x>y)
    print(f"    {lab:<26} {w}/6  mean {np.mean(res[lab]):6.2f} vs {np.mean(b):6.2f}")
