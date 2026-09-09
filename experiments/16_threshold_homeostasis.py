import numpy as np, sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from brainsim import BrainSim
# Threshold homeostasis exists so nothing goes silent or saturates (01: without
# it 90% of neurons went silent -- on a RECURRENT net). Before disabling it in
# the mainline, check the failure it prevents does not appear here over a long run.
TICKS=30
def run(seed, trials=3000, eta=None):
    rng=np.random.default_rng(seed)
    pats=[(rng.random(40)<0.35).astype(float) for _ in range(2)]
    b=BrainSim(seed=seed); b.SLEEP_ETA=0.0
    if eta is not None: b.ETA_TH=eta
    fired=np.zeros(b.n_hidden); h=[]
    for i in range(trials):
        c=i%2
        for _ in range(TICKS):
            b.step(pats[c]); fired+=b.fh
        a=b.decide(); r=1.0 if a==c else 0.0
        b.reward(r,action=a); h.append(r)
    rate=fired.sum()/(trials*TICKS*b.n_hidden)
    silent=np.mean(fired < 0.01*max(fired.max(),1e-9))
    return np.array(h)[-300:].mean(), rate, silent, b.thresh.mean(), (b.W_out>=b.WMAX*0.99).mean()
print("3000 trials, local rule only. k-WTA forces k/n = 6/80 = 0.075 firing.\n")
for eta,lab in ((None,"ETA_TH=0.02 (shipped)"),(0.0,"ETA_TH=0    (proposed)")):
    out=[run(s,eta=eta) for s in (0,1,2)]
    acc=np.mean([o[0] for o in out]); rate=np.mean([o[1] for o in out])
    sil=np.mean([o[2] for o in out]); th=np.mean([o[3] for o in out]); sat=np.mean([o[4] for o in out])
    print(f"  {lab:<24} acc={acc:.2f}  fire_rate={rate:.4f}  silent_cells={sil:5.0%}  "
          f"mean_thresh={th:5.2f}  W_out at ceiling={sat:4.0%}")
