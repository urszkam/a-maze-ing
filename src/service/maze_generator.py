"""Prepare maze grids and apply passages selected by an algorithm."""

from __future__ import annotations

import numpy as np
from typing import Iterator, TypeAlias

from src.constants import LOGO42, Dir
from .algorithms import AlgorithmType, MazeAlgorithm


Node: TypeAlias = tuple[int, int]
Edge: TypeAlias = tuple[Node, Node]


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
        self._logo_coords: list[Node] = []
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
    def entry(self) -> Node:
        """Return the configured entry coordinates as (row, column)."""
        return self._config.entry

    @property
    def exit(self) -> Node:
        """Return the configured exit coordinates as (row, column)."""
        return self._config.exit

    @property
    def maze(self) -> np.ndarray | None:
        """Return the stored maze array, or None before generation."""
        return self._maze

    @property
    def logo_coords(self) -> list[Node]:
        """Return logo coordinates independently of the current wall masks."""
        return self._logo_coords

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

    def _get_logo_coords(self, matrix: np.ndarray) -> list[Node]:
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
            open_edges: list[Edge]
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
                    maze[x1][y1] &= ~Dir.E
                    maze[x2][y2] &= ~Dir.W
                case ((x1, y1), (x2, y2)) if y1 == y2:
                    maze[x1][y1] &= ~Dir.S
                    maze[x2][y2] &= ~Dir.N

        return maze

    def generate_maze(self) -> np.ndarray:
        """Generate a maze using an algorithm.

        Returns:
            2d maze array with binary walls representation.
        """
        for maze in self.generate_maze_frames():
            self._maze = maze

        if self._maze is None:
            raise RuntimeError("Maze generation produced no frames.")

        return self._maze

    def generate_maze_frames(self) -> Iterator[np.ndarray]:
        """Return the maze step by step, with at most 30 animation frames.

        Yields:
            Separate maze snapshots, ending with the completed maze.
        """
        matrix: np.ndarray = np.full(
            (self._config.height, self._config.width), 15
        )
        self._insert_42(matrix)
        self._logo_coords = self._get_logo_coords(matrix)

        registered_algorithm: MazeAlgorithm = self._maze_algorithm.algorithm
        open_edges = registered_algorithm.generate_open_edges(
            matrix.shape, self._logo_coords)
        
        matrix[matrix == -1] = 15
        yield matrix.copy()

        frame_count = min(
            30, len(open_edges),
            max(1, (matrix.size - len(self._logo_coords) + 4) // 5)
        )
        for frame in range(frame_count):
            first_edge = frame * len(open_edges) // frame_count
            last_edge = (frame + 1) * len(open_edges) // frame_count
            self._open_maze_walls(matrix, open_edges[first_edge:last_edge])
            yield matrix.copy()

        self._maze = matrix.copy()

    def generate_path(self) -> list[Node]:
        """

        Returns:

        """
        path: list[Node] = []

        if self._maze is None:
            return path

        # TODO generate path

        placeholder = [(0, 0), (0, 1), (1, 1), (1, 2), (1, 3), (0, 3), (0, 2)]

        return placeholder
