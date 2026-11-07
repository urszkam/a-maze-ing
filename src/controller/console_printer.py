from __future__ import annotations

import numpy as np
from rich.console import Console
from rich.style import Style
from rich.text import Text
from rich.theme import Theme

from ..constants import THEME, WALL, COLORS
from .enums import Dir


class ConsolePrinter(Console):
    _instance: ConsolePrinter | None = None
    _initialized: bool = False

    def __new__(cls) -> ConsolePrinter:
        """Create singleton console printer instance.

        Returns:
            The existing or newly created instance.
        """
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        """Initialize the console and its theme. """
        if self._initialized:
            return

        self._theme: Theme = Theme(THEME)
        super().__init__(theme=self._theme)
        self._maze_text = Text()

        self._initialized = True


    def error(self, error: str) -> None:
        """Print formatted error message.

        Args:
            error: Error message.
        """
        self.print(error, style="txt.error")

    def _update_color(self, style: str) -> None:
        """Rotate colors of a chosen element.

        Args:
            style: style of a chosen element printed by Console.
        """
        current_style = self._theme.styles[style]
        current_color = current_style.color
        color = (
            current_color.name
            if current_color and current_color.name in COLORS
            else COLORS[0]
        )

        next_idx = (COLORS.index(color) + 1) % len(COLORS)

        self._theme.styles[style] = (
            current_style + Style(color=COLORS[next_idx])
        )

    def update_wall_color(self) -> None:
        """Change maze wall color.
        """
        self._update_color("maze.wall")

    def update_42_color(self) -> None:
        """Change 42 logo color.
        """
        self._update_color("maze.42")

    def show_hide_path(self) -> None:
        """Show/hide maze path by switching the conceal value.
        """
        current_style = self._theme.styles["maze.path"]
        new_conceal = not current_style.conceal

        self._theme.styles["maze.path"] = (
            current_style + Style(conceal=new_conceal)
        )


class MazeText(Text):
    @staticmethod
    def get_wall_text(dir: Dir, row: int, col: int, maze: np.ndarray) -> str:
        """Generates maze elements for a single cell level.

        Args:
            dir: Direction of current maze cell element.
            row: Row index of the cell.
            col: Column index of the cell.
            maze: 2D array of values describing walls for each cell.

        Returns:
            String with characters to be preinted as cell elements.
        """
        cell = maze[row][col]
        cell = 15 if cell == -1 else cell

        north = cell & Dir.N
        east = cell & Dir.E
        south = cell & Dir.S
        west = cell & Dir.W

        is_last_row = row == maze.shape[0] - 1
        is_last_col = col == maze.shape[1] - 1

        prev = 0 if col == 0 else maze[row][col - 1]
        bottom = 0 if is_last_row else maze[row + 1][col]

        # TODO implement missing borders
        # TODO divide this spaghetti into helper functions
        prefix = " "
        sufix = ""
        match (dir):
            case Dir.N:
                if col == 0 and row == 0:
                    prefix = WALL["top_left"]
                elif west:
                    prefix = WALL["top_join"]
                else:
                    prefix = WALL["horizontal"][0]
                if is_last_col and row == 0:
                    sufix = WALL["top_right"]
            case Dir.S:
                if west and south:
                    if not prev & Dir.S and not bottom & Dir.W:
                        prefix = WALL["bottom_left"]
                    elif not prev & Dir.S and bottom & Dir.W:
                        prefix = WALL["left_join"]
                    elif prev & Dir.S and bottom & Dir.W:
                        prefix = WALL["cross"]
                    elif prev & Dir.S and not bottom & Dir.W:
                        prefix = WALL["bottom_join"]

                elif col == 0:
                    prefix = WALL["vertical"]

                if is_last_row and is_last_col:
                    sufix = WALL["bottom_right"]
                elif is_last_col and south:
                    sufix = WALL["right_join"]
                elif is_last_col:
                    sufix = WALL["vertical"]

        match (dir):
            case Dir.W:
                if west:
                    return WALL["vertical"]
                return " "
            case Dir.E:
                if east:
                    return WALL["vertical"]
                return " "
            case Dir.N if north: return prefix + WALL["horizontal"] + sufix
            case Dir.S:
                if south:
                    return prefix + WALL["horizontal"] + sufix
                return prefix + "   " + sufix
            case _: return ""

    def append_wall(self, chars: str) -> None:
        """Add maze wall characters to be printed.

        Args:
            chars: Characters of maze wall.
        """
        self.append(chars, style="maze.wall")

    def append_wall_logo(self, chars: str) -> None:
        """Add wall characters of cells containing 42 logo to be printed.

        Args:
            chars: Characters of maze wall.
        """
        self.append(chars[0], style="maze.wall")
        self.append(chars[1:4], style="maze.42")

        if len(chars) > 4:
            self.append(chars[4:], style="maze.wall")

    def append_logo(self) -> None:
        """Add 42 logo characters to be printed. """
        self.append(WALL["logo"], style="maze.42")

    def append_path(self) -> None:
        """Add maze path characters to be printed. """
        self.append(WALL["path"], style="maze.path")

    def append_entry(self) -> None:
        """Add entry character to be printed. """
        self.append(WALL["entry"][:2], style="maze.entry")
        self.append_path()

    def append_exit(self) -> None:
        """Add exit character to be printed. """
        self.append(WALL["entry"], style="maze.exit")

    def append_nl(self) -> None:
        """Add new line character. """
        self.append("\n")
