# import parsing as par
import pyray as pr
from enum import IntEnum

from gui.file_tree import FileTree


class GlobalState(IntEnum):
    START = 1
    SIMULATION = 2


def main() -> None:
    pr.set_config_flags(pr.ConfigFlags.FLAG_WINDOW_RESIZABLE)
    pr.init_window(800, 800, "Fly-in")
    glob_state = GlobalState.START
    file_tree = FileTree()
    while not pr.window_should_close():
        pr.begin_drawing()
        pr.clear_background(pr.WHITE)
        if (glob_state == GlobalState.START):
            file_tree.select_map()
        pr.end_drawing()
    pr.close_window()


if __name__ == "__main__":
    main()
