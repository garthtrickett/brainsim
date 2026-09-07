import numpy as np, sys; sys.path.insert(0,'/tmp/brainsim')
from common import *
# H showed +sleep-grad beating local-only on all 3 seeds. But the sleep-grad arm
# also got 60 EXTRA updates every 50 trials that local-only never got. So the win
# could be from REPLAY (more updates off stored experience) rather than from the
# GRADIENT. Third arm added: replay the same stored episodes through the ordinary
# LOCAL rule, with update counts matched exactly. If local-replay matches
# sleep-grad, the gradient is doing nothing and claim #6 collapses into claim #3.
def softmax(z): z=z-z.max(); e=np.exp(z); return e/e.sum()

def run(Wih,PATS,seed,TRIALS=900,mode='local-only',every=50,nrep=60,eta=0.05):
    rng=np.random.default_rng(seed); Whm=np.full((NM_,NH),0.25)
    ebar=np.zeros((NM_,NH)); baseline=0.5; hist=[]; buf=[]
    for i in range(TRIALS):
        c=i%2
        act,e,trh=trial(Wih,Whm,PATS[c],rng)
        r=1.0 if act==c else 0.0
        rpe=r-baseline; baseline+=0.02*(r-baseline)
        Whm,ebar=apply_update(Whm,ebar,e,rpe)
        buf.append((e.copy(), rpe, trh/TICKS, act, r)); hist.append(r)
        if mode!='local-only' and (i+1)%every==0 and len(buf)>nrep:
            for j in rng.choice(len(buf), size=nrep):        # SAME count both arms
                eb,rb,z,a,rr=buf[j]
                if mode=='local-replay':
                    Whm,ebar=apply_update(Whm,ebar,eb,rb)
                else:
                    tgt = a if rr>0.5 else 1-a
                    p=softmax(Whm@z); g=p.copy(); g[tgt]-=1.0
                    Whm-=eta*np.outer(g,z); np.clip(Whm,0,WMAX,out=Whm)
    h=np.array(hist)
    return h[100:200].mean(), h[300:400].mean(), h[800:900].mean()

print("CLAIM 6 with the replay confound controlled. chance=0.50")
print("all three arms get identical numbers of weight updates\n")
res={m:[] for m in ('local-only','local-replay','sleep-grad')}
for seed in (0,1,2,3,4):
    rng=np.random.default_rng(seed)
    PATS=[(rng.random(NIN)<0.35).astype(float) for _ in range(2)]
    Wih=(rng.random((NH,NIN))<0.25)*rng.random((NH,NIN))*1.2
    line=f"seed {seed}: "
    for m in res:
        a=run(Wih,PATS,seed,mode=m); res[m].append(a)
        line+=f" {m}={a[0]:.2f}/{a[1]:.2f}/{a[2]:.2f} "
    print(line)
print("\nmeans (acc@200 / acc@400 / acc@900):")
for m in res:
    a=np.mean(res[m],axis=0)
    print(f"  {m:<13} {a[0]:.2f} / {a[1]:.2f} / {a[2]:.2f}")
g=np.mean(res['sleep-grad'],axis=0); l=np.mean(res['local-replay'],axis=0)
print(f"\ngradient beats matched local replay? @400: {g[1]>l[1]+0.03} ({g[1]:.2f} vs {l[1]:.2f})")
print("if False, the win was replay, not the gradient -- #6 reduces to #3.")
