"""Task suite for brainsim.

ONE Task API and ONE runner, so no experiment reimplements the loop -- twice in
this project a reimplemented loop silently broke and produced plausible numbers.

Every task exposes the same interface:
    reset(rng) -> obs           obs is a 40-dim vector in [0,1]
    step(action) -> obs, reward, done

Chance is measured by running a random policy, never assumed analytically.
That doubles as a control: if the agent cannot beat its own random baseline,
the task is unusable and its ablations are noise.
"""
import numpy as np

N_IN = 40

def _pat(rng, density=0.35):
    return (rng.random(N_IN) < density).astype(float)


class NWay:
    """N-way discrimination. Episode length 1. The task everything so far used."""
    def __init__(self, n=4, density=0.30, seed=0):
        rng = np.random.default_rng(seed)
        self.n_actions = n
        self.pats = [_pat(rng, density) for _ in range(n)]
        self.name = f"nway-{n}"
    def reset(self, rng):
        self.c = int(rng.integers(self.n_actions)); return self.pats[self.c]
    def step(self, a):
        return self.pats[self.c], float(a == self.c), True
    def correct(self): return self.c


class Lock:
    """Combination lock: one action advances, the other resets to 0.

    Sparse reward -- the failure that stopped us. Fully state-observable (each
    position has its own pattern), so replay alone can crack it; no working
    memory needed. That makes it a clean test of ONE module.
    """
    def __init__(self, length=10, seed=0):
        rng = np.random.default_rng(seed)
        self.n_actions = 2
        self.L = length
        self.codes = [_pat(rng, 0.30) for _ in range(length)]
        self.good = rng.integers(0, 2, length)
        self.name = f"lock-{length}"
    def reset(self, rng):
        self.s = 0; return self.codes[0]
    def step(self, a):
        self.s = self.s + 1 if a == self.good[self.s] else 0
        if self.s == self.L - 1:
            return self.codes[self.s], 1.0, True
        return self.codes[self.s], 0.0, False
    def correct(self): return int(self.good[self.s])


class Volatile:
    """N-way whose pattern->action mapping permutes every `switch_every` trials.

    Justifies adaptive learning rate / exploration (ACh, NE): a fixed LR and a
    fixed NOISE cannot be right both just after a switch and deep into a block.
    """
    def __init__(self, n=4, switch_every=300, density=0.30, seed=0):
        rng = np.random.default_rng(seed)
        self.n_actions = n
        self.pats = [_pat(rng, density) for _ in range(n)]
        self.switch_every = switch_every
        self.map = np.arange(n); self.t = 0; self._rng = rng
        self.name = f"volatile-{n}@{switch_every}"
    def reset(self, rng):
        if self.t and self.t % self.switch_every == 0:
            self.map = self._rng.permutation(self.n_actions)
        self.t += 1
        self.c = int(rng.integers(self.n_actions)); return self.pats[self.c]
    def step(self, a):
        return self.pats[self.c], float(a == self.map[self.c]), True
    def correct(self): return int(self.map[self.c])


class Conjunctive:
    """XOR: label is the PARITY of two feature groups, so marginals are identical.

    First version used 4 classes = A[i]+B[j], which gives four DISTINCT active
    sets -- the marginals differed, so it was just 4-way discrimination with
    overlap and the current design got 58% of the way up. Useless as a
    representation test.

    With parity, P(group A active | class 0) == P(... | class 1) = 0.5, so no
    single feature carries any information; only the conjunction does. A fixed
    random projection plus k-WTA codes marginals well and conjunctions badly,
    which is where representation quality should finally bind.
    """
    def __init__(self, seed=0, density=0.30):
        rng = np.random.default_rng(seed)
        self.n_actions = 2
        self.A = [_pat(rng, density) for _ in range(2)]
        self.B = [_pat(rng, density) for _ in range(2)]
        self.name = "xor-2"
    def reset(self, rng):
        self.i = int(rng.integers(2)); self.j = int(rng.integers(2))
        self.c = self.i ^ self.j
        return np.clip(self.A[self.i] + self.B[self.j], 0, 1)
    def step(self, a):
        return np.zeros(N_IN), float(a == self.c), True
    def correct(self): return self.c


class TMaze:
    """Cue at step 0, decision after `delay` neutral steps. Cue is GONE at choice.

    Requires holding information across decisions -- the partially-observable
    task PFC working memory needs, and which nothing we run currently requires.
    """
    def __init__(self, n=2, delay=3, seed=0):
        rng = np.random.default_rng(seed)
        self.n_actions = n
        self.cues = [_pat(rng, 0.30) for _ in range(n)]
        self.neutral = _pat(rng, 0.30)
        self.choice = _pat(rng, 0.30)
        self.delay = delay
        self.name = f"tmaze-{n}d{delay}"
    def reset(self, rng):
        self.c = int(rng.integers(self.n_actions)); self.k = 0
        return self.cues[self.c]
    def step(self, a):
        self.k += 1
        if self.k <= self.delay:
            return (self.neutral if self.k < self.delay else self.choice), 0.0, False
        return np.zeros(N_IN), float(a == self.c), True
    def correct(self): return self.c


class TMazeWithin:
    """Memory test with NO irrelevant decisions: cue, delay and choice all occur
    within a SINGLE scored decision, as phases of the tick sequence.

    `TMaze` turned out to measure tolerance of irrelevant decisions, not memory.
    Suppressing learning on its unscored steps took cue-visible from 54% to 99%
    of ceiling, and only then did a memory gap appear (0.248 visible vs 0.128
    hidden). This variant removes the confound at the task level instead: every
    decision is scored, so there is no arbitrary action to be punished for.

    Memory must span the tick gap, not a decision gap: trh decays at tau~4.5
    ticks, so a 40-tick separation is 0.8^40 = 1e-4 -- structurally impossible
    without a persistent store, which is the point.
    """
    def __init__(self, n=2, cue_ticks=10, delay_ticks=30, seed=0):
        rng = np.random.default_rng(seed)
        self.n_actions = n
        self.cues = [_pat(rng, 0.30) for _ in range(n)]
        self.neutral = _pat(rng, 0.30)
        self.choice = _pat(rng, 0.30)
        self.cue_ticks, self.delay_ticks = cue_ticks, delay_ticks
        self.name = f"tmaze-within-{n}d{delay_ticks}"
    def observation_sequence(self, rng):
        self.c = int(rng.integers(self.n_actions))
        return ([self.cues[self.c]] * self.cue_ticks
                + [self.neutral] * self.delay_ticks
                + [self.choice] * 10)
    def reset(self, rng):
        self._seq = self.observation_sequence(rng); self._i = 0
        return self._seq[0]
    def step(self, a):
        return np.zeros(N_IN), float(a == self.c), True
    def correct(self): return self.c


class Compositional:
    """shape x colour, label depends on BOTH. Train on 12 of 16, hold out 4.

    Previous representation tests measured DISCRIMINATION of patterns the encoder
    had already seen -- which a sparse random expansion does superbly (C(80,6) is
    ~3e8 possible codes). Representation learning should instead matter for
    generalising to combinations never seen, where a factorised code can place a
    novel pair and a conjunctive one cannot.
    """
    def __init__(self, n_shape=4, n_colour=4, seed=0, held_out=4):
        rng = np.random.default_rng(seed)
        self.n_actions = 4
        self.shapes  = [_pat(rng, 0.20) for _ in range(n_shape)]
        self.colours = [_pat(rng, 0.20) for _ in range(n_colour)]
        combos = [(i, j) for i in range(n_shape) for j in range(n_colour)]
        rng.shuffle(combos)
        # every held-out combo's LABEL must appear in training, or the task is
        # unsolvable for a reason unrelated to representation
        self.test, self.train = [], list(combos)
        for c in list(self.train):
            if len(self.test) >= held_out: break
            if sum(1 for t in self.train if t[0] == c[0]) > 1:
                self.train.remove(c); self.test.append(c)
        # Label = SHAPE identity; colour is a nuisance factor.
        #
        # The first version used (i+j) % n, which is not linearly decodable even
        # from a PERFECTLY factorised code -- so no representation could solve it
        # with a linear readout, and held-out scored 0.002 against a 0.256 floor
        # (systematically wrong, not chance). It tested the readout, not the code.
        #
        # With a nuisance factor the test is clean: a representation that
        # FACTORISES shape from colour generalises to unseen (shape, colour)
        # pairs for free, because colour is irrelevant. A purely CONJUNCTIVE code
        # has no representation of the unseen pair at all and must memorise.
        self.label = {(i, j): i % self.n_actions for i, j in combos}
        self.mode = "train"; self.name = f"compositional-{n_shape}x{n_colour}"
    def reset(self, rng):
        pool = self.train if self.mode == "train" else self.test
        self.i, self.j = pool[int(rng.integers(len(pool)))]
        self.c = self.label[(self.i, self.j)]
        return np.clip(self.shapes[self.i] + self.colours[self.j], 0, 1)
    def step(self, a):
        return np.zeros(N_IN), float(a == self.c), True
    def correct(self): return self.c


def run_within(agent, task, decisions, seed=0):
    """Runner for phase-structured tasks: the observation CHANGES across ticks
    within one decision, so the standard runner (one obs per decision) cannot
    present them."""
    rng = np.random.default_rng(seed); hist = []
    for _ in range(decisions):
        seq = task.observation_sequence(rng)
        for obs in seq:
            agent.step(obs)
        a = agent.decide()
        _, r, _ = task.step(a)
        agent.reward(r, action=a, done=True)
        hist.append(r)
    return np.array(hist)


def run(agent, task, decisions, ticks=30, seed=0):
    """The ONE runner. Returns reward per decision."""
    rng = np.random.default_rng(seed)
    obs = task.reset(rng); hist = []
    for _ in range(decisions):
        for _ in range(ticks): agent.step(obs)
        a = agent.decide()
        obs, r, done = task.step(a)
        agent.reward(r, action=a, done=done)   # episodic store needs boundaries
        hist.append(r)
        if done: obs = task.reset(rng)
    return np.array(hist)


def random_policy(task, decisions, seed=0):
    """Measured chance level. Never assume it analytically."""
    rng = np.random.default_rng(seed)
    task.reset(rng); hist = []
    for _ in range(decisions):
        _, r, done = task.step(int(rng.integers(task.n_actions)))
        hist.append(r)
        if done: task.reset(rng)
    return np.array(hist)


def oracle(task, decisions, seed=0):
    """Measured CEILING. A task is only usable if the agent can land between
    this and the random baseline -- floor and ceiling both make ablations
    meaningless, which cost 20 minutes on an uncalibrated 8-class task."""
    rng = np.random.default_rng(seed)
    task.reset(rng); hist = []
    for _ in range(decisions):
        _, r, done = task.step(task.correct())
        hist.append(r)
        if done: task.reset(rng)
    return np.array(hist)


ALL = lambda seed=0: [NWay(4, seed=seed), NWay(8, seed=seed), Lock(10, seed=seed),
                      Volatile(4, seed=seed), Conjunctive(seed=seed), TMaze(2, 3, seed=seed)]
