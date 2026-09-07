import numpy as np, sys; sys.path.insert(0,'/tmp/brainsim')
from common import *
# CLAIM #3: prioritised replay (by |NM|) preserves old learning better than
# uniform replay or none. SANITY GATE: the no-replay control MUST forget task A,
# otherwise there is no forgetting to prevent and the test is meaningless.
def phase(Wih,Whm,ebar,baseline,PATS,rng,trials,buf,replay,every=25,nrep=20):
    for i in range(trials):
        c=i%2
        act,e,_=trial(Wih,Whm,PATS[c],rng)
        r=1.0 if act==c else 0.0
        rpe=r-baseline; baseline+=0.02*(r-baseline)
        Whm,ebar=apply_update(Whm,ebar,e,rpe)
        buf.append((e.copy(),rpe))
        if replay!='none' and (i+1)%every==0 and len(buf)>30:
            mags=np.array([abs(b[1]) for b in buf])
            if replay=='uniform': p=np.ones(len(buf))/len(buf)
            else:                 p=(mags+1e-3)/ (mags+1e-3).sum()
            for j in rng.choice(len(buf), size=nrep, p=p):
                eb,rb=buf[j]; Whm,ebar=apply_update(Whm,ebar,eb,rb)
    return Whm,ebar,baseline

def test(Wih,Whm,PATS,seed=99,n=200):
    rng=np.random.default_rng(seed); ok=0
    for i in range(n):
        c=i%2; act,_,_=trial(Wih,Whm,PATS[c],rng); ok+=(act==c)
    return ok/n

print("CLAIM 3: replay vs forgetting. 12 seeds -- only 1 of 3 showed forgetting\nat all, so the sample of INTERPRETABLE seeds was n=1. More seeds, then\nsummarise ONLY the ones whose gate passes.")
ROWS=[]
print("train A -> train B (interference) -> retest A\n")
for seed in range(12):
    rng0=np.random.default_rng(seed)
    A=[(rng0.random(NIN)<0.35).astype(float) for _ in range(2)]
    B=[(rng0.random(NIN)<0.35).astype(float) for _ in range(2)]
    Wih=(rng0.random((NH,NIN))<0.25)*rng0.random((NH,NIN))*1.2
    out={}
    for mode in ('none','uniform','prioritised'):
        rng=np.random.default_rng(seed+500)
        Whm=np.full((NM_,NH),0.25); ebar=np.zeros((NM_,NH)); buf=[]
        Whm,ebar,bl=phase(Wih,Whm,ebar,0.5,A,rng,700,buf,'none')
        accA0=test(Wih,Whm,A)
        Whm,ebar,bl=phase(Wih,Whm,ebar,bl,B,rng,700,buf,mode)
        out[mode]=(accA0,test(Wih,Whm,A),test(Wih,Whm,B))
    n=out['none']
    gate="OK" if n[1] < n[0]-0.10 else "FAILED (no forgetting to fix)"
    print(f"seed {seed}: A after A={n[0]:.2f} -> A after B={n[1]:.2f}  [{gate}]")
    for m in ('none','uniform','prioritised'):
        print(f"         {m:<12} A_retained={out[m][1]:.2f}  B_learned={out[m][2]:.2f}")
    if n[1] < n[0]-0.10: ROWS.append(out)

print("\n" + "="*62)
print(f"seeds with genuine forgetting (gate passed): {len(ROWS)} of 12")
if ROWS:
    import numpy as _np
    for m in ('none','uniform','prioritised'):
        a=_np.mean([r[m][1] for r in ROWS]); b=_np.mean([r[m][2] for r in ROWS])
        print(f"  {m:<12} A_retained={a:.2f}   B_learned={b:.2f}")
    pa=_np.mean([r['prioritised'][1] for r in ROWS]); na=_np.mean([r['none'][1] for r in ROWS])
    ua=_np.mean([r['uniform'][1] for r in ROWS])
    print(f"\n  prioritised beats none:    {pa>na}  ({pa:.2f} vs {na:.2f})")
    print(f"  prioritised beats uniform: {pa>ua}  ({pa:.2f} vs {ua:.2f})")
else:
    print("  no interpretable seeds -- claim untestable with this task design")
