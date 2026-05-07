import pyray as pr
import os
from global_state import GlobalState


class FileTree():
    def __init__(self) -> None:
        self.path: str = "."
        self.view: pr.Rectangle = pr.Rectangle(0, 0, 0, 0)
        self.scroll: pr.Vector2 = pr.Vector2(0, 0)
        self.dirs: list = self.get_dir(self.path)
        self.files: list = self.get_files(self.path)
        self.last_path: list = []

    def get_dir(self, path: str) -> list:
        not_included_dirs: list = ["__pycache__", ".git", ".venv", ".mypy_cache"]
        dirs_list: list = [
            d for d in os.listdir(path)
            if os.path.isdir(os.path.join(path, d)) and d not in not_included_dirs
        ]
        return dirs_list

    def get_files(self, path: str) -> list:
        files_list: list = [
            f for f in os.listdir(path)
            if os.path.isfile(os.path.join(path, f))
        ]
        return files_list

    def select_map(self, win_width: int, win_height: int, global_state: dict) -> str:
        items_height: int = 35
        total_content_height: int = (len(self.dirs) + len(self.files)) * items_height
        map_selection_rect: pr.Rectangle = pr.Rectangle((win_width / 2) - 125, win_height / 2, 250, 300)
        map_selection_content_rect: pr.Rectangle = pr.Rectangle(0, 0, map_selection_rect.width - 20, total_content_height)
        pr.gui_window_box(map_selection_rect, "Select map")
        pr.gui_scroll_panel(map_selection_rect, "Select map", map_selection_content_rect, self.scroll, self.view)
        current_y: float = self.view.y + self.scroll.y + 10
        pr.begin_scissor_mode(
            int(self.view.x), int(self.view.y), int(self.view.width), int(self.view.height)
        )

        for _, dir in enumerate(self.dirs):
            if pr.gui_label_button(pr.Rectangle(self.view.x + 5, current_y, self.view.width - 10, 30), f"#001# {dir}"):
                self.path = os.path.join(self.path, dir)
                self.scroll.y = 0
                self.dirs = self.get_dir(self.path)
                self.files = self.get_files(self.path)
            current_y += items_height
        for _, file in enumerate(self.files):
            if pr.gui_label_button(pr.Rectangle(self.view.x + 5, current_y, self.view.width, 30), f"#010#{file}"):
                global_state["Current"] = GlobalState.PARSING
                if (self.path != "."):
                    self.path += f"/{file}"
                else:
                    self.path = file
            current_y += items_height
        pr.end_scissor_mode()

        if pr.gui_button(pr.Rectangle(map_selection_rect.x + map_selection_rect.width / 3, map_selection_rect.y + 2, 20, 20), "#056#"):
            try:
                self.path = os.path.dirname(self.path)
                self.scroll.y = 0
                self.dirs = self.get_dir(self.path)
                self.files = self.get_files(self.path)
            except FileNotFoundError:
                print("Can't go more back")
                self.path = "."
        return self.path

