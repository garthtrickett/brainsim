import numpy as np, sys; sys.path.insert(0,'/home/gust/code/brainsim')
import tasks
from brainsim import BrainSim
# The first ablation tested TD only WITH compression, so compression's effect
# under TD is untested -- and compression was the design's headline claim.
# Complete the factorial: direction x compression, with TD on throughout.
DEC=12000
def run(seed, **over):
    t=tasks.Lock(10,seed=0); a=BrainSim(n_motor=2,seed=seed)
    for k,v in over.items(): setattr(a,k,v)
    return float(tasks.run(a,t,DEC,seed=seed).sum())
CFG=[("rev, compressed,   TD", dict(HIPPO=True,HIPPO_REVERSE=True, HIPPO_TICKS=3, HIPPO_BOOTSTRAP=True)),
     ("rev, uncompressed, TD", dict(HIPPO=True,HIPPO_REVERSE=True, HIPPO_TICKS=30,HIPPO_BOOTSTRAP=True)),
     ("fwd, compressed,   TD", dict(HIPPO=True,HIPPO_REVERSE=False,HIPPO_TICKS=3, HIPPO_BOOTSTRAP=True)),
     ("fwd, uncompressed, TD", dict(HIPPO=True,HIPPO_REVERSE=False,HIPPO_TICKS=30,HIPPO_BOOTSTRAP=True)),
     ("rev, no trace at all, TD", dict(HIPPO=True,HIPPO_REVERSE=True,HIPPO_TICKS=10**4,HIPPO_BOOTSTRAP=True))]
print(f"lock-10, {DEC} decisions, 6 seeds. completing the factorial under TD.\n")
for lab,over in CFG:
    r=[run(s,**over) for s in range(6)]
    print(f"  {lab:<26} {[int(x) for x in r]}  mean={np.mean(r):7.2f}  median={np.median(r):6.1f}")
print("\n  'no trace at all' sets decay^ticks ~ 0: pure per-step TD, no eligibility.")
print("  If that matches the best arm, the eligibility trace is doing nothing and")
print("  the mechanism is plain TD bootstrapping in reverse -- not trace-spanning.")
