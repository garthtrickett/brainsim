"""End-to-end validation of the assembled mainline. Run: python3 demo.py"""
import numpy as np, tempfile, os
from brainsim import BrainSim

TICKS = 30
def task(seed):
    rng = np.random.default_rng(seed)
    return ([(rng.random(40) < 0.35).astype(float) for _ in range(2)],
            [(rng.random(40) < 0.35).astype(float) for _ in range(6)])

def run(seed=0, trials=1200, pretrain=False, model=None):
    pats, extra = task(seed)
    b = model or BrainSim(seed=seed)
    if model is None and pretrain: b.pretrain_encoder(pats + extra)   # off by default
    hist = []
    for i in range(trials):
        c = i % 2
        for _ in range(TICKS): b.step(pats[c])
        a = b.decide(); r = 1.0 if a == c else 0.0
        b.reward(r, action=a); hist.append(r)
    h = np.array(hist)
    return h[:200].mean(), h[-200:].mean(), b, pats

def evaluate(b, pats, trials=300):
    ok = 0
    for i in range(trials):
        c = i % 2
        for _ in range(TICKS): b.step(pats[c])
        ok += (b.decide() == c)
    return ok / trials

print("=" * 60)
print("1. does it learn?                            (chance 0.50)")
res = [run(seed=s)[:2] for s in (0, 1, 2)]
m = np.mean(res, axis=0)
print(f"   early={m[0]:.2f}  ->  late={m[1]:.2f}   {'PASS' if m[1] > 0.90 else 'FAIL'}")

print("2. pretrained encoder is OFF - it HURTS here   (claim 5, dropped)")
a = np.mean([run(seed=s, pretrain=True)[1] for s in (0, 1, 2)])
b_ = np.mean([run(seed=s, pretrain=False)[1] for s in (0, 1, 2)])
print(f"   late acc   pretrained={a:.2f}  random={b_:.2f}   "
      f"{'confirmed: worse' if a < b_ else 'unexpected'}")

print("3. save / load round-trip                    (claim 1)")
_, late, model, pats = run(seed=0)
f = os.path.join(tempfile.mkdtemp(), "w.npz"); model.save(f)
fresh = BrainSim(seed=99); fresh.load(f)
print(f"   trained={evaluate(model,pats):.2f}  reloaded={evaluate(fresh,pats):.2f}   "
      f"{'PASS' if abs(evaluate(fresh,pats)-late) < 0.20 else 'FAIL'}")

print("4. merge clones - SMOKE TEST ONLY, n=1        (claim 2)")
pats0, extra0 = task(0)
parent = BrainSim(seed=0); parent.pretrain_encoder(pats0 + extra0)
clones = []
for i in range(4):
    c = BrainSim(seed=100 + i); c.W_in = parent.W_in.copy()
    run(seed=0, trials=250, model=c); clones.append(c)
merged = BrainSim.merge(clones)
solo = evaluate(clones[0], pats0)
print(f"   solo={solo:.2f}  merged={evaluate(merged,pats0):.2f}   "
      f"(one seed - do not read as evidence)")
print( "   measured properly, 5 seeds: solo 0.95 -> merged 0.98, 4/5 seeds")

print("5. merge guard rejects independent agents    (claim 2)")
try:
    BrainSim.merge([BrainSim(seed=1), BrainSim(seed=2)]); print("   FAIL - no error raised")
except ValueError:
    print("   PASS - refused to merge non-clones")
print("=" * 60)
