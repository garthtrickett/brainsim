"""Step 8 follow-up. GATE 2 passed on ONE row (delay=1); at delay>=2 a PERFECT
gate does nothing. Four wrong conclusions in this project came from a single
data point, so the obvious reading -- "gating works" -- is not taken.

Hypothesis: at delay>=2 the binding constraint is not credit contamination but
that WM is cleared at every reward() call, so the cue cannot cross a decision
boundary at all. If so, PGATE is irrelevant there and WM_HOLD is the fix.

Also re-checks that PGATE/WM_HOLD defaults did NOT move the frozen table.
"""
import numpy as np, json
from fastsim import FastBrainSim
import tasks

SEEDS, DEC = 5, 6000
def score(h, tail=1500): return float(h[-tail:].mean())

MODES = {"off":                 dict(PGATE="off",          WM_HOLD=False),
         "gate":                dict(PGATE="oracle_carry", WM_HOLD=False),
         "hold":                dict(PGATE="off",          WM_HOLD=True),
         "gate+hold":           dict(PGATE="oracle_carry", WM_HOLD=True)}

print(f"step 8b: is delay>=2 a MEMORY limit, not a credit limit? {SEEDS} seeds\n", flush=True)
print(f"{'delay':>6} {'floor':>7} {'ceil':>7} | " + " ".join(f"{m:>10}" for m in MODES), flush=True)
out={}
for d in [1, 2, 3, 5]:
    fl = np.mean([score(tasks.random_policy(tasks.TMaze(2,d,seed=s), DEC, seed=s)) for s in range(SEEDS)])
    ce = np.mean([score(tasks.oracle(tasks.TMaze(2,d,seed=s), DEC, seed=s)) for s in range(SEEDS)])
    row={}
    for m,cfg in MODES.items():
        v=[]
        for s in range(SEEDS):
            a=FastBrainSim(n_motor=2, seed=s)
            for k,val in cfg.items(): setattr(a,k,val)
            v.append(score(tasks.run(a, tasks.TMaze(2,d,seed=s), DEC, seed=s)))
        row[m]=float(np.mean(v))
    fr={m:(row[m]-fl)/(ce-fl) for m in MODES}
    out[d]={"floor":float(fl),"ceiling":float(ce),**row,"frac":fr}
    print(f"{d:>6} {fl:>7.3f} {ce:>7.3f} | " + " ".join(f"{row[m]:>10.3f}" for m in MODES)
          + "   " + " ".join(f"{m}={fr[m]:.2f}" for m in MODES), flush=True)

print("\nVERDICT at delay>=2:")
g  = np.mean([out[d]['frac']['gate'] for d in (2,3,5)])
h  = np.mean([out[d]['frac']['hold'] for d in (2,3,5)])
gh = np.mean([out[d]['frac']['gate+hold'] for d in (2,3,5)])
o  = np.mean([out[d]['frac']['off'] for d in (2,3,5)])
print(f"  off={o:.3f} gate={g:.3f} hold={h:.3f} gate+hold={gh:.3f}")
print("  -> " + ("MEMORY was the limit; WM_HOLD is the fix" if h > o+0.05 or gh > g+0.05
                 else "NOT memory either -- delay>=2 fails for a third reason"))

print("\nREGRESSION: defaults must reproduce reference.json")
ref=json.load(open("reference.json"))["suite"]
bad=0
for name,mk,nact in [("nway-8",lambda s: tasks.NWay(8,seed=0),8),
                     ("volatile-4",lambda s: tasks.Volatile(4,300,seed=0),4),
                     ("xor-2",lambda s: tasks.Conjunctive(seed=0),2)]:
    got=[]
    for s in range(3):
        a=FastBrainSim(n_motor=nact,seed=s)
        got.append(score(tasks.run(a,mk(s),4000,seed=s),1000))
    exp=ref[name]["brainsim"][:3]
    same=np.allclose(got,exp)
    bad += 0 if same else 1
    print(f"  {name:<12} got={[round(x,4) for x in got]} ref={[round(x,4) for x in exp]}  {'OK' if same else '*** MOVED ***'}")
print("  " + ("defaults unchanged" if not bad else "*** PGATE/WM_HOLD PATCH CHANGED DEFAULT BEHAVIOUR ***"))
