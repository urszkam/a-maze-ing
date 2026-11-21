from enum import IntEnum


class Dir(IntEnum):
    """Define cardinal directions as cell wall bitmask flags."""

    N = 1
    W = 8
    E = 2
    S = 4
