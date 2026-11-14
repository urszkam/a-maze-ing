from __future__ import annotations
from collections import deque
from typing import TypeAlias
import numpy as np
from src.constants import Dir

Node: TypeAlias = tuple[int, int]

class MazeSolver:
    """Finds the shortest path through the generated maze using Breadth-First Search (BFS)."""

    def find_shortest_path(
        self, maze: np.ndarray, entry: Node, exit: Node
    ) -> list[Node]:
        """Compute the shortest path from entry to exit considering wall bitmasks.

        Returns:
            A list of coordinate nodes representing the path, or empty list if unreachable.
        """
        rows, cols = maze.shape
        queue: deque[Node] = deque([entry])
        visited: set[Node] = {entry}
        parent_map: dict[Node, Node] = {entry: entry}

        found = False
        while queue:
            current = queue.popleft()
            if current == exit:
                found = True
                break

            r, c = current
            cell_walls = maze[r][c]

            # Check neighbors based on open walls (inverted bitmasks)
            # North
            if not (cell_walls & Dir.N) and r > 0:
                neighbor = (r - 1, c)
                if neighbor not in visited:
                    visited.add(neighbor)
                    parent_map[neighbor] = current
                    queue.append(neighbor)
            # South
            if not (cell_walls & Dir.S) and r < rows - 1:
                neighbor = (r + 1, c)
                if neighbor not in visited:
                    visited.add(neighbor)
                    parent_map[neighbor] = current
                    queue.append(neighbor)
            # West
            if not (cell_walls & Dir.W) and c > 0:
                neighbor = (r, c - 1)
                if neighbor not in visited:
                    visited.add(neighbor)
                    parent_map[neighbor] = current
                    queue.append(neighbor)
            # East
            if not (cell_walls & Dir.E) and c < cols - 1:
                neighbor = (r, c + 1)
                if neighbor not in visited:
                    visited.add(neighbor)
                    parent_map[neighbor] = current
                    queue.append(neighbor)

        if not found:
            return []

        # Reconstruct path from exit to entry
        path: list[Node] = []
        curr = exit
        while curr != entry:
            path.append(curr)
            curr = parent_map[curr]
        path.append(entry)
        path.reverse()

        return path
