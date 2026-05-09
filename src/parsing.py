from global_state import GlobalState
from gui.error_popup import ErrorPopup
import pyray as pr
from hub import Hub


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
        data: list = [[], []]
        raw_data: list = []
        temp_nb_drones: int = 0
        if self.draw_error is False:
            try:
                with open(path, 'r') as f:
                    for line in f.readlines():
                        line_split = line.split()
                        if self.is_comments is False:
                            continue
                        # print(line_split)
                        if self.is_comments(line_split) and line_split != []:
                            raw_data.append(line_split)
                        
            except (FileNotFoundError, PermissionError, UnicodeDecodeError) as e:
                print(f"Caught error {e}")
                self.draw_error = True
                self.error_text = str(e)
        if self.draw_error is False:
            try:
                if raw_data[0][0] != "nb_drones:":
                    print("Error")
                    self.draw_error = True
                    self.error_text = "nb_drones not found"
                else:
                    temp_nb_drones = raw_data[0][0]
            except (IndexError) as e:
                print(f"Caught error {e}")
                self.draw_error = True
                self.error_text = str(e)

        # check number of start and end hub
        if self.draw_error is False:
            print(raw_data)
            count_start_hub = 0
            count_end_hub = 0
            for i in range(len(raw_data)):
                count_start_hub += raw_data[i][0].count("start_hub:")
                count_end_hub += raw_data[i][0].count("end_hub:")
            print(count_start_hub)
            if count_start_hub != 0:
                self.draw_error = True
                self.error_text = "Error on parsing number of start_hub not equal to 1"
            if count_end_hub != 0:
                self.draw_error = True
                self.error_text = "Error on parsing number of end_hub not equal to 1"

        # create new data for data list
        if self.draw_error is False:
            for data in raw_data:
                print(data)
                if data[0] == "nb_drones:":
                    pass

        if self.draw_error is False:
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


