import numpy as np, sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from brainsim import BrainSim
# Motor k-WTA picks a winner PER TICK; the decision is an aggregate over 30 ticks.
# Credit therefore smears across whichever cells won individual ticks. The
# non-local fix (action-gating) works because it credits the DECISION.
# The local equivalent is COMMITMENT: accumulate evidence to a bound, then lock
# in -- which is how real motor decisions work (drift to threshold, then commit).
# Once locked, per-tick credit and the trial decision coincide by construction.
class Commit(BrainSim):
    MARGIN = 3          # lead in spikes required to commit
    def new_trial(self): self.locked = None
    def step(self, x):
        self.ticks += 1
        si = (self.rng.random(self.n_in) < 0.6 * x).astype(float)
        self.vm = self.vm * self.LEAK + self.W_out @ self.fh \
                  + self.rng.normal(0, self.NOISE, self.n_motor)
        fm = np.zeros(self.n_motor)
        if getattr(self, "locked", None) is not None:
            if self.vm[self.locked] > 1.0: fm[self.locked] = 1.0      # committed
        else:
            if self.vm.max() > 1.0: fm[int(np.argmax(self.vm))] = 1.0
        self.vm[fm > 0] = 0
        self.vh = self.vh * self.LEAK + self.W_in @ si
        thr = np.partition(self.vh, -self.k)[-self.k]
        self.fh = ((self.vh >= thr) & (self.vh > self.thresh)).astype(float)
        self.vh[self.fh > 0] = 0
        self.trh = self.trh * self.TRACE_D + self.fh
        self.elig = self.elig * self.ELIG_D + (1 - self.ELIG_D) * np.outer(fm, self.trh)
        self.elig_w = self.elig_w * self.ELIG_D + (1 - self.ELIG_D)
        self.votes += fm
        if getattr(self, "locked", None) is None:                     # reached the bound?
            sv = np.sort(self.votes)[::-1]
            if len(sv) > 1 and sv[0] - sv[1] >= self.MARGIN:
                self.locked = int(np.argmax(self.votes))
        return fm
TICKS=30
def run(seed, ncls, cls, trials=3000, dens=0.30):
    rng=np.random.default_rng(seed)
    pats=[(rng.random(40)<dens).astype(float) for _ in range(ncls)]
    b=cls(n_motor=ncls, seed=seed); h=[]
    for i in range(trials):
        c=i%ncls
        if hasattr(b,"new_trial"): b.new_trial()
        for _ in range(TICKS): b.step(pats[c])
        a=b.decide(); r=1.0 if a==c else 0.0
        b.reward(r,action=a); h.append(r)
    return np.array(h)[-300:].mean(), float(np.mean(b.W_out.max(0)-b.W_out.min(0)))
print("does COMMITMENT let a purely local rule scale past 2 choices?\n")
for ncls in (2,4,8):
    out=[run(s,ncls,Commit) for s in (0,1,2)]
    print(f"  {ncls} classes (chance {1/ncls:.3f}): commitment="
          f"{np.mean([o[0] for o in out]):.3f} (spread {np.mean([o[1] for o in out]):.2f})  "
          f"seeds: {' '.join(f'{o[0]:.2f}' for o in out)}")
print("\n  reference  shipped: 1.000 / 0.323 / 0.152")
print("  reference  action-gated (NON-local): 1.000 / 0.923 / 0.919")
