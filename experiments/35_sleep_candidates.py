import numpy as np, sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import tasks
from brainsim import BrainSim
# The decomposition says the LOCAL REPLAY loop in sleep() costs nway-8 (+0.129 to
# remove). But "- everything" also disables HIPPOCAMPAL replay, which is what
# broke the lock 35x -- and I never measured the lock under the winning configs.
# SLEEP_REPLAY=0 disables the local loop while KEEPING hippo replay, so it is the
# candidate that could give both. 6 seeds; 4 was too noisy (shipped nway-8 read
# 0.882 at 6 seeds and 0.827 at 4).
DEC=4000; SEEDS=6
def go(mk, seed, dec=DEC, **o):
    t=mk(); a=BrainSim(n_motor=t.n_actions,seed=seed)
    for k,v in o.items(): setattr(a,k,v)
    return tasks.run(a,t,dec,seed=seed)[-dec//4:].mean()
TASKS=[("nway-8",lambda: tasks.NWay(8,seed=0)),
       ("xor-2",lambda: tasks.Conjunctive(seed=0)),
       ("volatile-4",lambda: tasks.Volatile(4,300,seed=0))]
CFG=[("shipped",                 {}),
     ("- local replay",          dict(SLEEP_REPLAY=0)),
     ("- local replay - downscale", dict(SLEEP_REPLAY=0, DOWNSCALE=1.0)),
     ("- gradient only",         dict(SLEEP_ETA=0.0))]
print(f"candidates, {SEEDS} seeds, incremental", flush=True)
print(f"  {'config':<30}" + "".join(f"{n:>13}" for n,_ in TASKS), flush=True)
for lab,o in CFG:
    row=f"  {lab:<30}"
    for nm,mk in TASKS:
        row += f"{np.mean([go(mk,s,**o) for s in range(SEEDS)]):13.3f}"
    print(row, flush=True)
print("\nlock-10, 5 seeds -- does the candidate keep hippocampal replay working?", flush=True)
for lab,o in (("shipped",{}),("- local replay",dict(SLEEP_REPLAY=0)),
              ("- local replay - downscale",dict(SLEEP_REPLAY=0,DOWNSCALE=1.0)),
              ("- gradient only",dict(SLEEP_ETA=0.0)),
              ("- ALL sleep (kills hippo)",dict(SLEEP_ETA=0.0,SLEEP_EVERY=10**9))):
    r=[]
    for s in range(5):
        t=tasks.Lock(10,seed=0); a=BrainSim(n_motor=2,seed=s)
        for k,v in o.items(): setattr(a,k,v)
        r.append(float(tasks.run(a,t,12000,seed=s).sum()))
    print(f"  {lab:<28} {[int(x) for x in r]}  mean={np.mean(r):.1f}", flush=True)
