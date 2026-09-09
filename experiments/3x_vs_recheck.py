import numpy as np, sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import tasks
from brainsim import BrainSim
# V(s) shipped in step 1 on volatile-4 0.276 -> 0.472. That was measured with the
# buggy decide(). Post-fix, 8 seeds: 0.301 with V(s) vs 0.404 without. Re-run the
# whole question in the current regime before keeping or dropping it.
DEC=4000
def go(mk, seed, dec=DEC, **o):
    t=mk(); a=BrainSim(n_motor=t.n_actions,seed=seed)
    for k,v in o.items(): setattr(a,k,v)
    return tasks.run(a,t,dec,seed=seed)[-dec//4:].mean()
TASKS=[("nway-4",lambda: tasks.NWay(4,seed=0)),
       ("nway-8",lambda: tasks.NWay(8,seed=0)),
       ("xor-2",lambda: tasks.Conjunctive(seed=0)),
       ("volatile-4",lambda: tasks.Volatile(4,300,seed=0))]
print("V(s) on vs off, post decide()-fix, 6 seeds\n")
print(f"  {'task':<12} {'V(s) on':>9} {'V(s) off':>10}   verdict")
for nm,mk in TASKS:
    on=[go(mk,s) for s in range(6)]; off=[go(mk,s,VALUE_STATE=False) for s in range(6)]
    d=np.mean(on)-np.mean(off)
    v = "helps" if d>0.03 else ("HURTS" if d<-0.03 else "neutral")
    print(f"  {nm:<12} {np.mean(on):9.3f} {np.mean(off):10.3f}   {v} ({d:+.3f})")
print("\nlock-10 (5 seeds, total rewards):")
for lab,o in (("V(s) on",{}),("V(s) off",dict(VALUE_STATE=False))):
    r=[]
    for s in range(5):
        t=tasks.Lock(10,seed=0); a=BrainSim(n_motor=2,seed=s)
        for k,v in o.items(): setattr(a,k,v)
        r.append(float(tasks.run(a,t,12000,seed=s).sum()))
    print(f"  {lab:<10} {[int(x) for x in r]}  mean={np.mean(r):.1f}")
