from __future__ import annotations

from enum import Enum
from typing import Any

import numpy as np

from ..constants import LOGO42

class AlgorithmType(str, Enum):
    algorithm: MazeAlgorithm

    def __new__(cls, title: str, maze_algorithm: MazeAlgorithm) -> AlgorithmType:
        obj = str.__new__(cls, title)
        obj._value_ = title

        obj.algorithm = maze_algorithm
        return obj

    def get_next(self) -> AlgorithmType:
        algorithms = list(self.__class__)
        new_idx = (algorithms.index(self) + 1) % len(algorithms)
        return algorithms[new_idx]

    KRUSKAL = ["kruskal's", KruskalAlgorithm]


class MazeGenerator:
    _instance: MazeGenerator | None = None
    _initialized: bool = False
    _algorithm: AlgorithmType | None = None

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
        self._register_algorithm()
        self._initialized = True

    @property
    def entry(self) -> tuple[int, int]:
        """TODO Will be removed. """
        return self._config["entry"]

    @property
    def exit(self) -> tuple[int, int]:
        """TODO Will be removed. """
        return self._config["exit"]

    @property
    def maze(self) -> np.ndarray | None:
        """TODO Will be removed. """
        return self._maze

    def register_algorithm(algorithm: AlgorithmType = AlgorithmType.KRUSKAL):
        """ Register algorithm.

            Args:
                algorithm: Enum representing chosen algorithm.
        """
        curr_algorithm: AlgorithmType = self._maze_algorithm
        if curr_algorith is None:
            self._maze_algorithm = algorithm
        else:
            self._maze_algorithm = curr_algorithm.get_next()

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

    def _get_logo_coords(matrix: np.ndarray) -> list[tuple[int, int]]:
        return [tuple(coords) for coords in np.argwhere(matrix == -1)]

    def generate_maze(self) -> np.ndarray:
        """Generate a maze using an algorithm.

        Returns:
            2d maze array with binary walls representation.
        """
        matrix: np.ndarray = np.full(
            (self._config["height"], self._config["width"]), 15
        )

        self._insert_42(matrix)
        logo_coords: list[tuple[int, int]] = _get_logo_coords(matrix)

        registered_algorithm = self._algorithm.algorithm
        maze = registered_algorithm.generate_maze(matrix.shape, logo_coords)

        # TODO generate maze
        self._maze = np.where(matrix == -1, 15, matrix)

        return self._maze

    def generate_path(self) -> list[tuple[int, int]]:
        """Generate maze path from entry to exit.

        Returns:
            Coordinates of every cell in the path.
        """
        path: list[tuple[int, int]] = []

        if self._maze is None or self._maze.isEmpty():
            return path

        # TODO generate path

        placeholder = [(0, 0), (0, 1), (1, 1), (1, 2), (1, 3), (0, 3), (0, 2)]

        return placeholder


class MazeAlgorithm():
    def generate_maze(
        perfect: bool = True
        ) -> list[tuple[tuple[int, int], tuple[int, int]]]:
        ...


    def _remove_dead_ends(
        maze: list[tuple[tuple[int, int], tuple[int, int]]]
        ) -> list[tuple[tuple[int, int], tuple[int, int]]]:
        ...


class KruskalAlgorithm(MazeAlgoritm):
    def generate_maze(
        shape: tuple[int, int], 
        logo_coords: list[tuple[int, int]],
        perfect: bool = True
        ) -> list[tuple[tuple[int, int], tuple[int, int]]]:
        zero_matrix: np.ndarray = np.zeroes(shape)
        nodes: list[tuple[int, int]] = [tuple(coords) for coords in np.argwhere(zero_matrix == 0)]
        nodes_map: dict[tuple[int, int], tuple[int, int]] = {coords: coords for coords in nodes}
        possible_edges = [((x, y), (x, y + 1)), (x + 1, y) ]


        if not perfect:
            _remove_dead_ends(maze_open_edges)


    def _remove_dead_ends(
        maze: list[tuple[tuple[int, int], tuple[int, int]]]
        ) -> list[tuple[tuple[int, int], tuple[int, int]]]:
        pass

    def _generate_edges(
        matrix_shape: tuple(int, int), 
        logo_coordinates: list[tuple[int, int]]
        ) -> list[tuple[]]: 