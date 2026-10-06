"""
ECS759P — Lab 3: finding a plan
================================

Last week successors(state, actions) gave you the neighbours of a state. This week
you walk the graph from the initial state until the goal holds, and keep enough
notes on the way to say how you got there. That is a plan.

Three ways to choose which state to look at next, three algorithms:

    first in, first out        breadth-first     fewest actions
    last in, first out         depth-first       any plan, little memory
    cheapest so far first      uniform-cost      cheapest plan

Every search returns a Result: the plan, and a record of the search itself (which
states it expanded, in what order, how big its frontier got), so that you can see
what each algorithm did and not only what it found.

A plan is a list of grounded action names, e.g. "move(c11, c12)", in order.

GIVEN: action_cost, plan_cost, Result, and everything in lab2.
YOURS: reconstruct, bfs, dfs, ucs.

    python -m pytest test_lab3.py
    python lab3.py
"""

from __future__ import annotations

import heapq
from collections import deque
from dataclasses import dataclass, field
from itertools import count

from lab2 import Action, Problem, goal_reached, load, successors

# GIVEN: do not change.
COST = {"walk-between-rooms": 3, "stack": 2, "unstack": 2, "slice-object": 2}


# GIVEN: do not change.
def action_cost(name: str) -> int:
    """Cost of a grounded action, from its name: 3 to walk between rooms, 2 to stack,
    unstack or slice, 1 for anything else. The same names cost the same in every
    world: blocks' stack and unstack cost 2; every vacuum action costs 1.

    >>> action_cost("walk-between-rooms(lab, outdoors)"), action_cost("suck(c12)")
    (3, 1)
    """
    return COST.get(name.split("(")[0], 1)


# GIVEN: do not change.
def plan_cost(plan: list[str]) -> int:
    """Total cost of a plan.

    >>> plan_cost(["walk-between-rooms(lab, outdoors)", "pick-up(cat, outdoors)"])
    4
    """
    return sum(action_cost(a) for a in plan)


# GIVEN: do not change.
@dataclass
class Result:
    """What a search returns.

    plan          the actions, in order; None when no plan exists
    expanded      the states that were expanded, in the order they were expanded
    generated     successor states generated, counting repeats
    max_frontier  the largest the frontier ever was

    len(r.expanded) is the work done; r.cost is the plan's cost; r.plan[0] is the first move.
    """
    plan: list[str] | None
    expanded: list = field(default_factory=list)
    generated: int = 0
    max_frontier: int = 0

    @property
    def cost(self) -> int:
        return plan_cost(self.plan) if self.plan else 0

    def __str__(self) -> str:
        head = "no plan" if self.plan is None else f"{len(self.plan)} actions, cost {self.cost}"
        return f"{head} | {len(self.expanded)} expanded, frontier up to {self.max_frontier}"


# =============================================================== YOURS ======

def reconstruct(parent: dict, state) -> list[str]:
    """Read the plan off the parent pointers.

    `parent` maps every state reached so far to (previous_state, action_name), and
    maps the start state to None. Walk back from `state` to the start and return
    the action names in the order they were taken.

    >>> parent = {"s0": None, "s1": ("s0", "a"), "s2": ("s1", "b")}
    >>> reconstruct(parent, "s2"), reconstruct(parent, "s0")
    (['a', 'b'], [])
    """
    # TODO
    raise NotImplementedError


def bfs(problem: Problem, actions: list[Action]) -> Result:
    """Breadth-first search: a plan with the fewest actions.

    The frontier is a queue (first in, first out). The parent dict is also the
    record of which states have been reached: a state is never put on the frontier
    twice. Test the goal when a state is generated. Record every state you expand,
    in order, and the largest size the frontier reaches. plan is [] if the goal
    already holds, None if no plan exists.

    >>> d, p, acts = load("vacuum-domain.pddl", "vacuum-tiny.pddl")
    >>> r = bfs(p, acts)
    >>> len(r.plan), r.plan[0], len(r.expanded)
    (5, 'move(c11, c12)', 13)
    """
    # TODO
    raise NotImplementedError


def dfs(problem: Problem, actions: list[Action], depth_limit: int = 30) -> Result:
    """Depth-first search: the most recently generated state is expanded next.

    The frontier is a stack. Keep each state's depth; do not generate the successors
    of a state at depth_limit. A visited set guarantees termination. Test the goal
    when a state is expanded. Return the first goal state reached: a valid plan,
    usually not a short one. plan is None if nothing is found within the limit.

    >>> d, p, acts = load("vacuum-domain.pddl", "vacuum-tiny.pddl")
    >>> r = dfs(p, acts)
    >>> r.plan is not None and len(r.plan) <= 30
    True
    """
    # TODO
    raise NotImplementedError


def ucs(problem: Problem, actions: list[Action], cost=action_cost) -> Result:
    """Uniform-cost search: the cheapest plan under `cost`.

    The frontier is a priority queue ordered by g, the cheapest known cost of
    reaching a state. Pop the cheapest; test the goal when a state is popped, not
    when it is generated; when you find a cheaper path to a state you have already
    seen, record the new cost and parent and push it again (a stale entry that pops
    later is skipped). The first goal state popped is the cheapest.

    >>> d, p, acts = load("domain.pddl", "problem.pddl")
    >>> r = ucs(p, acts)
    >>> len(r.plan), r.cost
    (9, 12)
    """
    # TODO
    raise NotImplementedError


if __name__ == "__main__":
    for dom, prob in [("vacuum-domain.pddl", "vacuum-tiny.pddl"), ("blocks-domain.pddl", "blocks-sussman.pddl"),
                      ("domain.pddl", "problem.pddl")]:
        d, p, acts = load(dom, prob)
        for name, fn in [("bfs", bfs), ("dfs", dfs), ("ucs", ucs)]:
            print(f"{p.name:12s} {name}: {fn(p, acts)}")
