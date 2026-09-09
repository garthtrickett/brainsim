import numpy as np, sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import tasks
from brainsim import BrainSim
# Two runs of this were killed at session boundaries with EMPTY logs -- python
# buffers stdout, so a killed run loses everything even though most configs had
# finished. Print and flush per config so a kill costs only the current row.
DEC=4000; SEEDS=4
def go(mk, seed, dec=DEC, **o):
    t=mk(); a=BrainSim(n_motor=t.n_actions,seed=seed)
    for k,v in o.items(): setattr(a,k,v)
    return tasks.run(a,t,dec,seed=seed)[-dec//4:].mean()
TASKS=[("nway-4",lambda: tasks.NWay(4,seed=0)),
       ("nway-8",lambda: tasks.NWay(8,seed=0)),
       ("xor-2",lambda: tasks.Conjunctive(seed=0)),
       ("volatile-4",lambda: tasks.Volatile(4,300,seed=0))]
CFG=[("shipped",               {}),
     ("- downscale",           dict(DOWNSCALE=1.0)),
     ("- local replay",        dict(SLEEP_REPLAY=0)),
     ("- downscale - replay",  dict(DOWNSCALE=1.0, SLEEP_REPLAY=0)),
     ("- gradient",            dict(SLEEP_ETA=0.0)),
     ("- everything",          dict(SLEEP_ETA=0.0, SLEEP_EVERY=10**9))]
print(f"decomposing sleep(), {SEEDS} seeds, incremental output", flush=True)
print(f"  {'config':<24}" + "".join(f"{n:>12}" for n,_ in TASKS), flush=True)
for lab,o in CFG:
    row=f"  {lab:<24}"
    for nm,mk in TASKS:
        row += f"{np.mean([go(mk,s,**o) for s in range(SEEDS)]):12.3f}"
    print(row, flush=True)
print("\nlock-10, 4 seeds:", flush=True)
for lab,o in (("shipped",{}),("- downscale",dict(DOWNSCALE=1.0)),
              ("- gradient",dict(SLEEP_ETA=0.0))):
    r=[]
    for s in range(4):
        t=tasks.Lock(10,seed=0); a=BrainSim(n_motor=2,seed=s)
        for k,v in o.items(): setattr(a,k,v)
        r.append(float(tasks.run(a,t,12000,seed=s).sum()))
    print(f"  {lab:<16} {[int(x) for x in r]}  mean={np.mean(r):.1f}", flush=True)
