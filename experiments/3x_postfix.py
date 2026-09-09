import numpy as np, sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import tasks
from brainsim import BrainSim
DEC=4000
def measure(ncls, seed, **over):
    t=tasks.NWay(ncls,seed=0); a=BrainSim(n_motor=ncls,seed=seed)
    for k,v in over.items(): setattr(a,k,v)
    rng=np.random.default_rng(seed); obs=t.reset(rng); acc=[]; agree=[]
    for i in range(DEC):
        for _ in range(30): a.step(obs)
        tagged=int(np.argmax(a.trm)); act=a.decide()
        obs,r,done=t.step(act); a.reward(r,action=act,done=done)
        acc.append(r)
        if i>DEC//2: agree.append(1.0 if tagged==act else 0.0)
        if done: obs=t.reset(rng)
    return np.mean(acc[-DEC//4:]), np.mean(agree)
print("after fixing decide(). previous numbers in brackets.\n")
prev={(4,'tag'):0.961,(8,'tag'):0.769,(4,'ag'):0.923,(8,'ag'):0.869}
for ncls in (4,8):
    tag=[measure(ncls,s) for s in (0,1,2)]
    ag=[measure(ncls,s,TAGGATE=False,ACTION_GATED=True) for s in (0,1,2)]
    print(f"  nway-{ncls}: TAGGATE={np.mean([x[0] for x in tag]):.3f} [{prev[(ncls,'tag')]}]"
          f"  agree={np.mean([x[1] for x in tag]):.1%}"
          f"   ACTION_GATED={np.mean([x[0] for x in ag]):.3f} [{prev[(ncls,'ag')]}]")
print("\nother tasks (regression):")
for nm,mk,dec in [("xor-2",lambda: tasks.Conjunctive(seed=0),4000),
                  ("volatile-4",lambda: tasks.Volatile(4,300,seed=0),4000)]:
    r=[]
    for s in (0,1,2):
        t=mk(); a=BrainSim(n_motor=t.n_actions,seed=s)
        r.append(tasks.run(a,t,dec,seed=s)[-dec//4:].mean())
    print(f"  {nm:<12} {np.mean(r):.3f}")
