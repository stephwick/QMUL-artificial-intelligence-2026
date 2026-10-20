"""
ECS759P — Lab 5: better estimates, and search without a frontier
=================================================================

Two ideas this week. First, a sharper heuristic: h_add counts the same work twice
when goal facts share it; the FF heuristic extracts a relaxed plan and counts
each action once. Second, local search: when the state space is too big for any
frontier, improve a plan you already have by changing it a little and keeping
what helps.

GIVEN: everything in lab2, lab3 and lab4; relaxed_layers (the building block of h_ff).
YOURS: weighted_astar, h_ff, prune_plan, anneal.

    python -m pytest test_lab5.py
    python lab5.py
"""

from __future__ import annotations

import math
import random
import time

from lab2 import Action, Problem, goal_reached, load, successors
from lab3 import Result, action_cost, plan_cost
from lab4 import astar, best_first, goal_count, greedy, h_add, relaxed_costs

# =============================================================== GIVEN ======

def relaxed_layers(state: frozenset, goal: frozenset, actions: list[Action]):
    """The relaxed planning graph: fact layers F0 ⊆ F1 ⊆ ... and action layers
    A0, A1, ..., where Ai holds the actions applicable in Fi that add something new,
    and Fi+1 = Fi ∪ their add lists. Stops when the goal is in a fact layer (returns
    the layers) or when nothing new appears (returns None: unreachable).

    >>> d, p, acts = load("domain.pddl", "problem.pddl")
    >>> facts, acts_by_layer = relaxed_layers(p.init, p.goal, acts)
    >>> len(facts), [len(a) for a in acts_by_layer]
    (3, [5, 12])
    """
    facts, layers = [frozenset(state)], []
    while not goal_reached(facts[-1], goal):
        current = facts[-1]
        layer = [a for a in actions if a.pre <= current and not a.add <= current]
        if not layer:
            return None
        facts.append(current | frozenset().union(*(a.add for a in layer)))
        layers.append(layer)
    return facts, layers


# =============================================================== YOURS ======

def weighted_astar(problem: Problem, actions: list[Action], h, w: float = 2.0, max_expanded: int = 200_000) -> Result:
    """Weighted A*: expand the state with the smallest g + w * h. With w = 1 it is A*;
    with a large w it behaves like greedy search. One line with best_first.

    >>> d, p, acts = load("domain.pddl", "p3.pddl")
    >>> weighted_astar(p, acts, h_add, 2.0).cost
    15
    """
    # TODO
    raise NotImplementedError


def h_ff(state: frozenset, goal: frozenset, actions: list[Action]) -> float:
    """The FF heuristic: build the relaxed planning graph with relaxed_layers, then
    extract a relaxed plan backwards: for every goal fact that first appeared in
    layer i, choose one action of layer i-1 that adds it and mark its preconditions
    as goals for earlier layers. The estimate is the number of chosen actions.
    0 when the goal holds; inf when the goal is unreachable even in the relaxation.

    Each action is counted once, so h_ff is usually smaller than h_add and closer
    to the truth. Like h_add it is not admissible.

    >>> d, p, acts = load("domain.pddl", "problem.pddl")
    >>> h_ff(p.init, p.goal, acts), h_add(p.init, p.goal, acts)
    (7, 10)
    """
    # TODO
    raise NotImplementedError


def prune_plan(problem: Problem, actions: list[Action], plan: list[str]) -> list[str]:
    """Local search in plan space, the simplest kind: try to delete one action, and
    if no single deletion works, any pair of actions (a walk out and back, a pick-up
    and its put-down); keep a deletion when the plan is still valid (every step
    applies and the goal holds at the end). Repeat until nothing can go. Returns a
    plan that is never longer or dearer than the one given.

    >>> d, p, acts = load("domain.pddl", "problem.pddl")
    >>> padded = ["walk-between-rooms(lab, outdoors)", "walk-between-rooms(outdoors, lab)"] + greedy(p, acts, goal_count).plan
    >>> len(padded), len(prune_plan(p, acts, padded))
    (11, 9)
    """
    # TODO
    raise NotImplementedError


def anneal(start, neighbour, score, seconds: float = 5.0, temperature: float = 1.0, seed: int = 0):
    """Simulated annealing, minimising `score`. Start from `start`; repeatedly take a
    random `neighbour(x)`; accept it if it scores lower, or with probability
    exp(-(worse by) / T) if it scores higher, where T falls from `temperature`
    to near 0 over `seconds`. Returns the best x seen.

    >>> best = anneal(10, lambda x: x + random.choice((-1, 1)), lambda x: abs(x - 3), seconds=0.5)
    >>> best
    3
    """
    # TODO
    raise NotImplementedError


if __name__ == "__main__":
    d, p, acts = load("domain.pddl", "p6.pddl")
    for name, h in [("goal_count", goal_count), ("h_add", h_add), ("h_ff", h_ff)]:
        print(f"greedy with {name:10s} {greedy(p, acts, h)}")
    for w in (1.0, 1.5, 2.0, 5.0):
        print(f"weighted A*, w = {w}: {weighted_astar(p, acts, h_ff, w, 20_000)}")
