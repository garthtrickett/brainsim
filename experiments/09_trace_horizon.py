import numpy as np
# D WAS INVALID. Decaying the trace analytically (e *= d**DELAY) multiplies the
# WHOLE trace by one constant -- so the update DIRECTION is untouched and only its
# magnitude shrinks. That is a learning-rate sweep, not credit assignment.
# It explains every odd number: slow-only kept effective LR=0.05 (too high, it
# saturated -> chance everywhere), and fast-only scored BETTER at D=20 than D=5
# because 0.9^20 happened to be a better LR than 0.9^5.
#
# Real credit loss needs INTERFERENCE: other activity writing into the trace
# during the gap. So the delay is now real ticks of distractor stimuli, and the
# update is NORMALISED per mode so all modes take equally sized steps -- isolating
# WHAT THE TRACE POINTS AT from HOW BIG IT IS.
NIN, NH, NM_, K, TICKS = 40, 60, 2, 6, 30
MODES = {'fast only  (tau~10)':  [0.90],
         'slow only  (tau~200)': [0.995],
         'bank (10/33/200)':     [0.90, 0.97, 0.995]}

def run(seed=0, TRIALS=1200, DELAY=0, mode='bank (10/33/200)'):
    rng = np.random.default_rng(seed)
    decays = MODES[mode]; nk = len(decays)
    PATS = [(rng.random(NIN)<0.35).astype(float) for _ in range(2)]
    DIST = [(rng.random(NIN)<0.35).astype(float) for _ in range(6)]   # distractors
    Wih = (rng.random((NH,NIN))<0.25)*rng.random((NH,NIN))*1.2
    Whm = np.full((NM_,NH),0.25)
    LEAK,TR_D,LR,WMAX = 0.85,0.80,0.05,1.0
    baseline=0.5
    e=np.zeros((nk,NM_,NH)); ebar=np.zeros((nk,NM_,NH))
    vh=np.zeros(NH); vm=np.zeros(NM_); trh=np.zeros(NH); fh=np.zeros(NH)
    hist=[]
    def step(x):
        nonlocal vh,vm,trh,fh
        si=(rng.random(NIN)<0.6*x).astype(float)
        vm=vm*LEAK+Whm@fh+rng.normal(0,0.35,NM_)
        fm=(vm>1.0).astype(float); vm[fm>0]=0
        vh=vh*LEAK+Wih@si
        thr=np.partition(vh,-K)[-K]; fh=((vh>=thr)&(vh>1.0)).astype(float); vh[fh>0]=0
        trh=trh*TR_D+fh
        o=np.outer(fm,trh)
        for k,d in enumerate(decays): e[k]=e[k]*d+o
        return fm
    for trial in range(TRIALS):
        c=int(rng.random()<0.5); count=np.zeros(NM_)
        for t in range(TICKS): count += step(PATS[c])
        act=int(np.argmax(count)) if count[0]!=count[1] else int(rng.random()<.5)
        r=1.0 if act==c else 0.0
        for t in range(DELAY): step(DIST[rng.integers(len(DIST))])   # REAL interference
        rpe=r-baseline; baseline+=0.02*(r-baseline)
        upd=np.zeros((NM_,NH))
        for k in range(nk):
            upd += (e[k]-ebar[k])/nk
            ebar[k]+=0.05*(e[k]-ebar[k])
        n=np.linalg.norm(upd)
        if n>1e-9: upd/=n                      # equal step size for every mode
        Whm+=LR*rpe*upd; np.clip(Whm,0,WMAX,out=Whm); hist.append(r)
    return np.array(hist)[-300:].mean()

print("delayed reward with REAL interference; chance = 0.50")
print("after acting, DELAY ticks of distractor stimuli write into the trace\n")
DELAYS=(0,20,60,150)
print(f"{'mode':<24}"+"".join(f"  D={d:<6}" for d in DELAYS))
for mode in MODES:
    row=f"{mode:<24}"
    for D in DELAYS:
        row += f"  {np.mean([run(seed=s,DELAY=D,mode=mode) for s in (0,1,2)]):.2f}   "
    print(row)
