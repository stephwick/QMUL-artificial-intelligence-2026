"""Tests for Lab 2.   python -m pytest test_lab2.py

One test is written for you. The rest are yours: for each function, ask what
you could get wrong, then write the test that would catch it. The marker runs
its own tests against the docstrings in lab2.py, and they are not gentle.
"""

import pytest

from lab2 import ground, load, parse_domain, parse_problem, successors


def test_parse_problem_reads_the_lab_file():
    # Arrange: the input.  Act: call the function.  Assert: what must be true.
    problem = parse_problem(open("problem.pddl").read())
    assert problem.objects["cat"] == "item"
    assert ("hand-empty",) in problem.init
    assert ("photo-taken", "cat") in problem.goal


def test_parse_domain():
    pytest.skip("write me")


def test_ground():
    pytest.skip("write me")


def test_successors():
    pytest.skip("write me")
