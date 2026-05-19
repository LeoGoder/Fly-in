from enum import IntEnum


class GlobalState(IntEnum):
    START = 1
    PARSING = 2
    FIND = 3
    SIMULATION = 4
