import pyray as pr
from gui.file_tree import FileTree
from global_state import GlobalState
from parsing import Parsing


class Window():
    def __init__(self) -> None:
        self.width = 0
        self.height = 0
        self.glob_state = {"Current": GlobalState.START}
        self.file_choose = ""
        self.file_tree = FileTree()
        self.parsing = Parsing()

    def start_window(self) -> None:
        pr.set_config_flags(pr.ConfigFlags.FLAG_WINDOW_RESIZABLE)
        pr.init_window(self.width, self.height, "Fly-in")
        self.main_loop()

    def start_gui_scene(self) -> None:
        # self.width = pr.get_screen_width()
        # self.height = pr.get_screen_width()
        pr.draw_text("FLY-IN", int(self.width * 0.5) - 50, 30, 32, pr.RAYWHITE)
        self.file_choose = self.file_tree.select_map(self.width, self.height, self.glob_state)

    def main_loop(self) -> None:
        pr.set_target_fps(120)
        while not pr.window_should_close():
            self.width = pr.get_screen_width()
            self.height = pr.get_screen_width()
            pr.begin_drawing()
            pr.clear_background(pr.SKYBLUE)
            if (self.glob_state["Current"] == GlobalState.START):
                self.start_gui_scene()
            if (self.glob_state["Current"] == GlobalState.PARSING):
                self.parsing.check_file(self.file_choose, self.glob_state)
            pr.end_drawing()
        pr.close_window()
