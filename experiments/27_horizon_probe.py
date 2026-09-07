import numpy as np, sys; sys.path.insert(0,'/home/gust/code/brainsim')
import tasks
from brainsim import BrainSim
# A. At what horizon does every seed find reward at least once? The ablation
#    conditions on rewards_found>=1, so this sets the run length. If most seeds
#    never find it, the task measures EXPLORATION and replay cannot be tested.
print("=== A. horizon needed for seeds to find reward at all ===")
DEC=12000
for seed in range(5):
    t=tasks.Lock(10,seed=0); a=BrainSim(n_motor=2,seed=seed)
    rng=np.random.default_rng(seed); obs=t.reset(rng)
    first=None; n=0; at4k=0
    for i in range(DEC):
        for _ in range(30): a.step(obs)
        act=a.decide(); obs,r,done=t.step(act); a.reward(r,action=act)
        if r>0:
            n+=1
            if first is None: first=i
        if i==3999: at4k=n
        if done: obs=t.reset(rng)
    print(f"  seed {seed}: first_reward={first if first is not None else 'NEVER':>6}  "
          f"by_4k={at4k}  by_12k={n}")
# B. Three writers on W_out already. What does the EXISTING sleep gradient do on
#    lock-10, before a fourth mechanism is added?
print("\n=== B. does the existing sleep gradient help or hurt on lock-10? ===")
for lab,over in (("sleep gradient ON (shipped)",{}),
                 ("sleep gradient OFF",dict(SLEEP_ETA=0.0)),
                 ("no sleep at all",dict(SLEEP_ETA=0.0,SLEEP_EVERY=10**9))):
    res=[]
    for seed in range(3):
        t=tasks.Lock(10,seed=0); a=BrainSim(n_motor=2,seed=seed)
        for k,v in over.items(): setattr(a,k,v)
        h=tasks.run(a,t,6000,seed=seed); res.append(h.sum())
    print(f"  {lab:<28} total rewards over 6000 decisions: {res}  mean={np.mean(res):.2f}")
