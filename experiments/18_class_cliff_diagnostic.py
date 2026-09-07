import numpy as np, sys; sys.path.insert(0,'/home/gust/code/brainsim')
from brainsim import BrainSim
# Why 1.00 at 2 classes and 0.32 at 4? Stop guessing; instrument it.
# Candidates: (a) all motor cells fire, so eligibility cannot identify the chosen
# action; (b) hidden codes for the classes are not separable; (c) the vote margin
# is swamped by noise; (d) W_out never differentiates by class.
TICKS=30
def diag(seed, ncls, trials=3000, dens=0.30):
    rng=np.random.default_rng(seed)
    pats=[(rng.random(40)<dens).astype(float) for _ in range(ncls)]
    b=BrainSim(n_motor=ncls, seed=seed)
    fired_per_tick=[]; margins=[]; h=[]; codes={c:[] for c in range(ncls)}
    for i in range(trials):
        c=i%ncls
        for _ in range(TICKS):
            fm=b.step(pats[c]); fired_per_tick.append(fm.sum())
        v=b.votes.copy()
        sv=np.sort(v)[::-1]; margins.append(sv[0]-sv[1])
        if i>trials-200: codes[c].append(b.trh.copy())
        a=b.decide(); r=1.0 if a==c else 0.0
        b.reward(r,action=a); h.append(r)
    # hidden-code separability between classes
    mus=[np.mean(codes[c],0) for c in range(ncls) if codes[c]]
    cos=[]
    for x in range(len(mus)):
        for y in range(x+1,len(mus)):
            d=np.linalg.norm(mus[x])*np.linalg.norm(mus[y])
            if d>0: cos.append(float(mus[x]@mus[y]/d))
    # does W_out differentiate? spread of each hidden cell's outgoing weights
    W=b.W_out
    per_cell_spread=float(np.mean(W.max(0)-W.min(0)))
    return (np.array(h)[-300:].mean(), np.mean(fired_per_tick), ncls,
            np.mean(margins), float(np.mean(cos)) if cos else float('nan'), per_cell_spread)
print("instrumenting the 2 -> 4 class cliff\n")
for ncls in (2,4,8):
    out=[diag(s,ncls) for s in (0,1)]
    acc=np.mean([o[0] for o in out]); fpt=np.mean([o[1] for o in out])
    mar=np.mean([o[3] for o in out]); cos=np.mean([o[4] for o in out]); spr=np.mean([o[5] for o in out])
    print(f"  {ncls} classes: acc={acc:.3f}  motor_cells_firing_per_tick={fpt:.2f}/{ncls}"
          f"  vote_margin={mar:.1f}  hidden_code_overlap={cos:.3f}  W_out_spread={spr:.3f}")
