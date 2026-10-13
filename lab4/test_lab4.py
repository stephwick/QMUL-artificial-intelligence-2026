"""Tests for Lab 4.   python -m pytest test_lab4.py

One test is written for you. The rest are yours: for each function, ask what you
could get wrong, then write the test that would catch it.
"""

import pytest

from lab2 import load
from lab3 import bfs
from lab4 import best_first, goal_count, h_add, iterative_deepening, relaxed_costs


def test_goal_count_counts_the_goal_facts_still_false():
    d, p, acts = load("domain.pddl", "problem.pddl")
    assert goal_count(p.init, p.goal, acts) == 3
    assert goal_count(p.init | p.goal, p.goal, acts) == 0


def test_iterative_deepening():
    pytest.skip("write me")


def test_relaxed_costs():
    pytest.skip("write me")


def test_best_first():
    pytest.skip("write me")
