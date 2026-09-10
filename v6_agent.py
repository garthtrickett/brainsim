"""Margin-directed exploration as a subclass; the frozen agent is untouched.

V6 adds no code to brainsim.py. All exploration state and logic lives here,
so the frozen reference (and every prior study bound to it) cannot change.
With both flags off, decide() delegates to the frozen implementation —
bit-identical by construction, not by code duplication — while still
recording neutral trace entries the evidence expects.
"""
import numpy as np

from brainsim import BrainSim


class ExploreAgent(BrainSim):
    EXPLORE_K = 0.0
    EXPLORE_ORACLE = 0.0

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.margin_hist = []
        self.dev_hist = []

    def decide(self, correct=None):
        v = self.votes.copy()
        ordered = np.sort(v)[::-1]
        total = ordered[0]+ordered[1] if len(ordered) > 1 else ordered[0]
        closeness = 1.0 if total <= 0 else 1.0-(ordered[0]-ordered[1])/total
        self.margin_hist.append(float(closeness))
        if not self.EXPLORE_K and not self.EXPLORE_ORACLE:
            action = super().decide()
            self.dev_hist.append((action, False))
            return action
        self.votes[:] = 0
        winners = np.flatnonzero(v == v.max())
        deviated, action = False, None
        if self.EXPLORE_ORACLE > 0:
            if correct is None or not 0 <= correct < self.n_motor:
                raise ValueError('oracle exploration needs a valid label')
            if self.rng.random() < self.EXPLORE_ORACLE:
                action, deviated = int(correct), correct not in winners
        if action is None and self.EXPLORE_K > 0:
            if self.rng.random() < min(1.0, self.EXPLORE_K*closeness):
                action = int(self.rng.integers(self.n_motor))
                deviated = action not in winners
        if action is None:
            action = int(winners[0]) if len(winners) == 1 else int(winners[self.rng.integers(len(winners))])
        self.dev_hist.append((action, bool(deviated)))
        return action
