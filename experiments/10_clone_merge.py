import numpy as np
# E2 passed its gate, but solo hit ~0.97 in 2 of 3 seeds: saturated,
# so pooling had nowhere to show a gain. Same test, 250 trials per agent.
# (Original note: E WAS INVALID: ceiling(3200 trials) scored BELOW solo(400) -- more training made
# it worse, so nothing was learning and the merge numbers were meaningless.
# Cause: I reimplemented the training loop instead of reusing the validated one.
# E used a continuously-decaying, un-normalised trace (~300x too large), which
# saturated Whm against the clip. This file uses the loop from 02_learning.py
# verbatim: per-trial eligibility, reset each trial, divided by TICKS.
NIN, NH, NM_, K, TICKS = 40, 60, 2, 6, 30
LEAK, TR_D, LR, WMAX = 0.85, 0.80, 0.05, 1.0

def train(Wih, Whm, trials, seed, PATS):
    rng = np.random.default_rng(seed); Whm = Whm.copy()
    baseline = 0.5; ebar = np.zeros((NM_, NH))
    for trial in range(trials):
        c = trial % 2; x = PATS[c]
        vh=np.zeros(NH); vm=np.zeros(NM_); trh=np.zeros(NH)
        fh=np.zeros(NH); e=np.zeros((NM_,NH)); count=np.zeros(NM_)
        for t in range(TICKS):
            si=(rng.random(NIN)<0.6*x).astype(float)
            vm=vm*LEAK+Whm@fh+rng.normal(0,0.35,NM_)
            fm=(vm>1.0).astype(float); vm[fm>0]=0
            vh=vh*LEAK+Wih@si
            thr=np.partition(vh,-K)[-K]
            fh=((vh>=thr)&(vh>1.0)).astype(float); vh[fh>0]=0
            trh=trh*TR_D+fh
            e+=np.outer(fm,trh); count+=fm
        act=int(np.argmax(count)) if count[0]!=count[1] else int(rng.random()<.5)
        r=1.0 if act==c else 0.0
        rpe=r-baseline; baseline+=0.02*(r-baseline)
        e/=TICKS; de=e-ebar; ebar+=0.05*(e-ebar)
        Whm+=LR*rpe*de; np.clip(Whm,0,WMAX,out=Whm)
    return Whm

def evaluate(Wih, Whm, PATS, seed=99, trials=400):
    rng=np.random.default_rng(seed); ok=0
    for trial in range(trials):
        c=trial%2; x=PATS[c]
        vh=np.zeros(NH); vm=np.zeros(NM_); trh=np.zeros(NH)
        fh=np.zeros(NH); count=np.zeros(NM_)
        for t in range(TICKS):
            si=(rng.random(NIN)<0.6*x).astype(float)
            vm=vm*LEAK+Whm@fh+rng.normal(0,0.35,NM_)
            fm=(vm>1.0).astype(float); vm[fm>0]=0
            vh=vh*LEAK+Wih@si
            thr=np.partition(vh,-K)[-K]
            fh=((vh>=thr)&(vh>1.0)).astype(float); vh[fh>0]=0
            trh=trh*TR_D+fh; count+=fm
        act=int(np.argmax(count)) if count[0]!=count[1] else int(rng.random()<.5)
        ok+=(act==c)
    return ok/trials

N_AGENTS, PER_AGENT = 8, 250
print(f"{N_AGENTS} agents x {PER_AGENT} trials each; chance=0.50")
print("SANITY GATE: ceiling must exceed solo, or the merge numbers mean nothing.\n")
rows=[]
for seed in (0,1,2):
    rng=np.random.default_rng(seed)
    PATS=[(rng.random(NIN)<0.35).astype(float) for _ in range(2)]
    Wsh=(rng.random((NH,NIN))<0.25)*rng.random((NH,NIN))*1.2
    Whm0=np.full((NM_,NH),0.25)
    solo=evaluate(Wsh, train(Wsh,Whm0,PER_AGENT,100,PATS), PATS)
    ceil=evaluate(Wsh, train(Wsh,Whm0,PER_AGENT*N_AGENTS,100,PATS), PATS)
    clones=[train(Wsh,Whm0,PER_AGENT,200+i,PATS) for i in range(N_AGENTS)]
    mc=evaluate(Wsh,np.mean(clones,axis=0),PATS)
    iW=[(rng.random((NH,NIN))<0.25)*rng.random((NH,NIN))*1.2 for _ in range(N_AGENTS)]
    ind=[train(iW[i],Whm0,PER_AGENT,300+i,PATS) for i in range(N_AGENTS)]
    mi=evaluate(iW[0],np.mean(ind,axis=0),PATS)
    gate = "OK" if ceil > solo else "FAILED -- ignore merge numbers"
    rows.append((solo,mc,mi,ceil,gate))
    print(f"seed {seed}:  solo={solo:.2f}  merged-CLONES={mc:.2f}  "
          f"merged-INDEP={mi:.2f}  ceiling={ceil:.2f}   gate: {gate}")
print()
if all(r[4]=="OK" for r in rows):
    s=np.mean([r[0] for r in rows]); c=np.mean([r[1] for r in rows]); i=np.mean([r[2] for r in rows])
    print(f"means: solo={s:.2f}  merged-CLONES={c:.2f}  merged-INDEP={i:.2f}")
    print(f"claim holds? clones>solo: {c>s}   independent~chance: {abs(i-0.5)<0.06}")
else:
    print("sanity gate failed on at least one seed; merge comparison is not interpretable.")
