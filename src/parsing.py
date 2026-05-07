from global_state import GlobalState
from gui.error_popup import ErrorPopup
import pyray as pr


class Parsing:
    def __init__(self) -> None:
        self.error_popup: ErrorPopup = ErrorPopup()
        self.draw_error: bool = False
        self.error_text: str = ""

    def is_comments(self, line_splits: list) -> bool:
        if '#' in line_splits:
            return False
        return True

    def check_zone_type(self) -> bool:
        all_zone_possible: list = ["normal", "blocked", "restricted", "priority"]
        pass

    def check_file(self, path: str, global_state: dict, window: 'Window') -> None:
        data: dict = {}
        raw_data: list = []
        if self.draw_error == False:
            try:
                with open(path, 'r') as f:
                    for line in f.readlines():
                        line_split = line.split()
                        if self.is_comments == False:
                            continue
                        # print(line_split)
                        if self.is_comments(line_split) and line_split != []:
                            raw_data.append(line_split)
                        
            except (FileNotFoundError, PermissionError, UnicodeDecodeError) as e:
                print(f"Caught error {e}")
                self.draw_error = True
                self.error_text = str(e)
        if self.draw_error == False:
            try:
                if raw_data[0][0] != "nb_drones:":
                    print("Error")
                    self.draw_error = True
                    self.error_text = "nb_drones not first"
            except (IndexError) as e:
                print(f"Caught error {e}")
                self.draw_error = True
                self.error_text = str(e)

        if self.draw_error == False:
            global_state["Current"] = GlobalState.SIMULATION

        else:
            if self.error_popup.draw_error_popup(pr.get_screen_width(), pr.get_screen_height(), self.error_text):
                self.draw_error = False
                window.file_choose = ""
                window.file_tree.path = "."
                window.file_tree.dirs = window.file_tree.get_dir(window.file_tree.path)
                window.file_tree.files = window.file_tree.get_files(window.file_tree.path)
                self.error_text = ""
                global_state["Current"] = GlobalState.START


