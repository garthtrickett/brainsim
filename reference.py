"""The frozen reference table. Step 7a.

The dominant failure of this project has been measurement, not mechanism: five
components were validated honestly and later turned harmful because NOTHING
re-checks a shipped component when its surroundings change. This file is the
thing that re-checks.

It records, for a fixed suite of tasks:
    floor    (random policy)        - never assumed analytically
    ceiling  (oracle)
    brainsim (the shipped defaults)
    external baselines             - softmax-SGD, tabular-Q, MLP+backprop

Committed as reference.json. Any change to brainsim.py, and any port of it, is
diffed against this. A port that cannot reproduce it is a broken port, not a
finding -- which is exactly the trap this project has hit twice.

    python3 reference.py --seeds 8 --out reference.json
"""
import argparse, json, sys, time
import numpy as np
sys.path.insert(0, "/home/gust/code/brainsim")
import tasks, baselines
from brainsim import BrainSim

# (name, task factory, n_actions, decisions, tail, runner)
SUITE = [
    ("nway-4",          lambda: tasks.NWay(4, seed=0),            4,  4000, 1000, "run"),
    ("nway-8",          lambda: tasks.NWay(8, seed=0),            8,  4000, 1000, "run"),
    ("xor-2",           lambda: tasks.Conjunctive(seed=0),        2,  4000, 1000, "run"),
    ("volatile-4",      lambda: tasks.Volatile(4, 300, seed=0),   4,  4000, 1000, "run"),
    ("tmaze-within-30", lambda: tasks.TMazeWithin(2, 10, 30, seed=0), 2, 6000, 1500, "within"),
    ("tmaze-within-60", lambda: tasks.TMazeWithin(2, 10, 60, seed=0), 2, 6000, 1500, "within"),
    ("lock-10",         lambda: tasks.Lock(10, seed=0),           2, 12000,    0, "run"),
]


def score(hist, tail):
    """tail=0 means the metric is TOTAL reward (lock: rewards are the unit)."""
    return float(hist.sum()) if tail == 0 else float(hist[-tail:].mean())


def measure(fn, mk, decisions, tail, seeds, **kw):
    out = []
    for s in range(seeds):
        out.append(score(fn(mk(), decisions, seed=s, **kw), tail))
    return out


def brainsim_run(mk, n_act, decisions, tail, seed, runner, **over):
    a = BrainSim(n_motor=n_act, seed=seed)
    for k, v in over.items(): setattr(a, k, v)
    r = tasks.run_within(a, mk(), decisions, seed=seed) if runner == "within" \
        else tasks.run(a, mk(), decisions, seed=seed)
    return score(r, tail)


def build(seeds, with_baselines=True):
    table = {"seeds": seeds, "suite": {}}
    for name, mk, n_act, dec, tail, runner in SUITE:
        t0 = time.time()
        row = {"decisions": dec, "tail": tail, "n_actions": n_act, "runner": runner}
        row["floor"]   = measure(tasks.random_policy, mk, dec, tail, seeds)
        row["ceiling"] = measure(tasks.oracle, mk, dec, tail, seeds)
        row["brainsim"] = [brainsim_run(mk, n_act, dec, tail, s, runner) for s in range(seeds)]
        if with_baselines and runner == "run":
            # the within-runner tasks present a phase sequence the flat
            # baselines cannot consume; they are compared separately.
            row["softmax-sgd"]  = measure(baselines.softmax_sgd,  mk, dec, tail, seeds)
            row["tabular-q"]    = measure(baselines.tabular_q,    mk, dec, tail, seeds)
            row["mlp-backprop"] = measure(baselines.mlp_backprop, mk, dec, tail, seeds)
        row["seconds"] = round(time.time() - t0, 1)
        table["suite"][name] = row
        s = " ".join(f"{k}={np.mean(v):.3f}" for k, v in row.items()
                     if isinstance(v, list))
        print(f"  {name:<18} {s}   [{row['seconds']}s]", flush=True)
    return table


def summary(table):
    lines = [f"{'task':<18} {'floor':>8} {'brainsim':>9} {'softmax':>8} {'tab-Q':>8} {'mlp-bp':>8} {'ceiling':>8}"]
    for name, row in table["suite"].items():
        def g(k): return f"{np.mean(row[k]):8.3f}" if k in row else "       -"
        lines.append(f"{name:<18} {g('floor')} {g('brainsim'):>9} {g('softmax-sgd')} "
                     f"{g('tabular-q')} {g('mlp-backprop')} {g('ceiling')}")
    return "\n".join(lines)


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--seeds", type=int, default=8)
    p.add_argument("--out", default="reference.json")
    p.add_argument("--no-baselines", action="store_true")
    args = p.parse_args()
    print(f"building reference table, {args.seeds} seeds\n", flush=True)
    t = build(args.seeds, not args.no_baselines)
    json.dump(t, open(args.out, "w"), indent=1)
    print("\n" + summary(t), flush=True)
    print(f"\nwritten to {args.out}", flush=True)
