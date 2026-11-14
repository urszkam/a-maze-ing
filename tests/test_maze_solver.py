import pytest

from typing import TypeAlias

import numpy as np

from src.service.maze_generator.maze_solver import MazeSolver


Node: TypeAlias = tuple[int, int]

@pytest.fixture
def solver() -> MazeSolver:
    return MazeSolver()

def get_maze() -> np.ndarray:
    """
    Generates maze with no internal walls:

    Returns:
     ___
    |   |
    |___|
    """
    matrix = [
        [9, 3],
        [12, 6]
    ]
    return np.array(matrix)


def test_find_shortest_path_start(solver: MazeSolver) -> None:
    start: Node = (0,1)
    end: Node = (0,0)

    path: list[Node] = solver.find_shortest_path(get_maze(), start, end)

    assert path[0] == start
    assert path[0] != end


def test_find_shortest_path_end(solver: MazeSolver) -> None:
    start: Node = (0,1)
    end: Node = (0,0)

    path: list[Node] = solver.find_shortest_path(get_maze(), start, end)

    assert path[-1] == end
    assert path[-1] != start

@pytest.mark.parametrize(
    "start, end, expected", [
        [(0, 0), (0, 1), 2],
        [(0, 1), (1, 0), 3],
    ])
def test_find_shortest_path_node_count(
    solver: MazeSolver,
    start: Node, end: Node, expected: int) -> None:

    path: list[Node] = solver.find_shortest_path(get_maze(), start, end)

    assert len(path) == expected

@pytest.mark.parametrize(
    "start, end, expected", [
        [(0, 0), (0, 1), [[(0, 0), (0, 1)]]],
        [(1, 1), (0, 0), [
            [(1, 1), (1, 0), (0, 0)], [(1, 1), (0, 1), (0, 0)]
            ]],
        [(0, 1), (0, 0), [[(0, 1), (0, 0)]]]
    ])
def test_find_shortest_path_nodes(
    solver: MazeSolver,
    start: Node, end: Node, expected: list[Node]) -> None:
    path: list[Node] = solver.find_shortest_path(get_maze(), start, end)

    assert path in expected
