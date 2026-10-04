"""Drawing helpers for the Lab 2 notebook. Given; nothing to write here."""

from collections import deque

import matplotlib.pyplot as plt
import networkx as nx

from lab2 import goal_reached, successors


def explore(init, actions, cap=None):
    """Every state reachable from init, as a graph. Edges carry the action name;
    each node carries "depth", the fewest actions needed to reach it.
    Stops after `cap` states if a cap is given."""
    G, q = nx.DiGraph(), deque([init])
    G.add_node(init, depth=0)
    while q:
        s = q.popleft()
        for name, s2 in successors(s, actions).items():
            if s2 not in G:
                G.add_node(s2, depth=G.nodes[s]["depth"] + 1)
                q.append(s2)
                if cap and G.number_of_nodes() >= cap:
                    G.add_edge(s, s2, action=name)
                    return G
            G.add_edge(s, s2, action=name)
    return G


# ------------------------------------------------------------ vacuum world ---

def _room(state):
    """A vacuum state drawn as in Lab 1: A robot, * dirt, @ robot on dirt, . clean."""
    robot = next(f[1] for f in state if f[0] == "robot-at")
    dirty = {f[1] for f in state if f[0] == "dirty"}

    def ch(c):
        return ("@" if c in dirty else "A") if c == robot else "*" if c in dirty else "."
    return "\n".join("".join(ch(f"c{r}{c}") for c in "123") for r in "12")


def _vacuum_layout(G, goal):
    """One block per set of dirty cells, blocks left to right by goal facts true;
    inside a block the node sits where the robot is in the room."""
    def dirty(s):
        return tuple(sorted(f[1] for f in s if f[0] == "dirty"))

    def progress(s):
        return len(goal & s)

    columns = {}
    for s in G:
        columns.setdefault(progress(s), set()).add(dirty(s))
    shelf = {p: {d: i - (len(ds) - 1) / 2 for i, d in enumerate(sorted(ds, reverse=True))}
             for p, ds in columns.items()}
    low = min(columns)
    pos = {}
    for s in G:
        robot = next(f[1] for f in s if f[0] == "robot-at")
        r, c = int(robot[1]), int(robot[2])
        pos[s] = (c + 5 * (progress(s) - low), -r - 3.5 * shelf[progress(s)][dirty(s)])
    return pos


def draw_vacuum(G, goal):
    pos = _vacuum_layout(G, goal)
    plt.figure(figsize=(14, 6.5))
    move = [e for e in G.edges if G.edges[e]["action"].startswith("move")]
    suck = [e for e in G.edges if G.edges[e]["action"].startswith("suck")]
    nx.draw_networkx_edges(G, pos, edgelist=move, edge_color="silver", arrows=False, width=1.5)
    nx.draw_networkx_edges(G, pos, edgelist=suck, edge_color="tab:orange", width=2, arrowsize=18,
                           node_size=1500, node_shape="s", connectionstyle="arc3,rad=0.15")
    colors = ["#a8e6a1" if goal_reached(s, goal) else "white" for s in G]
    nx.draw_networkx_nodes(G, pos, node_color=colors, node_size=1500, edgecolors="gray", node_shape="s")
    nx.draw_networkx_labels(G, pos, {s: _room(s) for s in G}, font_family="monospace", font_size=10)
    plt.title("each block is the room;  gray = move,  orange = suck,  green = goal reached")
    plt.axis("off")
    plt.tight_layout()


# ------------------------------------------------------------ blocks world ---

def _stacks(state):
    """A blocks state as text: towers side by side, held block in brackets on top."""
    on = {x: y for (_, x, y) in (f for f in state if f[0] == "on")}
    above = {y: x for x, y in on.items()}
    towers = []
    for base in sorted(f[1] for f in state if f[0] == "on-table"):
        t, x = [base], base
        while x in above:
            x = above[x]
            t.append(x)
        towers.append(t)
    h = max((len(t) for t in towers), default=0)
    lines = [" ".join((t[r].upper() if len(t) > r else " ") for t in towers) for r in range(h - 1, -1, -1)]
    held = next((f[1] for f in state if f[0] == "holding"), None)
    if held:
        lines.insert(0, f"[{held.upper()}]")
    return "\n".join(lines)


def draw_blocks(G, init, goal):
    """Columns are distance from the start; the start is orange, goal states green."""
    columns = {}
    for s in G:
        columns.setdefault(G.nodes[s]["depth"], []).append(s)
    pos = {}
    for d, nodes in columns.items():
        nodes.sort(key=_stacks)
        for i, s in enumerate(nodes):
            pos[s] = (d, (len(nodes) - 1) / 2 - i)
    plt.figure(figsize=(15, 7))
    nx.draw_networkx_edges(G, pos, edge_color="silver", arrows=False, width=1.2)
    colors = ["#a8e6a1" if goal_reached(s, goal) else ("#ffe8cc" if s == init else "white") for s in G]
    nx.draw_networkx_nodes(G, pos, node_color=colors, node_size=2300, edgecolors="gray", node_shape="s")
    nx.draw_networkx_labels(G, pos, {s: _stacks(s) for s in G}, font_family="monospace", font_size=9)
    top = max(len(v) for v in columns.values()) / 2 + 0.7
    for d in columns:
        plt.text(d, top, f"{d} actions", ha="center", fontsize=11, color="gray")
    plt.axis("off")
    plt.tight_layout()


# --------------------------------------------------------------- any world ---

def draw_cloud(G, init, goal, title=""):
    """Every state as a dot. Start orange, goal states green. No labels: too many.
    Layout takes a few seconds per thousand states."""
    pos = nx.spring_layout(G, seed=0, iterations=40)
    plt.figure(figsize=(9, 7))
    nx.draw_networkx_edges(G, pos, edge_color="silver", alpha=0.4, width=0.5, arrows=False)
    colors = ["#2a9d8f" if goal_reached(s, goal) else ("#e76f51" if s == init else "#264653") for s in G]
    size = 30 if G.number_of_nodes() < 500 else 6
    nx.draw_networkx_nodes(G, pos, node_color=colors, node_size=size)
    plt.title(f"{title}{G.number_of_nodes()} states, {G.number_of_edges()} transitions")
    plt.axis("off")


def workshop_problem(n_items):
    """A workshop problem file with n items (1 to 6), as text."""
    items = ["cat", "dog", "bird", "frog", "deer", "horse"][:n_items]
    init = ["(agent-at lab) (hand-empty)",
            "(tool-at knife lab) (can-cut knife)",
            "(tool-at dslr lab) (can-photo dslr)"]
    init += [f"(at {i} lab) (whole {i}) (clear {i}) (on-surface {i})" for i in items]
    return (f"(define (problem items-{n_items})\n"
            f"  (:domain workshop)\n"
            f"  (:objects {' '.join(items)} - item  knife dslr - tool  lab outdoors - location)\n"
            f"  (:init\n    " + "\n    ".join(init) + ")\n"
            f"  (:goal (and (photo-taken {items[0]}) (cut-into-pieces {items[-1]}) (at {items[-1]} outdoors))))\n")
