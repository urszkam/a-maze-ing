from enum import IntEnum


class MenuOption(IntEnum):
    REGENERATE = 1
    SHOW_HIDE = 2
    ROTATE_WALL_COLORS = 3
    ROTATE_42_COLORS = 4
    CHANGE_ALGORITHM = 5
    EXIT = 6


class Dir(IntEnum):
    N = 1
    W = 8
    E = 2
    S = 4
