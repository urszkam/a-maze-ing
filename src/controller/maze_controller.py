from enum import IntEnum
from typing import Any

from ..service import MazeGenerator
from ..constants import MENU


class MenuOption(IntEnum):
    REGENERATE = 1
    SHOW_HIDE = 2
    ROTATE_COLORS = 3
    EXIT = 4


def _choose_option() -> MenuOption:
    msg = f"Choose {min(MenuOption).value} - {max(MenuOption).value}: "
    option_num: int | None = None
    input_value: str = ""

    while True:
        try:
            option_num = int(input_value := input(msg))
        except ValueError:
            print(f"Input not of integer type: {input_value}")
            continue

        if min(MenuOption).value <= option_num <= max(MenuOption).value:
            return MenuOption(option_num)

        print(f"Value outside the requested range: {option_num}")


def _display_maze(
        generator: MazeGenerator,
        option: MenuOption | None) -> None:
    """
    """


def _display_menu() -> None:
    """
    """
    print(MENU)


def run_app(config: dict[str, Any] = {}) -> None:
    """
    """
    try:
        generator = MazeGenerator(config)
    except Exception as e:
        print(f"Error while generating maze: {e}")
        return

    option: MenuOption | None = None
    while (option != MenuOption.EXIT):
        _display_maze(generator=generator, option=option)
        _display_menu()
        option = _choose_option()

    print("Bye bye!")
