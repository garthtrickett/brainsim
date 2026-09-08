"""Focused execution gates for the remaining v1 work (nonzero exit on failure)."""
import copy
import numpy as np
from brainsim import BrainSim
from fastsim import FastBrainSim
import tasks


def trace_choices(agent):
    choices = []
    original = agent.decide
    def decide():
        action = original()
        choices.append(action)
        return action
    agent.decide = decide
    return choices


def check_pools():
    for pools in (1, 2, 3, 6):
        for seed in (0, 1):
            agents = [cls(n_motor=4, seed=seed) for cls in (BrainSim, FastBrainSim)]
            histories = []
            choices = [trace_choices(a) for a in agents]
            for a in agents:
                a.POOLS = pools
                histories.append(tasks.run(a, tasks.Volatile(4, 20, seed=seed), 100, seed=seed))
            np.testing.assert_array_equal(*histories)
            np.testing.assert_array_equal(*choices)
            for field in ('W_out', 'W_wm', 'w_v', 'ebar', 'vh', 'trh', 'wm'):
                np.testing.assert_allclose(getattr(agents[0], field), getattr(agents[1], field),
                                           rtol=1e-10, atol=1e-10, err_msg=field)
            # Strongly driven, distinct membranes exercise the winner quota;
            # zero input exercises threshold rejection rather than filling quotas.
            for cls in (BrainSim, FastBrainSim):
                a = cls(); a.POOLS = pools
                a.vh[:] = np.arange(a.n_hidden) + 10
                a.step(np.zeros(a.n_in))
                if isinstance(a, FastBrainSim): a._flush()
                assert a.fh.sum() == a.k
            print(f'PASS pools={pools}, seed={seed}: trajectory, state, winner budget', flush=True)
    for cls in (BrainSim, FastBrainSim):
        for pools in (0, 4, 8, -1, 1.5):
            a = cls(); a.POOLS = pools
            try:
                a.step(np.ones(40))
                if isinstance(a, FastBrainSim): a._flush()
            except ValueError:
                continue
            raise AssertionError(f'{cls.__name__} accepted invalid pools={pools}')
    # The phase-changing memory task must use the same buffers and resets too.
    for seed in (0, 1):
        histories = [tasks.run_within(cls(seed=seed), tasks.TMazeWithin(seed=seed),
                                      100, seed=seed) for cls in (BrainSim, FastBrainSim)]
        np.testing.assert_array_equal(*histories)
    print('PASS invalid configurations and phase-structured memory parity', flush=True)


def check_experiments():
    from research_agents import CuriousAgent, ContextReplayAgent, DynaAgent
    from transition_model import ObservedTask, TransitionModel
    for probability, gain in ((0.1, 1.0), (0.5, 1.0), (0.0, 0.5)):
        agents = [cls(n_motor=4, seed=3) for cls in (BrainSim, FastBrainSim)]
        histories = []
        choices = [trace_choices(a) for a in agents]
        for a in agents:
            a.TRANSMISSION_FAILURE, a.TRANSMISSION_GAIN = probability, gain
            histories.append(tasks.run(a, tasks.NWay(4), 100, seed=3))
        np.testing.assert_array_equal(*histories)
        np.testing.assert_array_equal(*choices)
        np.testing.assert_allclose(agents[0].W_out, agents[1].W_out, atol=1e-10, rtol=1e-10)
    for seed in (0, 1):
        baseline = FastBrainSim(seed=seed)
        expected = tasks.run(baseline, tasks.Lock(4, seed=seed), 250, seed=seed)
        for cls in (CuriousAgent, ContextReplayAgent, DynaAgent):
            a = cls(seed=seed)
            task = tasks.Lock(4, seed=seed)
            if isinstance(a, CuriousAgent): task = ObservedTask(task, a.observer.observe)
            actual = tasks.run(a, task, 250, seed=seed)
            np.testing.assert_array_equal(expected, actual)
            np.testing.assert_array_equal(baseline.W_out, a.W_out)
            assert all(total == sum(item[2] for item in ep) for ep, total in a.episodes)
    # The bonus can teach the policy without rewriting external reward/value.
    a, b = [BrainSim(seed=0) for _ in range(2)]
    for agent in (a, b):
        for _ in range(30): agent.step(np.ones(40))
    action_a, action_b = a.decide(), b.decide()
    assert action_a == action_b
    a.reward(0, action=action_a)
    b.reward(0, action=action_b, policy_bonus=0.5)
    np.testing.assert_array_equal(a.w_v, b.w_v)
    assert not np.array_equal(a.W_out, b.W_out)
    assert b.buffer[-1][4] == 0
    model = TransitionModel(2, 2)
    for _ in range(200):
        model.update(np.array([1., 0.]), 0, np.array([0., 1.]), 0., False)
        model.update(np.array([1., 0.]), 1, np.array([1., 0.]), 1., True)
    np.testing.assert_allclose(model.predict(np.array([1., 0.]), 0)[0], [0., 1.], atol=1e-6)
    np.testing.assert_allclose(model.predict(np.array([1., 0.]), 1)[0], [1., 0.], atol=1e-6)
    print('PASS transmission parity, zero-arm parity, external reward isolation, action-conditioned model', flush=True)


if __name__ == '__main__':
    check_pools()
    check_experiments()
