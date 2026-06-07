from global_state import GlobalState
from gui.error_popup import ErrorPopup
import pyray as pr
from hub import Hub
from connection import Connection
from typing import TYPE_CHECKING, Any
if TYPE_CHECKING:
    from window import Window
import os


class Parsing:
    def __init__(self) -> None:
        self.error_popup: ErrorPopup = ErrorPopup()
        self.draw_error: bool = False
        self.error_text: str = ""

    def is_comments(self, line_splits: list[Any]) -> bool:
        if '#' in line_splits:
            return False
        return True

    def check_zone_type(self, zone_verif: str) -> bool:
        all_zone_possible: list[str] = ["normal",
                                        "blocked",
                                        "restricted",
                                        "priority"]
        if zone_verif not in all_zone_possible:
            return False
        return True

    def check_options_hub(self, option_check: str) -> bool:
        all_options_hub = ["zone", "color", "max_drones"]
        if option_check not in all_options_hub:
            return False
        return True

    def check_options_connection(self, option_check: str) -> bool:
        all_options_connection = ["max_link_capacity"]
        if option_check not in all_options_connection:
            return False
        return True

    def check_zone_name(self, r_data: list[Any]) -> None:
        buffer_name: list[str] = []
        for hub in r_data[0]:
            if hub.name not in buffer_name:
                buffer_name.append(hub.name)
            elif hub.name in buffer_name:
                self.draw_error = True
                self.error_text = "Parsing error, duplicate name \
found"
            if "-" in hub.name:
                self.draw_error = True
                self.error_text = "Parsing error, found '-' in \
hub name"
            if " " in hub.name:
                self.draw_error = True
                self.error_text = "Parsing error, found space in hub name"
        for connection in r_data[1]:
            if connection.from_hub not in buffer_name:
                self.draw_error = True
                self.error_text = f"""Parsing error, name:
{connection.from_hub}:\ndon't exist in hub name"""

    def check_capacity_positive(self, r_data: list[Any]) -> None:
        for hub in r_data[0]:
            if int(hub.max_drones) < 0:
                self.draw_error = True
                msg = "Parsing error, max_drones can't be \
negative: {}".format(hub.max_drones)
                self.error_text = msg + " found"
        for connection in r_data[1]:
            if int(connection.max_link_capacity) < 0:
                self.draw_error = True
                msg = "Parsing error, max_link_capacity \
can't be negative: {}".format(
                    connection.max_link_capacity)
                self.error_text = msg + " found"

    def add_hub(self, data: list[Any],
                temp_nb_drones: int, r_data: list[Any]) -> int:
        hub_option_parsed: dict[str, Any] = {
            "zone": "normal",
            "color": "None",
            "max_drones": 1
        }
        # print(data)
        if len(data) > 4:
            args = data[4]
            if ("[" not in args or "]" not in args):
                self.draw_error = True
                self.error_text = "Error with bracket"
                return 1
            args = args.replace('[', '').replace(']', '')
            args = args.split(',')
            try:
                for arg in args:
                    arg = arg.split("=")
                    if self.check_options_hub(arg[0]) is False:
                        self.draw_error = True
                        msg = "Error on hub option {} in \
invalid".format(arg[0])
                        self.error_text = msg
                        break
                    if arg:
                        pass
                    hub_option_parsed.update({arg[0]: arg[1]})
            except (IndexError) as e:
                print(f"Caught error {e}")
                self.draw_error = True
                self.error_text = str(e)
                return 1
            # print(hub_option_parsed)
        if data[0] == "start_hub:":
            try:
                hub_instance = Hub(
                    name=data[1], x=data[2], y=data[3],
                    nb_drones=int(temp_nb_drones),
                    type_hub="start_hub",
                    zone=hub_option_parsed["zone"],
                    color=hub_option_parsed["color"],
                    max_drones=temp_nb_drones)
            except (ValueError, IndexError) as e:
                print(f"Caught error {e}")
                self.draw_error = True
                self.error_text = str(e)
                return 1
            r_data[0].append(hub_instance)
        elif data[0] == "hub:":
            try:
                hub_instance = Hub(
                    name=data[1], x=data[2], y=data[3],
                    type_hub="hub",
                    zone=hub_option_parsed["zone"],
                    color=hub_option_parsed["color"],
                    max_drones=hub_option_parsed["max_drones"])
            except (ValueError, IndexError) as e:
                print(f"Caught error {e}")
                self.draw_error = True
                self.error_text = str(e)
                return 1
            r_data[0].append(hub_instance)
        elif data[0] == "end_hub:":
            try:
                hub_instance = Hub(
                    name=data[1], x=data[2], y=data[3],
                    type_hub="end_hub",
                    zone=hub_option_parsed["zone"],
                    color=hub_option_parsed["color"],
                    max_drones=temp_nb_drones)
            except (ValueError, IndexError) as e:
                print(f"Caught error {e}")
                self.draw_error = True
                self.error_text = str(e)
                return 1
            r_data[0].append(hub_instance)
        if len(r_data[0]) > 0:
            if self.check_zone_type(r_data[0][-1].zone) is False:
                self.draw_error = True
                self.error_text = (f"Error on parsing invalid zone \
entered for "
                                   f"{r_data[0][-1].name}")
                return 1
        return 0

    def add_connection(self, data: list[Any], r_data: list[Any]) -> int:
        options_default = {"max_link_capacity": 1}
        if data[0] == "connection:":
            if len(data) > 2:
                option = data[2]
                if ("[" not in option or "]" not in option):
                    self.draw_error = True
                    self.error_text = "Error with bracket in connection"
                    return 1
                option = option.replace('[', '').replace(']', '')
                try:
                    option = option.split("=")
                    if self.check_options_connection(option[0]) is False:
                        self.draw_error = True
                        msg = "Error on connection option \
{} is invalid".format(option[0])
                        self.error_text = msg
                    if option:
                        pass
                    options_default.update({option[0]: option[1]})
                except (IndexError) as e:
                    print(f"Caught error {e}")
                    self.draw_error = True
                    self.error_text = str(e)
                    return 1
        if data[0] == "connection:":
            data_split = data[1].split("-")
            try:
                connection_instance = Connection(
                    from_hub=data_split[0],
                    to_hub=data_split[1],
                    max_link_capacity=options_default["max_link_capacity"])
            except (ValueError, IndexError) as e:
                print(f"Caught error {e}")
                self.draw_error = True
                self.error_text = str(e)
                return 1
            r_data[1].append(connection_instance)
        return 0

    def get_file_name(self, r_data: list[Any], path: str) -> None:
        path_split = path.split('/')
        r_data[2] = path_split[-1]

    def check_max_drones_number(self, r_data: list[Any]) -> None:
        try:
            for hub in r_data[0]:
                int(hub.max_drones)
        except ValueError as e:
            self.draw_error = True
            self.error_text = f"{e}"

    def check_max_link_capacity(self, r_data: list[Any]) -> None:
        try:
            for connection in r_data[1]:
                int(connection.max_link_capacity)
        except ValueError as e:
            self.draw_error = True
            self.error_text = f"{e}"

    def check_duplicate_connection(self, r_data: list[Any]) -> None:
        buffer_connection: list[tuple[str, str]] = []
        for connection in r_data[1]:
            if (((connection.from_hub, connection.to_hub)
                 not in buffer_connection)
                and ((connection.to_hub, connection.from_hub)
                     not in buffer_connection)):
                buffer_connection.append(
                    (connection.from_hub, connection.to_hub))
            else:
                self.draw_error = True
                self.error_text = (
                    f"Parsing error, duplicate connection \
found: {connection.from_hub} - \
{connection.to_hub}")

    def check_position_duplicate(self, r_data: list[Any]) -> None:
        buffer_position: list[tuple[int, int]] = []
        for hub in r_data[0]:
            if (hub.x, hub.y) not in buffer_position:
                buffer_position.append((hub.x, hub.y))
            else:
                self.draw_error = True
                self.error_text = (
                    f"Parsing error, duplicate position \
found: {hub.x} - {hub.y}")

    def check_file(self, path: str, global_state: dict[str, Any],
                   window: 'Window') -> list[Any]:
        r_data: list[Any] = [[], [], []]
        raw_data: list[Any] = []
        temp_nb_drones: int = 0
        self.get_file_name(r_data, path)
        print(r_data[2])
        if self.draw_error is False:
            try:
                with open(path, 'r') as f:
                    for line in f.readlines():
                        line_split = line.split()
                        if (self.is_comments(line_split) and
                                line_split != []):
                            raw_data.append(line_split)

            except (FileNotFoundError, PermissionError,
                    UnicodeDecodeError) as e:
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
            if type(temp_nb_drones) is not int:
                if not raw_data[0][1].isdigit():
                    self.draw_error = True
                    self.error_text = ("Caught error, nb_drones is \
not a number or is negatives")

        # check number of start and end hub
        if self.draw_error is False:
            # print(raw_data)
            count_start_hub = 0
            count_end_hub = 0
            for i in range(len(raw_data)):
                count_start_hub += raw_data[i][0].count("start_hub:")
                count_end_hub += raw_data[i][0].count("end_hub:")
                if len(raw_data[i]) > 4:
                    raw_data[i][4:] = [",".join(raw_data[i][4:])]
            if count_start_hub != 1:
                self.draw_error = True
                self.error_text = ("Error on parsing number of \
start_hub not equal to 1")
            if count_end_hub != 1:
                self.draw_error = True
                self.error_text = ("Error on parsing number of \
end_hub not equal to 1")

        # create new data for data list
        if self.draw_error is False:
            for data in raw_data:
                # print(data)
                self.add_hub(data, temp_nb_drones, r_data)
                self.add_connection(data, r_data)
            for hub in r_data[0]:
                print(hub.name, hub.x, hub.y, hub.type_hub,
                      hub.zone, hub.color, hub.max_drones)
        if self.draw_error is False:
            self.check_duplicate_connection(r_data)
        if self.draw_error is False:
            self.check_zone_name(r_data)
        if self.draw_error is False:
            self.check_max_drones_number(r_data)
        if self.draw_error is False:
            self.check_position_duplicate(r_data)
        if self.draw_error is False:
            self.check_max_link_capacity(r_data)
        if self.draw_error is False:
            self.check_capacity_positive(r_data)
        if self.draw_error is False:
            global_state["Current"] = GlobalState.FIND

        else:
            err_popup_result = (
                self.error_popup.draw_error_popup(
                    pr.get_screen_width(),
                    pr.get_screen_height(),
                    self.error_text))
            if err_popup_result:
                self.draw_error = False
                window.file_choose = ""
                window.file_tree.path = (
                    os.path.dirname(window.file_tree.path))
                if window.file_tree.path == "":
                    window.file_tree.path = "."
                window.file_tree.dirs = (
                    window.file_tree.get_dir(window.file_tree.path))
                window.file_tree.files = (
                    window.file_tree.get_files(window.file_tree.path))
                self.error_text = ""
                global_state["Current"] = GlobalState.START
        return r_data
