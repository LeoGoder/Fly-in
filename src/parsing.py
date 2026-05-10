from global_state import GlobalState
from gui.error_popup import ErrorPopup
import pyray as pr
from hub import Hub
from connection import Connection


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

    def add_hub(self, data: list, temp_nb_drones: int, r_data: list) -> int:
        if data[0] == "start_hub:":
            try:
                hub_instance = Hub(name=data[1], x=data[2], y=data[3], nb_drones=int(temp_nb_drones), type_hub="start_hub")
            except (ValueError, IndexError) as e:
                print(f"Caught error {e}")
                self.draw_error = True
                self.error_text = str(e)
                return 1
            r_data[0].append(hub_instance)
        elif data[0] == "hub:":
            try:
                hub_instance = Hub(name=data[1], x=data[2], y=data[3], type_hub="hub")
            except (ValueError, IndexError) as e:
                print(f"Caught error {e}")
                self.draw_error = True
                self.error_text = str(e)
                return 1
            r_data[0].append(hub_instance)
        elif data[0] == "end_hub:":
            try:
                hub_instance = Hub(name=data[1], x=data[2], y=data[3], type_hub="end_hub")
            except (ValueError, IndexError) as e:
                print(f"Caught error {e}")
                self.draw_error = True
                self.error_text = str(e)
                return 1
            r_data[0].append(hub_instance)
        return 0
    
    def add_connection(self, data: list, r_data: list) -> int:
        if data[0] == "connection:":
            data_split = data[1].split("-")
            try:
                connection_instance = Connection(from_hub=data_split[0], to_hub=data_split[1])
            except (ValueError, IndexError) as e:
                print(f"Caught error {e}")
                self.draw_error = True
                self.error_text = str(e)
                return 1
            r_data[1].append(connection_instance)
        return 0

    def check_file(self, path: str, global_state: dict, window: 'Window') -> list:
        r_data: list = [[], []]
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
                    temp_nb_drones = raw_data[0][1]
            except (IndexError) as e:
                print(f"Caught error {e}")
                self.draw_error = True
                self.error_text = str(e)

        # check number of start and end hub
        if self.draw_error is False:
            # print(raw_data)
            count_start_hub = 0
            count_end_hub = 0
            braces_open = 0
            braces_close = 0
            for i in range(len(raw_data)):
                count_start_hub += raw_data[i][0].count("start_hub:")
                count_end_hub += raw_data[i][0].count("end_hub:")
                if len(raw_data[i]) > 4:
                    raw_data[i][4:] = [",".join(raw_data[i][4:])]
                # for element in raw_data[i]:
                #     braces_open += element.count("[")
                #     braces_close += element.count("]")
                print(raw_data[i])
            # if (braces_open == 0 and braces_close == 0) or (braces_open != braces_close):
            #     self.draw_error = True
            #     self.error_text = "Error on parsing missing brackets or too many brackets"
            if count_start_hub != 1:
                self.draw_error = True
                self.error_text = "Error on parsing number of start_hub not equal to 1"
            if count_end_hub != 1:
                self.draw_error = True
                self.error_text = "Error on parsing number of end_hub not equal to 1"
            print(braces_open)
            print(braces_close)

        # create new data for data list
        if self.draw_error is False:
            for data in raw_data:
                print(data)
                self.add_hub(data, temp_nb_drones, r_data)
                self.add_connection(data, r_data)
            for hub in r_data[0]:
                print(hub.name)
            print(len(r_data[0]))
            # for hub in r_data[1]:
                # print("from: ", hub.from_hub)
                # print("to: ", hub.to_hub)
            print(r_data)

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
        return r_data

