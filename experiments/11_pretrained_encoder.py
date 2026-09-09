import numpy as np, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *
# CLAIM #5: pretraining the sensory encoder decorrelates representations and
# buys sample efficiency. SANITY GATE: pretraining must actually lower the
# hidden-pattern overlap, else it did nothing and accuracy is uninterpretable.
def pretrain(Wih, PATS_ALL, rng, steps=6000, eta=0.02):
    W=Wih.copy()
    for _ in range(steps):                       # competitive learning: local, no labels
        x=PATS_ALL[rng.integers(len(PATS_ALL))]
        si=(rng.random(NIN)<0.6*x).astype(float)
        v=W@si; thr=np.partition(v,-K)[-K]; win=v>=thr
        W[win]+=eta*(si-W[win])
    return np.clip(W,0,None)

def overlap(Wih, PATS, rng):
    reps=[]
    for c in (0,1):
        acc=[]
        for _ in range(40):
            _,_,trh = trial(Wih, np.zeros((NM_,NH)), PATS[c], rng)
            acc.append(trh)
        reps.append(np.mean(acc,0))
    a,b=reps
    return float(a@b/(np.linalg.norm(a)*np.linalg.norm(b)+1e-9))

def learn_curve(Wih, PATS, seed, TRIALS=900):
    rng=np.random.default_rng(seed); Whm=np.full((NM_,NH),0.25)
    ebar=np.zeros((NM_,NH)); baseline=0.5; hist=[]
    for i in range(TRIALS):
        c=i%2
        act,e,_=trial(Wih,Whm,PATS[c],rng)
        r=1.0 if act==c else 0.0
        rpe=r-baseline; baseline+=0.02*(r-baseline)
        Whm,ebar=apply_update(Whm,ebar,e,rpe); hist.append(r)
    h=np.array(hist)
    return h[100:200].mean(), h[300:400].mean(), h[800:900].mean()

print("CLAIM 5: pretrained sensory encoder vs random. chance=0.50\n")
for seed in (0,1,2):
    rng=np.random.default_rng(seed)
    PATS=[(rng.random(NIN)<0.35).astype(float) for _ in range(2)]
    EXTRA=[(rng.random(NIN)<0.35).astype(float) for _ in range(6)]
    Wr=(rng.random((NH,NIN))<0.25)*rng.random((NH,NIN))*1.2
    Wp=pretrain(Wr, PATS+EXTRA, rng)
    orand=overlap(Wr,PATS,np.random.default_rng(7)); opre=overlap(Wp,PATS,np.random.default_rng(7))
    a=learn_curve(Wr,PATS,seed); b=learn_curve(Wp,PATS,seed)
    gate="OK" if opre < orand else "FAILED (overlap not reduced)"
    print(f"seed {seed}: overlap random={orand:.3f} pretrained={opre:.3f}  [{gate}]")
    print(f"         acc@200/400/900  random={a[0]:.2f}/{a[1]:.2f}/{a[2]:.2f}   "
          f"pretrained={b[0]:.2f}/{b[1]:.2f}/{b[2]:.2f}")
