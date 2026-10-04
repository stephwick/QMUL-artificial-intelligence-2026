"""Tests for Lab 1.   python -m pytest test_lab1.py"""

from lab1 import WORLD, parse_world, render, run, step

ROOM = [
    "#####",
    "#A.*#",
    "#.#.#",
    "#####",
]


def test_parse_world():
    # placeholder test. This is NOT the correct implementation.
    world = parse_world(ROOM)    
    assert world


def test_render_undoes_parse():
    # placeholder test. This is NOT the correct implementation.
    world = parse_world(ROOM)
    assert word

# MORE TESTS YOU COME UP WITH
