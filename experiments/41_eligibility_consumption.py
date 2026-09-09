import numpy as np, sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import tasks
from brainsim import BrainSim
# Q2: what consumes eligibility without trial boundaries? v1 consumes fully at
# each decision (worth 0.58 -> 0.97). Continuous time has no decision. Test
# candidate rules IN v1, where full consumption is the known-good reference.
DEC=4000; SEEDS=5
class Rule(BrainSim):
    MODE="full"
    def reward(self, r, action=None, done=True):
        keep = self._keep(r)
        super().reward(r, action=action, done=done)   # this zeroes elig
        if keep is not None:                          # restore a fraction of it
            self.elig[:] = self._saved * keep
            self.elig_w  = self._saved_w * keep
    def _keep(self, r):
        if self.MODE == "full": return None
        self._saved = self.elig.copy(); self._saved_w = self.elig_w
        if self.MODE == "none":        return 1.0
        if self.MODE == "half":        return 0.5
        if self.MODE == "proportional":
            nm = abs(r - float(self.w_v @ (self.trh_sum/max(self.trh_n,1))))
            return float(max(0.0, 1.0 - min(1.0, nm)))
        return None
def run(mode, mk, seed, n, dec=DEC):
    t=mk(); a=Rule(n_motor=n, seed=seed); a.MODE=mode
    return tasks.run(a,t,dec,seed=seed)[-dec//4:].mean()
print("Q2: eligibility consumption rules, tested in v1 (5 seeds)\n", flush=True)
print(f"  {'rule':<16}{'nway-8':>10}{'volatile-4':>12}", flush=True)
for mode in ("full","none","half","proportional"):
    a=np.mean([run(mode, lambda: tasks.NWay(8,seed=0), s, 8) for s in range(SEEDS)])
    b=np.mean([run(mode, lambda: tasks.Volatile(4,300,seed=0), s, 4) for s in range(SEEDS)])
    print(f"  {mode:<16}{a:10.3f}{b:12.3f}", flush=True)
print("\n  lock-10, 3 seeds (total rewards):", flush=True)
for mode in ("full","proportional","half"):
    r=[]
    for s in range(3):
        t=tasks.Lock(10,seed=0); a=Rule(n_motor=2,seed=s); a.MODE=mode
        r.append(float(tasks.run(a,t,12000,seed=s).sum()))
    print(f"    {mode:<14} {[int(x) for x in r]}  mean={np.mean(r):.1f}", flush=True)
