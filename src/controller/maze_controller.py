from enum import IntEnum
from time import sleep
from typing import Any

import numpy as np

from readchar import readkey
from rich.console import Group
from rich.live import Live
from rich.text import Text

from ..service import MazeGenerator
from ..constants import MENU, WALL
from .console_printer import ConsolePrinter, MazeText
from ..constants import Dir


cp = ConsolePrinter()


class MenuOption(IntEnum):
    REGENERATE = 1
    SHOW_HIDE = 2
    ROTATE_WALL_COLORS = 3
    ROTATE_42_COLORS = 4
    CHANGE_ALGORITHM = 5
    EXIT = 6


def _choose_option() -> tuple[MenuOption | None, str]:
    """Choose one of menu options to perform action.

    Returns:
        Chosen MenuOption or None in case of incorrect choice.
        Error mesage in case of incorrect choice.
    """
    key = readkey()
    try:
        option_num = int(key)
    except ValueError:
        return None, f"Input not of integer type: {key!r}"

    if min(MenuOption).value <= option_num <= max(MenuOption).value:
        return MenuOption(option_num), ""

    return None, f"Value outside the requested range: {option_num}"


def _display_maze(generator: MazeGenerator) -> MazeText:
    """Generate new maze and prepare it for terminal display.

    Args:
        generator: object responsible for maze generation.

    Returns:
        Text representation of the generated maze.
    """
    maze: np.ndarray = generator.generate_maze()
    maze_text = MazeText()

    for row_idx, row in enumerate(maze):
        for dir in Dir:
            if dir is Dir.N and row_idx != 0:
                continue
            for col_idx, col_val in enumerate(row):
                if dir is Dir.W and col_idx != 0:
                    continue

                is_logo = col_val == 15
                if dir is dir.E:
                    if is_logo:
                        maze_text.append_logo()
                    elif (row_idx, col_idx) == generator.entry:
                        maze_text.append_entry()
                    elif (row_idx, col_idx) == generator.exit:
                        maze_text.append_exit()
                    else:
                        maze_text.append_wall(WALL["empty"])

                wall_text = MazeText.get_wall_text(
                    dir=dir, row=row_idx, col=col_idx, maze=maze
                )
                if is_logo and dir is Dir.S:
                    maze_text.append_wall_logo(wall_text)
                else:
                    maze_text.append_wall(wall_text)

            if dir is not Dir.W:
                maze_text.append_nl()

    return maze_text


def _build_frame(
        maze_text: Text,
        algorithm_name: str,
        error_msg: str = "") -> Group:
    """Create frame for specific TUI objects.

    Args:
        maze_text: Text representation of the maze.
        algorithm_name: Value of the current maze generation algorithm.
        error_msg: Optional error message caused by option choice.

    Returns:
        Group of TUI objects: maze, menu, options prompt, error placeholder.
    """
    header, menu = MENU.format(algorithm=algorithm_name).split("\n", 1)
    option_msg = f"Choose {min(MenuOption).value} - {max(MenuOption).value}: "

    return Group(
        maze_text,
        Text(header, style="txt.header"),
        Text(menu, style="txt.menu"),
        Text(option_msg, style="txt.options"),
        Text(error_msg, style="txt.error"),
    )


def _animate_maze(live: Live, generator: MazeGenerator) -> MazeText:
    """Animate new maze display line by line.

    Args:
        live: Active Rich Live display to be updated.
        generator: Object that generates maze.

    Returns:
        Text representation of maze.
    """
    maze_text = _display_maze(generator)
    lines = maze_text.split("\n", allow_blank=True)

    for count in range(1, len(lines) + 1):
        visible = Text("\n").join(lines[:count])
        visible.append("\n" * (len(lines) - count))
        live.update(_build_frame(
            visible, generator.algorithm_name), refresh=True)
        sleep(0.05)

    return maze_text


def run_app(
        config: dict[str, Any] = {"width": 15, "height": 19,
                                  "entry": (0, 0), "exit": (0, 2)}) -> None:
    """Run the maze TUI application.

    Args:
        config: TODO placeholder for tests.
    """
    try:
        generator = MazeGenerator(config)
    except Exception as e:
        cp.error(f"Error while generating maze: {e}")
        return

    option: MenuOption | None = None
    error_msg = ""

    with Live(console=cp, auto_refresh=False) as live:
        maze_text = _animate_maze(live, generator)

        while option != MenuOption.EXIT:
            live.update(
                _build_frame(maze_text, generator.algorithm_name, error_msg),
                refresh=True
            )

            option, error_msg = _choose_option()
            match (option):
                case MenuOption.ROTATE_WALL_COLORS: cp.update_wall_color()
                case MenuOption.ROTATE_42_COLORS: cp.update_42_color()
                case MenuOption.SHOW_HIDE: cp.show_hide_path()
                case MenuOption.REGENERATE:
                    maze_text = _animate_maze(live, generator)
                case MenuOption.CHANGE_ALGORITHM:
                    generator.next_algorithm()
                    maze_text = _animate_maze(live, generator)
                case _: continue

    cp.print("Bye bye!")
