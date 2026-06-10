from enum import IntEnum


class GlobalState(IntEnum):
    START = 1
    PARSING = 2
    FIND = 3
    THREAD = 4
    TRANSIT = 5
    SIMULATION = 6
