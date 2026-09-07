import numpy as np
# CLAIM #4: a BANK of eligibility traces at different decay rates beats a single
# trace, fixing the measured ~10-tick credit horizon.
# The discriminating control is "slow only": if one slow trace works everywhere,
# the bank is pointless complexity and the recommendation should just be
# "use a longer trace". The bank only earns its place if it beats BOTH.
#
# Idealisation: during the reward delay the net is silent, so traces are decayed
# analytically (elig *= decay**DELAY). Exact, and applied identically to all modes.
NIN, NH, NM_, K, TICKS = 40, 60, 2, 6, 30
MODES = {'fast only  (tau~10)':   [0.90],
         'slow only  (tau~200)':  [0.995],
         'bank (10/33/200)':      [0.90, 0.97, 0.995]}

def run(seed=0, TRIALS=1500, DELAY=5, mode='bank (10/33/200)', label=""):
    rng = np.random.default_rng(seed)
    decays = MODES[mode]; nk = len(decays)
    PATS = [(rng.random(NIN) < 0.35).astype(float) for _ in range(2)]
    Wih = (rng.random((NH, NIN)) < 0.25) * rng.random((NH, NIN)) * 1.2
    Whm = np.full((NM_, NH), 0.25)
    LEAK, TR_D, LR, WMAX = 0.85, 0.80, 0.05, 1.0
    baseline = 0.5
    e = np.zeros((nk, NM_, NH)); ebar = np.zeros((nk, NM_, NH))
    vh=np.zeros(NH); vm=np.zeros(NM_); trh=np.zeros(NH); fh=np.zeros(NH)
    hist = []
    for trial in range(TRIALS):
        c = int(rng.random() < 0.5)          # randomised, not alternating
        x = PATS[c]; count = np.zeros(NM_)
        for t in range(TICKS):
            si = (rng.random(NIN) < 0.6*x).astype(float)
            vm = vm*LEAK + Whm@fh + rng.normal(0, 0.35, NM_)
            fm = (vm > 1.0).astype(float); vm[fm>0] = 0
            vh = vh*LEAK + Wih@si
            thr = np.partition(vh,-K)[-K]
            fh = ((vh>=thr)&(vh>1.0)).astype(float); vh[fh>0]=0
            trh = trh*TR_D + fh
            outer = np.outer(fm, trh)
            for k,d in enumerate(decays): e[k] = e[k]*d + outer   # traces NOT reset
            count += fm
        act = int(np.argmax(count)) if count[0]!=count[1] else int(rng.random()<.5)
        r = 1.0 if act==c else 0.0
        for k,d in enumerate(decays): e[k] *= d**DELAY            # the reward gap
        rpe = r - baseline; baseline += 0.02*(r-baseline)
        upd = np.zeros((NM_, NH))
        for k in range(nk):
            upd += (e[k] - ebar[k]) / nk
            ebar[k] += 0.05*(e[k] - ebar[k])
        Whm += LR*rpe*upd; np.clip(Whm, 0, WMAX, out=Whm); hist.append(r)
    return np.array(hist)[-300:].mean()

print("delayed-reward discrimination; chance = 0.50")
print("action happens, THEN reward arrives DELAY ticks later\n")
print(f"{'mode':<24}" + "".join(f"  D={d:<6}" for d in (5,20,60,200)))
for mode in MODES:
    row = f"{mode:<24}"
    for D in (5,20,60,200):
        accs = [run(seed=s, DELAY=D, mode=mode) for s in (0,1,2)]
        row += f"  {np.mean(accs):.2f}   "
    print(row)
