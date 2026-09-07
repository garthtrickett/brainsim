import numpy as np, sys; sys.path.insert(0,'/home/gust/code/brainsim')
import tasks
from brainsim import BrainSim
# The probes say the nway-8 gap is ALIGNMENT (tagged==chosen only 67.3%), not
# selection. The gate reads trm (decay 0.97 -> weighted to recent ticks); the
# decision reads cumulative votes. Different accumulators, hence disagreement.
# TRM_D -> 1.0 makes trm == votes, so the gate and the decision become the SAME
# quantity. An earlier sweep found 1.0 worse, but that predates V(s) and replay.
DEC=4000
def measure(ncls, seed, **over):
    t=tasks.NWay(ncls,seed=0); a=BrainSim(n_motor=ncls,seed=seed)
    for k,v in over.items(): setattr(a,k,v)
    rng=np.random.default_rng(seed); obs=t.reset(rng); acc=[]; agree=[]
    for i in range(DEC):
        for _ in range(30): a.step(obs)
        tagged=int(np.argmax(a.trm)); act=a.decide()
        obs,r,done=t.step(act); a.reward(r,action=act,done=done)
        acc.append(r)
        if i>DEC//2: agree.append(1.0 if tagged==act else 0.0)
        if done: obs=t.reset(rng)
    return np.mean(acc[-DEC//4:]), np.mean(agree)
print("nway-8: does aligning the gate's accumulator with the decision's close the gap?\n")
print(f"  {'TRM_D':<10} {'accuracy':>9} {'tagged==chosen':>16}")
for d in (0.90, 0.97, 0.99, 1.0):
    r=[measure(8,s,TRM_D=d) for s in (0,1,2)]
    print(f"  {d:<10} {np.mean([x[0] for x in r]):9.3f} {np.mean([x[1] for x in r]):15.1%}")
print("\n  reference: ACTION_GATED (non-local, 100% aligned by construction)")
r=[measure(8,s,TAGGATE=False,ACTION_GATED=True) for s in (0,1,2)]
print(f"  {'--':<10} {np.mean([x[0] for x in r]):9.3f}")
print("\nnway-4 control (already aligned at 89.6%, so expect little movement):")
for d in (0.97, 1.0):
    r=[measure(4,s,TRM_D=d) for s in (0,1,2)]
    print(f"  {d:<10} {np.mean([x[0] for x in r]):9.3f} {np.mean([x[1] for x in r]):15.1%}")
