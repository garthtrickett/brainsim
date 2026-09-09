import numpy as np, sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import tasks
from brainsim import BrainSim
# Hypothesis: the UNREWARDED intermediate decision is what defeats the design.
# It produces nm = 0 - V(s) < 0, punishing an action that was irrelevant, and
# cue/choice observations share hidden units so the damage lands on the policy
# that matters. Test: suppress learning on non-scored decisions and see whether
# cue-VISIBLE then reaches its ceiling. If it does, tmaze measures tolerance of
# irrelevant decisions, NOT working memory.
DEC=6000; SEEDS=4
class CueVisible(tasks.TMaze):
    def reset(self, rng):
        o=super().reset(rng); self._cue=self.cues[self.c]; return o
    def step(self, a_):
        o,r,d=super().step(a_); return np.clip(o+self._cue,0,1), r, d
def run(mk, seed, skip_unscored=False, dec=DEC):
    t=mk(); ag=BrainSim(n_motor=t.n_actions,seed=seed)
    rng=np.random.default_rng(seed); obs=t.reset(rng); h=[]
    for i in range(dec):
        for _ in range(30): ag.step(obs)
        a=ag.decide(); obs,r,done=t.step(a)
        if skip_unscored and not done:
            ag.elig[:]=0.0; ag.elig_w=0.0; ag.trh_sum[:]=0.0; ag.trh_n=0; ag.trm[:]=0.0
        else:
            ag.reward(r, action=a, done=done)
        h.append(r)
        if done: obs=t.reset(rng)
    return np.mean(h[-dec//4:])
print("does suppressing learning on irrelevant decisions rescue it?\n", flush=True)
print(f"  {'variant':<40} {'score':>7} {'ceiling':>8} {'of ceil':>9}", flush=True)
for lab, mk, delay, skip in [
    ("delay=1 visible, learn on all",  lambda: CueVisible(2,1,seed=0), 1, False),
    ("delay=1 visible, skip unscored", lambda: CueVisible(2,1,seed=0), 1, True),
    ("delay=3 visible, learn on all",  lambda: CueVisible(2,3,seed=0), 3, False),
    ("delay=3 visible, skip unscored", lambda: CueVisible(2,3,seed=0), 3, True),
    ("delay=3 HIDDEN, skip unscored",  lambda: tasks.TMaze(2,3,seed=0), 3, True)]:
    ceil=1.0/(delay+1)
    v=np.mean([run(mk,s,skip) for s in range(SEEDS)])
    print(f"  {lab:<40} {v:7.3f} {ceil:8.3f} {v/ceil:8.0%}", flush=True)
print("\n  If 'skip unscored' reaches ceiling with the cue visible, tmaze measures", flush=True)
print("  tolerance of irrelevant decisions, not memory -- and the last row then", flush=True)
print("  isolates whether memory alone is the remaining gap.", flush=True)
