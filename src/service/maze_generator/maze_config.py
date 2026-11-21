from typing import Any
from .algorithms import AlgorithmType
from pydantic import (
        BaseModel,
        Field,
        field_validator,
        model_validator
)


class MazeConfig(BaseModel):
    """Configuration parser and validator for maze generation parameters.

    This class reads a configuration text file, parses key-value pairs,
    and validates constraints such as grid boundaries, mandatory fields,
    and unique entry/exit points using Pydantic.

    Attributes:
        width: The width of the maze grid. Must be greater than 0.
        height: The height of the maze grid. Must be greater than 0.
        output_file: The file path to save generated maze.
        perfect: Flag indicating if the maze should be perfect
            (no loops, unique path between any two points).
        entry: The (x, y) start coordinates of the maze.
        exit: The (x, y) end coordinates of the maze.
        seed (optional): Random seed used for maze generation.
            Defaults to None.
        algorithm (optional): The algorithm used to generate the maze.
            Defaults to Prim when omitted.
    """
    width: int = Field(..., gt=0, le=100, description="Width of the maze grid")
    height: int = Field(..., gt=0, le=100, description="Height of the maze grid")
    output_file: str = Field(..., description="Destination file path")
    entry: tuple[int, int] = Field(..., description="Start coordinates (x, y)")
    exit: tuple[int, int] = Field(..., description="End coordinates (x, y)")

    # Optional fields with default values
    perfect: bool = Field(
        default=False, description="Whether the maze is perfect")
    seed: int = Field(default=666, description="Random seed for maze")
    algorithm: AlgorithmType = Field(
        default=AlgorithmType.PRIM, description="Algorithm to use")

    @field_validator("entry", "exit", mode="before")
    @classmethod
    def parse_coordinates(cls, value: Any) -> Any:
        """Converts an 'x,y' string into an integer tuple before validation.

        Args:
            value (Any): Raw input from the config file (string or tuple).

        Returns:
            Any: Parsed tuple of integers `(x, y)`

        Raises:
            ValueError: If the coordinate string does not contain exactly two
            comma-separated values or if the values cannot be converted to
            integers.
        """
        if isinstance(value, str):
            parts = value.split(",")
            if len(parts) != 2:
                raise ValueError("Coordinate must have exactly two"
                                 " comma-separated values (e.g. 0,0).")
            try:
                return (int(parts[0].strip()), int(parts[1].strip()))
            except ValueError:
                raise ValueError("Coordinate values must be integers.")
        return value

    @model_validator(mode="after")
    def validate_coordinates(self) -> "MazeConfig":
        """Applies advanced business rules and maze boundary constraints.

        Ensures that entry and exit coordinates fall in the grid dimensions
        and that they are not set to same location.

        Returns:
            MazeConfig: The validated model instance.

        Raises:
            ValueError: If coordinates are out of bounds or if entry
            matches exit.
        """
        if not ((0 <= self.entry[0] < self.width) and
                (0 <= self.entry[1] < self.height)):
            raise ValueError("ENTRY coordinates are out of grid bounds.")

        if not ((0 <= self.exit[0] < self.width) and
                (0 <= self.exit[1] < self.height)):
            raise ValueError("EXIT coordinates are out of grid bounds.")

        # Check if entry and exit are distinct
        if self.entry == self.exit:
            raise ValueError("ENTRY and EXIT must be different locations.")

        return self
