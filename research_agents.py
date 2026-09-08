"""Opt-in v1 study arms. The baseline tick/update implementations stay shared."""
from collections import deque
import numpy as np
from fastsim import FastBrainSim
from transition_model import TransitionModel, TransitionObserver


class CuriousAgent(FastBrainSim):
    def __init__(self, *args, curiosity=0.0, **kwargs):
        super().__init__(*args, **kwargs)
        self.curiosity = curiosity
        self.observer = TransitionObserver(self.n_in, self.n_motor)
        self.bonus_total = 0.0

    def reward(self, r, action=None, done=True):
        bonus = self.curiosity * self.observer.last_bonus
        self.bonus_total += bonus
        # Only the online policy receives intrinsic reward. The value estimate,
        # adaptive reward-rate signal, buffer and episodic store remain extrinsic.
        return super().reward(r, action=action, done=done, policy_bonus=bonus)


class ContextReplayAgent(FastBrainSim):
    def __init__(self, *args, query='off', **kwargs):
        super().__init__(*args, **kwargs)
        self.query_mode = query
        self.query_rng = np.random.default_rng([kwargs.get('seed', 0), 1301])
        self.query = np.zeros(self.n_hidden)
        self._centroid_key = None

    def reward(self, *args, **kwargs):
        self._flush()
        self.query = self.trh_sum / max(self.trh_n, 1)
        return super().reward(*args, **kwargs)

    def _sample_episode(self):
        if self.query_mode == 'off':
            return super()._sample_episode()
        key = tuple(id(ep) for ep, _ in self.episodes)
        if key != self._centroid_key:
            centres = np.array([np.mean([item[0] for item in ep], axis=0)
                                for ep, _ in self.episodes])
            self._centres = centres / np.maximum(np.linalg.norm(centres, axis=1, keepdims=True), 1e-9)
            self._rewards = np.array([r for _, r in self.episodes]) + 1e-3
            self._centroid_key = key
        query = self.query / max(float(np.linalg.norm(self.query)), 1e-9)
        if self.query_mode == 'shuffled':
            query = self._centres[self.query_rng.integers(len(self._centres))]
        weights = self._rewards * (0.05 + np.maximum(self._centres @ query, 0))
        return int(self.rng.choice(len(self.episodes), p=weights/weights.sum()))


class DynaAgent(FastBrainSim):
    """Extra real vs imagined one-step TD backups, identical update counts/rules.

The model learns the next observed hidden trace from state/action. Unobserved
state/action pairs are excluded: imagination is limited to supported transitions.
The experiment therefore tests model-based recomputation, not unsupported
counterfactual discovery or an unrestricted planner.
"""
    def __init__(self, *args, planning='off', **kwargs):
        super().__init__(*args, **kwargs)
        self.planning = planning
        self.model = TransitionModel(self.n_hidden, self.n_motor)
        self.plan_rng = np.random.default_rng([kwargs.get('seed', 0), 1101])
        self.transitions = deque(maxlen=512)
        self.pending = None
        self.support = {}
        self.backups = 0
        self.model_errors = []

    def step(self, obs):
        self.current_obs = obs
        return super().step(obs)

    def decide(self):
        self._flush()
        z = self.trh_sum / max(self.trh_n, 1)
        if self.pending is not None:
            self._finish_transition(z)
        return super().decide()

    def reward(self, r, action=None, done=True):
        self._flush()
        z = (self.trh_sum / max(self.trh_n, 1)).copy()
        w = (self.wm_sum / max(self.wm_n, 1)).copy()
        self.pending = (np.asarray(self.current_obs).tobytes(), z, w, action, r, done)
        if done:
            self._finish_transition(np.zeros(self.n_hidden))
        super().reward(r, action=action, done=done)
        if self.planning != 'off': self._plan()

    def _finish_transition(self, successor):
        key, z, w, action, reward, done = self.pending
        predicted, predicted_r, predicted_d = self.model.predict(z, action)
        self.model_errors.append((float(np.mean((predicted-successor)**2)),
                                  (predicted_r-reward)**2, (predicted_d-done)**2))
        self.model.update(z, action, successor, reward, done)
        self.support[(key, action)] = self.support.get((key, action), 0)+1
        self.transitions.append((key, z, w, action, reward, done, successor.copy()))
        self.pending = None

    def _plan(self):
        if not self.transitions: return
        transition = self.transitions[self.plan_rng.integers(len(self.transitions))]
        key, z, w, action, reward, done, successor = transition
        if self.planning == 'model':
            successor, reward, done = self.model.predict(z, action)
        v = float(self.w_v @ z)
        nm = reward + self.HIPPO_GAMMA * (1-done) * float(self.w_v @ successor) - v
        self.W_out[action] += self.HIPPO_LR * nm * z
        self.w_v += self.VALUE_W_LR * nm * z / (z @ z + 1e-6)
        if self.WM: self.W_wm[action] += self.HIPPO_LR * nm * w
        np.clip(self.W_out, self.WMIN, self.WMAX, out=self.W_out)
        self.backups += 1
