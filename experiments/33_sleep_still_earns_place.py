import numpy as np, sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import tasks
from brainsim import BrainSim
# Does the sleep gradient still earn its place? Validated in Part 3 at +0.06 over
# matched replay -- before V(s), before the hippocampus, before the decide() fix.
DEC=4000
def go(mk, seed, dec=DEC, **o):
    t=mk(); a=BrainSim(n_motor=t.n_actions,seed=seed)
    for k,v in o.items(): setattr(a,k,v)
    return tasks.run(a,t,dec,seed=seed)[-dec//4:].mean()
TASKS=[("nway-4",lambda: tasks.NWay(4,seed=0)),
       ("nway-8",lambda: tasks.NWay(8,seed=0)),
       ("xor-2",lambda: tasks.Conjunctive(seed=0)),
       ("volatile-4",lambda: tasks.Volatile(4,300,seed=0))]
CFG=[("shipped (gradient on)", {}),
     ("gradient OFF",          dict(SLEEP_ETA=0.0)),
     ("no sleep at all",       dict(SLEEP_ETA=0.0, SLEEP_EVERY=10**9)),
     ("gradient off + no hippo", dict(SLEEP_ETA=0.0, HIPPO=False))]
print("does the sleep gradient still contribute? 6 seeds\n")
print(f"  {'config':<26}" + "".join(f"{n:>13}" for n,_ in TASKS))
for lab,o in CFG:
    row=f"  {lab:<26}"
    for nm,mk in TASKS:
        row += f"{np.mean([go(mk,s,**o) for s in range(6)]):13.3f}"
    print(row)
print("\nlock-10, 5 seeds (total rewards; replay's flagship result):")
for lab,o in (("shipped",{}),("gradient OFF",dict(SLEEP_ETA=0.0))):
    r=[]
    for s in range(5):
        t=tasks.Lock(10,seed=0); a=BrainSim(n_motor=2,seed=s)
        for k,v in o.items(): setattr(a,k,v)
        r.append(float(tasks.run(a,t,12000,seed=s).sum()))
    print(f"  {lab:<16} {[int(x) for x in r]}  mean={np.mean(r):.1f}")
