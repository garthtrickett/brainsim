import numpy as np, sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from brainsim import BrainSim
# The gate reads trm (decay 0.90 => ~10-tick memory) but the DECISION is
# argmax(votes) over all 30 ticks. Different windows, so the gate often tags a
# cell that does not end up winning -- the same temporal misalignment that broke
# motor k-WTA. Slow trm down so it approximates the cumulative count, and the
# tagged cell becomes the decided cell.
TICKS=30
def run(seed,ncls,trials=3000,dens=0.30,**over):
    rng=np.random.default_rng(seed)
    pats=[(rng.random(40)<dens).astype(float) for _ in range(ncls)]
    b=BrainSim(n_motor=ncls,seed=seed)
    for k,v in over.items(): setattr(b,k,v)
    h=[]
    for i in range(trials):
        c=i%ncls
        for _ in range(TICKS): b.step(pats[c])
        a=b.decide(); r=1.0 if a==c else 0.0
        b.reward(r,action=a); h.append(r)
    return np.array(h)[-300:].mean()
CFG=[("TRM_D=0.90 (shipped)", dict(TRM_D=0.90)),
     ("TRM_D=0.97",           dict(TRM_D=0.97)),
     ("TRM_D=0.99",           dict(TRM_D=0.99)),
     ("TRM_D=1.0 (cumulative)",dict(TRM_D=1.0)),
     ("TRM_D=1.0 + persist",  dict(TRM_D=1.0, PERSIST=True)),
     ("ACTION_GATED (ref)",   dict(ACTION_GATED=True, TAGGATE=False))]
for ncls in (8,4):
    print(f"\n  === {ncls} classes (chance {1/ncls:.3f}) ===")
    for lab,over in CFG:
        a=[run(s,ncls,**over) for s in (0,1,2)]
        print(f"    {lab:<24} {np.mean(a):.3f}   seeds: {' '.join(f'{x:.2f}' for x in a)}")
