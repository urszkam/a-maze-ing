"""Prepare maze grids and apply passages selected by an algorithm."""

from __future__ import annotations

import numpy as np
from typing import Iterator, TypeAlias

from src.constants import LOGO42, Dir
from .algorithms import AlgorithmType, MazeAlgorithm
from src.service.parse_config import MazeConfig
from .maze_solver import MazeSolver

Node: TypeAlias = tuple[int, int]
Edge: TypeAlias = tuple[Node, Node]


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
            Previous path cell, or None if the cell is not on the path or is
            the first path cell.
        """
        idx = self._path.index((row, col))

        return self._path[idx - 1] if idx > 0 else None

    def _next_path(self, row: int, col: int) -> Node | None:
        """Return the next cell on the path.

        Args:
            row: Row index of the cell.
            col: Column index of the cell.

        Returns:
            Next path cell, or None if the cell is not on the path or is the
            last path cell.
        """
        idx = self._path.index((row, col))

        return self._path[idx + 1] if idx + 1 < len(self._path) else None

    def get_path_cell_bitmask(self, row: int, col: int) -> int | None:
        """
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
        """
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

    @property
    def walls(self) -> np.ndarray:
        """Return the wall bitmask matrix."""
        return self._walls


class MazeGenerator:
    """Manage a singleton maze, its configuration and selected algorithm."""
    _instance: MazeGenerator | None = None
    _initialized: bool = False

    def __new__(cls, config: MazeConfig) -> MazeGenerator:
        """Create singleton maze generator instance.

        Args:
            config: Maze settings class passed to the initializer.

        Returns:
            The existing or newly created instance.
        """
        if cls._instance is None:
            cls._instance = super().__new__(cls)

        return cls._instance

    def __init__(self, config: MazeConfig) -> None:
        """Initialize the maze generator instance.

        Args:
            config: Maze settings, including
                dimensions and entry and exit coordinates.
        """
        if self._initialized:
            return

        self._maze: Maze | None = None
        self._solver = MazeSolver()
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
        col, row = self._config.entry

        return (row, col)

    @property
    def exit(self) -> Node:
        """Return the configured exit coordinates as (row, column)."""
        col, row = self._config.exit

        return (row, col)

    @property
    def maze(self) -> Maze | None:
        """Return the stored maze, or None before generation."""
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
            RuntimeError: When config area is not enough for logo and proper maze.
        """
        logo42 = np.array(LOGO42)
        logo_rows, logo_cols = logo42.shape
        matrix_rows, matrix_cols = matrix.shape

        if logo_rows + 1 >= matrix_rows or logo_cols + 1 >= matrix_cols:
            raise RuntimeError("Insufficient area for maze generation.")

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
                case ((row1, col1), (row2, col2)) if row1 == row2:
                    maze[row1][col1] &= ~Dir.E
                    maze[row2][col2] &= ~Dir.W
                case ((row1, col1), (row2, col2)) if col1 == col2:
                    maze[row1][col1] &= ~Dir.S
                    maze[row2][col2] &= ~Dir.N

        return maze

    def generate_maze(self) -> Maze:
        """Generate a maze using an algorithm.

        Returns:
            2d maze array with binary walls representation.
        """
        maze: np.ndarray | None = None

        for generated_maze in self.generate_maze_frames():
            maze = generated_maze

        if maze is None:
            raise RuntimeError("Maze generation produced no frames.")

        return self.store_maze(maze)

    def store_maze(self, maze: np.ndarray) -> Maze:
        """Store a completed maze from its final wall matrix.

        Args:
            maze: Final maze wall matrix.

        Returns:
            Maze instance storing the completed maze.
        """
        path: list[Node] = self.generate_path(maze)
        self._maze = Maze(maze, self._logo_coords, path,
                          self.entry, self.exit)

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
        if not self._logo_coords:
            self._logo_coords = self._get_logo_coords(matrix)

        registered_algorithm: MazeAlgorithm = self._maze_algorithm.algorithm
        open_edges = registered_algorithm.generate_open_edges(
            shape=matrix.shape,
            logo_coords=self._logo_coords,
            is_perfect=self._config.perfect)

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

    def generate_path(self, walls: np.ndarray) -> list[Node]:
        """ Generates the shortest path from entry to exit.

        Returns:
            List of path coordinates
        """
        return self._solver.find_shortest_path(
            walls, self.entry, self.exit
        )
