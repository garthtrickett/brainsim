"""Interference-as-discovery toy: interval conflict + cue-trained conditioning.

y is the EXACT forgetting fixture process (unchanged bytes at equal seeds).
The evaluator adds a hidden binary context per coordinate (toggles at each
target_* event; constant 0 otherwise) and a scalar cue
x = (2c-1)*SEP + N(0,1), SEP = 0.5, available BEFORE each prediction.
Deployable arms see (y history, current x). y-only baselines ignore x.
Oracle arms receive true c pre-update (privileged). No future, no targets.
"""
import numpy as np
from numba import njit

SEP = 0.5
KAPPA = 1.0
CUE_BASE = 96000
SPLIT_BASE = 97000
SHUFFLE_BASE = 98000

FAMILIES = ('discover', 'oracle', 'window', 'sgd', 'adwin')
ARMS = FAMILIES + ('oracle_matched', 'random', 'shuffled', 'nocontext_matched')

# 2*2*2*2 = 16 combos, first 12 lexicographic (TAU, alpha, cue_lr, lr).
_FULL = [{'tau': t, 'alpha': a, 'cue_lr': c, 'lr': l}
         for t in (0.05, 0.5) for a in (0.01, 0.1)
         for c in (0.01, 0.1) for l in (0.05, 0.2)]
DISCOVER_MENUS = [dict(c) for c in _FULL[:12]]
GRIDS = {
    'discover': [dict(c) for c in DISCOVER_MENUS],
    'oracle': [dict(c) for c in DISCOVER_MENUS],
    'window': [{'window': w} for w in (1, 2, 4, 8, 16, 32, 64, 128, 256, 512, 1024, 6000)],
    'sgd': [{'lr': lr} for lr in (.0001, .0004, .001, .004, .008, .016,
                                  .035743040182210514, .064, .128, .256, .512, 1.)],
    'adwin': [{'delta': d, 'clock': c} for d in (.0001, .001, .01, .1) for c in (1, 8, 32)],
}


def _seed(*parts):
    return np.random.SeedSequence(list(parts))


def true_contexts(data):
    """Evaluator-owned hidden context; toggles at each target_* event."""
    n = data.y.shape[0]
    contexts = np.zeros_like(data.y)
    for j, events in enumerate(data.events):
        targets = sorted(s for s, k in events if k.startswith('target_'))
        state = 0
        bounds = targets + [n]
        prev = 0
        for b in bounds:
            contexts[prev:b, j] = state
            if b < n:
                state = 1 - state
            prev = b
    return contexts


def cue_observations(seed, fixture_ordinal, contexts):
    n, w = contexts.shape
    x = np.empty_like(contexts, dtype=np.float64)
    for j in range(w):
        noise = np.random.default_rng(_seed(seed, CUE_BASE + fixture_ordinal, j)).normal(size=n)
        x[:, j] = (2.0 * contexts[:, j] - 1.0) * SEP + noise
    return x


def shuffled_cue(x, seed, fixture_ordinal):
    n, w = x.shape
    out = np.empty_like(x)
    for j in range(w):
        perm = np.random.default_rng(_seed(seed, SHUFFLE_BASE + fixture_ordinal, j)).permutation(n)
        out[:, j] = x[perm, j]
    return out


def random_splits(seed, fixture_ordinal, shape):
    n, w = shape
    out = np.empty(shape, dtype=np.float64)
    for j in range(w):
        out[:, j] = (np.random.default_rng(
            _seed(seed, SPLIT_BASE + fixture_ordinal, j)).random(n) < 0.5).astype(np.float64)
    return out


@njit(cache=True)
def discover_kernel(y, x, tau, alpha, cue_lr, lr, mode, context, splits, use_conditioning):
    """mode: 0 discover, 1 oracle, 2 random. x already shuffled for shuffled arm.

    Returns predictions, sigma (as gates), norms, scores z, hats.
    """
    n, w = y.shape
    predictions = np.zeros_like(y)
    sigmas = np.zeros_like(y)
    scores = np.zeros_like(y)
    hats = np.zeros_like(y)
    norms = np.zeros(n)
    mu = np.zeros(w)
    mu0 = np.zeros(w)
    mu1 = np.zeros(w)
    sig = np.zeros(w)
    cw = np.zeros(w)
    cb = np.zeros(w)
    kappa = 1.0
    for t in range(n):
        sq = 0.0
        for j in range(w):
            if mode == 1:
                hat = context[t, j]
                z = 20.0 * hat - 10.0
            elif mode == 2:
                hat = splits[t, j]
                z = 20.0 * hat - 10.0
            else:
                z = cw[j] * x[t, j] + cb[j]
                hat = 1.0 if z > 0.0 else 0.0
            if use_conditioning > 0 and sig[j] >= tau:
                pred = mu1[j] if hat > 0.5 else mu0[j]
            else:
                pred = mu[j]
            predictions[t, j] = pred
            scores[t, j] = z
            hats[t, j] = hat
            sigmas[t, j] = sig[j]
            err_pool = y[t, j] - mu[j]
            pull = y[t, j] - pred
            target = 1.0 if pull >= 0.0 else 0.0
            # Online logistic step on (x, target); clipped score for stability.
            zc = z
            if zc > 30.0:
                zc = 30.0
            if zc < -30.0:
                zc = -30.0
            p = 1.0 / (1.0 + np.exp(-zc))
            g = p - target
            if mode == 0:
                cw[j] -= cue_lr * g * x[t, j]
                cb[j] -= cue_lr * g
            sig[j] = (1.0 - alpha) * sig[j] + alpha * err_pool * err_pool
            step = lr * err_pool / (1.0 + kappa * sig[j])
            mu[j] += step
            if hat > 0.5:
                mu1[j] += lr * (y[t, j] - mu1[j])
            else:
                mu0[j] += lr * (y[t, j] - mu0[j])
            sq += step * step
        norms[t] = np.sqrt(sq)
    return predictions, sigmas, norms, scores, hats


def slow_cue_step(w, b, x, target, cue_lr):
    z = min(30.0, max(-30.0, w * x + b))
    p = 1.0 / (1.0 + np.exp(-z))
    g = p - target
    return w - cue_lr * g * x, b - cue_lr * g


def run(y, x, arm, config, *, contexts=None, splits=None):
    import numpy as _np
    y = _np.asarray(y, dtype=_np.float64)
    if y.ndim != 2 or not y.shape[0] or not y.shape[1] or not _np.isfinite(y).all():
        raise ValueError('finite nonempty observations required')
    if arm not in ARMS:
        raise ValueError('unknown policy')
    if contexts is not None and arm not in ('oracle', 'oracle_matched'):
        raise ValueError('privileged context forbidden')
    if splits is not None and arm != 'random':
        raise ValueError('privileged splits forbidden')
    if arm in ('window', 'sgd', 'adwin'):
        from v3_forgetting import run as base_run
        if arm == 'window':
            preds, _, norms, widths, removed = base_run(y, 'window', config)
            gates = _np.zeros_like(y)
            return preds, gates, norms, _np.zeros_like(y), _np.zeros_like(y), widths, removed
        out = base_run(y, arm, config)
        preds, _, norms = out[0], out[1], out[2]
        gates = _np.zeros_like(y)
        zeros = _np.zeros_like(y)
        if arm == 'adwin':
            return preds, gates, norms, zeros, zeros, out[3], out[4]
        return preds, gates, norms, zeros, zeros, None, None
    for key in ('tau', 'alpha', 'cue_lr', 'lr'):
        if key not in config or not np.isfinite(config[key]):
            if not (key == 'tau' and config.get(key) == float('inf')):
                raise ValueError('finite discover config required')
    tau, alpha, cue_lr, lr = (float(config['tau']), float(config['alpha']),
                              float(config['cue_lr']), float(config['lr']))
    if not (tau >= 0 and 0.0 < alpha < 1.0 and cue_lr > 0 and lr > 0) or tau != tau:
        raise ValueError('positive discover hyperparameters required')
    xx = _np.asarray(x, dtype=_np.float64)
    if xx.shape != y.shape or not _np.isfinite(xx).all():
        raise ValueError('finite cue matrix required')
    if arm in ('oracle', 'oracle_matched'):
        cc = _np.asarray(contexts, dtype=_np.float64)
        if cc.shape != y.shape or not _np.isfinite(cc).all() or _np.any((cc != 0) & (cc != 1)):
            raise ValueError('binary evaluator context required')
        mode, use_cond, sp = 1, 1, _np.zeros_like(y)
    elif arm == 'random':
        sp = _np.asarray(splits, dtype=_np.float64)
        if sp.shape != y.shape or not _np.isfinite(sp).all() or _np.any((sp != 0) & (sp != 1)):
            raise ValueError('binary independent splits required')
        mode, use_cond, cc = 2, 1, _np.zeros_like(y)
    elif arm == 'shuffled':
        mode, use_cond, cc, sp = 0, 1, _np.zeros_like(y), _np.zeros_like(y)
    elif arm == 'nocontext_matched':
        mode, use_cond, cc, sp = 0, 0, _np.zeros_like(y), _np.zeros_like(y)
    else:
        mode, use_cond, cc, sp = 0, 1, _np.zeros_like(y), _np.zeros_like(y)
    preds, sigmas, norms, scores, hats = discover_kernel(y, xx, tau, alpha, cue_lr, lr, mode, cc, sp, use_cond)
    return preds, sigmas, norms, scores, hats, None, None
