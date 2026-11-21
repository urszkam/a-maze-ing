import numpy as np
import pytest

from typing import TypeAlias

from src.constants import Dir
from src.service.maze_generator.maze import Maze


Node: TypeAlias = tuple[int, int]


@pytest.fixture
def maze() -> Maze:
    """ Path: (0, 0) -> (0, 1) -> (1, 1) -> (1, 0)
    Walls:
     ____
    |_ |_|
    |__|_|
    """

    walls = np.array([[13, 3, 15], [13, 6, 15]])
    return Maze(
        walls,
        logo_coords=[(0, 2), (1, 2)],
        path=[(0, 0), (0, 1), (1, 1), (1, 0)],
        entry=(0, 0),
        exit=(1, 0),
    )


def test_maze_metadata(maze: Maze) -> None:
    assert maze.entry == (0, 0)
    assert maze.exit == (1, 0)
    assert maze.logo_coords == [(0, 2), (1, 2)]
    np.testing.assert_array_equal(
        maze.walls, [[13, 3, 15], [13, 6, 15]]
    )


@pytest.mark.parametrize(
    "cell, expected",
    [
        ((0, 0), (True, False, False, True)),
        ((0, 1), (False, False, False, True)),
        ((1, 0), (False, True, False, True)),
        ((0, 2), (False, False, True, False)),
        ((1, 2), (False, False, True, False)),
    ],
)
def test_cell_roles(
    maze: Maze,
    cell: Node,
    expected: tuple[bool, bool, bool, bool],
) -> None:
    assert (
        maze.is_entry(*cell),
        maze.is_exit(*cell),
        maze.is_logo(*cell),
        maze.is_path(*cell),
    ) == expected


@pytest.mark.parametrize("row, col, expected", [(0, 1, 3), (1, 0, 13)])
def test_wall_bitmask(maze: Maze, row: int, col: int, expected: int) -> None:
    wall = maze.get_wall(row, col)
    assert wall == expected


@pytest.mark.parametrize(
    "cell, expected",
    [
        ((0, 0), Dir.E),
        ((0, 1), Dir.W | Dir.S),
        ((1, 1), Dir.N | Dir.W),
        ((1, 0), Dir.E),
        ((0, 2), None),
    ],
)
def test_path_cell_bitmask(
    maze: Maze, cell: Node, expected: int | None
) -> None:
    assert maze.get_path_cell_bitmask(*cell) == expected


def test_full_path_bitmasks(maze: Maze) -> None:
    assert maze.get_full_path_bitmask() == [2, 12, 9, 2]
