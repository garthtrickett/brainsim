import numpy as np
# CLAIM #2: clones of a common ancestor can be merged by averaging weights;
# independently-grown nets cannot (neuron 7 means different things in each).
# Controls: a lone agent on 1/Nth the data (what you get WITHOUT pooling) and
# a lone agent on all of it (the ceiling pooling is trying to reach).
NIN, NH, NM_, K, TICKS = 40, 60, 2, 6, 30
def train(Wih, Whm, trials, seed, PATS):
    rng = np.random.default_rng(seed)
    Whm = Whm.copy(); LEAK,TR_D,LR,WMAX = 0.85,0.80,0.05,1.0
    baseline=0.5; e=np.zeros((NM_,NH)); ebar=np.zeros((NM_,NH))
    vh=np.zeros(NH); vm=np.zeros(NM_); trh=np.zeros(NH); fh=np.zeros(NH)
    for _ in range(trials):
        c=int(rng.random()<0.5); x=PATS[c]; count=np.zeros(NM_)
        for t in range(TICKS):
            si=(rng.random(NIN)<0.6*x).astype(float)
            vm=vm*LEAK+Whm@fh+rng.normal(0,0.35,NM_)
            fm=(vm>1.0).astype(float); vm[fm>0]=0
            vh=vh*LEAK+Wih@si
            thr=np.partition(vh,-K)[-K]; fh=((vh>=thr)&(vh>1.0)).astype(float); vh[fh>0]=0
            trh=trh*TR_D+fh; e=e*0.90+np.outer(fm,trh); count+=fm
        act=int(np.argmax(count)) if count[0]!=count[1] else int(rng.random()<.5)
        r=1.0 if act==c else 0.0; rpe=r-baseline; baseline+=0.02*(r-baseline)
        ebar+=0.05*(e-ebar); Whm+=LR*rpe*(e-ebar); np.clip(Whm,0,WMAX,out=Whm)
    return Whm

def evaluate(Wih, Whm, PATS, seed=99, trials=400):
    rng=np.random.default_rng(seed); ok=0
    vh=np.zeros(NH); vm=np.zeros(NM_); trh=np.zeros(NH); fh=np.zeros(NH)
    for _ in range(trials):
        c=int(rng.random()<0.5); x=PATS[c]; count=np.zeros(NM_)
        for t in range(TICKS):
            si=(rng.random(NIN)<0.6*x).astype(float)
            vm=vm*LEAK_+Whm@fh+rng.normal(0,0.35,NM_)
            fm=(vm>1.0).astype(float); vm[fm>0]=0
            vh=vh*LEAK_+Wih@si
            thr=np.partition(vh,-K)[-K]; fh=((vh>=thr)&(vh>1.0)).astype(float); vh[fh>0]=0
            trh=trh*0.80+fh; count+=fm
        act=int(np.argmax(count)) if count[0]!=count[1] else int(rng.random()<.5)
        ok += (act==c)
    return ok/trials
LEAK_=0.85

N_AGENTS, PER_AGENT = 8, 400
for seed in (0,1,2):
    rng=np.random.default_rng(seed)
    PATS=[(rng.random(NIN)<0.35).astype(float) for _ in range(2)]
    Wih_shared=(rng.random((NH,NIN))<0.25)*rng.random((NH,NIN))*1.2
    Whm0=np.full((NM_,NH),0.25)

    solo   = evaluate(Wih_shared, train(Wih_shared,Whm0,PER_AGENT,100,PATS), PATS)
    ceil   = evaluate(Wih_shared, train(Wih_shared,Whm0,PER_AGENT*N_AGENTS,100,PATS), PATS)
    clones = [train(Wih_shared,Whm0,PER_AGENT,200+i,PATS) for i in range(N_AGENTS)]
    merged_clone = evaluate(Wih_shared, np.mean(clones,axis=0), PATS)
    indep_W = [(rng.random((NH,NIN))<0.25)*rng.random((NH,NIN))*1.2 for _ in range(N_AGENTS)]
    indep   = [train(indep_W[i],Whm0,PER_AGENT,300+i,PATS) for i in range(N_AGENTS)]
    merged_indep = evaluate(indep_W[0], np.mean(indep,axis=0), PATS)
    print(f"seed {seed}:  solo({PER_AGENT} trials)={solo:.2f}  "
          f"merged-CLONES={merged_clone:.2f}  merged-INDEPENDENT={merged_indep:.2f}  "
          f"ceiling({PER_AGENT*N_AGENTS} trials)={ceil:.2f}")
print("\nchance=0.50. Claim holds only if merged-CLONES > solo AND merged-INDEPENDENT ~ chance.")
