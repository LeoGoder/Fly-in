import pyray as pr
from gui.file_tree import FileTree
from global_state import GlobalState
from parsing import Parsing


class Window():
    def __init__(self) -> None:
        self.width = pr.get_screen_width()
        self.height = pr.get_screen_width()
        self.glob_state = {"Current": GlobalState.START}
        self.file_choose = ""

    def start_window(self) -> None:
        pr.set_config_flags(pr.ConfigFlags.FLAG_WINDOW_RESIZABLE)
        pr.init_window(self.width, self.height, "Fly-in")
        self.width = pr.get_screen_width()
        self.height = pr.get_screen_width()
        self.main_loop()

    def main_loop(self) -> None:
        file_tree = FileTree()
        parsing = Parsing()
        pr.set_target_fps(120)
        while not pr.window_should_close():
            pr.begin_drawing()
            pr.clear_background(pr.SKYBLUE)
            if (self.glob_state["Current"] == GlobalState.START):
                self.file_choose = file_tree.select_map(self.width, self.height, self.glob_state)
            if (self.glob_state["Current"] == GlobalState.PARSING):
                parsing.check_file(self.file_choose, self.glob_state)
            pr.end_drawing()
        pr.close_window()
