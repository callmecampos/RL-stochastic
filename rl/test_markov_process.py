import itertools
from typing import Tuple
import unittest

from rl.distribution import Bernoulli, Distribution, SampledDistribution
from rl.markov_process import (FiniteMarkovProcess, MarkovProcess,
                               MarkovRewardProcess)


# Example classes:
class FlipFlop(MarkovProcess[bool]):
    '''A simple example Markov chain with two states, flipping from one to
    the other with probability p and staying at the same state with
    probability 1 - p.

    '''

    p: float

    def __init__(self, p: float):
        self.p = p

    def transition(self, state: bool) -> Distribution[bool]:
        def next_state(state=state):
            switch_states = Bernoulli(self.p).sample()
            return not state if switch_states else state

        return SampledDistribution(next_state)


class FiniteFlipFlop(FiniteMarkovProcess[bool]):
    ''' A version of FlipFlop implemented with the FiniteMarkovProcess machinery.

    '''
    def __init__(self, p: float):
        transition_map = {b: {not b: p, b: 1 - p} for b in {True, False}}
        super().__init__(transition_map)


class RewardFlipFlop(MarkovRewardProcess[bool]):
    p: float

    def __init__(self, p: float):
        self.p = p

    def transition_reward(self, state: bool) -> Distribution[Tuple[bool, float]]:
        def next_state(state=state):
            switch_states = Bernoulli(self.p).sample()

            if switch_states:
                next_s = not state
                reward = 1 if state else 0.5
                return next_s, reward
            else:
                return state, 0.5

        return SampledDistribution(next_state)


class TestMarkovProcess(unittest.TestCase):
    def setUp(self):
        self.flip_flop = FlipFlop(0.5)

    def test_flip_flop(self):
        trace = list(itertools.islice(self.flip_flop.simulate(True), 10))

        self.assertTrue(all(isinstance(outcome, bool) for outcome in trace))

        longer_trace = itertools.islice(self.flip_flop.simulate(True), 10000)
        count_trues = len(list(outcome for outcome in longer_trace if outcome))

        # If the code is correct, this should fail with a vanishingly
        # small probability
        self.assertTrue(1000 < count_trues < 9000)


class TestFiniteMarkovProcess(unittest.TestCase):
    def setUp(self):
        self.flip_flop = FiniteFlipFlop(0.5)

    def test_flip_flop(self):
        trace = list(itertools.islice(self.flip_flop.simulate(True), 10))

        self.assertTrue(all(isinstance(outcome, bool) for outcome in trace))

        longer_trace = itertools.islice(self.flip_flop.simulate(True), 10000)
        count_trues = len(list(outcome for outcome in longer_trace if outcome))

        # If the code is correct, this should fail with a vanishingly
        # small probability
        self.assertTrue(1000 < count_trues < 9000)


class TestRewardMarkovProcess(unittest.TestCase):
    def setUp(self):
        self.flip_flop = RewardFlipFlop(0.5)

    def test_flip_flop(self):
        trace = list(itertools.islice(self.flip_flop.simulate_reward(True), 10))

        self.assertTrue(all(isinstance(outcome, bool) for outcome, _ in trace))

        cumulative_reward = sum(reward for _, reward in trace)
        self.assertTrue(0 <= cumulative_reward <= 10)
