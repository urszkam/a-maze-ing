"""Prepare maze grids and apply passages selected by an algorithm."""

from __future__ import annotations

import numpy as np
from typing import Iterator, TypeAlias
from collections import deque

from src.constants import LOGO42, Dir
from .algorithms import AlgorithmType, MazeAlgorithm
from src.parse_config import MazeConfig
from .maze_solver import MazeSolver

Node: TypeAlias = tuple[int, int]
Edge: TypeAlias = tuple[Node, Node]


class MazeGenerator:
    """Manage a singleton maze, its configuration and selected algorithm."""
    _instance: MazeGenerator | None = None
    _initialized: bool = False

    def __new__(cls, config: MazeConfig) -> MazeGenerator:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(
            self, config: MazeConfig) -> None:
        if self._initialized:
            return
        self._maze = None
        self._logo_coords: list[Node] = []
        self._config = config
        self.register_algorithm()
        self._initialized = True

    @property
    def algorithm_name(self) -> str:
        if self._maze_algorithm is None:
            return "—"
        return str(self._maze_algorithm.value)

    @property
    def entry(self) -> Node:
        x, y = self._config.entry
        return (y, x)

    @property
    def exit(self) -> Node:
        x, y = self._config.exit
        return (y, x)

    @property
    def maze(self) -> np.ndarray | None:
        return self._maze

    @property
    def logo_coords(self) -> list[Node]:
        return self._logo_coords

    def register_algorithm(
            self,
            algorithm: AlgorithmType = AlgorithmType.KRUSKAL) -> None:
        self._maze_algorithm = algorithm

    def next_algorithm(self) -> None:
        self._maze_algorithm = self._maze_algorithm.get_next()

    def _insert_42(self, matrix: np.ndarray) -> None:
        """Place the 42 logo cells using the exact pattern mask (1 = wall/blocked, 0 = open)."""
        logo42 = np.array(LOGO42)
        logo_rows, logo_cols = logo42.shape
        matrix_rows, matrix_cols = matrix.shape

        if logo_rows + 1 >= matrix_rows or logo_cols + 1 >= matrix_cols:
            raise Exception("Insufficient area for maze generation.")

        mid_row: int = matrix_rows // 2
        mid_col: int = matrix_cols // 2

        row_offset: int = logo_rows // 2
        col_offset: int = logo_cols // 2

        # Only mark cells as blocked (-1) where the logo pattern has a 1
        for r in range(logo_rows):
            for c in range(logo_cols):
                if logo42[r][c] == 1:
                    matrix[mid_row - row_offset + r, mid_col - col_offset + c] = -1

    def _get_logo_coords(self, matrix: np.ndarray) -> list[Node]:
        return [tuple(coords) for coords in np.argwhere(matrix == -1)]

    def _open_maze_walls(
            self,
            maze: np.ndarray,
            open_edges: list[Edge]
            ) -> np.ndarray:
        for neighbor_nodes in open_edges:
            match (neighbor_nodes):
                case ((x1, y1), (x2, y2)) if x1 == x2:
                    maze[x1][y1] &= ~Dir.E
                    maze[x2][y2] &= ~Dir.W
                case ((x1, y1), (x2, y2)) if y1 == y2:
                    maze[x1][y1] &= ~Dir.S
                    maze[x2][y2] &= ~Dir.N

        # Enforce closed outer boundary walls to prevent West/outer wall gaps
        maze[0, :] |= Dir.N
        maze[-1, :] |= Dir.S
        maze[:, 0] |= Dir.W
        maze[:, -1] |= Dir.E

        return maze

    def generate_maze(self) -> np.ndarray:
        for maze in self.generate_maze_frames():
            self._maze = maze

        if self._maze is None:
            raise RuntimeError("Maze generation produced no frames.")

        return self._maze

    def generate_maze_frames(self) -> Iterator[np.ndarray]:
        """Return the maze step by step, keeping self._maze updated on every frame."""
        matrix: np.ndarray = np.full(
            (self._config.height, self._config.width), 15
        )
        self._insert_42(matrix)
        self._logo_coords = self._get_logo_coords(matrix)

        registered_algorithm: MazeAlgorithm = self._maze_algorithm.algorithm
        open_edges = registered_algorithm.generate_open_edges(
            matrix.shape, self._logo_coords)
        
        matrix[matrix == -1] = 15
        self._maze = matrix.copy()  # Ensure _maze is available immediately
        yield matrix.copy()

        frame_count = min(
            30, len(open_edges),
            max(1, (matrix.size - len(self._logo_coords) + 4) // 5)
        )
        for frame in range(frame_count):
            first_edge = frame * len(open_edges) // frame_count
            last_edge = (frame + 1) * len(open_edges) // frame_count
            self._open_maze_walls(matrix, open_edges[first_edge:last_edge])
            self._maze = matrix.copy()  # Keep _maze current for path calculation during animation
            yield matrix.copy()

        self._maze = matrix.copy()

    def generate_path(self) -> list[Node]:
        """Compute the shortest path from entry to exit using BFS."""
        if self._maze is None:
            return []
    
        solver = MazeSolver(self._maze, self.entry, self.exit)
        return solver.find_shortest_path()