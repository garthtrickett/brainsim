"""Local, online transition predictors used only by the v1 experiments.

Each predicted component learns from its own scalar error and presynaptic state.
No gradient passes through the agent's encoder or policy.
"""
import numpy as np


class TransitionModel:
    def __init__(self, size, actions, rate=0.2):
        self.rate = rate
        self.next_weights = np.zeros((actions, size, size+1))
        self.reward_weights = np.zeros((actions, size+1))
        self.done_weights = np.zeros((actions, size+1))

    def predict(self, state, action):
        x = np.append(state, 1.0)
        return (np.maximum(self.next_weights[action] @ x, 0.0),
                float(np.clip(self.reward_weights[action] @ x, 0.0, 1.0)),
                float(np.clip(self.done_weights[action] @ x, 0.0, 1.0)))

    def update(self, state, action, next_state, reward, done):
        x = np.append(state, 1.0)
        step = self.rate * x / (x @ x + 1e-6)
        # Learn the un-clipped linear predictions; clipping is only an output
        # domain constraint, never a way to hide training error.
        self.next_weights[action] += np.outer(next_state - self.next_weights[action] @ x, step)
        self.reward_weights[action] += (reward - self.reward_weights[action] @ x) * step
        self.done_weights[action] += (done - self.done_weights[action] @ x) * step


class ObservedTask:
    """Expose only the public transition to a callback, never correct()/latent state."""
    def __init__(self, task, callback):
        self.task, self.callback = task, callback
        self.n_actions = task.n_actions

    def reset(self, rng):
        self.obs = self.task.reset(rng)
        return self.obs

    def step(self, action):
        next_obs, reward, done = self.task.step(action)
        self.callback(self.obs, action, next_obs, reward, done)
        self.obs = next_obs
        return next_obs, reward, done


class TransitionObserver:
    def __init__(self, size, actions):
        self.model = TransitionModel(size, actions)
        self.state_only = TransitionModel(size, 1)
        self.mean = np.zeros(size)
        self.reward_mean = 0.0
        self.count = 0
        self.support = {}
        self.errors = []
        self.last_bonus = 0.0

    def observe(self, obs, action, next_obs, reward, done):
        predicted, predicted_reward, _ = self.model.predict(obs, action)
        state_predicted, _, _ = self.state_only.predict(obs, 0)
        error = float(np.mean((predicted-next_obs)**2))
        self.last_bonus = error
        self.errors.append((error, float(np.mean((state_predicted-next_obs)**2)),
                            float(np.mean((self.mean-next_obs)**2)),
                            (predicted_reward-reward)**2, (self.reward_mean-reward)**2,
                            float(reward), predicted_reward))
        self.model.update(obs, action, next_obs, reward, done)
        self.state_only.update(obs, 0, next_obs, reward, done)
        self.count += 1
        self.mean += (next_obs-self.mean)/self.count
        self.reward_mean += (reward-self.reward_mean)/self.count
        key = (obs.tobytes(), action)
        self.support[key] = self.support.get(key, 0) + 1

    def summary(self, tail=2000):
        errors = np.asarray(self.errors[-tail:])
        positive = errors[:, 5] > 0
        return {'next_mse': float(errors[:, 0].mean()),
                'state_only_mse': float(errors[:, 1].mean()),
                'unconditional_mse': float(errors[:, 2].mean()),
                'reward_mse': float(errors[:, 3].mean()),
                'reward_mean_mse': float(errors[:, 4].mean()),
                'positive_reward_samples': int(positive.sum()),
                'predicted_on_positive': float(errors[positive, 6].mean()) if positive.any() else None,
                'observed_state_action_pairs': len(self.support),
                'pairs_with_3_samples': sum(n >= 3 for n in self.support.values())}
