import pyray as pr


class AlgoChoice:
    def __init__(self) -> None:
        self.algos: list = ["Bellman-Ford", "Dijkstra", "A* (A-Star)"]
        self.active_index = pr.ffi.new('int *', 0)
        self.algos_string: str = ";".join(self.algos)

    def draw_choice_window(self, win_width: int, win_height: int) -> str:
        rect = pr.Rectangle(win_width / 2 + 125, win_height / 2, 250, 160)
        pr.gui_window_box(rect, "Configuration")
        pr.gui_label(pr.Rectangle(rect.x + 20, rect.y + 40, rect.width - 40, 20), "Choisir l'algorithme :")
        pr.gui_combo_box(
            pr.Rectangle(rect.x + 20, rect.y + 70, rect.width - 40, 30), 
            self.algos_string, 
            self.active_index
        )
        mapping = ["bellman", "dijkstra", "astar"]
        temp = self.active_index[0]
        return mapping[temp]
