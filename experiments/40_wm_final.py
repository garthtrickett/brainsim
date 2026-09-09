import numpy as np, sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import tasks
from brainsim import BrainSim
SEEDS=4
print("step 5 final: WM on vs off, all tasks\n", flush=True)
print(f"  {'task':<20} {'WM on':>8} {'WM off':>8}  {'delta':>8}", flush=True)
for nm,mk,n in [("nway-4",lambda: tasks.NWay(4,seed=0),4),
                ("nway-8",lambda: tasks.NWay(8,seed=0),8),
                ("xor-2",lambda: tasks.Conjunctive(seed=0),2),
                ("volatile-4",lambda: tasks.Volatile(4,300,seed=0),4)]:
    on=[];off=[]
    for s in range(SEEDS):
        a=BrainSim(n_motor=n,seed=s); a.WM=True; on.append(tasks.run(a,mk(),4000,seed=s)[-1000:].mean())
        b=BrainSim(n_motor=n,seed=s); off.append(tasks.run(b,mk(),4000,seed=s)[-1000:].mean())
    print(f"  {nm:<20} {np.mean(on):8.3f} {np.mean(off):8.3f} {np.mean(on)-np.mean(off):+8.3f}", flush=True)
for d in (30,60):
    on=[];off=[]
    for s in range(SEEDS):
        a=BrainSim(n_motor=2,seed=s); a.WM=True
        on.append(tasks.run_within(a,tasks.TMazeWithin(2,10,d,seed=0),6000,seed=s)[-1500:].mean())
        b=BrainSim(n_motor=2,seed=s)
        off.append(tasks.run_within(b,tasks.TMazeWithin(2,10,d,seed=0),6000,seed=s)[-1500:].mean())
    print(f"  {'tmaze-within d'+str(d):<20} {np.mean(on):8.3f} {np.mean(off):8.3f} {np.mean(on)-np.mean(off):+8.3f}", flush=True)
on=[];off=[]
for s in range(SEEDS):
    a=BrainSim(n_motor=2,seed=s); a.WM=True; on.append(float(tasks.run(a,tasks.Lock(10,seed=0),12000,seed=s).sum()))
    b=BrainSim(n_motor=2,seed=s); off.append(float(tasks.run(b,tasks.Lock(10,seed=0),12000,seed=s).sum()))
print(f"  {'lock-10 (rewards)':<20} {np.mean(on):8.1f} {np.mean(off):8.1f} {np.mean(on)-np.mean(off):+8.1f}", flush=True)
