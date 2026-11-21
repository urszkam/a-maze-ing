import numpy as np
from src.service import InputHandler, MazeGenerator
from pathlib import Path


def _write_config_file(
    path: Path,
    output_file: str,
    seed: int,
    width: int = 10,
    height: int = 10
) -> Path:
    """Helper to write a config file for testing."""
    config_content = f"""
    width = {width}
    height = {height}
    output_file = {output_file}
    entry = 0,0
    exit = {width - 1},{height - 1}
    seed = {seed}
    """
    config_path = path / "config.txt"
    config_path.parent.mkdir(parents=True, exist_ok=True)
    config_path.write_text(config_content)
    return config_path


def test_same_seed_produces_identical_mazes(tmp_path: Path) -> None:
    """Test that two generators configured with the same seed generate
      identical maze walls."""
    out1 = tmp_path / "maze1.txt"
    out2 = tmp_path / "maze2.txt"

    cfg1 = _write_config_file(tmp_path / "dir1", str(out1), seed=42)
    gen1 = MazeGenerator(InputHandler.get_config_data(cfg1))
    maze1 = gen1.generate_maze()

    cfg2 = _write_config_file(tmp_path / "dir2", str(out2), seed=42)
    gen2 = MazeGenerator(InputHandler.get_config_data(cfg2))
    maze2 = gen2.generate_maze()

    # The wall structures should be completely identical for the same seed
    assert np.array_equal(maze1.walls, maze2.walls)


def test_different_seeds_produce_different_mazes(tmp_path: Path) -> None:
    """Test that generators configured with different seeds produce different
      maze layouts."""
    out1 = tmp_path / "maze1.txt"
    out3 = tmp_path / "maze3.txt"

    cfg1 = _write_config_file(tmp_path / "dir1", str(out1), seed=42)
    gen1 = MazeGenerator(InputHandler.get_config_data(cfg1))
    maze1 = gen1.generate_maze()

    cfg3 = _write_config_file(tmp_path / "dir3", str(out3), seed=999)
    gen3 = MazeGenerator(InputHandler.get_config_data(cfg3))
    maze3 = gen3.generate_maze()

    # The wall structures should differ when using distinct random seeds
    assert not np.array_equal(maze1.walls, maze3.walls)
