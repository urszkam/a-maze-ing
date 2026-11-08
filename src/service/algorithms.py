from __future__ import annotations

import random
from abc import ABC, abstractmethod
from enum import Enum

import numpy as np


class MazeAlgorithm(ABC):
    """Define the interface for selecting maze passages."""

    @abstractmethod
    def generate_open_edges(
        self,
        shape: tuple[int, int],
        logo_coords: list[tuple[int, int]],
        is_perfect: bool = True
    ) -> list[tuple[tuple[int, int], tuple[int, int]]]:
        """Select passages between adjacent non-logo cells.

        Args:
            shape: Matrix dimensions.
            logo_coords: Blocked cells as (row, column) pairs.
            is_perfect: Whether to require passages without cycles.

        Returns:
            Pairs of neighbor nodes coordinates where wall should open.
        """
        ...

    def _remove_dead_ends(
        self,
        open_edges: list[tuple[tuple[int, int], tuple[int, int]]]
    ) -> list[tuple[tuple[int, int], tuple[int, int]]]:
        """Removes dead-ends.

        Args:
            open_edges: Existing passages between neighbor cells.

        Returns:
            The list of passages with no nead-ends.
        """
        return open_edges


class KruskalAlgorithm(MazeAlgorithm):
    """Select maze passages using randomized Kruskal and disjoint sets."""
    def generate_open_edges(
        self,
        shape: tuple[int, int],
        logo_coords: list[tuple[int, int]],
        is_perfect: bool = True
    ) -> list[tuple[tuple[int, int], tuple[int, int]]]:
        """Build a spanning forest of the grid, excluding logo cells.

        Args:
            shape: Matrix dimensions.
            logo_coords: Blocked cells as (row, column) pairs.
            is_perfect: If false, remove dead-ends.

        Returns:
            Randomly selected passages connecting each reachable component.
        """
        zero_matrix: np.ndarray = np.zeros(shape)
        nodes: list[tuple[int, int]] = [
            tuple(coords) for coords in np.argwhere(zero_matrix == 0)
            if tuple(coords) not in logo_coords
        ]
        nodes_map: dict[tuple[int, int], tuple[int, int]] = {
            coords: coords for coords in nodes}

        edges: list[tuple[tuple[int, int], tuple[int, int]]] = []
        for x, y in nodes:
            for neighbor in ((x + 1, y), (x, y + 1)):
                if neighbor in nodes_map:
                    edges.append(((x, y), neighbor))

        random.shuffle(edges)

        open_edges: list[tuple[tuple[int, int], tuple[int, int]]] = []
        for neighbor_nodes in edges:
            if self._is_on_different_path(neighbor_nodes, nodes_map):
                self._union(neighbor_nodes, nodes_map, open_edges)

        if not is_perfect:
            self._remove_dead_ends(open_edges)

        return open_edges

    def _union(
            self,
            nodes: tuple[tuple[int, int], tuple[int, int]],
            nodes_map: dict[tuple[int, int], tuple[int, int]],
            open_edges: list[tuple[tuple[int, int], tuple[int, int]]]
            ) -> None:
        """Merge two disjoint sets and record the passage between their cells.

        Args:
            nodes: Adjacent cells whose roots must be different.
            nodes_map: Cell-to-parent mapping, updated in place.
            open_edges: Passage list to which the cell pair is appended.
        """
        node1, node2 = nodes

        root1: tuple[int, int] = self._find(node1, nodes_map)
        root2: tuple[int, int] = self._find(node2, nodes_map)
        nodes_map[root1] = root2

        open_edges.append(nodes)

    def _find(self, node: tuple[int, int],
              nodes_map: dict[tuple[int, int], tuple[int, int]]
              ) -> tuple[int, int]:
        """Follow parent links to find the representative of a cell's set.

        Args:
            node: Cell whose representative is needed.
            nodes_map: Cell-to-parent mapping with self-parented roots.

        Returns:
            Coordinates of the root representing the set.
        """
        while (node != nodes_map[node]):
            node = nodes_map[node]

        return node

    def _is_on_different_path(
            self, nodes: tuple[tuple[int, int], tuple[int, int]],
            nodes_map: dict[tuple[int, int], tuple[int, int]]
            ) -> bool:
        """Check whether two cells belong to different disjoint sets.

        Args:
            nodes: Pair of cells to compare.
            nodes_map: Cell-to-parent mapping used to find their roots.

        Returns:
            True if joining the cells would not create a cycle.
        """
        node1, node2 = nodes

        return self._find(node1, nodes_map) != self._find(node2, nodes_map)


class AlgorithmType(str, Enum):
    """Associate display names with shared algorithm instances."""
    algorithm: MazeAlgorithm

    def __new__(cls, title: str, maze_algorithm: MazeAlgorithm
                ) -> AlgorithmType:
        """Create an enum member and instantiate its algorithm.

        Args:
            title: Display name used as the enum value.
            maze_algorithm: Algorithm class to instantiate without arguments.

        Returns:
            Enum member holding the display name and algorithm instance.
        """
        obj = str.__new__(cls, title)
        obj._value_ = title

        obj.algorithm = maze_algorithm
        return obj

    def get_next(self) -> AlgorithmType:
        """Return the next declared algorithm, wrapping after the last one."""
        algorithms = list(self.__class__)
        new_idx = (algorithms.index(self) + 1) % len(algorithms)
        return algorithms[new_idx]

    KRUSKAL = ("Kruskal's algorithm", KruskalAlgorithm())
    PLACEHOLDER = ("placeholder", KruskalAlgorithm())
