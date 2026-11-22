from __future__ import annotations
from random import Random

import numpy as np
from typing import Iterator, TypeAlias

from src.constants import LOGO42, Dir
from .maze import Maze
from .maze_config import MazeConfig
from src.service import OutputHandler
from .algorithms import AlgorithmType, MazeAlgorithm
from .maze_solver import MazeSolver


Node: TypeAlias = tuple[int, int]
Edge: TypeAlias = tuple[Node, Node]


class MazeGenerator:
    """Manage a maze, its configuration and selected algorithm.

    Attributes:
        _maze (Maze | None): Current maze or None before generation.
        _solver (MazeSolver): Finds the shortest path from entry to exit.
        _logo_coords (list[Node]): Logo cells as (row, column) pairs.
            Empty if there is no logo.
        _config (MazeConfig): Validated maze generation settings.
        _rand (Random): Random number generator using the chosen seed.
        _output_handler (OutputHandler): Saves the maze to a file.
        _maze_algorithm (AlgorithmType): Algorithm used to create the maze.
        _logo_initialized (bool): True after finding the logo cells.
    """

    def __init__(self, config_data: dict[str, str]) -> None:
        """Initialize the maze generator instance.

        Args:
            config_data: Dictionary of raw configuration values.

        Raises:
            ValidationError: When config data is incorrect
        """
        self._initialize_maze_config(config_data)
        self._register_algorithm(self._config.algorithm)
        self._maze: Maze | None = None
        self._solver = MazeSolver()
        self._logo_coords: list[Node] = []
        self._rand = Random(self._config.seed)
        self._output_handler = OutputHandler(self._config.output_file)
        self._logo_initialized = False

    @property
    def algorithm_name(self) -> str:
        """Return the selected algorithm name or an em dash if none is set."""
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

    def _register_algorithm(
            self,
            algorithm: AlgorithmType = AlgorithmType.KRUSKAL) -> None:
        """Select the initial algorithm.

        Args:
            algorithm: Initial choice, used only when no algorithm is selected.
        """
        self._maze_algorithm = algorithm

    def _initialize_maze_config(self, config_data: dict[str, str]) -> None:
        """Validate and initialize maze config with configuration information.

        Args:
            config_data: dictionary with configuration data.

        Raises:
            ValidationError: When config data is incorrect.
        """
        self._config = MazeConfig.model_validate(config_data)

    def next_algorithm(self) -> None:
        """Select the next available algorithm."""
        self._maze_algorithm = self._maze_algorithm.get_next()

    def _insert_42(self, matrix: np.ndarray) -> None:
        """Place the 42 logo cells in the initial maze as -1.

        Args:
            matrix: initial 2d array filled with number 15.
        """
        logo42 = np.array(LOGO42)
        logo_rows, logo_cols = logo42.shape
        matrix_rows, matrix_cols = matrix.shape

        if logo_rows + 1 >= matrix_rows or logo_cols + 1 >= matrix_cols:
            return

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
        self._logo_initialized = True
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
            Maze object containing walls, logo cells and the solution path.

        Raises:
            OSError: when the write operation cannot be completed
            RuntimeError: If generation produces no frames or entry/exit
                overlaps the logo.
        """
        for _ in self.generate_maze_frames():
            pass

        if self._maze is None:
            raise RuntimeError("Maze generation produced no frames.")

        return self._maze

    def _store_maze(self, maze: np.ndarray) -> Maze:
        """Store a completed maze from its final wall matrix.

        Args:
            maze: Final maze wall matrix.

        Returns:
            Maze instance storing the completed maze.

        Raises:
            OSError: when the write operation cannot be completed
        """
        path: list[Node] = self.generate_path(maze)
        self._maze = Maze(maze, self._logo_coords, path,
                          self.entry, self.exit)
        self._save_output()

        return self._maze

    def generate_maze_frames(self) -> Iterator[Maze]:
        """Yield maze snapshots and finalize the maze when fully consumed.

        Yields:
            Maze objects with independent wall snapshots and no solution path.

        Raises:
            RuntimeError: When entry/exit in logo cell.
            OSError: When saving the completed maze fails.
        """
        matrix: np.ndarray = np.full(
            (self._config.height, self._config.width), 15
        )
        self._insert_42(matrix)
        if not self._logo_initialized:
            self._logo_coords = self._get_logo_coords(matrix)

        if self.entry in self._logo_coords:
            raise RuntimeError(
                "ENTRY cannot be placed in the same cell as logo.")

        if self.exit in self._logo_coords:
            raise RuntimeError(
                "EXIT cannot be placed in the same cell as logo.")

        registered_algorithm: MazeAlgorithm = self._maze_algorithm.algorithm
        open_edges: list[Edge] = registered_algorithm.generate_open_edges(
            shape=matrix.shape,
            logo_coords=self._logo_coords,
            rand=self._rand,
            is_perfect=self._config.perfect)

        matrix[matrix == -1] = 15
        yield Maze(matrix.copy(), self._logo_coords, [],
                   self.entry, self.exit)

        frame_count = min(
            30, len(open_edges),
            max(1, (matrix.size - len(self._logo_coords) + 4) // 5)
        )
        for frame in range(frame_count):
            first_edge = frame * len(open_edges) // frame_count
            last_edge = (frame + 1) * len(open_edges) // frame_count
            self._open_maze_walls(matrix, open_edges[first_edge:last_edge])

            yield Maze(matrix.copy(), self._logo_coords, [],
                       self.entry, self.exit)

        self._store_maze(matrix)

    def generate_path(self, walls: np.ndarray) -> list[Node]:
        """Generate the shortest path from entry to exit.

        Args:
            walls: Matrix of cell wall bitmasks.

        Returns:
            Path coordinates as (row, column) pairs, or an empty list
            if the exit is unreachable.
        """
        return self._solver.find_shortest_path(
            walls, self.entry, self.exit
        )

    def _generate_path_output(self) -> str:
        """Convert the solution path to direction letters.

        Returns:
            A string of N, E, S and W letters
            or an empty string if there is no maze or path.
        """
        path_dirs = ""

        if not self._maze:
            return path_dirs

        path_bitmask: list[int] = self._maze.get_full_path_bitmask()

        for idx in range(len(path_bitmask) - 1):
            cell: int = path_bitmask[idx]
            next: int = path_bitmask[idx + 1]
            if cell & Dir.N and next & (prev_dir := Dir.S):
                path_dirs += Dir.N.name
            elif cell & Dir.S and next & (prev_dir := Dir.N):
                path_dirs += Dir.S.name
            elif cell & Dir.E and next & (prev_dir := Dir.W):
                path_dirs += Dir.E.name
            else:
                path_dirs += Dir.W.name
                prev_dir = Dir.E

            path_bitmask[idx + 1] -= prev_dir

        return path_dirs

    def _generate_maze_output(self) -> str:
        """Convert maze walls to hexadecimal digits.

        Returns:
            String containing one line per maze row
            or an empty string if there is no maze.
        """
        if not self._maze:
            return ""

        maze_bitmask: np.ndarray = self._maze.walls
        maze_hex = np.char.mod('%x', maze_bitmask)

        return '\n'.join(''.join(row) for row in maze_hex)

    def _generate_output(self) -> dict[str, str]:
        """Prepare maze data for saving to a file.

        Returns:
            A dictionary of strings, with maze rows,
            entry and exit coordinates and path directions.
        """
        output = {}

        output["maze"] = self._generate_maze_output()

        entry_row, entry_col = self.entry
        output["entry"] = f"{entry_col}, {entry_row}"

        exit_row, exit_col = self.exit
        output["exit"] = f"{exit_col}, {exit_row}"

        output["path_dirs"] = self._generate_path_output()

        return output

    def _save_output(self) -> None:
        """Generates the final output txt and saves it to a file

        Raises:
            OSError: when the write operation cannot be completed
        """
        output_data: dict[str, str] = self._generate_output()
        self._output_handler.save_output(output_data)
