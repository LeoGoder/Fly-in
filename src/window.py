from hub import Hub
import pyray as pr
from gui.file_tree import FileTree
from global_state import GlobalState
from parsing import Parsing
import os


class Cam():
    def __init__(self) -> None:
        self.cam: pr.Camera3D = pr.Camera3D()
        self.cam.fovy = 45
        self.cam.position = pr.Vector3(0.0, 20.0, 20.0)
        self.cam.projection = pr.CameraProjection.CAMERA_PERSPECTIVE
        self.cam.target = pr.Vector3(0.0, 0.0, 0.0)       
        self.cam.up = pr.Vector3(0.0, 1.0, 0.0)

    def get_camera_3D(self) -> pr.Camera3D:
        return self.cam

    def move_cam(self, dt: float) -> None:
        speed = 10.0 * dt
        if pr.is_key_down(pr.KeyboardKey.KEY_A):
            self.cam.target.x -= speed
            self.cam.position.x -= speed
        if pr.is_key_down(pr.KeyboardKey.KEY_D):
            self.cam.target.x += speed
            self.cam.position.x += speed
        if pr.is_key_down(pr.KeyboardKey.KEY_W):
            self.cam.target.z -= speed
            self.cam.position.z -= speed
        if pr.is_key_down(pr.KeyboardKey.KEY_S):
            self.cam.target.z += speed
            self.cam.position.z += speed
        pr.update_camera(self.cam, pr.CameraProjection.CAMERA_PERSPECTIVE)


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
        self.data: list = [[], []]
        self.dt: float
        self.change_map: bool = False
        self.show_change_map: bool = False

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

    def change_maps(self) -> None:
        if self.change_map is True:
            self.change_map = False
        else:
            self.file_choose = self.file_tree.select_map(self.width, self.height, self.glob_state)
            try:
                if os.path.isfile(self.file_choose):
                    self.show_change_map = False
            except Exception as e:
                print(e)
                print(type(self.file_choose))

    def mode3d_scene_manager(self, data: list) -> None:
        self.cam.move_cam(self.dt)
        for hub in data[0]:
            position = pr.Vector3(int(hub.x) * 5, 0.0, int(hub.y) * 5)
            pr.draw_cube(position, 1.5, 1.5, 1.5, pr.PURPLE)
            pr.draw_cube_wires(position, 1.5, 1.5, 1.5, pr.BLACK)
        for connection in data[1]:
            from_hub: Hub
            to_hub: Hub
            for hub in data[0]:
                if connection.from_hub == hub.name:
                    from_hub = hub
                if connection.to_hub == hub.name:
                    to_hub = hub
            pr.draw_line_3d(pr.Vector3(int(from_hub.x) * 5, 0.0, int(from_hub.y) * 5), pr.Vector3(int(to_hub.x) * 5, 0.0, int(to_hub.y) * 5), pr.WHITE)

    def gui_scene_manager(self) -> None:
        if (self.glob_state["Current"] == GlobalState.START):
            self.start_gui_scene()
        elif (self.glob_state["Current"] == GlobalState.PARSING):
            self.data = self.parsing.check_file(self.file_choose, self.glob_state, self)
        elif (self.glob_state["Current"] == GlobalState.SIMULATION):
            if pr.is_key_pressed(pr.KeyboardKey.KEY_F):
                self.file_choose = ""
                self.file_tree.path = "."
                self.file_tree.dirs = self.file_tree.get_dir(self.file_tree.path)
                self.file_tree.files = self.file_tree.get_files(self.file_tree.path)
                if self.change_map is True:
                    self.change_map = False
                else:
                    self.change_map = True
                if self.show_change_map is False:
                    self.show_change_map = True 
                else:
                    self.show_change_map = False
            if self.show_change_map is True:
                self.change_maps()
        pr.draw_fps(10, 10)

    def frame_counter(self):
        self.current_frame += 1
        if self.current_frame > self.max_fps:
            self.current_frame = 0

    def main_loop(self) -> None:
        pr.set_target_fps(self.max_fps)
        res_loc = pr.get_shader_location(self.shader, "resolution")
        time_loc = pr.get_shader_location(self.shader, "time")
        font = pr.load_font("assets/PixelOperator.ttf")
        pr.gui_load_style("assets/genesis.rgs")
        pr.gui_set_font(font)
        while not pr.window_should_close():
            self.dt = pr.get_frame_time()
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
            if (self.glob_state["Current"] == GlobalState.SIMULATION):
                self.mode3d_scene_manager(self.data)
            pr.end_mode_3d()
            self.gui_scene_manager()
            pr.end_drawing()
            self.frame_counter()
        pr.unload_shader(self.shader)
        pr.unload_font(font)
        pr.close_window()
