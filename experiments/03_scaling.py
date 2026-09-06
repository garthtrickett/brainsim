import numpy as np
# Does synaptic scaling earn its place? Test at higher plasticity + longer horizon,
# and measure SELECTIVITY (do synapses differentiate?) not just firing rate.
def run(seed=0, N=200, T=60000, syn_scaling=True, LR=0.006, label=""):
    rng = np.random.default_rng(seed)
    NE = int(0.8*N); is_exc = np.zeros(N, bool); is_exc[:NE] = True
    sign = np.where(is_exc, 1.0, -1.0)
    mask = rng.random((N, N)) < 0.1; np.fill_diagonal(mask, False)
    W = mask * rng.random((N, N)) * 0.15 * np.where(sign > 0, 1.0, 4.0)[None,:] * sign[None,:]
    exc_mask = mask & (sign > 0)[None, :]
    target_in = np.abs(W*exc_mask).sum(1).copy()
    v=np.zeros(N); thresh=np.ones(N); refrac=np.zeros(N,int); tr=np.zeros(N); rate=np.zeros(N)
    WMAX=0.6; fired=np.zeros(N,bool); h=[]
    for t in range(T):
        inp = W @ fired if t else np.zeros(N)
        inp[:20] += 0.12*(1+np.sin(t/200.0)); inp += rng.normal(0,0.02,N)
        v = v*LEAK if False else v*0.90 + inp
        v[refrac>0]=0; fired=(v>thresh)&(refrac<=0); v[fired]=0
        refrac[fired]=5; refrac=np.maximum(refrac-1,0)
        tr=tr*0.90+fired; rate=rate*0.999+0.001*fired
        f=fired.astype(float)
        W += LR*(np.outer(f,tr)-np.outer(tr,f))*exc_mask
        np.clip(W,0,WMAX,out=W,where=exc_mask)
        thresh += 0.02*(rate-0.01); np.clip(thresh,0.05,20.,out=thresh)
        if syn_scaling and t%100==0:
            cur=(W*exc_mask).sum(1)
            W=np.where(exc_mask, W*np.where(cur>1e-6,target_in/np.maximum(cur,1e-6),1.)[:,None], W)
        h.append(fired.mean())
    h=np.array(h); we=W[exc_mask]
    print(f"{label:<24} rate_late={h[-5000:].mean():.4f} peak={h.max():.3f} "
          f"at_wmax={np.mean(we>0.95*WMAX):5.1%} at_zero={np.mean(we<0.01*WMAX):5.1%} "
          f"cv={we.std()/max(we.mean(),1e-9):.2f}")
print("cv = coefficient of variation of excitatory weights (higher = more differentiated)\n")
run(syn_scaling=True,  label="with synaptic scaling")
run(syn_scaling=False, label="  clip only")
run(syn_scaling=True,  LR=0.02, label="high LR, w/ scaling")
run(syn_scaling=False, LR=0.02, label="high LR, clip only")
