import numpy as np

def run(seed=0, TRIALS=3000, use_rpe=True, subtract_mean_elig=True, use_elig=True,
        noise=True, lateral_inhib=True, K=6, label="", diag=False):
    rng = np.random.default_rng(seed)
    NIN, NH, NM, TICKS = 40, 60, 2, 30
    PATS = [(rng.random(NIN) < 0.35).astype(float) for _ in range(2)]
    Wih = (rng.random((NH, NIN)) < 0.25) * rng.random((NH, NIN)) * 1.2
    Whm = np.full((NM, NH), 0.25)
    LEAK, TR_D, LR, WMAX = 0.85, 0.80, 0.05, 1.0
    baseline = 0.5; ebar = np.zeros((NM, NH)); hist = []; hid = [[], []]

    for trial in range(TRIALS):
        c = trial % 2; x = PATS[c]
        vh = np.zeros(NH); vm = np.zeros(NM); trh = np.zeros(NH)
        fh = np.zeros(NH); e = np.zeros((NM, NH)); count = np.zeros(NM)
        for t in range(TICKS):
            si = (rng.random(NIN) < 0.6 * x).astype(float)
            vm = vm * LEAK + Whm @ fh
            if noise: vm += rng.normal(0, 0.35, NM)
            fm = (vm > 1.0).astype(float); vm[fm > 0] = 0
            vh = vh * LEAK + Wih @ si
            if lateral_inhib:                      # the inhibitory population, doing work:
                thr = np.partition(vh, -K)[-K]     # only the K best-driven cells survive
                fh = ((vh >= thr) & (vh > 1.0)).astype(float)
            else:
                fh = (vh > 1.0).astype(float)
            vh[fh > 0] = 0
            trh = trh * TR_D + fh
            e += np.outer(fm, trh); count += fm
        if diag: hid[c].append(trh.copy())

        act = int(np.argmax(count)) if count[0] != count[1] else int(rng.random() < .5)
        r = 1.0 if act == c else 0.0
        rpe = (r - baseline) if use_rpe else r
        baseline += 0.02 * (r - baseline)
        e /= TICKS
        de = (e - ebar) if subtract_mean_elig else e
        ebar += 0.05 * (e - ebar)
        if not use_elig: de = np.zeros_like(de)
        Whm += LR * rpe * de
        np.clip(Whm, 0.0, WMAX, out=Whm); hist.append(r)

    h = np.array(hist)
    if diag:
        a, b = np.mean(hid[0], 0), np.mean(hid[1], 0)
        print(f"   [diag] hidden overlap cos={a @ b / (np.linalg.norm(a)*np.linalg.norm(b)):.3f}")
    print(f"{label:<30} acc_first300={h[:300].mean():.2f}  acc_last300={h[-300:].mean():.2f}")
    return h

print("chance = 0.50\n")
run(seed=0, label="full design", diag=True)
for s in (1,2,3): run(seed=s, label=f"full design (seed {s})")
print()
run(lateral_inhib=False,      label="  -lateral inhibition", diag=True)
run(subtract_mean_elig=False, label="  -deviation (raw Hebb elig)")
run(use_rpe=False,            label="  -RPE (raw reward)")
run(use_elig=False,           label="  -eligibility trace")
run(noise=False,              label="  -noise (no exploration)")
