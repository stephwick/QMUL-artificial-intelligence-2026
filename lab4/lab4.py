"""
ECS759P — Lab 4: search with a sense of direction
==================================================

Last week every search was blind: it recognised a goal when it stumbled on one.
This week the frontier is ordered by an estimate of how far the goal is, and the
estimate is computed from the problem itself.

    goal_count      how many goal facts are still false
    relaxed_costs   how cheaply each fact could become true if nothing were ever deleted
    best_first      the one search loop, ordered by whatever priority you give it

With those three, greedy best-first search and A* are one line each, and they are
given below. Iterative deepening, from Wednesday's lecture, is the warm-up.

Every search returns the Result of Lab 3.

GIVEN: h_add, greedy, astar, and everything in lab2 and lab3.
YOURS: iterative_deepening, goal_count, relaxed_costs, best_first.

    python -m pytest test_lab4.py
    python lab4.py
"""

from __future__ import annotations

import heapq
from itertools import count

from lab2 import Action, Problem, goal_reached, load, successors
from lab3 import Result, action_cost, bfs, dfs, plan_cost, reconstruct, ucs

# =============================================================== YOURS ======

def iterative_deepening(problem: Problem, actions: list[Action], max_depth: int = 30) -> Result:
    """Depth-limited search with the limit 0, 1, 2, ... up to max_depth; the first plan
    found is returned, and it has the fewest actions.

    Use dfs from Lab 3 for each round. The Result's expanded list is every state
    expanded in every round, in order (shallow levels appear again and again: that
    is the price of the method); max_frontier is the largest frontier of any round.
    plan is None if no round up to max_depth finds one.

    >>> d, p, acts = load("vacuum-domain.pddl", "vacuum-tiny.pddl")
    >>> r = iterative_deepening(p, acts)
    >>> len(r.plan), len(bfs(p, acts).expanded) < len(r.expanded), r.max_frontier <= bfs(p, acts).max_frontier
    (5, True, True)
    """
    raise NotImplementedError


def goal_count(state: frozenset, goal: frozenset, actions: list[Action]) -> int:
    """The number of goal facts that are not true in the state. 0 exactly when the
    goal holds. The simplest heuristic there is; `actions` is unused but every
    heuristic takes the same three arguments so that searches can swap them.

    >>> d, p, acts = load("domain.pddl", "problem.pddl")
    >>> goal_count(p.init, p.goal, acts)
    3
    """
    # TODO
    raise NotImplementedError


def relaxed_costs(state: frozenset, actions: list[Action], cost=action_cost) -> dict:
    """The delete relaxation: pretend that no action ever deletes anything, and
    compute the cheapest cost of making each fact true, starting from `state`.

    cost(f) = 0 for every fact in the state. Otherwise cost(f) is the minimum, over
    the actions a that add f, of cost(a) + the sum of the costs of a's preconditions.
    Repeat until nothing changes. Facts no action can reach are absent from the dict.

    >>> d, p, acts = load("domain.pddl", "problem.pddl")
    >>> c = relaxed_costs(p.init, acts)
    >>> c[("holding", "cat")], c[("photo-taken", "cat")], c[("at", "dog", "outdoors")]
    (1, 2, 5)
    >>> ("can-cut", "dslr") in c
    False
    """
    # TODO
    raise NotImplementedError


def best_first(problem: Problem, actions: list[Action], priority, max_expanded: int = 200_000) -> Result:
    """The one search loop, ordered by `priority(g, state)`: the frontier is a
    priority queue, and the state with the smallest priority is expanded next.
    g is the cheapest known cost of reaching the state (action_cost).

    Test the goal when a state is expanded. When a cheaper path to a state turns
    up, record the new g and parent and push the state again, even if it was already
    expanded. Stop with plan None after max_expanded expansions. With
    priority = g this is uniform-cost search; the two functions below are the
    other two orders.

    >>> d, p, acts = load("domain.pddl", "problem.pddl")
    >>> best_first(p, acts, lambda g, s: g).cost
    12
    """
    # TODO
    raise NotImplementedError


# =============================================================== GIVEN ======
# Three heuristic searches, one line each, once best_first exists.

def h_add(state: frozenset, goal: frozenset, actions: list[Action]) -> float:
    """The additive heuristic: the sum over goal facts of their relaxed cost.
    Informative, and an overestimate whenever goal facts share work. inf if some
    goal fact cannot be reached even in the relaxation."""
    costs = relaxed_costs(state, actions)
    return sum(costs.get(f, float("inf")) for f in goal)


def greedy(problem: Problem, actions: list[Action], h, max_expanded: int = 200_000) -> Result:
    """Greedy best-first search: expand the state with the smallest h."""
    return best_first(problem, actions, lambda g, s: h(s, problem.goal, actions), max_expanded)


def astar(problem: Problem, actions: list[Action], h, max_expanded: int = 200_000) -> Result:
    """A*: expand the state with the smallest g + h. Optimal when h never overestimates."""
    return best_first(problem, actions, lambda g, s: g + h(s, problem.goal, actions), max_expanded)


if __name__ == "__main__":
    for prob in ["problem.pddl", "p3.pddl", "p4.pddl"]:
        d, p, acts = load("domain.pddl", prob)
        print(f"{p.name:14s} bfs {bfs(p, acts)}")
        print(f"{'':14s} greedy, goal_count {greedy(p, acts, goal_count)}")
        print(f"{'':14s} greedy, h_add      {greedy(p, acts, h_add)}")
        print(f"{'':14s} A*, h_add          {astar(p, acts, h_add)}")
