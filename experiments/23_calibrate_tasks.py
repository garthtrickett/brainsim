"""Calibrate every task before any of them is used for an ablation.

Reports the measured floor (random policy), the measured ceiling (oracle), and
where the current design lands. A task is USABLE only if the agent sits clearly
between the two: at the floor an ablation cannot show damage, at the ceiling it
cannot show improvement, and either way the numbers are noise.
"""
import numpy as np, sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import tasks
from brainsim import BrainSim

DECISIONS = 4000
print(f"{DECISIONS} decisions, 3 seeds\n")
print(f"  {'task':<18} {'floor':>7} {'agent':>7} {'ceiling':>8}   verdict")
for i, t in enumerate(tasks.ALL(0)):
    fl = np.mean([tasks.random_policy(tasks.ALL(0)[i], DECISIONS, seed=s).mean() for s in (1,2,3)])
    ce = np.mean([tasks.oracle(tasks.ALL(0)[i], DECISIONS, seed=s).mean() for s in (1,2,3)])
    ag = []
    for s in (0,1,2):
        task = tasks.ALL(0)[i]
        a = BrainSim(n_motor=task.n_actions, seed=s)
        ag.append(tasks.run(a, task, DECISIONS, seed=s)[-DECISIONS//4:].mean())
    ag = np.mean(ag)
    span = ce - fl
    pos = (ag - fl) / span if span > 1e-9 else 0.0
    verdict = ("FLOOR - ablations cannot show damage" if pos < 0.10 else
               "CEILING - ablations cannot show gain" if pos > 0.90 else
               f"USABLE ({pos:.0%} of the way up)")
    print(f"  {t.name:<18} {fl:7.4f} {ag:7.4f} {ce:8.4f}   {verdict}")
