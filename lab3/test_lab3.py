"""Tests for Lab 3.   python -m pytest test_lab3.py

One test is written for you. The rest are yours: for each function, ask what you
could get wrong, then write the test that would catch it.
"""

import pytest

from lab2 import load
from lab3 import Result, bfs, dfs, plan_cost, reconstruct, ucs


def test_reconstruct_walks_back_to_the_start():
    parent = {"s0": None, "s1": ("s0", "go"), "s2": ("s1", "turn"), "s3": ("s2", "stop")}
    assert reconstruct(parent, "s3") == ["go", "turn", "stop"]
    assert reconstruct(parent, "s0") == []


def test_bfs():
    pytest.skip("write me")


def test_dfs():
    pytest.skip("write me")


def test_ucs():
    pytest.skip("write me")
