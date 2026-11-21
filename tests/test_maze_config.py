import pytest

from pydantic import ValidationError

from src.service.maze_generator.maze_config import MazeConfig
from src.service.maze_generator.algorithms import AlgorithmType


def test_valid_config_with_tuples() -> None:
    """Test successful initialization with standard integer tuples and
      default values."""
    config = MazeConfig(
        width=10,
        height=10,
        output_file="maze_output.txt",
        entry=(0, 0),
        exit=(9, 9)
    )
    assert config.width == 10
    assert config.height == 10
    assert config.output_file == "maze_output.txt"
    assert config.entry == (0, 0)
    assert config.exit == (9, 9)
    assert config.perfect is False
    assert config.seed == 666
    assert config.algorithm == AlgorithmType.PRIM


def test_valid_config_with_string_coordinates() -> None:
    """Test coordinate parsing from comma-separated strings."""
    config = MazeConfig(
        width=5,
        height=5,
        output_file="out.txt",
        entry="1, 2",   # type: ignore[arg-type]
        exit="4,3"      # type: ignore[arg-type]
    )
    assert config.entry == (1, 2)
    assert config.exit == (4, 3)


def test_invalid_coordinate_string_format() -> None:
    """Test that invalid string formats raise validation errors."""
    with pytest.raises(ValidationError) as exc_info:
        MazeConfig(
            width=5,
            height=5,
            output_file="out.txt",
            entry="1,2,3",  # type: ignore[arg-type]
            exit="4,3"      # type: ignore[arg-type]
        )
    assert "Coordinate must have exactly two" in str(exc_info.value)

    with pytest.raises(ValidationError) as exc_info:
        MazeConfig(
            width=5,
            height=5,
            output_file="out.txt",
            entry="1, a",   # type: ignore[arg-type]
            exit="4,3"      # type: ignore[arg-type]
        )
    assert "Coordinate values must be integers." in str(exc_info.value)


def test_grid_dimensions_must_be_positive() -> None:
    """Test that width and height must be strictly greater than 0."""
    with pytest.raises(ValidationError):
        MazeConfig(
            width=0,
            height=5,
            output_file="out.txt",
            entry=(0, 0),
            exit=(1, 1)
        )

    with pytest.raises(ValidationError):
        MazeConfig(
            width=5,
            height=-2,
            output_file="out.txt",
            entry=(0, 0),
            exit=(1, 1)
        )


def test_entry_out_of_bounds() -> None:
    """Test validation failure when entry coordinates exceed grid
      dimensions."""
    with pytest.raises(ValidationError) as exc_info:
        MazeConfig(
            width=5,
            height=5,
            output_file="out.txt",
            entry=(5, 2),  # Out of bounds (width is 5, max index is 4)
            exit=(0, 0)
        )
    assert "ENTRY coordinates are out of grid bounds." in str(exc_info.value)

    with pytest.raises(ValidationError) as exc_info:
        MazeConfig(
            width=5,
            height=5,
            output_file="out.txt",
            entry=(-1, 2),  # Negative index
            exit=(0, 0)
        )
    assert "ENTRY coordinates are out of grid bounds." in str(exc_info.value)


def test_exit_out_of_bounds() -> None:
    """Test validation failure when exit coordinates exceed grid dimensions."""
    with pytest.raises(ValidationError) as exc_info:
        MazeConfig(
            width=5,
            height=5,
            output_file="out.txt",
            entry=(0, 0),
            exit=(2, 5)  # Out of bounds (height is 5, max index is 4)
        )
    assert "EXIT coordinates are out of grid bounds." in str(exc_info.value)


def test_entry_and_exit_must_be_different() -> None:
    """Test that entry and exit cannot occupy the same location."""
    with pytest.raises(ValidationError) as exc_info:
        MazeConfig(
            width=5,
            height=5,
            output_file="out.txt",
            entry=(2, 2),
            exit=(2, 2)
        )
    assert "ENTRY and EXIT must be different locations." in str(exc_info.value)
