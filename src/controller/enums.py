from enum import IntEnum

from ..constants import Dir


class MenuOption(IntEnum):
    REGENERATE = 1
    SHOW_HIDE = 2
    ROTATE_WALL_COLORS = 3
    ROTATE_42_COLORS = 4
    EXIT = 5


__all__ = ["MenuOption", "Dir"]
