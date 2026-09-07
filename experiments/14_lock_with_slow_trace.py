import numpy as np
# Does the D2 fix repair the ORIGINAL measured failure? Experiment 08 scored at
# chance on a 14-state combination lock (1.75 rewards observed vs 1.53 expected
# by luck). Diagnosis was the ~10-tick credit horizon. So: same task, same code,
# only the eligibility decay changes. tau~10 (original) vs tau~200 (the fix).
# Chance baseline is computed, not assumed: expected waiting time for 13
# consecutive correct actions at p=0.5 is 2^14-2 = 16382 actions.
NIN, NH, K, L = 40, 80, 6, 14
def run(seed=0, T=150000, DECAY=0.90, label=""):
    rng=np.random.default_rng(seed)
    C=[(rng.random(NIN)<0.30).astype(float) for _ in range(L)]
    GOOD=rng.integers(0,2,L)
    Wih=(rng.random((NH,NIN))<0.25)*rng.random((NH,NIN))*1.2
    Whm=np.full((2,NH),0.25)
    vh=np.zeros(NH); trh=np.zeros(NH); vm=np.zeros(2)
    e=np.zeros((2,NH)); ebar=np.zeros((2,NH))
    LR,WMAX=0.02,1.0; value=0.0
    s=0; count=np.zeros(2); first=None; nr=0; deep=0
    for t in range(T):
        si=(rng.random(NIN)<0.8*C[s]).astype(float)
        vh=vh*0.85+Wih@si
        thr=np.partition(vh,-K)[-K]; fh=((vh>=thr)&(vh>1.0)).astype(float); vh[fh>0]=0
        trh=trh*0.80+fh
        vm=vm*0.85+Whm@fh+rng.normal(0,0.40,2)
        fm=(vm>1.0).astype(float); vm[fm>0]=0; count+=fm
        e=e*DECAY+np.outer(fm,trh)
        r=0.0
        if t%6==5:
            a=int(np.argmax(count)) if count[0]!=count[1] else int(rng.random()<.5)
            count[:]=0
            s = s+1 if a==GOOD[s] else 0
            deep=max(deep,s)
            if s==L-1: r=1.0; nr+=1; first=first or t; s=0
        value+=0.005*(r-value); NM=r-value
        ebar+=0.02*(e-ebar); Whm+=LR*NM*(e-ebar); np.clip(Whm,0,WMAX,out=Whm)
    return nr, deep, first
ACTIONS=150000//6
CHANCE=ACTIONS/(2**14-2)
print(f"combination lock, {L} states. {ACTIONS} actions per run.")
print(f"EXPECTED BY CHANCE: {CHANCE:.2f} rewards. Above this = actually learning.\n")
for dec,lab in ((0.90,'tau~10  (original, failed)'), (0.995,'tau~200 (the D2 fix)')):
    tot=[]
    for s in (0,1,2):
        nr,deep,first=run(seed=s,DECAY=dec)
        tot.append(nr)
        print(f"  {lab:<26} seed {s}: rewards={nr:3d}  maxdepth={deep:2d}/13  "
              f"first={str(first) if first else 'NEVER'}")
    print(f"  {'':<26} mean={np.mean(tot):.2f} vs chance {CHANCE:.2f}\n")
