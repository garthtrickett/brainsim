import numpy as np, sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import tasks
from brainsim import BrainSim
DEC=4000
def run(ncls, seed, **over):
    t=tasks.NWay(ncls,seed=0); a=BrainSim(n_motor=ncls,seed=seed)
    for k,v in over.items(): setattr(a,k,v)
    h=tasks.run(a,t,DEC,seed=seed)
    return h[-DEC//4:].mean(), a
print("=== claim 1: does a SIGNED readout help now? (tested at 0.152 pre-TAGGATE) ===")
for ncls in (4,8):
    on=[run(ncls,s,WMIN=-1.0)[0] for s in (0,1,2)]
    off=[run(ncls,s)[0] for s in (0,1,2)]
    print(f"  nway-{ncls}: signed={np.mean(on):.3f}  non-negative={np.mean(off):.3f}")
print("\n=== claim 4: what is TAGGATE contributing at 8 actions now? ===")
for ncls in (4,8):
    on=[run(ncls,s)[0] for s in (0,1,2)]
    off=[run(ncls,s,TAGGATE=False)[0] for s in (0,1,2)]
    ag=[run(ncls,s,TAGGATE=False,ACTION_GATED=True)[0] for s in (0,1,2)]
    print(f"  nway-{ncls}: TAGGATE={np.mean(on):.3f}  none={np.mean(off):.3f}  ACTION_GATED={np.mean(ag):.3f}")
print("\n=== claims 2+3: vote margin, and does the TAGGED cell match the CHOSEN action? ===")
for ncls in (4,8):
    margins=[]; agree=[]
    for seed in (0,1,2):
        t=tasks.NWay(ncls,seed=0); a=BrainSim(n_motor=ncls,seed=seed)
        rng=np.random.default_rng(seed); obs=t.reset(rng)
        for i in range(DEC):
            for _ in range(30): a.step(obs)
            v=a.votes.copy(); sv=np.sort(v)[::-1]
            tagged=int(np.argmax(a.trm))
            act=a.decide()
            if i>DEC//2:
                margins.append(float(sv[0]-sv[1])); agree.append(1.0 if tagged==act else 0.0)
            obs,r,done=t.step(act); a.reward(r,action=act,done=done)
            if done: obs=t.reset(rng)
    print(f"  nway-{ncls}: vote_margin={np.mean(margins):5.2f}  tagged==chosen: {np.mean(agree):.1%}")
