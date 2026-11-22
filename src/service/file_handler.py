from pathlib import Path


class InputHandler:
    """Read configuration key-value pairs from a text file."""

    @staticmethod
    def get_config_data(file_path: str | Path) -> dict[str, str]:
        """Reads config file with key-value pairs.

        Args:
            file_path (Union[str, Path]): Path to the configuration file.

        Returns:
            Dictionary with config variables names as keys and corresponding
            values.

        Raises:
            FileNotFoundError: If the specified config file does not exist.
            OSError: If the configuration file cannot be opened or read.
            UnicodeDecodeError: If the configuration file is not valid UTF-8.
            ValueError: If a non-empty, non-comment line has no '=' separator.
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(
                f"Error: Configuration file '{path}' not found")

        config_data: dict[str, str] = {}
        with open(path, "r", encoding="utf-8") as file:
            for line_number, line in enumerate(file, start=1):
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if "=" in line:
                    key, value = line.split("=", 1)
                    config_data[key.strip().lower()] = value.strip()
                else:
                    raise ValueError(
                        f"Invalid configuration at line {line_number}: "
                        "expected KEY=VALUE."
                    )
        return config_data


class OutputHandler:
    """Class responsible for saving the maze output to the file.

    Attributes:
        _output_filename (str): output path relative to the working directory
    """
    def __init__(self, output_filename: str) -> None:
        """Initialize instance that handles writing maze output data to file

        Args:
            output_filename: name of the filename declared in the config
        """
        self._output_filename: str = output_filename

    def save_output(self, output_data: dict[str, str]) -> None:
        """Write maze generator output data to a file

        Args:
            output_data: dictionary with maze hex bitmask,
                entry, exit and path

        Raises:
            OSError: when the write operation cannot be completed
        """
        with open(self._output_filename, "w", encoding="utf-8") as file:
            for key, value in output_data.items():
                file.write(value)
                file.write("\n\n" if key == "maze" else "\n")
