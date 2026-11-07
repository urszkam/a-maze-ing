from __future__ import annotations

from typing import Any

import numpy as np

from ..constants import LOGO42


class MazeGenerator:
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

    def generate_maze(self) -> np.ndarray:
        """Generate a maze using an algorithm.

        Returns:
            2d maze array with binary walls representation.
        """
        initial_matrix: np.ndarray = np.full(
            (self._config["height"], self._config["width"]), 15
        )

        self._insert_42(initial_matrix)

        # TODO generate maze

        self._maze = initial_matrix

        return initial_matrix

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
