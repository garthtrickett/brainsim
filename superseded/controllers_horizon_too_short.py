import numpy as np
# The two homeostatic controllers fight: settled rate undershot target (0.0080 vs
# 0.0100). Do they separate cleanly if their time constants are pulled apart?
def run(seed=0, N=200, T=40000, SCALE_EVERY=100, ETA_TH=0.02, LR=0.006, label=""):
    rng = np.random.default_rng(seed)
    NE = int(0.8*N); sign = np.where(np.arange(N) < NE, 1.0, -1.0)
    mask = rng.random((N,N)) < 0.1; np.fill_diagonal(mask, False)
    W = mask*rng.random((N,N))*0.15*np.where(sign>0,1.0,4.0)[None,:]*sign[None,:]
    exc = mask & (sign>0)[None,:]; target_in = np.abs(W*exc).sum(1).copy()
    v=np.zeros(N); th=np.ones(N); refr=np.zeros(N,int); tr=np.zeros(N); rate=np.zeros(N)
    WMAX=0.6; fired=np.zeros(N,bool); h=[]
    for t in range(T):
        inp = W@fired if t else np.zeros(N)
        inp[:20] += 0.12*(1+np.sin(t/200.)); inp += rng.normal(0,0.02,N)
        v = v*0.90 + inp; v[refr>0]=0
        fired=(v>th)&(refr<=0); v[fired]=0; refr[fired]=5; refr=np.maximum(refr-1,0)
        tr=tr*0.90+fired; rate=rate*0.999+0.001*fired
        f=fired.astype(float)
        W += LR*(np.outer(f,tr)-np.outer(tr,f))*exc
        np.clip(W,0,WMAX,out=W,where=exc)
        th += ETA_TH*(rate-0.01); np.clip(th,0.05,20.,out=th)
        if t % SCALE_EVERY == 0:
            cur=(W*exc).sum(1)
            W=np.where(exc, W*np.where(cur>1e-6,target_in/np.maximum(cur,1e-6),1.)[:,None], W)
        h.append(fired.mean())
    h=np.array(h); we=W[exc]
    print(f"{label:<40} rate_late={h[-5000:].mean():.4f} (target .0100)  "
          f"at_wmax={np.mean(we>0.95*WMAX):5.1%}  cv={we.std()/max(we.mean(),1e-9):.2f}")
print("separating the two controllers' time constants\n")
for se in (100, 1000, 5000):
    for eta in (0.02, 0.05):
        run(SCALE_EVERY=se, ETA_TH=eta, label=f"scale every {se:>4} ticks, eta_thresh={eta}")
