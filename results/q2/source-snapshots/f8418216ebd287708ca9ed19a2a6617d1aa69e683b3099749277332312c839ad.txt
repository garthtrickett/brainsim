"""External baselines. Step 7a.

Every number in this project so far is measured against OUR floor, OUR ceiling
and OUR ablations. Nothing has ever been compared to something outside the
system, so "0.978 on nway-8" and "419 rewards on lock-10" are unanchored: they
could be a good result or a slow reinvention of something a ten-line algorithm
does better.

These baselines are deliberately GENEROUS -- several get privileged information
the agent never sees (exact state identity, noiseless observations). That is the
point. A generous baseline that brainsim still beats is a strong result; one it
loses to tells us what the constraint actually costs.

Each baseline states what it is given that brainsim is not.
"""
import numpy as np
import tasks


# ---------------------------------------------------------------------------
def softmax_sgd(task, decisions, seed=0, lr=0.05, ticks=30):
    """Online softmax regression on the SAME stochastic observation stream.

    Given that brainsim is not: nothing. It sees the identical input (the mean
    of `ticks` Bernoulli draws, which is what brainsim's trace effectively
    integrates) and learns online by SGD with the true label from reward.
    Withheld: it only learns from the action it took (bandit feedback), same as
    brainsim -- it is NOT given the correct label directly.

    This is the honest "does the hidden layer buy anything?" control: a linear
    readout straight off the input.
    """
    rng = np.random.default_rng(seed)
    obs = task.reset(rng)
    W = np.zeros((task.n_actions, tasks.N_IN)); b = np.zeros(task.n_actions)
    hist = []
    for _ in range(decisions):
        x = np.mean([(rng.random(tasks.N_IN) < 0.6 * obs) for _ in range(ticks)], axis=0)
        logit = W @ x + b
        p = np.exp(logit - logit.max()); p /= p.sum()
        a = int(rng.choice(task.n_actions, p=p))
        obs, r, done = task.step(a)
        # REINFORCE with a moving baseline -- bandit feedback, like brainsim.
        g = -p.copy(); g[a] += 1.0
        W += lr * r * np.outer(g, x); b += lr * r * g
        hist.append(r)
        if done: obs = task.reset(rng)
    return np.array(hist)


def tabular_q(task, decisions, seed=0, alpha=0.2, gamma=0.9, eps=0.1, ticks=30):
    """Tabular Q-learning keyed on the EXACT underlying state.

    Given that brainsim is not: perfect state abstraction. It is handed a
    discrete state id (the noiseless pattern identity), so it solves no
    perception problem at all and no credit assignment across a distributed
    code. On lock-10 that is a large gift -- brainsim must discover from a
    40-dim noisy binary vector that position 7 is a distinct situation.

    This is the upper reference for "what does a textbook RL algorithm get on
    this MDP", not a like-for-like comparison.
    """
    rng = np.random.default_rng(seed)
    task.reset(rng)
    Q = {}
    def key(t):
        # exact state: lock position, nway/volatile class, tmaze phase+cue
        for attr in ("s", "c"):
            if hasattr(t, attr): return (attr, int(getattr(t, attr)))
        return ("_", 0)
    hist = []
    s = key(task)
    for _ in range(decisions):
        q = Q.setdefault(s, np.zeros(task.n_actions))
        a = int(rng.integers(task.n_actions)) if rng.random() < eps else int(np.argmax(q))
        _, r, done = task.step(a)
        s2 = key(task)
        q2 = Q.setdefault(s2, np.zeros(task.n_actions))
        q[a] += alpha * (r + (0.0 if done else gamma * q2.max()) - q[a])
        hist.append(r)
        if done: task.reset(rng); s2 = key(task)
        s = s2
    return np.array(hist)


def mlp_backprop(task, decisions, seed=0, lr=0.05, hidden=80, ticks=30):
    """One-hidden-layer MLP trained by BACKPROP on the same observation stream.

    Given that brainsim is not: a global error signal propagated through the
    hidden layer. Same width (80), same input, same bandit feedback. This is the
    control for the project's central constraint -- what does refusing backprop
    actually cost?
    """
    rng = np.random.default_rng(seed)
    obs = task.reset(rng)
    W1 = rng.normal(0, 0.3, (hidden, tasks.N_IN)); b1 = np.zeros(hidden)
    W2 = rng.normal(0, 0.3, (task.n_actions, hidden)); b2 = np.zeros(task.n_actions)
    base = 0.0
    hist = []
    for _ in range(decisions):
        x = np.mean([(rng.random(tasks.N_IN) < 0.6 * obs) for _ in range(ticks)], axis=0)
        h = np.tanh(W1 @ x + b1)
        logit = W2 @ h + b2
        p = np.exp(logit - logit.max()); p /= p.sum()
        a = int(rng.choice(task.n_actions, p=p))
        obs, r, done = task.step(a)
        base += 0.02 * (r - base)
        adv = r - base
        g2 = -p.copy(); g2[a] += 1.0            # d log p / d logit
        gh = (W2.T @ g2) * (1 - h * h)
        W2 += lr * adv * np.outer(g2, h); b2 += lr * adv * g2
        W1 += lr * adv * np.outer(gh, x); b1 += lr * adv * gh
        hist.append(r)
        if done: obs = task.reset(rng)
    return np.array(hist)


BASELINES = {"softmax-sgd": softmax_sgd, "tabular-q": tabular_q, "mlp-backprop": mlp_backprop}
