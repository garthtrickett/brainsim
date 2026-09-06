import numpy as np

NIN, NH, K, NS = 40, 80, 6, 10
def codes(rng): return [(rng.random(NIN) < 0.30).astype(float) for _ in range(NS)]

# ── B1: can a LOCAL delta rule learn to predict the next input, and does
#        surprise spike when the world changes underneath it? ──────────────
def b1(seed=0, T=30000, FLIP=15000):
    rng = np.random.default_rng(seed)
    C = codes(rng); Wih = (rng.random((NH,NIN))<0.25)*rng.random((NH,NIN))*1.2
    Wp = np.zeros((NIN, NH)); vh = np.zeros(NH); trh = np.zeros(NH)
    LRp = 0.02; s = 0; sur = []; pred = np.zeros(NIN)
    for t in range(T):
        s = (s + 1) % 5 if t < FLIP else (s + 2) % 7      # the world's rule changes
        si = (rng.random(NIN) < 0.8*C[s]).astype(float)
        err = si - pred                                    # error is LOCAL to the cell
        Wp += LRp * np.outer(err, trh)                     # delta rule: err_post x act_pre
        sur.append(np.abs(err).mean())
        vh = vh*0.85 + Wih@si
        thr = np.partition(vh,-K)[-K]; fh = ((vh>=thr)&(vh>1.0)).astype(float); vh[fh>0]=0
        trh = trh*0.80 + fh
        pred = np.clip(Wp @ trh, 0, 1)
    sur = np.array(sur)
    print("B1  world-model learning (local delta rule, no backprop)")
    print(f"    surprise: start={sur[:500].mean():.3f}  learned={sur[FLIP-2000:FLIP].mean():.3f}"
          f"  at flip={sur[FLIP:FLIP+300].mean():.3f}  relearned={sur[-2000:].mean():.3f}")

# ── B2: does surprise-as-intrinsic-reward buy anything when the body's
#        reward is sparse and far away? Corridor: reward only at state 9. ──
def b2(seed=0, T=60000, CURIOSITY=0.0, label=""):
    rng = np.random.default_rng(seed)
    C = codes(rng); Wih = (rng.random((NH,NIN))<0.25)*rng.random((NH,NIN))*1.2
    Whm = np.full((2,NH), 0.25); Wp = np.zeros((NIN,NH))
    vh=np.zeros(NH); trh=np.zeros(NH); vm=np.zeros(2); trm=np.zeros(2)
    e=np.zeros((2,NH)); ebar=np.zeros((2,NH)); pred=np.zeros(NIN)
    LR,LRp,WMAX = 0.02,0.02,1.0; value=0.0
    s=0; count=np.zeros(2); visited=set([0]); first_r=None; nr=0; ep=0
    for t in range(T):
        si = (rng.random(NIN) < 0.8*C[s]).astype(float)
        err = si - pred; Wp += LRp*np.outer(err, trh)
        surprise = np.abs(err).mean()
        vh = vh*0.85 + Wih@si
        thr=np.partition(vh,-K)[-K]; fh=((vh>=thr)&(vh>1.0)).astype(float); vh[fh>0]=0
        trh = trh*0.80 + fh
        vm = vm*0.85 + Whm@fh + rng.normal(0,0.40,2)
        fm = (vm>1.0).astype(float); vm[fm>0]=0; trm=trm*0.80+fm
        count += fm
        e = e*0.90 + np.outer(fm, trh)
        r = 0.0
        if t % 6 == 5:                                   # act on an accumulated vote
            a = int(np.argmax(count)) if count[0]!=count[1] else int(rng.random()<.5)
            s = max(0, min(NS-1, s + (1 if a else -1))); visited.add(s); count[:]=0
            if s == NS-1:
                r = 1.0; nr += 1; first_r = first_r or t; s = 0; ep += 1
        total = r + CURIOSITY*surprise
        value += 0.005*(total - value); NM = total - value
        ebar += 0.02*(e - ebar)
        Whm += LR*NM*(e - ebar); np.clip(Whm,0,WMAX,out=Whm)
        pred = np.clip(Wp @ trh, 0, 1)
        if t == 20000: mid = (len(visited), nr)
    print(f"{label:<26} states_seen@20k={mid[0]:2d}/10  rewards@20k={mid[1]:3d}  "
          f"first_reward_tick={first_r if first_r else '  never'}  rewards_total={nr}")

b1(); print()
print("B2  sparse-reward corridor: reward ONLY at state 9, 10 states away")
for s in (0,1,2):
    b2(seed=s, CURIOSITY=0.0, label=f"  curiosity=0.0 (seed {s})")
for s in (0,1,2):
    b2(seed=s, CURIOSITY=3.0, label=f"  curiosity=3.0 (seed {s})")
