class InputHandler:
    @staticmethod
    def get_config_data(file_name: str) -> dict[str, str]:
        """
        """
        pass


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
