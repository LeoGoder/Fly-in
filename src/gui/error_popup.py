import pyray as pr

class ErrorPopup():
    def __init__(self) -> None:
        self.width: int = 200
        self.height: int = 200
        self.text_font_size: int = 16

    def draw_error_popup(self, win_width: int, win_height: int, text: str) -> int:
        len_text  = pr.measure_text(text, self.text_font_size)
        error_rect = pr.Rectangle((win_width / 2) - (self.width / 2) - (len_text / 2), (win_height / 2) - (self.height / 2), self.width + len_text, self.height)
        if pr.gui_window_box(error_rect, "ERROR"):
            return 1
        pr.gui_label(pr.Rectangle(error_rect.x + (len_text / 3), error_rect.y, len_text, error_rect.height), text)
        return 0


