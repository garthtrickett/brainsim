import numpy as np, sys; sys.path.insert(0,'/home/gust/code/brainsim')
import tasks
from brainsim import BrainSim
# The oracle probe killed the design: cue VISIBLE at decision scores 0.134 against
# a 0.250 ceiling, so memory is not the missing piece. tmaze-2d3 confounds three
# things -- hold a cue, learn WHEN to act, and absorb 3 unrewarded decisions per
# episode. Isolate them before building anything.
DEC=6000; SEEDS=4
class CueVisible(tasks.TMaze):
    def reset(self, rng):
        o=super().reset(rng); self._cue=self.cues[self.c]; return o
    def step(self, a_):
        o,r,d=super().step(a_); return np.clip(o+self._cue,0,1), r, d
def run(mk, seed, dec=DEC):
    t=mk(); ag=BrainSim(n_motor=t.n_actions,seed=seed)
    h=tasks.run(ag,t,dec,seed=seed)
    return h[-dec//4:].mean()
print("isolating memory from multi-step credit assignment", flush=True)
print(f"  {'variant':<34} {'score':>7} {'floor':>7} {'ceiling':>8} {'of ceiling':>11}", flush=True)
for lab, mk, delay in [
    ("delay=1, cue hidden",  lambda: tasks.TMaze(2,1,seed=0), 1),
    ("delay=1, cue VISIBLE", lambda: CueVisible(2,1,seed=0),  1),
    ("delay=2, cue hidden",  lambda: tasks.TMaze(2,2,seed=0), 2),
    ("delay=2, cue VISIBLE", lambda: CueVisible(2,2,seed=0),  2),
    ("delay=3, cue hidden",  lambda: tasks.TMaze(2,3,seed=0), 3),
    ("delay=3, cue VISIBLE", lambda: CueVisible(2,3,seed=0),  3)]:
    ceil = 1.0/(delay+1); floor = 0.5/(delay+1)
    v=np.mean([run(mk,s) for s in range(SEEDS)])
    print(f"  {lab:<34} {v:7.3f} {floor:7.3f} {ceil:8.3f} {v/ceil:10.0%}", flush=True)
print("\n  If cue-VISIBLE is far below its ceiling even at delay=1, the task's", flush=True)
print("  multi-step reward structure -- not memory -- is what defeats the design.", flush=True)
