import numpy as np

def run(seed=0, N=200, T=15000, inhibition=True, thresh_homeo=True,
        syn_scaling=True, refractory=True, noise=True, label=""):
    rng = np.random.default_rng(seed)
    NE = int(0.8 * N)
    is_exc = np.zeros(N, bool); is_exc[:NE] = True
    sign = np.where(is_exc, 1.0, -1.0)
    if not inhibition:
        sign[:] = 1.0                      # ablation: everyone excitatory

    p = 0.1
    mask = (rng.random((N, N)) < p)
    np.fill_diagonal(mask, False)
    W = mask * rng.random((N, N)) * 0.15
    G_INH = 4.0                            # inhibitory synapses are stronger
    W = W * np.where(sign > 0, 1.0, G_INH)[None, :] * sign[None, :]   # W[post,pre]

    exc_mask = mask & (sign > 0)[None, :]  # plastic set: -> from excitatory
    target_in = np.abs(W * exc_mask).sum(axis=1).copy()   # scaling set-point

    v      = np.zeros(N)
    thresh = np.ones(N)
    refrac = np.zeros(N, int)
    tr     = np.zeros(N)                   # fast spike trace (STDP)
    rate   = np.zeros(N)                   # slow rate estimate (homeostasis)

    LEAK, TR_D, RATE_D = 0.90, 0.90, 0.999
    TARGET, ETA_TH, LR = 0.01, 0.02, 0.002
    WMAX = 0.6
    SENS = 20

    hist = []
    for t in range(T):
        inp = W @ (tr * 0 + fired) if t else np.zeros(N)
        inp = np.zeros(N)
        if t:
            inp = W @ fired
        inp[:SENS] += 0.12 * (1 + np.sin(t / 200.0))          # a "world"
        if noise:
            inp += rng.normal(0, 0.02, N)

        v = v * LEAK + inp
        v[refrac > 0] = 0
        fired = (v > thresh) & (refrac <= 0)
        v[fired] = 0
        if refractory:
            refrac[fired] = 5
        refrac = np.maximum(refrac - 1, 0)

        tr   = tr * TR_D + fired
        rate = rate * RATE_D + (1 - RATE_D) * fired

        if fired.any():                                        # STDP, exc->any
            f = fired.astype(float)
            dW = LR * (np.outer(f, tr) - np.outer(tr, f))
            W += dW * exc_mask
            np.clip(W, 0, WMAX, out=W, where=exc_mask)

        if thresh_homeo:
            thresh += ETA_TH * (rate - TARGET)
            np.clip(thresh, 0.05, 20.0, out=thresh)

        if syn_scaling and t % 100 == 0:                        # multiplicative
            cur = (W * exc_mask).sum(axis=1)
            scale = np.where(cur > 1e-6, target_in / np.maximum(cur, 1e-6), 1.0)
            W = np.where(exc_mask, W * scale[:, None], W)

        hist.append(fired.mean())
        if not np.isfinite(v).all():
            break

    h = np.array(hist)
    late = h[-3000:]
    wexc = np.abs(W[exc_mask])
    print(f"{label:<28} rate_early={h[:2000].mean():.4f}  rate_late={late.mean():.4f}"
          f"  peak={h.max():.3f}  sat@wmax={np.mean(wexc > 0.95*WMAX):.2%}"
          f"  silent={np.mean(rate < TARGET/10):.0%}")
    return h

print("target rate = 0.0100 spikes/neuron/tick\n")
run(label="full design")
run(inhibition=False,  label="  -inhibition")
run(thresh_homeo=False,label="  -threshold homeostasis")
run(syn_scaling=False, label="  -synaptic scaling")
run(refractory=False,  label="  -refractory period")
run(noise=False,       label="  -noise")
