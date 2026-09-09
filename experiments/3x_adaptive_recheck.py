import numpy as np, sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import tasks
from brainsim import BrainSim
# V(s) costs 0.125 on volatile because a state-dependent value must RELEARN every
# state when contingencies permute, while a global scalar adapts in one update.
# ADAPTIVE (volatility-driven LR/noise) targets exactly that, and was shelved in
# step 1 for "cancelling V(s)" -- measured under the buggy decide(). Retest.
DEC=4000
def go(mk, seed, dec=DEC, **o):
    t=mk(); a=BrainSim(n_motor=t.n_actions,seed=seed)
    for k,v in o.items(): setattr(a,k,v)
    return tasks.run(a,t,dec,seed=seed)[-dec//4:].mean()
TASKS=[("volatile-4",lambda: tasks.Volatile(4,300,seed=0)),
       ("nway-4",lambda: tasks.NWay(4,seed=0)),
       ("nway-8",lambda: tasks.NWay(8,seed=0)),
       ("xor-2",lambda: tasks.Conjunctive(seed=0))]
CFG=[("shipped: V(s)",        {}),
     ("V(s) + ADAPTIVE",      dict(ADAPTIVE=True)),
     ("ADAPTIVE only",        dict(ADAPTIVE=True, VALUE_STATE=False)),
     ("neither",              dict(VALUE_STATE=False))]
print("post-fix retest, 6 seeds\n")
print(f"  {'config':<20}" + "".join(f"{n:>13}" for n,_ in TASKS))
for lab,o in CFG:
    row=f"  {lab:<20}"
    for nm,mk in TASKS:
        row += f"{np.mean([go(mk,s,**o) for s in range(6)]):13.3f}"
    print(row)
print("\nlock-10, 5 seeds (V(s) is essential there: 330.8 vs 65.6):")
for lab,o in (("shipped: V(s)",{}),("V(s) + ADAPTIVE",dict(ADAPTIVE=True))):
    r=[]
    for s in range(5):
        t=tasks.Lock(10,seed=0); a=BrainSim(n_motor=2,seed=s)
        for k,v in o.items(): setattr(a,k,v)
        r.append(float(tasks.run(a,t,12000,seed=s).sum()))
    print(f"  {lab:<18} {[int(x) for x in r]}  mean={np.mean(r):.1f}")
