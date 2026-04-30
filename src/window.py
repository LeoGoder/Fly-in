import pyray as pr
from gui.file_tree import FileTree
from global_state import GlobalState

class Window():
    def __init__(self) -> None:
        self.width = 800
        self.height = 800
        self.glob_state = GlobalState.START

    def start_window(self) -> None:
        pr.set_config_flags(pr.ConfigFlags.FLAG_WINDOW_RESIZABLE)
        pr.init_window(800, 800, "Fly-in")
        self.main_loop()

    def main_loop(self) -> None:
        file_tree = FileTree()
        while not pr.window_should_close():
            pr.begin_drawing()
            pr.clear_background(pr.SKYBLUE)
            if (self.glob_state == GlobalState.START):
                file_tree.select_map()
            pr.end_drawing()
        pr.close_window()
