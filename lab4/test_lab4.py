"""Tests for Lab 4.   python -m pytest test_lab4.py

One test is written for you. The rest are yours: for each function, ask what you
could get wrong, then write the test that would catch it.
"""
import unittest

import pytest

from lab2.lab2 import load
from lab3.lab3 import bfs
from lab4.lab4 import best_first, goal_count, h_add, iterative_deepening, relaxed_costs


class TestLab4(unittest.TestCase):
    def test_simple(self):
        domain, problem, actions = load("domain.pddl", "problem.pddl")
        costs = relaxed_costs(problem.init, actions)
        # for f in sorted(problem.goal):
        #     print(f"{str(f):30s} relaxed cost {costs[f]}")
        # print("goal_count", goal_count(problem.init, problem.goal, actions), "  h_add",
        #       h_add(problem.init, problem.goal, actions), "  true cost", ucs(problem, actions).cost)

    def test_goal_count_counts_the_goal_facts_still_false(self):
        d, p, acts = load("domain.pddl", "problem.pddl")
        assert goal_count(p.init, p.goal, acts) == 3
        assert goal_count(p.init | p.goal, p.goal, acts) == 0


    def test_iterative_deepening(self):
        pytest.skip("write me")


    def test_relaxed_costs(self):
        pytest.skip("write me")


    def test_best_first(self):
        pytest.skip("write me")
