import numpy as np, sys; sys.path.insert(0,'/home/gust/code/brainsim')
import tasks
from brainsim import BrainSim
def run(seed, mk, decisions=4000, **over):
    t = mk(); a = BrainSim(n_motor=t.n_actions, seed=seed)
    for k,v in over.items(): setattr(a,k,v)
    h = tasks.run(a, t, decisions, seed=seed)
    return h[-decisions//4:].mean()
CFG=[("baseline (shipped)",   {}),
     ("+ V(s) state value",   dict(VALUE_STATE=True)),
     ("+ adaptive LR/noise",  dict(ADAPTIVE=True)),
     ("+ both",               dict(VALUE_STATE=True, ADAPTIVE=True))]
for name, mk, floor, ceil in [("volatile-4", lambda: tasks.Volatile(4,300,seed=0), 0.250, 1.000),
                              ("nway-4  (regression)", lambda: tasks.NWay(4,seed=0), 0.253, 1.000),
                              ("lock-10 (sparse)", lambda: tasks.Lock(10,seed=0), 0.001, 0.111)]:
    print(f"\n  === {name}   floor={floor:.3f} ceiling={ceil:.3f} ===")
    for lab, over in CFG:
        a=[run(s, mk, **over) for s in (0,1,2)]
        print(f"    {lab:<22} {np.mean(a):.4f}   seeds: {' '.join(f'{x:.3f}' for x in a)}")
