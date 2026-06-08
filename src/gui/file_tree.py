import pyray as pr
import os
from typing import Any
from global_state import GlobalState


class FileTree():
    def __init__(self) -> None:
        self.path: str = "."
        self.view: pr.Rectangle = pr.Rectangle(0, 0, 0, 0)
        self.scroll: pr.Vector2 = pr.Vector2(0, 0)
        self.dirs: list[str] = self.get_dir(self.path)
        self.files: list[str] = self.get_files(self.path)
        self.last_path: list[str] = []

    def get_dir(self, path: str) -> list[str]:
        not_included_dirs: list[str] = ["__pycache__", ".git", ".venv",
                                        ".mypy_cache"]
        dirs_list: list[str] = [
            d for d in os.listdir(path)
            if os.path.isdir(os.path.join(path,
                             d)) and d not in not_included_dirs
        ]
        return dirs_list

    def get_files(self, path: str) -> list[str]:
        files_list: list[str] = [
            f for f in os.listdir(path)
            if os.path.isfile(os.path.join(path, f))
        ]
        return files_list

    def select_map(self, win_width: int, win_height: int,
                   global_state: dict[str, Any]) -> str:
        items_height: int = 35
        total_content_height: int = (len(self.dirs) +
                                     len(self.files)) * items_height
        map_selec_rect: pr.Rectangle = pr.Rectangle((win_width / 2) - 125,
                                                    win_height / 2,
                                                    250, 300)
        map_select_cont_rect: pr.Rectangle = pr.Rectangle(0,
                                                          0,
                                                          (map_selec_rect.width
                                                           - 20),
                                                          total_content_height)
        pr.gui_window_box(map_selec_rect, "Select map")
        pr.gui_scroll_panel(map_selec_rect, "Select map",
                            map_select_cont_rect, self.scroll, self.view)
        current_y: float = self.view.y + self.scroll.y + 10
        pr.begin_scissor_mode(
            int(self.view.x),
            int(self.view.y),
            int(self.view.width),
            int(self.view.height)
        )
        selected_file: str = ""

        for _, dir in enumerate(self.dirs):
            if pr.gui_label_button(pr.Rectangle(self.view.x + 5,
                                                current_y,
                                                self.view.width - 10,
                                                30), f"#001# {dir}"):
                self.path = os.path.join(self.path, dir)
                self.scroll.y = 0
                self.dirs = self.get_dir(self.path)
                self.files = self.get_files(self.path)
            current_y += items_height
        for _, file in enumerate(self.files):
            if pr.gui_label_button(pr.Rectangle(self.view.x + 5,
                                                current_y,
                                                self.view.width,
                                                30), f"#010#{file}"):
                global_state["Current"] = GlobalState.PARSING
                if (self.path != "."):
                    selected_file = self.path + f"/{file}"
                else:
                    selected_file = file
            current_y += items_height
        pr.end_scissor_mode()

        if pr.gui_button(pr.Rectangle(map_selec_rect.x + map_selec_rect.width
                                      / 3,
                                      map_selec_rect.y + 2,
                                      20, 20), "#056#"):
            try:
                self.path = os.path.dirname(self.path)
                self.scroll.y = 0
                self.dirs = self.get_dir(self.path)
                self.files = self.get_files(self.path)
            except FileNotFoundError:
                print("Can't go more back")
                self.path = "."
        if selected_file:
            return selected_file
        return self.path
