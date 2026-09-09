import numpy as np, sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import tasks
from brainsim import BrainSim
# volatile-4 read 0.472 before the decide() fix and 0.269 after, on 3 seeds.
# The two decide() versions consume the RNG differently, so seed-matched runs
# diverge entirely -- this is effectively a different seed set, not a controlled
# comparison. 8 seeds, and the full suite re-measured.
DEC=4000
def go(mk, seed, dec=DEC, **o):
    t=mk(); a=BrainSim(n_motor=t.n_actions,seed=seed)
    for k,v in o.items(): setattr(a,k,v)
    return tasks.run(a,t,dec,seed=seed)[-dec//4:].mean()
print("volatile-4, 8 seeds (was 0.472 pre-fix on 3 seeds):")
r=[go(lambda: tasks.Volatile(4,300,seed=0),s) for s in range(8)]
print(f"  {[round(x,3) for x in r]}  mean={np.mean(r):.3f}  median={np.median(r):.3f}")
off=[go(lambda: tasks.Volatile(4,300,seed=0),s,VALUE_STATE=False) for s in range(8)]
print(f"  V(s) off: mean={np.mean(off):.3f}   (V(s) still earning its place: {np.mean(r)>np.mean(off)})")
print("\nfull suite after the fix, 5 seeds:")
for nm,mk,fl in [("nway-4",lambda: tasks.NWay(4,seed=0),0.253),
                 ("nway-8",lambda: tasks.NWay(8,seed=0),0.122),
                 ("xor-2",lambda: tasks.Conjunctive(seed=0),0.501),
                 ("volatile-4",lambda: tasks.Volatile(4,300,seed=0),0.250),
                 ("tmaze-2d3",lambda: tasks.TMaze(2,3,seed=0),0.123)]:
    v=[go(mk,s) for s in range(5)]
    print(f"  {nm:<12} floor={fl:.3f}  now={np.mean(v):.3f}")
print("\nlock-10 (hippocampus target), 5 seeds:")
lk=[float(tasks.run(BrainSim(n_motor=2,seed=s), tasks.Lock(10,seed=0), 12000, seed=s).sum()) for s in range(5)]
print(f"  rewards={[int(x) for x in lk]}  mean={np.mean(lk):.1f}  (was 333.5)")
