import numpy as np, sys; sys.path.insert(0,'/home/gust/code/brainsim')
import tasks
from brainsim import BrainSim
DEC=6000; SEEDS=4
print("=== claim 2: does anything persist across a 3-decision gap? ===", flush=True)
t=tasks.TMaze(2,3,seed=0); a=BrainSim(n_motor=2,seed=0)
rng=np.random.default_rng(0); obs=t.reset(rng); snaps=[]
for i in range(8):
    for _ in range(30): a.step(obs)
    snaps.append(a.trh.copy()); act=a.decide(); obs,r,done=t.step(act); a.reward(r,action=act,done=done)
    if done: obs=t.reset(rng)
c=lambda x,y: float(x@y/(np.linalg.norm(x)*np.linalg.norm(y)+1e-12))
print(f"  trh similarity decision k vs k+3: {np.mean([c(snaps[i],snaps[i+3]) for i in range(4)]):.4f}", flush=True)
print(f"  (adjacent decisions, for scale:   {np.mean([c(snaps[i],snaps[i+1]) for i in range(6)]):.4f})", flush=True)

print("\n=== claim 3: is the CUE more surprising than the delay steps? ===", flush=True)
class CueTMaze(tasks.TMaze):
    """Same task, but reports which phase each observation belongs to."""
    def phase(self): return "cue" if self.k==0 else ("delay" if self.k<self.delay else "choice")
t=CueTMaze(2,3,seed=0); a=BrainSim(n_motor=2,seed=0)
rng=np.random.default_rng(0); obs=t.reset(rng); byphase={}
pred=np.zeros(40); Wp=np.zeros((40,a.n_hidden)); LRp=0.02
for i in range(3000):
    ph=t.phase()
    for _ in range(30):
        si=(a.rng.random(40)<0.6*obs).astype(float)
        err=si-pred; Wp+=LRp*np.outer(err,a.trh)/(a.trh@a.trh+1e-6)
        a.step(obs); pred=np.clip(Wp@a.trh,0,1)
    if i>500: byphase.setdefault(ph,[]).append(float(np.abs(err).mean()))
    act=a.decide(); obs,r,done=t.step(act); a.reward(r,action=act,done=done)
    if done: obs=t.reset(rng)
for k in ("cue","delay","choice"):
    if k in byphase: print(f"  surprise at {k:<7}: {np.mean(byphase[k]):.4f}", flush=True)

print("\n=== claims 1+4: cue available at decision time (oracle memory) ===", flush=True)
class CueVisible(tasks.TMaze):
    """Cue superimposed on every observation -- memory is no longer needed."""
    def reset(self, rng):
        o=super().reset(rng); self._cue=self.cues[self.c]; return o
    def step(self, a_):
        o,r,d=super().step(a_)
        return np.clip(o+self._cue,0,1), r, d
def run(mk, seed):
    t=mk(); ag=BrainSim(n_motor=t.n_actions,seed=seed)
    return tasks.run(ag,t,DEC,seed=seed)[-DEC//4:].mean()
base=np.mean([run(lambda: tasks.TMaze(2,3,seed=0),s) for s in range(SEEDS)])
vis =np.mean([run(lambda: CueVisible(2,3,seed=0),s) for s in range(SEEDS)])
print(f"  standard tmaze (cue hidden):  {base:.3f}   floor 0.123 ceiling 0.250", flush=True)
print(f"  cue visible at decision:      {vis:.3f}", flush=True)
print(f"  -> memory is the only missing piece? {vis > 0.20}", flush=True)
