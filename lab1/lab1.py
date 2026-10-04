"""
ECS759P — Lab 1: Python review, in a small world
=================================================

A robot vacuum lives in a grid. Some cells are dirty. It can move N/E/S/W or SUCK.

Map: one string per row, always surrounded by walls.

    #  wall      .  clean      *  dirty      A  robot      @  robot on a dirty cell

Positions are (row, col) tuples, counting from the top-left corner.

    python -m pytest test_lab1.py     run the tests
    python lab1.py                    run the demo at the bottom
"""


MOVES = {"N": (-1, 0), "E": (0, 1), "S": (1, 0), "W": (0, -1)}

WORLD = [
    "#######",
    "#A..*.#",
    "#.##..#",
    "#*...*#",
    "#######",
]

def validate_wall_boundary(world):
    valid = True
    valid &= all(ch == '#' for ch in world[0])
    valid &= all(ch == '#' for ch in world[-1])
    valid &= all(line[0] == '#' and line[-1] == '#' for line in world)

    if not valid:
        raise Exception('World is not surrounded by walls')


def parse_world(rows):
    """Read a map. Returns (walls, dirty, robot): two sets of positions and one position.

    >>> walls, dirty, robot = parse_world(["####", "#A*#", "####"])
    >>> robot, dirty, (0, 0) in walls
    ((1, 1), {(1, 2)}, True)
    """
    validate_wall_boundary(rows)

    walls, dirty, robot = set(), set(), None
    for r, a_row in enumerate(rows):
        for c, ch in enumerate(a_row):
            if ch == '#':
                walls.add((r, c))
            elif ch in '*@':
                dirty.add((r, c))
            elif ch in 'A@':
                robot = (r, c)
            elif ch != '.':
                raise Exception(f'Invalid character "{ch}" in world')
    
    return walls, dirty, robot


def render(walls, dirty, robot):
    """The opposite of parse_world: turn a world back into a printable map.

    Maps are surrounded by walls, so the height is the largest row in walls, plus one.

    >>> print(render(*parse_world(["####", "#A*#", "####"])))
    ####
    #A*#
    ####
    """
    height = max(r for r, c in walls) + 1
    width = max(c for r,c in walls) + 1
    lines = []

    for r in range(height):
        line = ''
        for c in range(width):
            if (r,c) in walls:
                line += '#'
            elif (r,c) == robot:
                line += '@' if (r,c) in dirty else 'A'
            elif (r,c) in dirty:
                line += '*'
            else:
                line += '.'
        lines.append(line)

    return '\n'.join(lines)


def step(walls, dirty, robot, action):
    """What the world looks like after one action. Returns (dirty, robot).

    Moving into a wall does nothing. SUCK cleans the robot's cell.
    Do not change the `dirty` you were given — return a new set.

    >>> walls, dirty, robot = parse_world(["####", "#A*#", "####"])
    >>> step(walls, dirty, robot, "E")
    ({(1, 2)}, (1, 2))
    >>> step(walls, dirty, robot, "N")
    ({(1, 2)}, (1, 1))
    """
    
    if action == 'SUCK':
        return dirty - {robot}, robot

    if action not in MOVES:
        raise Exception('Invalid action "{action}"')

    dr, dc = MOVES[action]
    new_robot = (robot[0] + dr, robot[1] + dc)
    if new_robot in walls:
        return dirty, robot

    return dirty, new_robot


def run(walls, dirty, robot, actions):
    """Apply the actions one after another. Returns the list of (dirty, robot)
    after each action — so the list is as long as `actions`.

    >>> walls, dirty, robot = parse_world(["####", "#A*#", "####"])
    >>> run(walls, dirty, robot, ["E", "SUCK"])
    [({(1, 2)}, (1, 2)), (set(), (1, 2))]
    """

    history = []
    for action in actions:
        dirty, robot = step(walls, dirty, robot, action)
        history.append((dirty, robot))

    return history


if __name__ == "__main__":
    walls, dirty, robot = parse_world(WORLD)
    print(render(walls, dirty, robot), "\n")
    for dirty, robot in run(walls, dirty, robot, ["E", "E", "E", "SUCK"]):
        print(render(walls, dirty, robot), "\n")
