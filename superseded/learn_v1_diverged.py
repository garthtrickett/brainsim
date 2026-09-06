import numpy as np

def run(seed=0, TRIALS=4000, use_rpe=True, use_elig=True, noise=True, label=""):
    rng = np.random.default_rng(seed)
    NIN, NH, NM = 40, 80, 2
    TICKS = 40

    PATS = [(rng.random(NIN) < 0.3).astype(float) for _ in range(2)]
    Wih = rng.random((NH, NIN)) * 0.30
    Whm = rng.random((NM, NH)) * 0.10

    LEAK, TR_D, LR, WMAX = 0.85, 0.85, 0.02, 1.0
    baseline, hist, wsum = 0.0, [], []

    for trial in range(TRIALS):
        c = trial % 2
        x = PATS[c]
        vh = np.zeros(NH); vm = np.zeros(NM)
        trh = np.zeros(NH); trm = np.zeros(NM); tri = np.zeros(NIN)
        e_ih = np.zeros((NH, NIN)); e_hm = np.zeros((NM, NH))
        count = np.zeros(NM)

        for t in range(TICKS):
            si = (rng.random(NIN) < 0.5 * x).astype(float)        # stochastic sensor
            vh = vh * LEAK + Wih @ si
            vm = vm * LEAK + Whm @ fh if t else vm * LEAK
            if noise:
                vh += rng.normal(0, 0.05, NH); vm += rng.normal(0, 0.15, NM)
            fh = (vh > 1.0).astype(float); vh[fh > 0] = 0
            fm = (vm > 1.0).astype(float); vm[fm > 0] = 0
            count += fm

            tri = tri * TR_D + si; trh = trh * TR_D + fh; trm = trm * TR_D + fm
            e_ih += np.outer(fh, tri) - np.outer(trh, si)         # STDP-shaped
            e_hm += np.outer(fm, trh) - np.outer(trm, fh)

        act = int(np.argmax(count)) if count[0] != count[1] else int(rng.random() < .5)
        r = 1.0 if act == c else 0.0
        signal = (r - baseline) if use_rpe else r
        baseline += 0.01 * (r - baseline)

        if not use_elig:                       # ablation: no trace -> credit is lost
            e_ih[:] = 0; e_hm[:] = 0
        Wih += LR * signal * e_ih * (act == 0 or True)
        Whm += LR * signal * e_hm
        np.clip(Wih, 0, WMAX, out=Wih); np.clip(Whm, 0, WMAX, out=Whm)

        hist.append(r); wsum.append(Whm.sum())

    h = np.array(hist)
    print(f"{label:<26} acc_first500={h[:500].mean():.2f}  acc_last500={h[-500:].mean():.2f}"
          f"  |Whm|_end={wsum[-1]:7.1f}  drift_last1k={wsum[-1]-wsum[-1000]:+7.1f}")

print("chance = 0.50\n")
for s in (0, 1, 2):
    run(seed=s, label=f"full (seed {s})")
print()
run(use_rpe=False, label="  reward, not RPE")
run(use_elig=False, label="  no eligibility trace")
run(noise=False,    label="  no noise")
