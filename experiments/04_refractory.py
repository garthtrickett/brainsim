import numpy as np
# Hypothesis for why refractory showed no effect: at target rate 0.01/tick a
# 5-tick refractory is almost never binding. It should matter under STRONG drive,
# where one cell can otherwise fire every tick and monopolise the code.
def run(seed=0, TRIALS=2500, refractory=True, GAIN=1.0, K=6, label=""):
    rng = np.random.default_rng(seed)
    NIN, NH, NM, TICKS = 40, 60, 2, 30
    PATS = [(rng.random(NIN) < 0.35).astype(float) for _ in range(2)]
    Wih = (rng.random((NH, NIN)) < 0.25) * rng.random((NH, NIN)) * 1.2 * GAIN
    Whm = np.full((NM, NH), 0.25)
    LEAK, TR_D, LR, WMAX = 0.85, 0.80, 0.05, 1.0
    baseline = 0.5; ebar = np.zeros((NM, NH)); hist = []; sc = np.zeros(NH)
    for trial in range(TRIALS):
        c = trial % 2; x = PATS[c]
        vh=np.zeros(NH); vm=np.zeros(NM); trh=np.zeros(NH); fh=np.zeros(NH)
        refr=np.zeros(NH,int); e=np.zeros((NM,NH)); count=np.zeros(NM)
        for t in range(TICKS):
            si = (rng.random(NIN) < 0.6*x).astype(float)
            vm = vm*LEAK + Whm@fh + rng.normal(0,0.35,NM)
            fm = (vm > 1.0).astype(float); vm[fm>0] = 0
            vh = vh*LEAK + Wih@si
            elig = np.where(refr>0, -1e9, vh) if refractory else vh
            thr = np.partition(elig, -K)[-K]
            fh = ((elig >= thr) & (vh > 1.0) & ((refr<=0) if refractory else True)).astype(float)
            vh[fh>0] = 0
            if refractory: refr[fh>0] = 5
            refr = np.maximum(refr-1, 0)
            trh = trh*TR_D + fh; e += np.outer(fm, trh); count += fm; sc += fh
        act = int(np.argmax(count)) if count[0]!=count[1] else int(rng.random()<.5)
        r = 1.0 if act==c else 0.0
        rpe = r - baseline; baseline += 0.02*(r-baseline)
        e /= TICKS; de = e - ebar; ebar += 0.05*(e-ebar)
        Whm += LR*rpe*de; np.clip(Whm,0,WMAX,out=Whm); hist.append(r)
    h = np.array(hist); s = np.sort(sc)[::-1]
    top = s[:3].sum()/max(sc.sum(),1)          # share of all spikes from top 5% of cells
    used = np.mean(sc > 0.01*sc.max())          # fraction of cells meaningfully active
    print(f"{label:<34} acc_last300={h[-300:].mean():.2f}  top5%_share={top:5.1%}  cells_used={used:5.0%}")

print("chance = 0.50\n")
for g,gl in ((1.0,"normal drive"), (3.0,"strong drive"), (8.0,"very strong drive")):
    run(GAIN=g, refractory=True,  label=f"{gl}, refractory")
    run(GAIN=g, refractory=False, label=f"{gl}, NO refractory")
    print()
