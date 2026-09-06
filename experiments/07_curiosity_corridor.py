import numpy as np
# B2 was a broken test, twice over:
#  (1) 10-state corridor was solved by random walk (10/10 states seen even at
#      curiosity=0) -- there was no exploration bottleneck to relieve.
#  (2) magnitude mismatch: CURIOSITY=3 x surprise~0.2 = ~0.6 EVERY tick, vs an
#      external reward of 1.0 delivered ONCE. Curiosity outweighed reward ~100x.
# Fix both: longer corridor (real bottleneck) + sweep curiosity magnitude.
NIN, NH, K, NS = 40, 80, 6, 30
def run(seed=0, T=120000, CURIOSITY=0.0, label=""):
    rng = np.random.default_rng(seed)
    C = [(rng.random(NIN)<0.30).astype(float) for _ in range(NS)]
    Wih = (rng.random((NH,NIN))<0.25)*rng.random((NH,NIN))*1.2
    Whm = np.full((2,NH),0.25); Wp = np.zeros((NIN,NH))
    vh=np.zeros(NH); trh=np.zeros(NH); vm=np.zeros(2)
    e=np.zeros((2,NH)); ebar=np.zeros((2,NH)); pred=np.zeros(NIN)
    LR,LRp,WMAX=0.02,0.02,1.0; value=0.0
    s=0; count=np.zeros(2); vis=set([0]); first=None; nr=0; v5=v20=0
    for t in range(T):
        si=(rng.random(NIN)<0.8*C[s]).astype(float)
        err=si-pred; Wp+=LRp*np.outer(err,trh); surprise=np.abs(err).mean()
        vh=vh*0.85+Wih@si
        thr=np.partition(vh,-K)[-K]; fh=((vh>=thr)&(vh>1.0)).astype(float); vh[fh>0]=0
        trh=trh*0.80+fh
        vm=vm*0.85+Whm@fh+rng.normal(0,0.40,2)
        fm=(vm>1.0).astype(float); vm[fm>0]=0; count+=fm
        e=e*0.90+np.outer(fm,trh)
        r=0.0
        if t%6==5:
            a=int(np.argmax(count)) if count[0]!=count[1] else int(rng.random()<.5)
            s=max(0,min(NS-1,s+(1 if a else -1))); vis.add(s); count[:]=0
            if s==NS-1: r=1.0; nr+=1; first=first or t; s=0
        tot=r+CURIOSITY*surprise
        value+=0.005*(tot-value); NM=tot-value
        ebar+=0.02*(e-ebar); Whm+=LR*NM*(e-ebar); np.clip(Whm,0,WMAX,out=Whm)
        pred=np.clip(Wp@trh,0,1)
        if t==5000: v5=len(vis)
        if t==20000: v20=len(vis)
    print(f"{label:<28} seen@5k={v5:2d}/30 seen@20k={v20:2d}/30 "
          f"first_reward={str(first) if first else 'NEVER':>7}  total={nr}")
print(f"corridor of {NS} states, reward ONLY at the far end\n")
for cur in (0.0, 0.1, 0.3, 1.0, 3.0):
    for s in (0,1,2):
        run(seed=s, CURIOSITY=cur, label=f"  curiosity={cur} (seed {s})")
    print()
