from collections import Counter
from typing import TypeAlias, cast

import pytest

from src.service.maze_generator.algorithms import MazeAlgorithm
from src.service.maze_generator.algorithms import KruskalAlgorithm
from src.service.maze_generator.algorithms import PrimAlgorithm
from src.service.maze_generator.algorithms import AlgorithmType


Node: TypeAlias = tuple[int, int]
Edge: TypeAlias = tuple[Node, Node]


@pytest.fixture(params=[KruskalAlgorithm, PrimAlgorithm])
def algorithm(request: pytest.FixtureRequest) -> MazeAlgorithm:
    algorithm_class = cast(type[MazeAlgorithm], request.param)
    return algorithm_class()


@pytest.mark.parametrize(
    "shape, expected",
    [
        ((3, 3), 8),
        ((2, 2), 3)
    ],
)
def test_perfect_maze_passage_count(
    shape: tuple[int, int],
    expected: int,
    algorithm: MazeAlgorithm
) -> None:

    edges = algorithm.generate_open_edges(shape, [])

    assert len(set(edges)) == expected


@pytest.mark.parametrize(
    "rows, cols, logo",
    [
        (2, 2, []),
        (3, 3, [(1, 1)]),
        (4, 3, [(0, 1), (0, 2), (1, 2)])
    ],
)
def test_passages_connect_neighbors(
    rows: int, cols: int, logo: list[Node], algorithm: MazeAlgorithm
) -> None:
    edges = algorithm.generate_open_edges((rows, cols), logo)

    for (row1, col1), (row2, col2) in edges:
        assert row1 == row2 or col1 == col2
        assert row1 - row2 in [0, -1] and col1 - col2 in [0, -1]


@pytest.mark.parametrize(
    "rows, cols, logo",
    [
        (2, 2, []),
        (4, 3, [(0, 1), (0, 2), (1, 2)])
    ],
)
def test_passages_within_maze_bounds(
    rows: int, cols: int, logo: list[Node], algorithm: MazeAlgorithm
) -> None:
    edges = algorithm.generate_open_edges((rows, cols), logo)

    for (row1, col1), (row2, col2) in edges:
        assert 0 <= row1 < rows and 0 <= col1 < cols
        assert 0 <= row2 < rows and 0 <= col2 < cols


@pytest.mark.parametrize(
    "shape, logo, expected",
    [
        ((2, 2), [(0, 0)], 2),
        ((3, 3), [(1, 1)], 7),
        ((3, 3), [(0, 2)], 7),
    ],
)
def test_logo_cells_have_no_passages(
    shape: tuple[int, int], logo: list[Node], expected: int,
    algorithm: MazeAlgorithm
) -> None:
    edges: list[Edge] = algorithm.generate_open_edges(shape, logo)

    assert len(edges) == expected
    for first, second in edges:
        assert first not in logo
        assert second not in logo


@pytest.mark.parametrize(
    "shape, logo",
    [
        ((2, 2), []),
        ((3, 3), [(1, 1)]),
        ((4, 3), [(0, 2), (1, 2)])
    ],
)
def test_braided_maze_no_dead_ends(
    shape: tuple[int, int], logo: list[Node], algorithm: MazeAlgorithm
) -> None:
    edges = algorithm.generate_open_edges(shape, logo, is_perfect=False)
    nodes_from_open_edges: tuple[Node, ...] = sum(edges, ())
    nodes_counter = Counter(nodes_from_open_edges)
    dead_ends: list[Node] = [
            node for node in nodes_counter if nodes_counter[node] == 1
        ]

    assert dead_ends == []


@pytest.mark.parametrize(
    "current, expected",
    [
        (AlgorithmType.KRUSKAL, AlgorithmType.PRIM),
        (AlgorithmType.PRIM, AlgorithmType.KRUSKAL),
    ],
)
def test_algorithm_type_enum_get_next(
    current: AlgorithmType,
    expected: AlgorithmType,
) -> None:
    assert current.get_next() is expected
