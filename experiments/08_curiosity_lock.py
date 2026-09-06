import numpy as np
# B2b failed the same sanity check as B2: control saw 30/30 states by tick 5000.
# A 30-state corridor is still solved by diffusion (~833 actions in 5k ticks,
# random-walk range ~sqrt(833)~29). No bottleneck => no possible positive result.
#
# Combination lock: at each state ONE of the two actions advances, the other
# resets to 0. Random policy reaches the end with prob 2^-(L-1). This CANNOT be
# solved by diffusion, so the control has somewhere to fail.
NIN, NH, K, L = 40, 80, 6, 14
def run(seed=0, T=150000, CURIOSITY=0.0, label=""):
    rng = np.random.default_rng(seed)
    C=[(rng.random(NIN)<0.30).astype(float) for _ in range(L)]
    GOOD = rng.integers(0,2,L)                      # the correct action per state
    Wih=(rng.random((NH,NIN))<0.25)*rng.random((NH,NIN))*1.2
    Whm=np.full((2,NH),0.25); Wp=np.zeros((NIN,NH))
    vh=np.zeros(NH); trh=np.zeros(NH); vm=np.zeros(2)
    e=np.zeros((2,NH)); ebar=np.zeros((2,NH)); pred=np.zeros(NIN)
    LR,LRp,WMAX=0.02,0.02,1.0; value=0.0
    s=0; count=np.zeros(2); first=None; nr=0; deep=0; d10=d50=0
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
            count[:]=0
            s = s+1 if a==GOOD[s] else 0
            deep=max(deep,s)
            if s==L-1: r=1.0; nr+=1; first=first or t; s=0
        tot=r+CURIOSITY*surprise
        value+=0.005*(tot-value); NM=tot-value
        ebar+=0.02*(e-ebar); Whm+=LR*NM*(e-ebar); np.clip(Whm,0,WMAX,out=Whm)
        pred=np.clip(Wp@trh,0,1)
        if t==10000: d10=deep
        if t==50000: d50=deep
    print(f"{label:<28} maxdepth@10k={d10:2d}/13 @50k={d50:2d}/13 final={deep:2d}/13  "
          f"first_reward={str(first) if first else 'NEVER':>7}  total={nr}")
print(f"combination lock, {L} states: random policy reaches the end with p=2^-13\n")
for cur in (0.0, 0.1, 0.3, 1.0):
    for s in (0,1,2):
        run(seed=s, CURIOSITY=cur, label=f"  curiosity={cur} (seed {s})")
    print()
