import numpy as np, sys; sys.path.insert(0,'/home/gust/code/brainsim')
import tasks
from brainsim import BrainSim
# The store must fill during the 10-tick cue phase and then CLOSE, or the 40
# ticks of delay+choice swamp it. But first: what cos would a PERFECT cue-only
# store give? The cue codes overlap, so 0 is not the target -- without this
# reference "0.97 is bad" is unanchored.
t=tasks.TMazeWithin(2,10,30,seed=0); a=BrainSim(n_motor=2,seed=0)
rng=np.random.default_rng(0); byc={0:[],1:[]}
for _ in range(300):
    seq=t.observation_sequence(rng)
    a.trh[:]=0
    for o in seq[:10]: a.step(o)          # cue phase only
    byc[t.c].append(a.trh.copy())
    for o in seq[10:]: a.step(o)
    act=a.decide(); _,r,_=t.step(act); a.reward(r,action=act,done=True)
m0,m1=np.mean(byc[0],0),np.mean(byc[1],0)
ref=float(m0@m1/(np.linalg.norm(m0)*np.linalg.norm(m1)+1e-12))
print(f"REFERENCE: a perfect cue-only store gives cos={ref:.3f}", flush=True)
print(f"           anything near that is storing the cue; 1.0 is storing nothing.\n", flush=True)
DEC=6000; SEEDS=4
def measure(lr, cap, dec=DEC):
    coss=[]; 
    t=tasks.TMazeWithin(2,10,30,seed=0); a=BrainSim(n_motor=2,seed=0)
    a.WM=True; a.WM_GATE="capacity"; a.WM_LR=lr; a.WM_CAP=cap
    rng=np.random.default_rng(0); byc={0:[],1:[]}
    for _ in range(300):
        for o in t.observation_sequence(rng): a.step(o)
        byc[t.c].append(a.wm.copy())
        act=a.decide(); _,r,_=t.step(act); a.reward(r,action=act,done=True)
    m0,m1=np.mean(byc[0],0),np.mean(byc[1],0)
    c=float(m0@m1/(np.linalg.norm(m0)*np.linalg.norm(m1)+1e-12))
    accs=[]
    for s in range(SEEDS):
        t2=tasks.TMazeWithin(2,10,30,seed=0); ag=BrainSim(n_motor=2,seed=s)
        ag.WM=True; ag.WM_GATE="capacity"; ag.WM_LR=lr; ag.WM_CAP=cap
        accs.append(tasks.run_within(ag,t2,dec,seed=s)[-dec//4:].mean())
    return c, float(np.mean(accs))
print(f"  {'WM_LR':>6} {'WM_CAP':>7} {'cos':>7} {'acc':>7}   (floor 0.504, ceiling 1.000)", flush=True)
for lr,cap in [(0.15,6.0),(0.5,3.0),(1.0,2.0),(1.0,1.0),(2.0,1.0),(2.0,0.5)]:
    c,acc=measure(lr,cap)
    print(f"  {lr:6.2f} {cap:7.2f} {c:7.3f} {acc:7.3f}", flush=True)
