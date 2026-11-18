import pytest
import numpy as np
from src.service.parse_config import MazeConfig
from src.service.maze_generator.generator import MazeGenerator
from pathlib import Path
from typing import Generator


@pytest.fixture(autouse=True)
def reset_maze_generator_singleton() -> Generator[None, None, None]:
    """Resets the MazeGenerator singleton state before and after each test."""
    # Using setattr to safely bypass mypy class attribute checks on dynamic
    # singletons
    setattr(MazeGenerator, "_instance", None)
    setattr(MazeGenerator, "_initialized", False)
    yield
    setattr(MazeGenerator, "_instance", None)
    setattr(MazeGenerator, "_initialized", False)


def test_same_seed_produces_identical_mazes(tmp_path: Path) -> None:
    """Test that two generators configured with the same seed generate
      identical maze walls."""
    # Use temporary file paths for output files to avoid cluttering the
    # workspace
    out1 = tmp_path / "maze1.txt"
    out2 = tmp_path / "maze2.txt"

    config1 = MazeConfig(
        width=10,
        height=10,
        output_file=str(out1),
        entry=(0, 0),
        exit=(9, 9),
        seed=42
    )
    gen1 = MazeGenerator(config1)
    maze1 = gen1.generate_maze()

    # Reset singleton state
    setattr(MazeGenerator, "_instance", None)
    setattr(MazeGenerator, "_initialized", False)

    config2 = MazeConfig(
        width=10,
        height=10,
        output_file=str(out2),
        entry=(0, 0),
        exit=(9, 9),
        seed=42
    )
    gen2 = MazeGenerator(config2)
    maze2 = gen2.generate_maze()

    # The wall structures should be completely identical for the same seed
    assert np.array_equal(maze1.walls, maze2.walls)


def test_different_seeds_produce_different_mazes(tmp_path: Path) -> None:
    """Test that generators configured with different seeds produce different
      maze layouts."""
    out1 = tmp_path / "maze1.txt"
    out3 = tmp_path / "maze3.txt"

    config1 = MazeConfig(
        width=10,
        height=10,
        output_file=str(out1),
        entry=(0, 0),
        exit=(9, 9),
        seed=42
    )
    gen1 = MazeGenerator(config1)
    maze1 = gen1.generate_maze()

    # Reset singleton state
    setattr(MazeGenerator, "_instance", None)
    setattr(MazeGenerator, "_initialized", False)

    config3 = MazeConfig(
        width=10,
        height=10,
        output_file=str(out3),
        entry=(0, 0),
        exit=(9, 9),
        seed=999  # Different seed
    )
    gen3 = MazeGenerator(config3)
    maze3 = gen3.generate_maze()

    # The wall structures should differ when using distinct random seeds
    assert not np.array_equal(maze1.walls, maze3.walls)
