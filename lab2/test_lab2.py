"""Tests for Lab 2.   python -m pytest test_lab2.py

One test is written for you. The rest are yours: for each function, ask what
you could get wrong, then write the test that would catch it. The marker runs
its own tests against the docstrings in lab2.py, and they are not gentle.
"""

import pytest
import unittest

from lab2 import ground, load, parse_domain, parse_problem, successors, tokenize, parse_tree, Action


class TestLab2(unittest.TestCase):
    def test_parse_problem_reads_the_lab_file(self):
        # Arrange: the input.  Act: call the function.  Assert: what must be true.
        problem = parse_problem(open("problem.pddl").read())
        assert problem.objects["cat"] == "item"
        assert ("hand-empty",) in problem.init
        assert ("photo-taken", "cat") in problem.goal


    def test_run_function(self):
        tokens = tokenize("(:action suck :parameters (?c - cell) :effect (and (clean ?c) (not (dirty ?c))))")
        print(tokens)

        tree = parse_tree(tokens)
        print(tree)


    def test_parse_problem_vacuum_tiny(self):
        problem = parse_problem(open("vacuum-tiny.pddl").read())
        self.assertEqual(problem.name, 'tiny')
        self.assertEqual(problem.domain, 'vacuum')
        self.assertListEqual(list(problem.objects.keys()), [
            'c11', 'c12', 'c13', 'c21', 'c22', 'c23'
        ])
        self.assertTrue(all(v == 'cell' for v in problem.objects.values()))
        self.assertSetEqual(
            problem.init,
        frozenset({('adjacent', 'c11', 'c12'), ('adjacent', 'c11', 'c21'), ('adjacent', 'c12', 'c11'),
                   ('adjacent', 'c12', 'c13'), ('adjacent', 'c12', 'c22'), ('adjacent', 'c13', 'c12'),
                   ('adjacent', 'c13', 'c23'), ('adjacent', 'c21', 'c11'), ('adjacent', 'c21', 'c22'),
                   ('adjacent', 'c22', 'c12'), ('adjacent', 'c22', 'c21'), ('adjacent', 'c22', 'c23'),
                   ('adjacent', 'c23', 'c13'), ('adjacent', 'c23', 'c22'), ('clean', 'c11'), ('clean', 'c13'),
                   ('clean', 'c21'), ('clean', 'c22'), ('dirty', 'c12'), ('dirty', 'c23'), ('robot-at', 'c11')})
        )

    def test_parse_problem_blocks_sussman(self):
        problem = parse_problem(open("blocks-sussman.pddl").read())
        print(problem)


    def test_parse_domain_vacuum_domain(self):
        domain = parse_domain(open("vacuum-domain.pddl").read())
        self.assertEqual(domain.name, 'vacuum')
        self.assertDictEqual(domain.types, {'cell': 'object'})
        self.assertDictEqual(
            domain.predicates,
            {
                'adjacent': (('?a', 'cell'), ('?b', 'cell')),
                'clean': (('?c', 'cell'),),
                'dirty': (('?c', 'cell'),),
                'robot-at': (('?c', 'cell'),)
            }
        )
        self.assertDictEqual(
            domain.actions,
            {'move': Action(name='move', params=(('?from', 'cell'), ('?to', 'cell')),
                            pre=frozenset({('robot-at', '?from'), ('adjacent', '?from', '?to')}),
                            add=frozenset({('robot-at', '?to')}), delete=frozenset({('robot-at', '?from')})),
             'suck': Action(name='suck', params=(('?c', 'cell'),), pre=frozenset({('dirty', '?c'), ('robot-at', '?c')}),
                            add=frozenset({('clean', '?c')}), delete=frozenset({('dirty', '?c')}))}
        )

    def test_parse_domain_blocks_domain(self):
        domain = parse_domain(open("blocks-domain.pddl").read())
        print(domain)

    def test_ground(self):
        pytest.skip("write me")


    def test_successors(self):
        pytest.skip("write me")
