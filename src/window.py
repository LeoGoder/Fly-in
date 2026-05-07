import pyray as pr
from gui.file_tree import FileTree
from global_state import GlobalState
from parsing import Parsing


class Cam():
    def __init__(self) -> None:
        self.cam: pr.Camera3D = pr.Camera3D()
        self.cam.fovy = 45
        self.cam.position = pr.Vector3(0.0, 0.0, 0.0)
        self.cam.projection = pr.CameraProjection.CAMERA_PERSPECTIVE
        self.cam.target = pr.Vector3(0.0, 0.0, 0.0)       
        self.cam.up = pr.Vector3(0.0, 1.0, 0.0)

    def get_camera_3D(self) -> pr.Camera3D:
        return self.cam

    def move_cam(self) -> None:
        pass


class Window():
    def __init__(self) -> None:
        self.width: int = 0
        self.height: int = 0
        self.glob_state: dict = {"Current": GlobalState.START}
        self.file_choose: str = ""
        self.file_tree: FileTree = FileTree()
        self.parsing: Parsing = Parsing()
        self.cam: Cam = Cam()
        self.g_cam: pr.Camera3D = self.cam.get_camera_3D()
        self.font_size: int = 16
        self.reverse_title: bool = False
        self.current_frame: int = 0
        self.max_fps: int = 60
        self.scale: int = 1
        self.shader: pr.Shader

    def start_window(self) -> None:
        pr.set_config_flags(pr.ConfigFlags.FLAG_WINDOW_RESIZABLE)
        pr.init_window(self.width, self.height, "Fly-in")
        self.shader: pr.Shader = pr.load_shader("", "src/shader_sky.fs")
        self.main_loop()

    def start_gui_scene(self) -> None:
        pr.draw_text("FLY-IN", int(self.width * 0.5) - 94, 60, 64, pr.RAYWHITE)
        pr.draw_text_pro(pr.get_font_default(), "By Lgoderne", pr.Vector2(int(self.width * 0.5) + 94, 130.0), pr.Vector2(0.0, 0.0), -45, self.font_size, 2, pr.YELLOW)
        self.file_choose = self.file_tree.select_map(self.width, self.height, self.glob_state)
        if self.current_frame % 2 == 0:
            if self.reverse_title is False:
                self.font_size += 1
            if self.font_size > 34:
                self.reverse_title = True
            if self.reverse_title is True:
                self.font_size -= 1
            if self.font_size < 16:
                self.reverse_title = False

    def mode3d_scene_manager(self) -> None:
        pass

    def gui_scene_manager(self) -> None:
        if (self.glob_state["Current"] == GlobalState.START):
            self.start_gui_scene()
        if (self.glob_state["Current"] == GlobalState.PARSING):
            self.parsing.check_file(self.file_choose, self.glob_state, self)

    def frame_counter(self):
        self.current_frame += 1
        if self.current_frame > self.max_fps:
            self.current_frame = 0

    def main_loop(self) -> None:
        pr.set_target_fps(self.max_fps)
        res_loc = pr.get_shader_location(self.shader, "resolution")
        time_loc = pr.get_shader_location(self.shader, "time")
        while not pr.window_should_close():
            self.width = pr.get_screen_width()
            self.height = pr.get_screen_height()
            pr.set_shader_value(self.shader, res_loc, pr.Vector2(self.width, self.height), pr.ShaderUniformDataType.SHADER_UNIFORM_VEC2)
            pr.set_shader_value(self.shader, time_loc, pr.ffi.new('float *', pr.get_time()), pr.ShaderUniformDataType.SHADER_UNIFORM_FLOAT)
            pr.begin_drawing()
            pr.clear_background(pr.BLACK)
            pr.begin_shader_mode(self.shader)
            pr.draw_rectangle(0, 0, self.width, self.height, pr.WHITE)
            pr.end_shader_mode()
            pr.begin_mode_3d(self.g_cam)
            pr.end_mode_3d()
            self.gui_scene_manager()
            pr.end_drawing()
            self.frame_counter()
        pr.unload_shader(self.shader)
        pr.close_window()

