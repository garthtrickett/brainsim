import numpy as np, sys; sys.path.insert(0,'/tmp/brainsim')
from common import *
# CLAIM #6: put gradient learning in the SLEEP slot -- offline, on replayed
# experience, body unplugged -- and the online loop stays local and always-on.
# SANITY GATE: local-only must be below ceiling at the checkpoints, or there is
# no headroom for the gradient pass to show anything.
def softmax(z): z=z-z.max(); e=np.exp(z); return e/e.sum()

def run(Wih,PATS,seed,TRIALS=900,sleepgrad=False,every=50,nrep=60,eta=0.05):
    rng=np.random.default_rng(seed); Whm=np.full((NM_,NH),0.25)
    ebar=np.zeros((NM_,NH)); baseline=0.5; hist=[]; buf=[]
    for i in range(TRIALS):
        c=i%2
        act,e,trh=trial(Wih,Whm,PATS[c],rng)
        r=1.0 if act==c else 0.0
        rpe=r-baseline; baseline+=0.02*(r-baseline)
        Whm,ebar=apply_update(Whm,ebar,e,rpe)
        buf.append((trh/TICKS, act, r)); hist.append(r)
        if sleepgrad and (i+1)%every==0 and len(buf)>nrep:
            for j in rng.choice(len(buf), size=nrep):     # body unplugged, replayed only
                z,a,rr=buf[j]
                tgt = a if rr>0.5 else 1-a                # what experience says was right
                p=softmax(Whm@z); g=p.copy(); g[tgt]-=1.0
                Whm-=eta*np.outer(g,z); np.clip(Whm,0,WMAX,out=Whm)
    h=np.array(hist)
    return h[100:200].mean(), h[300:400].mean(), h[800:900].mean()

print("CLAIM 6: gradient descent inside the sleep phase. chance=0.50\n")
for seed in (0,1,2):
    rng=np.random.default_rng(seed)
    PATS=[(rng.random(NIN)<0.35).astype(float) for _ in range(2)]
    Wih=(rng.random((NH,NIN))<0.25)*rng.random((NH,NIN))*1.2
    a=run(Wih,PATS,seed,sleepgrad=False); b=run(Wih,PATS,seed,sleepgrad=True)
    gate="OK" if a[0]<0.95 else "FAILED (local-only already at ceiling)"
    print(f"seed {seed}: acc@200/400/900  local-only={a[0]:.2f}/{a[1]:.2f}/{a[2]:.2f}   "
          f"+sleep-grad={b[0]:.2f}/{b[1]:.2f}/{b[2]:.2f}  [{gate}]")
