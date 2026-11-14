from __future__ import annotations

import random
from abc import ABC, abstractmethod
from collections import Counter
from enum import Enum
from functools import reduce
from typing import TypeAlias

import numpy as np


Node: TypeAlias = tuple[int, int]
Edge: TypeAlias = tuple[Node, Node]


class MazeAlgorithm(ABC):
    """Define the interface for selecting maze passages."""

    @abstractmethod
    def generate_open_edges(
        self,
        shape: tuple[int, int],
        logo_coords: list[Node],
        is_perfect: bool = True
    ) -> list[Edge]:
        """Select passages between adjacent non-logo cells.

        Args:
            shape: Matrix dimensions.
            logo_coords: Blocked cells as (row, column) pairs.
            is_perfect: Whether to require passages without cycles.

        Returns:
            Pairs of neighbor nodes coordinates where wall should open.
        """
        ...

    def _remove_dead_ends(self, open_edges: list[Edge]) -> None:
        """Open extra passages from dead ends to eligible neighbors.

        Args:
            open_edges: Existing passages between neighbor cells.

        Dead ends without an eligible neighboring passage remain unchanged.
        """
        nodes_from_open_edges: tuple[Node, ...] = sum(
            open_edges, ())
        nodes_counter = Counter(nodes_from_open_edges)
        dead_ends: list[Node] = [node for node in nodes_counter
                     if nodes_counter[node] == 1]

        for dead_end in dead_ends:
            if nodes_counter[dead_end] > 1:
                continue

            row, col = dead_end
            neighbors: list[Node] = [(row + 1, col), (row - 1, col),
                         (row, col + 1), (row, col - 1)]
            neighbors_counter: dict[Node, int] = {
                node: nodes_counter[node]
                for node in neighbors
                if node in nodes_counter
                and tuple(sorted((dead_end, node))) not in open_edges
            }

            if not neighbors_counter:
                continue

            node_to_pass: Node = min(neighbors_counter, key=neighbors_counter.__getitem__)
            nodes_counter[node_to_pass] += 1
            nodes_counter[dead_end] += 1
            new_open_edge: Edge = (min(node_to_pass, dead_end), max(node_to_pass, dead_end))
            open_edges.append(new_open_edge)


class KruskalAlgorithm(MazeAlgorithm):
    """Select maze passages using randomized Kruskal and disjoint sets."""
    def generate_open_edges(
        self,
        shape: tuple[int, int],
        logo_coords: list[Node],
        is_perfect: bool = False
    ) -> list[Edge]:
        """Build a spanning forest of the grid, excluding logo cells.

        Args:
            shape: Matrix dimensions.
            logo_coords: Blocked cells as (row, column) pairs.
            is_perfect: If false, remove dead-ends.

        Returns:
            Randomly selected passages connecting each reachable component.
        """
        zero_matrix: np.ndarray = np.zeros(shape)
        nodes: list[Node] = [
            tuple(coords) for coords in np.argwhere(zero_matrix == 0)
            if tuple(coords) not in logo_coords
        ]

        nodes_map: dict[Node, Node] = {
            coords: coords for coords in nodes}

        edges: list[Edge] = []
        for x, y in nodes:
            for neighbor in ((x + 1, y), (x, y + 1)):
                if neighbor in nodes_map:
                    edges.append(((x, y), neighbor))

        random.shuffle(edges)

        open_edges: list[Edge] = []
        for neighbor_nodes in edges:
            if self._is_on_different_path(neighbor_nodes, nodes_map):
                self._union(neighbor_nodes, nodes_map, open_edges)

        if not is_perfect:
            self._remove_dead_ends(open_edges)

        return open_edges

    def _union(
            self,
            nodes: Edge,
            nodes_map: dict[Node, Node],
            open_edges: list[Edge]
            ) -> None:
        """Merge two disjoint sets and record the passage between their cells.

        Args:
            nodes: Adjacent cells whose roots must be different.
            nodes_map: Cell-to-parent mapping, updated in place.
            open_edges: Passage list to which the cell pair is appended.
        """
        node1, node2 = nodes

        root1: Node = self._find(node1, nodes_map)
        root2: Node = self._find(node2, nodes_map)
        nodes_map[root1] = root2

        open_edges.append(nodes)

    def _find(self, node: Node,
              nodes_map: dict[Node, Node]
              ) -> Node:
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
            self, nodes: Edge,
            nodes_map: dict[Node, Node]
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


class PrimAlgorithm(MazeAlgorithm):
    """Select maze passages using randomized Prim's algorithm."""
    
    def generate_open_edges(
        self,
        shape: tuple[int, int],
        logo_coords: list[Node],
        is_perfect: bool = True
    ) -> list[Edge]:
        """Build a maze using randomized Prim's algorithm, excluding logo cells.

        Args:
            shape: Matrix dimensions (rows, cols).
            logo_coords: Blocked cells as (row, column) pairs.
            is_perfect: Whether to require a perfect maze.

        Returns:
            Selected passages connecting the cells.
        """
        rows, cols = shape
        
        all_nodes = {
            (r, c) for r in range(rows) for c in range(cols)
            if (r, c) not in logo_coords
        }
        if not all_nodes:
            return []

        # Start with an arbitrary node
        start_node = next(iter(all_nodes))
        visited: set[Node] = {start_node}
        open_edges: list[Edge] = []
        
        # Track active frontier walls/edges connecting visited to unvisited nodes
        frontier: dict[Edge, Node] = {}

        def add_frontier_neighbors(node: Node) -> None:
            r, c = node
            for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                neighbor = (r + dr, c + dc)
                if neighbor in all_nodes and neighbor not in visited:
                    edge = (min(node, neighbor), max(node, neighbor))
                    frontier[edge] = neighbor

        add_frontier_neighbors(start_node)

        while frontier:
            # Pick a random edge from the frontier
            edge = random.choice(list(frontier.keys()))
            neighbor = frontier.pop(edge)

            if neighbor not in visited:
                visited.add(neighbor)
                open_edges.append(edge)
                add_frontier_neighbors(neighbor)

        if not is_perfect:
            self._remove_dead_ends(open_edges)

        return open_edges


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
    PRIM = ("Prim's algorithm", PrimAlgorithm())
