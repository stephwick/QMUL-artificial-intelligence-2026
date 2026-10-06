"""Tests for Lab 3.   python -m pytest test_lab3.py

One test is written for you. The rest are yours: for each function, ask what you
could get wrong, then write the test that would catch it.
"""
import time
import unittest

import pytest

from lab2.lab2 import load
from lab3.lab3 import Result, bfs, dfs, plan_cost, reconstruct, ucs

class TestSearchAlgorithms(unittest.TestCase):
    def test_sample_test(self):
        domain, problem, actions = load("domain.pddl", "problem.pddl")
        results = {}
        for name, fn in [("bfs", bfs), ("dfs", dfs), ("ucs", ucs)]:
            t = time.time();
            results[name] = fn(problem, actions)
            print(f"{name}: {results[name]}  ({time.time() - t:.2f}s)")

    def test_reconstruct_walks_back_to_the_start(self):
        parent = {"s0": None, "s1": ("s0", "go"), "s2": ("s1", "turn"), "s3": ("s2", "stop")}
        assert reconstruct(parent, "s3") == ["go", "turn", "stop"]
        assert reconstruct(parent, "s0") == []


    def test_bfs(self):
        pytest.skip("write me")


    def test_dfs(self):
        pytest.skip("write me")


    def test_ucs(self):
        pytest.skip("write me")
