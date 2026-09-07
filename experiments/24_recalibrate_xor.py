import numpy as np, sys; sys.path.insert(0,'/home/gust/code/brainsim')
import tasks
from brainsim import BrainSim
D=4000
print("recalibrating the fixed XOR task\n")
for mk in (lambda: tasks.Conjunctive(seed=0),):
    fl=np.mean([tasks.random_policy(mk(),D,seed=s).mean() for s in (1,2,3)])
    ce=np.mean([tasks.oracle(mk(),D,seed=s).mean() for s in (1,2,3)])
    ag=[]
    for s in (0,1,2):
        t=mk(); a=BrainSim(n_motor=t.n_actions,seed=s)
        ag.append(tasks.run(a,t,D,seed=s)[-D//4:].mean())
    ag=np.mean(ag); pos=(ag-fl)/max(ce-fl,1e-9)
    v=("FLOOR - representation binds (as intended)" if pos<0.10 else
       "CEILING" if pos>0.90 else f"USABLE ({pos:.0%} up) - does NOT bind on representation")
    print(f"  {mk().name:<12} floor={fl:.4f} agent={ag:.4f} ceiling={ce:.4f}   {v}")
