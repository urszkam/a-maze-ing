from __future__ import annotations

import numpy as np
from rich.console import Console
from rich.style import Style
from rich.text import Text
from rich.theme import Theme

from src.constants import THEME, WALL, COLORS, Dir


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

    def show_hide_path(self, visible: bool | None = None) -> bool:
        """Toggle or set path visibility and return its previous value."""
        current_style = self._theme.styles["maze.path"]
        was_visible = not current_style.conceal
        if visible is None:
            visible = not was_visible
        self._theme.styles["maze.path"] = (
            current_style + Style(conceal=not visible)
        )
        return was_visible


class MazeText(Text):
    @staticmethod
    def _get_bottom_wall(
            west: bool,
            south: bool,
            prev_south: int,
            bottom_west: int,
            is_last_row: bool,
            is_last_col: bool,
            ) -> str:
        """Generate the bottom wall segment of a cell."""
        prefix = " "

        if west:
            if south:
                if not prev_south and not bottom_west:
                    prefix = WALL["bottom_left"]
                elif not prev_south and bottom_west:
                    prefix = WALL["left_join"]
                elif prev_south and bottom_west:
                    prefix = WALL["cross"]
                elif prev_south and not bottom_west:
                    prefix = WALL["bottom_join"]
            else:
                if not prev_south and bottom_west:
                    prefix = WALL["vertical"]
                elif prev_south and not bottom_west:
                    prefix = WALL["bottom_right"]
                elif prev_south and bottom_west:
                    prefix = WALL["right_join"]
        else:
            if south:
                if prev_south and not bottom_west:
                    prefix = WALL["horizontal"][0]
                if prev_south and bottom_west:
                    prefix = WALL["top_join"]
                if not prev_south and bottom_west:
                    prefix = WALL["top_left"]
            else:
                if prev_south and bottom_west:
                    prefix = WALL["top_right"]

        sufix = ""
        if is_last_row and is_last_col:
            sufix = WALL["bottom_right"]
        elif is_last_col and south:
            sufix = WALL["right_join"]
        elif is_last_col:
            sufix = WALL["vertical"]

        if south:
            return prefix + WALL["horizontal"] + sufix
        return prefix + "   " + sufix

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

        north = cell & Dir.N
        east = cell & Dir.E
        south = cell & Dir.S
        west = cell & Dir.W

        is_last_row = row == maze.shape[0] - 1
        is_last_col = col == maze.shape[1] - 1

        prev = 0 if col == 0 else maze[row][col - 1]
        bottom = 0 if is_last_row else maze[row + 1][col]

        prev_south = prev & Dir.S
        bottom_west = bottom & Dir.W

        prefix = " "
        sufix = ""
        if dir is Dir.N:
            if col == 0:
                prefix = WALL["top_left"]
            elif west:
                prefix = WALL["top_join"]
            else:
                prefix = WALL["horizontal"][0]
            if is_last_col:
                sufix = WALL["top_right"]
        elif dir is Dir.S:
            return MazeText._get_bottom_wall(
                bool(west),
                bool(south),
                prev_south,
                bottom_west,
                is_last_row,
                is_last_col,
            )

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
            case _: return ""

    @staticmethod
    def get_path_text(bitmask: int | None) -> tuple[str, str, str]:
        if bitmask is None:
            return WALL["empty"], WALL["empty"], WALL["empty"]

        prefix = WALL["path"] if bitmask & Dir.W else WALL["empty"]

        if bitmask == Dir.N | Dir.S: mid = WALL["vertical"]
        elif bitmask == Dir.N | Dir.E: mid = WALL["bottom_left"]
        elif bitmask == Dir.N | Dir.W: mid = WALL["bottom_right"]
        elif bitmask == Dir.S | Dir.E: mid = WALL["top_left"]
        elif bitmask == Dir.S | Dir.W: mid = WALL["top_right"]
        else: mid = WALL["path"]

        sufix = WALL["path"] if bitmask & Dir.E else WALL["empty"]

        return prefix, mid, sufix

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

    def append_path(self, char: str) -> None:
        """Add maze path characters to be printed. """
        self.append(char, style="maze.path")

    def append_entry(self) -> None:
        """Add entry character to be printed. """
        self.append(WALL["entry"], style="maze.entry")

    def append_exit(self) -> None:
        """Add exit character to be printed. """
        self.append(WALL["entry"], style="maze.exit")

    def append_empty(self, width: int = 1) -> None:
        """Add exit character to be printed. """
        self.append(WALL["empty"] * width, style="maze.exit")

    def append_nl(self) -> None:
        """Add new line character. """
        self.append("\n")
