"""Tests for Lab 5.   python -m pytest test_lab5.py

One test is written for you. The rest are yours.
"""

import pytest

from lab2 import load
from lab4 import goal_count, greedy, h_add
from lab5 import anneal, h_ff, prune_plan, weighted_astar


def test_weighted_astar_with_weight_one_is_optimal_like_astar():
    d, p, acts = load("domain.pddl", "problem.pddl")
    assert weighted_astar(p, acts, lambda s, g, a: 0, 1.0).cost == 12


def test_h_ff():
    pytest.skip("write me")


def test_prune_plan():
    pytest.skip("write me")


def test_anneal():
    pytest.skip("write me")
