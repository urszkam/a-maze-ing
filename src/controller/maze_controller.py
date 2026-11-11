from enum import IntEnum
from time import sleep
from typing import Any

from readchar import readkey
from rich.console import Group
from rich.live import Live
from rich.text import Text

from ..service import Maze, MazeGenerator
from ..constants import MENU, WALL, WIDTH
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


def _append_wall_or_path(
        maze_text: MazeText, dir: Dir,
        wall_text: str, path_mask: int | None) -> None:
    """Append a wall segment, replacing it with a path where applicable."""
    if path_mask is None or not path_mask & dir:
        maze_text.append_wall(wall_text)
        return

    match dir:
        case Dir.S:
            maze_text.append_wall(wall_text[:2])
            maze_text.append_path(WALL["vertical"])
            maze_text.append_wall(wall_text[3:])
        case Dir.E:
            maze_text.append_path(WALL["horizontal"][0])
        case _:
            maze_text.append_wall(wall_text)


def _append_middle_path(
        maze_text: MazeText, path_mask: int, is_entry: bool,
        is_exit: bool) -> None:
    """Append the horizontal representation of a path cell."""
    prefix, mid, sufix = MazeText.get_path_text(path_mask)
    maze_text.append_path(prefix)

    if is_entry:
        maze_text.append_entry()
    elif is_exit:
        maze_text.append_exit()
    else:
        maze_text.append_path(mid)

    maze_text.append_path(sufix)


def _display_maze(maze: Maze) -> MazeText:
    """Render a maze snapshot for terminal display.

    Args:
        maze: Maze instance to render.

    Returns:
        Text representation of the generated maze.
    """
    maze_text = MazeText()

    for row_idx, row in enumerate(maze.walls):
        for dir in Dir:
            if dir is Dir.N and row_idx != 0:
                continue

            for col_idx in range(len(row)):
                if dir is Dir.W and col_idx != 0:
                    continue

                is_logo = maze.is_logo(row_idx, col_idx)
                is_entry = maze.is_entry(row_idx, col_idx)
                is_exit = maze.is_exit(row_idx, col_idx)
                path_mask = maze.get_path_cell_bitmask(row_idx, col_idx)

                # middle part of the cell
                if dir is Dir.E:
                    if is_logo:
                        maze_text.append_logo()
                    elif not path_mask:
                        maze_text.append_empty(WIDTH)
                    else:
                        _append_middle_path(
                            maze_text, path_mask, is_entry, is_exit
                        )
                # append border part of the cell
                wall_text = MazeText.get_wall_text(
                    dir=dir, row=row_idx, col=col_idx, maze=maze.walls
                )
                if is_logo and dir is Dir.S:
                    maze_text.append_wall_logo(wall_text)
                else:
                    _append_wall_or_path(
                        maze_text, dir, wall_text, path_mask
                    )

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
    """Animate passage opening with duration proportional to maze size.

    Args:
        live: Active Rich Live display to be updated.
        generator: Object that generates maze.

    Returns:
        Text representation of maze.
    """
    path_visible: bool = cp.show_hide_path(False)
    for frame in generator.generate_maze_frames():
        maze = generator.store_maze(frame)
        maze_text = _display_maze(maze)
        live.update(_build_frame(
            maze_text, generator.algorithm_name), refresh=True)
        sleep(0.01)
    cp.show_hide_path(path_visible)

    return maze_text


def run_app(
        config: dict[str, Any] = {"width": 13, "height": 13,
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
