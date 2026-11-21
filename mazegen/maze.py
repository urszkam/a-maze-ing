"""Represent a maze and provide access to its cells and path."""

from __future__ import annotations

from typing import TypeAlias

import numpy as np

from .directions import Dir

Node: TypeAlias = tuple[int, int]


class Maze:
    """Store the completed maze and its derived information.

    Attributes:
        _walls: Wall bitmask for every cell in the maze.
        _logo_coords: Coordinates of the 42 logo.
        _path: Coordinates forming the path from entry to exit.
        _entry: Entry cell coordinates.
        _exit: Exit cell coordinates.
    """

    def __init__(self, maze_walls: np.ndarray,
                 logo_coords: list[Node], path: list[Node],
                 entry: Node, exit: Node) -> None:
        """Initialize a completed maze.

        Args:
            maze_walls: Array containing the wall bitmask for each cell.
            logo_coords: Coordinates occupied by the 42 logo.
            path: Coordinates forming the path from entry to exit.
            entry: Entry cell coordinates.
            exit: Exit cell coordinates.
        """
        self._walls: np.ndarray = maze_walls
        self._logo_coords: list[Node] = logo_coords
        self._path: list[Node] = path
        self._entry: Node = entry
        self._exit: Node = exit

    @property
    def entry(self) -> Node:
        """Return the entry cell coordinates.

        Returns:
            Entry cell coordinates.
        """
        return self._entry

    @property
    def exit(self) -> Node:
        """Return the exit cell coordinates.

        Returns:
            Exit cell coordinates.
        """
        return self._exit

    @property
    def logo_coords(self) -> list[Node]:
        """Return the coordinates occupied by the 42 logo.

        Returns:
            Coordinates occupied by the 42 logo.
        """
        return self._logo_coords

    @property
    def path(self) -> list[Node]:
        """Return the coordinates occupied by the path.

        Returns:
            Coordinates occupied by the path.
        """
        return self._path

    @property
    def walls(self) -> np.ndarray:
        """Return the wall bitmask matrix.

        Returns:
            Bitmask matrix representing walls in the maze.
        """
        return self._walls

    def is_logo(self, row: int, col: int) -> bool:
        """Check whether a cell belongs to the 42 logo.

        Args:
            row: Row index of the cell.
            col: Column index of the cell.

        Returns:
            True if the cell belongs to the 42 logo, otherwise False.
        """
        return (row, col) in self._logo_coords

    def is_entry(self, row: int, col: int) -> bool:
        """Check whether a given coordinates are entry.

        Args:
            row: Row index of the cell.
            col: Column index of the cell.

        Returns:
            True if it is the entry, otherwise False.
        """
        return (row, col) == self._entry

    def is_exit(self, row: int, col: int) -> bool:
        """Check whether the given coordinates are exit.

        Args:
            row: Row index of the cell.
            col: Column index of the cell.

        Returns:
            True if it is the exit, otherwise False.
        """
        return (row, col) == self._exit

    def is_path(self, row: int, col: int) -> bool:
        """Check whether a cell belongs to the entry-to-exit path.

        Args:
            row: Row index of the cell.
            col: Column index of the cell.

        Returns:
            True if the cell belongs to the path, otherwise False.
        """
        return (row, col) in self._path

    def _prev_path(self, row: int, col: int) -> Node | None:
        """Return the previous cell on the path.

        Args:
            row: Row index of the cell.
            col: Column index of the cell.

        Returns:
            Previous path cell, or None for the first path cell.

        Raises:
            ValueError: If the cell is not on the path.
        """
        idx = self._path.index((row, col))

        return self._path[idx - 1] if idx > 0 else None

    def _next_path(self, row: int, col: int) -> Node | None:
        """Return the next cell on the path.

        Args:
            row: Row index of the cell.
            col: Column index of the cell.

        Returns:
            Next path cell, or None for the last path cell.

        Raises:
            ValueError: If the cell is not on the path.
        """
        idx = self._path.index((row, col))

        return self._path[idx + 1] if idx + 1 < len(self._path) else None

    def get_path_cell_bitmask(self, row: int, col: int) -> int | None:
        """Compute directions connecting a cell to its path neighbors.

        Args:
            row: Row index of the cell.
            col: Column index of the cell.

        Returns:
            Direction bitmask for open passages to adjacent path cells,
            or None if the cell is not on the path.
        """
        if not self.is_path(row, col):
            return None

        next = self._next_path(row, col)
        prev = self._prev_path(row, col)

        path_bitmask = 0

        for cell in (prev, next):
            if cell is None:
                continue

            cell_row, cell_col = cell
            if cell_row > row:
                direction = Dir.S
            elif cell_row < row:
                direction = Dir.N
            elif cell_col > col:
                direction = Dir.E
            else:
                direction = Dir.W

            if not self._walls[row][col] & direction:
                path_bitmask |= direction

        return path_bitmask

    def get_full_path_bitmask(self) -> list[int]:
        """Return cell direction bitmasks in path order.

        Returns:
            Bitmasks from entry to exit, or an empty list for an empty path.
        """
        if not self._path:
            return []

        return [
            bitmask
            for row, col in self._path
            if (bitmask := self.get_path_cell_bitmask(row, col)) is not None
        ]

    def get_wall(self, row: int, col: int) -> int:
        """Return the wall bitmask for a cell.

        Args:
            row: Row index of the cell.
            col: Column index of the cell.

        Returns:
            Integer bitmask representing the cell's walls.
        """
        return int(self._walls[row][col])
