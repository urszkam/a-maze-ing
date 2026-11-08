"""Prepare maze grids and apply passages selected by an algorithm."""

from __future__ import annotations

import numpy as np

from src.constants import LOGO42, Dir
from .algorithms import AlgorithmType, MazeAlgorithm


class MazeGenerator:
    """Manage a singleton maze, its configuration and selected algorithm."""
    _instance: MazeGenerator | None = None
    _initialized: bool = False

    def __new__(
            cls, config: dict[str, tuple[int, int] | bool | str]
            ) -> MazeGenerator:
        """Create singleton maze generator instance.

        Args:
            config: Maze settings passed to the initializer.

        Returns:
            The existing or newly created instance.
        """
        if cls._instance is None:
            cls._instance = super().__new__(cls)

        return cls._instance

    def __init__(
            self, config: dict[str, tuple[int, int] | bool | str]) -> None:
        """Initialize the maze generator instance.

        Args:
            config: Maze settings, including
                dimensions and entry and exit coordinates.
        """
        if self._initialized:
            return
        self._maze = None
        self._config = config
        self.register_algorithm()
        self._initialized = True

    @property
    def algorithm_name(self) -> str:
        """Return the selected algorithm name, or an em dash if none is set."""
        if self._maze_algorithm is None:
            return "—"
        return str(self._maze_algorithm.value)

    @property
    def entry(self) -> tuple[int, int]:
        """Return the configured entry coordinates as (row, column)."""
        return self._config["entry"]

    @property
    def exit(self) -> tuple[int, int]:
        """Return the configured exit coordinates as (row, column)."""
        return self._config["exit"]

    @property
    def maze(self) -> np.ndarray | None:
        """Return the stored maze array, or None before generation."""
        return self._maze

    def register_algorithm(
            self,
            algorithm: AlgorithmType = AlgorithmType.KRUSKAL) -> None:
        """Select the initial algorithm.

        Args:
            algorithm: Initial choice, used only when no algorithm is selected.
        """
        self._maze_algorithm = algorithm

    def next_algorithm(self) -> None:
        """Select the next available algorithm."""
        self._maze_algorithm = self._maze_algorithm.get_next()

    def _insert_42(self, matrix: np.ndarray) -> None:
        """Place the 42 logo cells in the initial maze as -1.

        Args:
            matrix: initial 2d array filled with number 15.

        Raises:
            Exception: When config area is not enough for logo and proper maze.
        """
        logo42 = np.array(LOGO42)
        logo_rows, logo_cols = logo42.shape
        matrix_rows, matrix_cols = matrix.shape

        if logo_rows + 1 >= matrix_rows or logo_cols + 1 >= matrix_cols:
            raise Exception("Insufficient area for maze generation.")

        mid_row: int = matrix_rows // 2
        mid_col: int = matrix_cols // 2

        row_offset: int = logo_rows // 2
        col_offset: int = logo_cols // 2

        matrix[
            mid_row - row_offset: mid_row + row_offset + 1,
            mid_col - col_offset: mid_col + col_offset + 1
        ] = np.where(logo42 == 1, -1, 15)

    def _get_logo_coords(self, matrix: np.ndarray) -> list[tuple[int, int]]:
        """Collect coordinates of cells marked as part of the logo.

        Args:
            matrix: Grid in which logo cells have the value -1.

        Returns:
            Logo coordinates as (row, column) pairs.
        """
        return [tuple(coords) for coords in np.argwhere(matrix == -1)]

    def _open_maze_walls(
            self,
            maze: np.ndarray,
            open_edges: list[tuple[tuple[int, int], tuple[int, int]]]
            ) -> np.ndarray:
        """Remove both sides of each passage's shared wall in place.

        Args:
            maze: Grid of wall bitmasks with the relevant walls still closed.
            open_edges: Unique adjacent cell pairs ordered toward increasing
                column or increasing row.

        Returns:
            The same maze array with passage walls removed.
        """
        for neighbor_nodes in open_edges:
            match (neighbor_nodes):
                case ((x1, y1), (x2, y2)) if x1 == x2:
                    maze[x1][y1] -= Dir.E
                    maze[x2][y2] -= Dir.W
                case ((x1, y1), (x2, y2)) if y1 == y2:
                    maze[x1][y1] -= Dir.S
                    maze[x2][y2] -= Dir.N

        return maze

    def generate_maze(self) -> np.ndarray:
        """Generate a maze using an algorithm.

        Returns:
            2d maze array with binary walls representation.
        """
        matrix: np.ndarray = np.full(
            (self._config["height"], self._config["width"]), 15
        )

        self._insert_42(matrix)
        logo_coords: list[tuple[int, int]] = self._get_logo_coords(matrix)

        registered_algorithm: MazeAlgorithm = self._maze_algorithm.algorithm
        open_edges = registered_algorithm.generate_open_edges(
            matrix.shape, logo_coords)

        maze = self._open_maze_walls(matrix, open_edges)
        self._maze = np.where(matrix == -1, 15, maze)

        return self._maze

    def generate_path(self) -> list[tuple[int, int]]:
        """Return a placeholder path when a maze has been generated.

        Returns:
            An empty list before generation, otherwise a fixed example path.
            Actual pathfinding is not implemented yet.
        """
        path: list[tuple[int, int]] = []

        if self._maze is None:
            return path

        # TODO generate path

        placeholder = [(0, 0), (0, 1), (1, 1), (1, 2), (1, 3), (0, 3), (0, 2)]

        return placeholder
