import numpy as np, sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import tasks
from brainsim import BrainSim
# Verify the design's assumptions before building anything.
print("=== 1/2. reward encounters and episode lengths (current agent, lock-10) ===")
for seed in (0,1,2):
    t=tasks.Lock(10,seed=0); a=BrainSim(n_motor=2,seed=seed)
    rng=np.random.default_rng(seed); obs=t.reset(rng)
    n_rew=0; ep_len=0; lens=[]; depths=[]; maxd=0
    for i in range(4000):
        for _ in range(30): a.step(obs)
        act=a.decide(); obs,r,done=t.step(act); a.reward(r,action=act)
        ep_len+=1; maxd=max(maxd,t.s)
        if r>0: n_rew+=1
        if done or t.s==0:
            lens.append(ep_len); ep_len=0
            if done: obs=t.reset(rng)
    print(f"  seed {seed}: rewards={n_rew}  max_depth={maxd}/9  "
          f"runs={len(lens)}  mean_run_len={np.mean(lens):.2f}  p95_run={np.percentile(lens,95):.0f}")
print("\n=== 3. hidden-code overlap between adjacent lock states ===")
t=tasks.Lock(10,seed=0); a=BrainSim(n_motor=2,seed=0)
codes=[]
for s in range(10):
    a.trh[:]=0
    for _ in range(30): a.step(t.codes[s])
    codes.append(a.trh.copy())
ov=[]
for i in range(9):
    x,y=codes[i],codes[i+1]
    ov.append(float(x@y/(np.linalg.norm(x)*np.linalg.norm(y)+1e-9)))
allp=[float(codes[i]@codes[j]/(np.linalg.norm(codes[i])*np.linalg.norm(codes[j])+1e-9))
      for i in range(10) for j in range(i+1,10)]
print(f"  adjacent-state overlap: mean={np.mean(ov):.3f}  all-pairs mean={np.mean(allp):.3f} max={np.max(allp):.3f}")
print("\n=== 4. eligibility decay arithmetic ===")
d=0.995
for steps,tps in ((10,30),(10,3),(10,1)):
    print(f"  10 steps x {tps:2d} ticks = {steps*tps:3d} ticks -> trace at episode start = {d**(steps*tps):.3f}")
