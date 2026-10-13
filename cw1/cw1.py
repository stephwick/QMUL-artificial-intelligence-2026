"""
ECS759P — Coursework 1: planning as search
===========================================

Everything in this file runs on the state graph of Lab 2 (facts are tuples, a
state is a frozenset, grounded actions come from ground(), neighbours from
successors()) and on the searches of Labs 3, 4 and 5, which this file imports.

You were given:  domain.pddl (the workshop), p2.pddl, p4.pddl, p6.pddl,
p10.pddl (two to ten items, one goal each), delivery.pddl and tower.pddl (the two
hard problems of Part B), and cw1.ipynb (to try things; not submitted).

Part A, six functions marked by tests:  apply_plan, is_valid_plan, is_simple_plan,
h_max, admissibility_counterexample, consistency_counterexample.
Part B, five pieces of work ranked against the class:  my_heuristic, delivery_plan,
tower_plan, longest_simple_plan, most_expensive_simple_plan.
Question 4:  my_plan.

Rules
  * Implement every function marked TODO with EXACTLY this name and signature: the
    marker calls each one by name with exactly these arguments, and a function whose
    name or parameters differ scores zero for that piece. You may add helpers.
    Everything marked GIVEN must not be changed.
  * lab2, lab3, lab4 and lab5 are imported at the top. Submit any
    lab file you want us to use.
  * Only the Python standard library plus the libraries used in the labs
    (networkx, matplotlib). No planning or machine-learning libraries.
  * A plan is a list of grounded action names, e.g. "pick-up(cat, lab)", in order.
    
    python cw1.py                   Part A on p2, then every challenge once
"""

from __future__ import annotations

import heapq
import random
import time
from collections import deque
from itertools import count

from lab2 import Action, Domain, Problem, goal_reached, ground, load, parse_domain, parse_problem, successors
from lab3 import Result, action_cost, bfs, dfs, plan_cost, reconstruct, ucs
try:                                                            # from Lab 4 (week 4)
    from lab4 import astar, best_first, goal_count, greedy, h_add, relaxed_costs
except ImportError:
    pass
try:                                                            # from Lab 5 (week 5)
    from lab5 import anneal, h_ff, prune_plan, weighted_astar
except ImportError:
    pass


# ======================================================== GIVEN: helpers ====

# GIVEN: do not change.
def reachable_graph(problem: Problem, actions: list[Action], max_states: int = 3000):
    """Breadth-first exploration from problem.init. Returns (states, edges): the set of
    states reached and a list of (state, action_name, next_state), stopping once
    max_states states are known."""
    states, edges, q = {problem.init}, [], deque([problem.init])
    while q:
        s = q.popleft()
        for name, s2 in successors(s, actions).items():
            if s2 not in states:
                if len(states) >= max_states:
                    continue
                states.add(s2)
                q.append(s2)
            edges.append((s, name, s2))
    return states, edges


# GIVEN: do not change.
def true_costs_to_goal(problem: Problem, states, edges) -> dict:
    """h*(s) for every explored state: the cheapest cost from s to any goal state
    along the explored edges (Dijkstra backwards from every goal state). States that
    cannot reach a goal are absent."""
    back = {}
    for s, name, s2 in edges:
        back.setdefault(s2, []).append((s, action_cost(name)))
    dist = {s: 0 for s in states if goal_reached(s, problem.goal)}
    tie = count()
    pq = [(0, next(tie), s) for s in dist]
    heapq.heapify(pq)
    while pq:
        d, _, s = heapq.heappop(pq)
        if d > dist.get(s, float("inf")):
            continue
        for prev, c in back.get(s, ()):
            if d + c < dist.get(prev, float("inf")):
                dist[prev] = d + c
                heapq.heappush(pq, (d + c, next(tie), prev))
    return dist


# GIVEN: do not change.
def by_name(actions: list[Action]) -> dict:
    """{action name: Action}, so a plan can be replayed without successors()."""
    return {a.name: a for a in actions}


# ======================================================== PART A: plans =====

def apply_plan(init: frozenset, actions: list[Action], plan: list[str]) -> frozenset:
    """Apply a plan to a state one action at a time and return the final state.

    Raises ValueError naming the first step that cannot be applied: an action name
    that is not one of the grounded `actions`, or an action whose preconditions are
    not all in the current state (say which facts are missing).

    >>> d, p, acts = load("domain.pddl", "p2.pddl")
    >>> s = apply_plan(p.init, acts, ["pick-up-tool(dslr, lab)", "take-photo(cat, dslr, lab)"])
    >>> ("photo-taken", "cat") in s, ("hand-empty",) in s
    (True, False)
    >>> apply_plan(p.init, acts, ["take-photo(cat, dslr, lab)"])
    Traceback (most recent call last):
    ...
    ValueError: step 0: take-photo(cat, dslr, lab) needs [('has-tool', 'dslr')]
    """
    # TODO
    raise NotImplementedError


def is_valid_plan(problem: Problem, actions: list[Action], plan: list[str]) -> bool:
    """True when every step applies in turn (as apply_plan checks) and the goal
    holds in the final state. Never raises.

    >>> d, p, acts = load("domain.pddl", "p2.pddl")
    >>> is_valid_plan(p, acts, ucs(p, acts).plan), is_valid_plan(p, acts, []), is_valid_plan(p, acts, ["nonsense"])
    (True, False, False)
    """
    # TODO
    raise NotImplementedError


def is_simple_plan(init: frozenset, actions: list[Action], plan: list[str]) -> bool:
    """True when every step applies in turn AND no state is visited twice: the
    start state and the state after each action are all different. The goal plays
    no part. Never raises. Used by the two longest-path challenges.

    >>> d, p, acts = load("domain.pddl", "p2.pddl")
    >>> out, back = "walk-between-rooms(lab, outdoors)", "walk-between-rooms(outdoors, lab)"
    >>> is_simple_plan(p.init, acts, [out]), is_simple_plan(p.init, acts, [out, back]), is_simple_plan(p.init, acts, [back])
    (True, False, False)
    """
    # TODO
    raise NotImplementedError


# =================================================== PART A: heuristics ====

def h_max(state: frozenset, goal: frozenset, actions: list[Action]) -> float:
    """The max heuristic: like relaxed_costs from Lab 4, but the cost of an action's
    preconditions is the MAX of their costs instead of the sum, and the value is the
    max over goal facts. 0 when the goal holds; inf when some goal fact is
    unreachable even in the relaxation. Admissible: it never exceeds the true
    cheapest cost to the goal.

    >>> d, p, acts = load("domain.pddl", "p2.pddl")
    >>> h_max(p.init, p.goal, acts), h_add(p.init, p.goal, acts)
    (4, 10)
    """
    # TODO
    raise NotImplementedError


def admissibility_counterexample(h, problem: Problem, actions: list[Action], max_states: int = 3000):
    """A state s, reachable from problem.init, where h(s, goal, actions) > h*(s), the
    true cheapest cost from s to the goal; or None if no such state exists among the
    explored states. Explore at most max_states states (reachable_graph), compute
    h* for all of them at once (true_costs_to_goal), then compare. Any state
    returned is a genuine counterexample even when the exploration was cut short.

    >>> d, p, acts = load("domain.pddl", "p2.pddl")
    >>> admissibility_counterexample(h_max, p, acts) is None, admissibility_counterexample(h_add, p, acts) is None
    (True, False)
    """
    # TODO
    raise NotImplementedError


def consistency_counterexample(h, problem: Problem, actions: list[Action], max_states: int = 3000):
    """An explored transition (s, action_name) with h(s) > action_cost + h(s'), where
    s' is the state the action leads to; or None if every explored transition
    satisfies h(s) <= cost + h(s'). A heuristic that is not 0 on some goal state
    fails too: return (that state, None).

    >>> d, p, acts = load("domain.pddl", "p2.pddl")
    >>> consistency_counterexample(h_max, p, acts) is None
    True
    >>> s, a = consistency_counterexample(h_add, p, acts)
    >>> h_add(s, p.goal, acts) > action_cost(a) + h_add(successors(s, acts)[a], p.goal, acts)
    True
    """
    # TODO
    raise NotImplementedError


# ======================================================== PART B: ranked ====

def my_heuristic(state: frozenset, goal: frozenset, actions: list[Action]) -> float:
    """Your best heuristic for the workshop. Any number >= 0; 0 whenever the goal
    holds; finite on every state from which the goal is reachable.

    Marked by running greedy best-first search (the module's) with YOUR heuristic on
    three workshop problems you have not seen, each with a limit of 20,000
    expansions and 120 seconds: 1 mark for each problem it solves, and a rank by
    the total number of states expanded among those who solve all three. goal_count
    solves all three in about 200 expansions. h_ff alone does not solve all three:
    the notebook shows it failing on p10.pddl, and why.
    """
    # TODO
    raise NotImplementedError






def delivery_plan(seconds: float = 60.0) -> list[str]:
    """The cheapest valid plan you can find for delivery.pddl: four rooms, ten items
    to deliver, two photographs, one slicing. Walking costs 3, so this is a routing
    problem with a hand that carries one thing at a time.

    Must return within `seconds`. Valid when is_valid_plan accepts it; ranked by
    plan_cost against the class. 
    """
    # TODO
    raise NotImplementedError


def tower_plan(seconds: float = 60.0) -> list[str]:
    """A valid plan for tower.pddl: every item photographed and all ten stacked in the
    lab in the order the goal gives (truck at the bottom, cat on top). No heuristic
    search in the labs finds this plan: the frontier drowns. Think about the order
    in which the goal facts can possibly be achieved.

    Must return within `seconds`. Valid when is_valid_plan accepts it; ranked by
    plan_cost. 
    """
    # TODO
    raise NotImplementedError




def longest_simple_plan(problem: Problem, actions: list[Action], seconds: float = 60.0) -> list[str]:
    """The longest simple plan you can find in the problem's state graph: a sequence
    of actions from problem.init that never visits a state twice (the goal plays no
    part). Works on any Lab 2 world; must return within `seconds`.

    Ranked on p2.pddl, whose graph has 2,560 states, so no plan there can have more
    than 2,559 actions; finding a long one is NP-hard. Checked
    on one more problem you have not seen. Lab 3's dfs already returns
    a simple path of 27 actions on p2 (its path to the goal).
    """
    # TODO
    raise NotImplementedError


def most_expensive_simple_plan(problem: Problem, actions: list[Action], seconds: float = 60.0) -> list[str]:
    """Like longest_simple_plan, but ranked by plan_cost: the most expensive simple plan 
    is not the longest one. Same problems, same limits.
    """
    # TODO
    raise NotImplementedError


# ======================================================== QUESTION 4 =======

def my_plan() -> list[str]:
    """A valid plan of at least 8 actions for your own problem (Question 4), found by
    your own code. We check it with apply_plan on my_domain.pddl and my_problem.pddl.
    """
    # TODO
    raise NotImplementedError


if __name__ == "__main__":
    d, p, acts = load("domain.pddl", "p2.pddl")
    print("p2: h_max admissible:", admissibility_counterexample(h_max, p, acts) is None,
          "| h_add admissible:", admissibility_counterexample(h_add, p, acts) is None)
    for name, fn, prob, judge in [("delivery", delivery_plan, "delivery.pddl", is_valid_plan),
                                  ("tower", tower_plan, "tower.pddl", is_valid_plan)]:
        d, p, acts = load("domain.pddl", prob)
        plan = fn(20)
        print(f"{name}: {len(plan)} actions, cost {plan_cost(plan)}, valid {judge(p, acts, plan)}")
    d, p, acts = load("domain.pddl", "p2.pddl")
    for name, fn in [("longest", longest_simple_plan), ("most expensive", most_expensive_simple_plan)]:
        plan = fn(p, acts, 10)
        print(f"{name}: {len(plan)} actions, cost {plan_cost(plan)}, simple {is_simple_plan(p.init, acts, plan)}")
