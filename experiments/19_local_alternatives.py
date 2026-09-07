import numpy as np, sys; sys.path.insert(0,'/home/gust/code/brainsim')
from brainsim import BrainSim
# My previous motor-kWTA test was broken: I edited votes AFTER step() so the
# eligibility never saw it, and picked the winner from vm AFTER step() had reset
# vm[fired]=0 -- argmax over zeros, always the lowest index, hence exact chance.
# Correct version: competition happens INSIDE the tick, before the reset, so fm
# is one-hot and outer(fm, trh) credits only the chosen action -- locally.
class MotorWTA(BrainSim):
    def step(self, x):
        self.ticks += 1
        si = (self.rng.random(self.n_in) < 0.6 * x).astype(float)
        self.vm = self.vm * self.LEAK + self.W_out @ self.fh \
                  + self.rng.normal(0, self.NOISE, self.n_motor)
        fm = np.zeros(self.n_motor)
        if self.vm.max() > 1.0:                 # lateral inhibition: 1 winner
            fm[int(np.argmax(self.vm))] = 1.0
        self.vm[fm > 0] = 0
        self.vh = self.vh * self.LEAK + self.W_in @ si
        thr = np.partition(self.vh, -self.k)[-self.k]
        self.fh = ((self.vh >= thr) & (self.vh > self.thresh)).astype(float)
        self.vh[self.fh > 0] = 0
        self.trh = self.trh * self.TRACE_D + self.fh
        self.elig = self.elig * self.ELIG_D + (1 - self.ELIG_D) * np.outer(fm, self.trh)
        self.elig_w = self.elig_w * self.ELIG_D + (1 - self.ELIG_D)
        self.votes += fm
        return fm
TICKS=30
def run(seed, ncls, cls, trials=3000, dens=0.30):
    rng=np.random.default_rng(seed)
    pats=[(rng.random(40)<dens).astype(float) for _ in range(ncls)]
    b=cls(n_motor=ncls, seed=seed); h=[]
    for i in range(trials):
        c=i%ncls
        for _ in range(TICKS): b.step(pats[c])
        a=b.decide(); r=1.0 if a==c else 0.0
        b.reward(r,action=a); h.append(r)
    return np.array(h)[-300:].mean(), float(np.mean(b.W_out.max(0)-b.W_out.min(0)))
print("can LOCAL motor competition do what non-local action-gating did?\n")
for ncls in (2,4,8):
    line=f"  {ncls} classes (chance {1/ncls:.3f}): "
    for cls,lab in ((BrainSim,"shipped"),(MotorWTA,"motor k-WTA")):
        out=[run(s,ncls,cls) for s in (0,1,2)]
        line+=f"  {lab}={np.mean([o[0] for o in out]):.3f} (spread {np.mean([o[1] for o in out]):.2f})"
    print(line)
print("\n  action-gated (non-local) reference: 1.000 / 0.923 / 0.919")
