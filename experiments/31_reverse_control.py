import numpy as np, sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import tasks
from brainsim import BrainSim
# Trace and compression are both harmful. The winner is per-step TD over replayed
# episodes. Last control: does REVERSE order still matter once the trace is gone?
# If forward matches reverse, direction is irrelevant too and this is simply
# TD + prioritised experience replay -- a standard algorithm, not a hippocampus.
DEC=12000; NOTRACE=10**4
def run(seed, **over):
    t=tasks.Lock(10,seed=0); a=BrainSim(n_motor=2,seed=seed)
    for k,v in over.items(): setattr(a,k,v)
    return float(tasks.run(a,t,DEC,seed=seed).sum())
CFG=[("rev, no trace, TD", dict(HIPPO=True,HIPPO_REVERSE=True, HIPPO_TICKS=NOTRACE,HIPPO_BOOTSTRAP=True)),
     ("fwd, no trace, TD", dict(HIPPO=True,HIPPO_REVERSE=False,HIPPO_TICKS=NOTRACE,HIPPO_BOOTSTRAP=True)),
     ("rev, no trace, NO TD", dict(HIPPO=True,HIPPO_REVERSE=True,HIPPO_TICKS=NOTRACE,HIPPO_BOOTSTRAP=False)),
     ("rev, no trace, TD, more replay", dict(HIPPO=True,HIPPO_REVERSE=True,HIPPO_TICKS=NOTRACE,HIPPO_BOOTSTRAP=True,HIPPO_N=24))]
print(f"lock-10, {DEC} decisions, 6 seeds. baseline=9.50, ceiling~1333.\n")
res={}
for lab,over in CFG:
    r=[run(s,**over) for s in range(6)]; res[lab]=r
    print(f"  {lab:<32} {[int(x) for x in r]}  mean={np.mean(r):7.2f}  median={np.median(r):6.1f}")
rev=np.mean(res["rev, no trace, TD"]); fwd=np.mean(res["fwd, no trace, TD"])
print(f"\n  direction still matters? {'YES' if rev > fwd*1.2 else 'NO -- it is TD + replay, not reverse replay'}")
print(f"    reverse={rev:.1f}  forward={fwd:.1f}")
