"""
ECS759P — Lab 2: reading a world from a file
=============================================

Last week the world was Python code. This week it is a PDDL file, and your code
reads it, turns it into actions, and walks the graph of states those actions
make. You will import this file every week from now on.

    A fact is a tuple of strings          ("at", "cat", "lab")      ("hand-empty",)
    A state is a frozenset of facts
    An Action has preconditions, facts it adds, and facts it deletes

The PDDL we read (STRIPS with types). A problem file:

    (define (problem two-animals)
      (:domain workshop)
      (:objects cat dog - item  knife - tool  lab outdoors - location)
      (:init (agent-at lab) (at cat lab) ...)
      (:goal (and (photo-taken cat) (at dog outdoors))))

A domain file has (:requirements ...), (:types ...), (:predicates ...) and actions:

    (:action pick-up
      :parameters (?i - item ?l - location)
      :precondition (and (agent-at ?l) (at ?i ?l) (hand-empty) ...)
      :effect (and (holding ?i) (not (hand-empty)) (not (at ?i ?l)) ...))

Rules of the format:
  * ; starts a comment that runs to the end of the line.
  * Whitespace is free. PDDL is case-insensitive: everything is lowercased.
  * (and ...) wraps one or more literals; a single literal may also stand alone.
  * (not ...) is allowed only in effects. A state lists what is true; anything
    not listed is false. So "not dirty" is not a fact you can ask for: you
    declare a predicate for it (clean), as the vacuum domain does.
  * Types may form a hierarchy: (:types cat - animal  animal - object).
    Every type descends from object.

GIVEN, already written: tokenize, parse_tree, typed_list, literals, is_a,
goal_reached, load. Read them; do not rewrite them.
YOURS: parse_problem, parse_domain, ground, successors.

    python -m pytest test_lab2.py
    python lab2.py
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from itertools import product

SUPPORTED_REQUIREMENTS = {":strips", ":typing"}


@dataclass(frozen=True)
class Action:
    """An action schema, or (after ground) one concrete action.

    name    "pick-up"                 or  "pick-up(cat, lab)"
    params  (("?i", "item"), ("?l", "location"))   or  () once grounded
    pre     facts that must all be in the state
    add     facts that become true
    delete  facts that become false
    """
    name: str
    params: tuple[tuple[str, str], ...]
    pre: frozenset[tuple[str, ...]]
    add: frozenset[tuple[str, ...]]
    delete: frozenset[tuple[str, ...]]


@dataclass(frozen=True)
class Domain:
    """name, types {"item": "object", ...}, predicates {"at": (("?i", "item"), ("?l", "location")), ...},
    actions {"pick-up": Action, ...}"""
    name: str
    types: dict[str, str]
    predicates: dict[str, tuple[tuple[str, str], ...]]
    actions: dict[str, Action]


@dataclass(frozen=True)
class Problem:
    """name, domain (the domain's name), objects {"cat": "item", ...},
    init (a state), goal (facts that must all be true)"""
    name: str
    domain: str
    objects: dict[str, str]
    init: frozenset[tuple[str, ...]]
    goal: frozenset[tuple[str, ...]]


# =============================================================== GIVEN ======
# Text to tree, and small readers for the pieces of a tree. Nothing here
# knows what a plan is.

def tokenize(text: str) -> list[str]:
    """Split PDDL text into tokens: "(" and ")" are tokens; everything else is
    split on whitespace. Comments are removed. Everything is lowercased.

    >>> tokenize("(:objects Cat - item) ; the cat\\n(hand-empty)")
    ['(', ':objects', 'cat', '-', 'item', ')', '(', 'hand-empty', ')']
    """
    text = re.sub(r";[^\n]*", "", text).lower()
    return re.findall(r"\(|\)|[^\s()]+", text)


def parse_tree(tokens: list[str]) -> list | str:
    """Turn a token list into nested lists: one list per pair of parentheses,
    a string per word. Linear time. Raises ValueError on unbalanced parentheses.

    >>> parse_tree(["(", "and", "(", "at", "cat", "lab", ")", "(", "hand-empty", ")", ")"])
    ['and', ['at', 'cat', 'lab'], ['hand-empty']]
    """
    def read(i):
        if i >= len(tokens):
            raise ValueError("unbalanced parentheses: missing ')'")
        if tokens[i] == ")":
            raise ValueError("unbalanced parentheses: unexpected ')'")
        if tokens[i] != "(":
            return tokens[i], i + 1
        out, i = [], i + 1
        while i < len(tokens) and tokens[i] != ")":
            node, i = read(i)
            out.append(node)
        if i >= len(tokens):
            raise ValueError("unbalanced parentheses: missing ')'")
        return out, i + 1

    if not tokens:
        raise ValueError("no tokens")
    tree, end = read(0)
    if end != len(tokens):
        raise ValueError("unbalanced parentheses: extra tokens after the expression")
    return tree


def typed_list(tokens: list[str]) -> dict[str, str]:
    """Read PDDL's "name name - type name - type" form into {name: type}.
    Names with no type get the type "object". Order is preserved.

    >>> typed_list(["cat", "dog", "-", "item", "knife", "-", "tool", "x"])
    {'cat': 'item', 'dog': 'item', 'knife': 'tool', 'x': 'object'}
    """
    out, pending = {}, []
    it = iter(tokens)
    for tok in it:
        if tok == "-":
            typ = next(it)
            for name in pending:
                out[name] = typ
            pending = []
        else:
            pending.append(tok)
    for name in pending:
        out[name] = "object"
    return out


def literals(expr: list) -> tuple[frozenset, frozenset]:
    """Read a condition or effect. Returns (positive facts, negated facts).
    `expr` is (and lit lit ...) or a single literal; a literal is (pred args...)
    or (not (pred args...)).

    >>> pos, neg = literals(["and", ["holding", "?i"], ["not", ["hand-empty"]]])
    >>> sorted(pos), sorted(neg)
    ([('holding', '?i')], [('hand-empty',)])
    """
    parts = expr[1:] if expr and expr[0] == "and" else [expr]
    pos, neg = set(), set()
    for p in parts:
        if p[0] == "not":
            neg.add(tuple(p[1]))
        else:
            pos.add(tuple(p))
    return frozenset(pos), frozenset(neg)


def is_a(t: str, target: str, types: dict[str, str]) -> bool:
    """True when type `t` is `target` or descends from it. Every type descends
    from "object", whether or not the file says so.

    >>> is_a("cat", "animal", {"cat": "animal", "animal": "object"})
    True
    >>> is_a("tool", "item", {"item": "object", "tool": "object"})
    False
    """
    while t is not None:
        if t == target:
            return True
        t = types.get(t)
    return target == "object"


def goal_reached(state: frozenset, goal: frozenset) -> bool:
    """True when every goal fact is in the state."""
    return goal <= state


def load(domain_path: str, problem_path: str) -> tuple[Domain, Problem, list[Action]]:
    """Read both files and ground every action. Returns (domain, problem, grounded actions).
    Raises ValueError if the problem was written for a different domain."""
    with open(domain_path) as f:
        domain = parse_domain(f.read())
    with open(problem_path) as f:
        problem = parse_problem(f.read())
    if problem.domain != domain.name:
        raise ValueError(f"problem is for domain {problem.domain!r}, but this is {domain.name!r}")
    actions = [g for a in domain.actions.values() for g in ground(a, problem.objects, domain.types)]
    return domain, problem, actions


# =============================================================== YOURS ======

def parse_problem(text: str) -> Problem:
    """Read a PDDL problem file.

    Raises ValueError if the goal contains (not ...).

    >>> p = parse_problem(open("problem.pddl").read())
    >>> p.name, p.domain, p.objects["knife"]
    ('two-animals', 'workshop', 'tool')
    >>> ("at", "cat", "lab") in p.init, len(p.init)
    (True, 14)
    >>> sorted(p.goal)
    [('at', 'dog', 'outdoors'), ('cut-into-pieces', 'dog'), ('photo-taken', 'cat')]
    """
    tree = parse_tree(tokenize(text))
    name, domain, objects, init, goal = tree[1][1], '', {}, frozenset(), frozenset()
    for section in tree[2:]:
        if section[0] == ':domain':
            domain = section[1]
        elif section[0] == ':objects':
            objects = typed_list(section[1:])
        elif section[0] == ':init':
            init = frozenset(tuple(f) for f in section[1:])
        elif section[0] == ':goal':
            goal, neg = literals(section[1])
            # goals should not be negative
            if neg:
                raise ValueError(f'Negative goals are not supported {sorted(neg)}')
    return Problem(name=name, domain=domain, objects=objects, init=init, goal=goal)

def parse_domain(text: str) -> Domain:
    """Read a PDDL domain file.

    Raises ValueError if a requirement other than :strips or :typing is
    declared, or if a precondition contains (not ...).

    >>> d = parse_domain(open("domain.pddl").read())
    >>> d.name, d.types["tool"], d.predicates["at"]
    ('workshop', 'object', (('?i', 'item'), ('?l', 'location')))
    >>> a = d.actions["pick-up"]
    >>> a.paramsx


    
    (('?i', 'item'), ('?l', 'location'))
    >>> sorted(a.delete)
    [('at', '?i', '?l'), ('clear', '?i'), ('hand-empty',), ('on-surface', '?i')]
    """
    tree = parse_tree(tokenize(text))
    name, types, predicates, actions = tree[1][1], {}, {}, {}

    for section in tree[2:]:
        if section[0] == ':requirements':
            unsupported = set(section[1:]) - SUPPORTED_REQUIREMENTS
            if unsupported:
                raise ValueError(f'Unsupported requirements {sorted(unsupported)}')
        elif section[0] == ':types':
            types = typed_list(section[1:])
        elif section[0] == ':predicates':
            predicates = {p[0]: tuple(typed_list(p[1:]).items()) for p in section[1:]}
        elif section[0] == ':action':
            fields = dict(zip(section[2::2], section[3::2]))
            params = tuple(typed_list(fields[':parameters']).items())
            pre, neg = literals(fields[':precondition'])

            if neg:
                raise ValueError(f'Negative preconditions are not supported {sorted(neg)}')

            add, delete = literals(fields[':effect'])
            actions[section[1]] = Action(section[1], params, pre, add, delete)

    return Domain(name, types, predicates, actions)
    


def ground(action: Action, objects: dict[str, str], types: dict[str, str]) -> list[Action]:
    """Every way of filling the action's parameters with objects of the right
    type (is_a decides: a cat is an animal is an object).

    One Action per combination: name "pick-up(cat, lab)", params (), and every
    ?parameter in pre/add/delete replaced by its object. Symbols that are not
    parameters are left as they are. Objects are tried in the order of `objects`.

    >>> d = parse_domain(open("domain.pddl").read())
    >>> objects = {"cat": "item", "lab": "location", "outdoors": "location"}
    >>> [a.name for a in ground(d.actions["pick-up"], objects, d.types)]
    ['pick-up(cat, lab)', 'pick-up(cat, outdoors)']
    """
    candidates = [[o for o, t in objects.items() if is_a(t, ptype, types)] for _, ptype in action.params]
    
    grounded = []
    for combo in product(*candidates):
        binding = dict(zip([p for p, _ in action.params], combo))
        sub = lambda facts: frozenset(tuple(binding.get(x, x) for x in f) for f in facts)
        name = f'{action.name}({", ".join(combo)})'
        grounded.append(Action(name, (), sub(action.pre), sub(action.add), sub(action.delete)))

    return grounded


def successors(state: frozenset, actions: list[Action]) -> dict[str, frozenset]:
    """Every grounded action that applies to `state`, and the state it leads to.

    An action applies when all of its preconditions are in the state. The next
    state is the state minus what the action deletes, plus what it adds. Actions
    that leave the state unchanged are left out, as in Lab 1.

    >>> domain, problem, actions = load("vacuum-domain.pddl", "vacuum-tiny.pddl")
    >>> sorted(successors(problem.init, actions))
    ['move(c11, c12)', 'move(c11, c21)']
    """
    out = {}
    for a in actions:
        if a.pre <= state:
            nxt = (state - a.delete) | a.add
            if nxt != state:
                out[a.name] = nxt

    return out


if __name__ == "__main__":
    domain, problem, actions = load("domain.pddl", "problem.pddl")
    print(f"{problem.name}: {len(problem.objects)} objects, {len(problem.init)} facts, "
          f"{len(domain.actions)} action schemas -> {len(actions)} grounded actions")
    for name in successors(problem.init, actions):
        print(" ", name)
