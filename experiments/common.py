import numpy as np
NIN, NH, NM_, K, TICKS = 40, 60, 2, 6, 30
LEAK, TR_D, LR, WMAX = 0.85, 0.80, 0.05, 1.0
# The validated loop from 02_learning.py, factored out so no experiment
# reimplements it. (E was invalid because I rewrote it and broke it.)
def trial(Wih, Whm, x, rng, learn=True, state=None):
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
    return act, e/TICKS, trh

def apply_update(Whm, ebar, e, rpe):
    de=e-ebar; ebar+=0.05*(e-ebar)
    Whm+=LR*rpe*de; np.clip(Whm,0,WMAX,out=Whm)
    return Whm, ebar
