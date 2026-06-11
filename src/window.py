import os
import random
import pyray as pr
import threading

from typing import Any
from color import Color
from global_state import GlobalState
from gui.file_tree import FileTree
from hub import Hub
from parsing import Parsing
from algo.bellmanford import BellmanFord


class Cam:
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
        if pr.is_key_down(pr.KeyboardKey.KEY_LEFT_SHIFT):
            speed = 30.0 * dt
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
        if pr.get_mouse_wheel_move() != 0:
            mouse_wheel_movement = pr.get_mouse_wheel_move()
            self.cam.position.y += -mouse_wheel_movement * speed * 10
            self.cam.target.y += -mouse_wheel_movement * speed * 10
        if pr.is_key_down(pr.KeyboardKey.KEY_SPACE):
            self.cam.position.y += speed
            self.cam.target.y += speed
        if pr.is_key_down(pr.KeyboardKey.KEY_LEFT_CONTROL):
            self.cam.position.y -= speed
            self.cam.target.y -= speed

        pr.update_camera(self.cam, pr.CameraProjection.CAMERA_PERSPECTIVE)


class Window:
    def __init__(self) -> None:
        self.width: int = 0
        self.height: int = 0
        self.glob_state: dict[str, Any] = {"Current": GlobalState.START}
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
        self.data: list[Any] = [[], [], []]
        self.dt: float
        self.change_map: bool = False
        self.show_change_map: bool = False
        self.color: Color
        self.spaceship_model: pr.Model
        self.planet_model: dict[str, Any] = {}
        self.planet_rotation: float = 0.0
        self.bellman: BellmanFord
        self.choice: str
        self.drones_index: int = 0
        self.drones_index_max: int = 0
        self.last_drones_position: list[Any] = []
        self.number_drone_move: list[Any] = []
        self.auto_play: bool = False
        self.show_info: bool = False
        self.color_choice = random.choice(list(Color)).value
        self.thread_algo: threading.Thread
        self.loading_model: list[Any] = [[], [], []]

    def start_window(self) -> None:
        pr.set_config_flags(pr.ConfigFlags.FLAG_WINDOW_RESIZABLE)
        pr.init_window(self.width, self.height, "Fly-in")
        self.shader = pr.load_shader("", "src/shader_sky.fs")
        self.main_loop()

    def start_gui_scene(self) -> None:
        pr.draw_text("FLY-IN", int(self.width * 0.5) - 94, 60, 64, pr.RAYWHITE)
        pr.draw_text_pro(
            pr.get_font_default(),
            "By Lgoderne",
            pr.Vector2(int(self.width * 0.5) + 94, 130.0),
            pr.Vector2(0.0, 0.0),
            -45,
            self.font_size,
            2,
            pr.YELLOW,
        )
        self.file_choose = self.file_tree.select_map(
            self.width, self.height, self.glob_state
        )
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
            self.file_choose = self.file_tree.select_map(
                self.width, self.height, self.glob_state
            )
            try:
                if os.path.isfile(self.file_choose):
                    self.show_change_map = False
                    self.drones_index = 0
                    self.number_drone_move = []
                    self.last_drones_position = []
                    self.g_cam.position = pr.Vector3(0.0, 20.0, 20.0)
                    self.g_cam.target = pr.Vector3(0.0, 0.0, 0.0)
                    self.get_random_loading_planet()
            except Exception as e:
                print(e)
                print(type(self.file_choose))

    def mode3d_scene_manager(self, data: list[Any]) -> None:
        if self.show_change_map is False:
            self.cam.move_cam(self.dt)
        for hub in data[0]:
            position = pr.Vector3(int(hub.x) * 5, 0.0, int(hub.y) * 5)
            match hub.color:
                case "green":
                    pr.draw_model_ex(
                        self.planet_model["green"],
                        position,
                        pr.Vector3(0, 1, 0),
                        self.planet_rotation,
                        pr.Vector3(1.5, 1.5, 1.5),
                        pr.WHITE,
                    )
                case "blue":
                    pr.draw_model_ex(
                        self.planet_model["blue"],
                        position,
                        pr.Vector3(0, 1, 0),
                        self.planet_rotation,
                        pr.Vector3(1.5, 1.5, 1.5),
                        pr.WHITE,
                    )
                case "red":
                    pr.draw_model_ex(
                        self.planet_model["red"],
                        position,
                        pr.Vector3(0, 1, 0),
                        self.planet_rotation,
                        pr.Vector3(1.5, 1.5, 1.5),
                        pr.WHITE,
                    )
                case "orange":
                    pr.draw_model_ex(
                        self.planet_model["orange"],
                        position,
                        pr.Vector3(0, 1, 0),
                        self.planet_rotation,
                        pr.Vector3(1.5, 1.5, 1.5),
                        pr.WHITE,
                    )
                case "purple":
                    pr.draw_model_ex(
                        self.planet_model["purple"],
                        position,
                        pr.Vector3(0, 1, 0),
                        self.planet_rotation,
                        pr.Vector3(1.5, 1.5, 1.5),
                        pr.WHITE,
                    )
                case "gold":
                    pr.draw_model_ex(
                        self.planet_model["gold"],
                        position,
                        pr.Vector3(0, 1, 0),
                        self.planet_rotation,
                        pr.Vector3(1.5, 1.5, 1.5),
                        pr.WHITE,
                    )
                case "cyan":
                    pr.draw_model_ex(
                        self.planet_model["cyan"],
                        position,
                        pr.Vector3(0, 1, 0),
                        self.planet_rotation,
                        pr.Vector3(1.5, 1.5, 1.5),
                        pr.WHITE,
                    )
                case "yellow":
                    pr.draw_model_ex(
                        self.planet_model["yellow"],
                        position,
                        pr.Vector3(0, 1, 0),
                        self.planet_rotation,
                        pr.Vector3(1.5, 1.5, 1.5),
                        pr.WHITE,
                    )
                case "black":
                    pr.draw_model_ex(
                        self.planet_model["black"],
                        position,
                        pr.Vector3(0, 1, 0),
                        self.planet_rotation,
                        pr.Vector3(1.5, 1.5, 1.5),
                        pr.WHITE,
                    )
                case "lime":
                    pr.draw_model_ex(
                        self.planet_model["lime"],
                        position,
                        pr.Vector3(0, 1, 0),
                        self.planet_rotation,
                        pr.Vector3(1.5, 1.5, 1.5),
                        pr.WHITE,
                    )
                case "magenta":
                    pr.draw_model_ex(
                        self.planet_model["magenta"],
                        position,
                        pr.Vector3(0, 1, 0),
                        self.planet_rotation,
                        pr.Vector3(1.5, 1.5, 1.5),
                        pr.WHITE,
                    )
                case "darkred":
                    pr.draw_model_ex(
                        self.planet_model["darkred"],
                        position,
                        pr.Vector3(0, 1, 0),
                        self.planet_rotation,
                        pr.Vector3(1.5, 1.5, 1.5),
                        pr.WHITE,
                    )
                case "crimson":
                    pr.draw_model_ex(
                        self.planet_model["crimson"],
                        position,
                        pr.Vector3(0, 1, 0),
                        self.planet_rotation,
                        pr.Vector3(1.5, 1.5, 1.5),
                        pr.WHITE,
                    )
                case "maroon":
                    pr.draw_model_ex(
                        self.planet_model["maroon"],
                        position,
                        pr.Vector3(0, 1, 0),
                        self.planet_rotation,
                        pr.Vector3(1.5, 1.5, 1.5),
                        pr.WHITE,
                    )
                case "brown":
                    pr.draw_model_ex(
                        self.planet_model["brown"],
                        position,
                        pr.Vector3(0, 1, 0),
                        self.planet_rotation,
                        pr.Vector3(1.5, 1.5, 1.5),
                        pr.WHITE,
                    )
                case "violet":
                    pr.draw_model_ex(
                        self.planet_model["violet"],
                        position,
                        pr.Vector3(0, 1, 0),
                        self.planet_rotation,
                        pr.Vector3(1.5, 1.5, 1.5),
                        pr.WHITE,
                    )
                case "rainbow":
                    if self.current_frame % 5 == 0:
                        self.color_choice = random.choice(list(Color)).value
                    pr.draw_cube(
                        position, 1.0, 1.0, 1.0, self.color_choice
                    )
                case "None":
                    pr.draw_model_ex(
                        self.planet_model["yellow"],
                        position,
                        pr.Vector3(0, 1, 0),
                        self.planet_rotation,
                        pr.Vector3(1.5, 1.5, 1.5),
                        pr.WHITE,
                    )

                case _:
                    pr.draw_model_ex(
                        self.planet_model["error"],
                        position,
                        pr.Vector3(0, 1, 0),
                        180.0,
                        pr.Vector3(1.5, 1.5, 1.5),
                        pr.WHITE,
                    )
        self.planet_rotation_calc()
        for connection in data[1]:
            from_hub: Hub | None = None
            to_hub: Hub | None = None
            for hub in data[0]:
                if connection.from_hub == hub.name:
                    from_hub = hub
                if connection.to_hub == hub.name:
                    to_hub = hub
            if from_hub is not None and to_hub is not None:
                from_pos = pr.Vector3(
                    int(from_hub.x) * 5, 0.0,
                    int(from_hub.y) * 5)
                to_pos = pr.Vector3(
                    int(to_hub.x) * 5, 0.0,
                    int(to_hub.y) * 5)
                pr.draw_line_3d(from_pos, to_pos, pr.WHITE)

    def planet_rotation_calc(self) -> None:
        self.planet_rotation += 10 * self.dt
        if self.planet_rotation > 360:
            self.planet_rotation = 0

    def init_drones_position(self, path: list[Any]) -> None:
        for drones in path:
            try:
                hub = self.get_hub_for_drones(
                    drones[self.drones_index])
                drones_position = pr.Vector3(
                    int(hub.x) * 5, 5.0, int(hub.y) * 5)
                self.last_drones_position.append(
                    drones_position)
            except IndexError as e:
                print(f"Caught error: {e}")

    def drones_index_input(self) -> None:
        if pr.is_key_pressed(pr.KeyboardKey.KEY_LEFT):
            self.drones_index -= 1
        if pr.is_key_pressed(pr.KeyboardKey.KEY_RIGHT):
            self.drones_index += 1
        if self.drones_index < 0:
            self.drones_index = 0
        if self.drones_index > self.drones_index_max:
            self.drones_index = self.drones_index_max
        if pr.is_key_pressed(pr.KeyboardKey.KEY_ENTER):
            if self.auto_play is False:
                self.auto_play = True
            else:
                self.auto_play = False
        if pr.is_key_pressed(pr.KeyboardKey.KEY_R):
            self.drones_index = 0

    def get_hub_for_drones(self, name: str) -> Hub | Any:
        i = 0
        len_hub = len(self.data[0])
        while i < len_hub:
            if self.data[0][i].name == name:
                return self.data[0][i]
            i += 1
        return self.data[0][0]

    def draw_drones(self, path: list[Any]) -> None:
        self.drones_index_input()
        speed = 5
        i = 0
        for drones in path:
            try:
                if isinstance(drones[self.drones_index], str):
                    hub = self.get_hub_for_drones(
                        drones[self.drones_index])
                    hub_x = hub.x
                    hub_y = hub.y
                else:
                    hub_x = drones[self.drones_index].x
                    hub_y = drones[self.drones_index].y

                target_position = pr.Vector3(
                    float(hub_x) * 5, 2.0,
                    float(hub_y) * 5)
                if self.last_drones_position[i] != target_position:
                    dx = (target_position.x -
                          self.last_drones_position[i].x)
                    self.last_drones_position[i].x += (
                        dx * (speed * self.dt))
                    dz = (target_position.z -
                          self.last_drones_position[i].z)
                    self.last_drones_position[i].z += (
                        dz * (speed * self.dt))
                    dy = (target_position.y -
                          self.last_drones_position[i].y)
                    self.last_drones_position[i].y += (
                        dy * (speed * self.dt))
                pr.draw_model_ex(
                    self.spaceship_model,
                    self.last_drones_position[i],
                    pr.Vector3(0, 1, 0),
                    90,
                    pr.Vector3(1, 1, 1),
                    pr.WHITE
                )
                i += 1
            except IndexError as e:
                print(f"Caught error: {e}")

    def draw_controls(self) -> None:
        controls_text = (
            "Controls: WASD to move\n"
            "Mouse wheel to zoom\n"
            "SPACE to go up, LEFT CONTROL to go down\n"
            "SHIFT to speed up\n"
            "LEFT and RIGHT ARROW to change turn\n"
            "F to change map\n"
            "ENTER autoplay\n"
            "R to reset animation\n"
            "I to show/hide info")
        pr.draw_text(controls_text, int(15), 40, 20,
                     pr.RAYWHITE)

    def auto_play_animation(self) -> None:
        if self.auto_play is True:
            if self.current_frame == 30:
                self.drones_index += 1
                if self.drones_index > self.drones_index_max:
                    self.drones_index = self.drones_index_max

    def gui_scene_manager(self) -> None:
        if self.glob_state["Current"] == GlobalState.START:
            self.start_gui_scene()
        elif self.glob_state["Current"] == GlobalState.PARSING:
            self.data = self.parsing.check_file(
                self.file_choose, self.glob_state, self)
        elif self.glob_state["Current"] == GlobalState.SIMULATION:
            if pr.is_key_pressed(pr.KeyboardKey.KEY_F):
                self.file_choose = ""
                self.file_tree.path = "."
                self.file_tree.dirs = (
                    self.file_tree.get_dir(
                        self.file_tree.path))
                self.file_tree.files = (
                    self.file_tree.get_files(
                        self.file_tree.path))
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
            # show map name
            len_map_text = pr.measure_text(self.data[2], 64)
            map_label = f"Map: {self.data[2]}"
            len_map_text_prefix = pr.measure_text(map_label, 64)
            map_x = int(self.width / 2 - (len_map_text / 2))
            map_rect = pr.Rectangle(
                map_x, 20, len_map_text_prefix + 20, 64)
            pr.draw_rectangle(
                int(map_rect.x - 10), int(map_rect.y),
                int(map_rect.width), int(map_rect.height),
                pr.Color(0, 0, 0, 120))
            pr.draw_text(map_label, map_x, 20, 64,
                         pr.RAYWHITE)
            # show max turn and actual turn
            max_turn_text = (
                f"Max Turn: {self.drones_index_max}")
            len_max_turn_text = (
                pr.measure_text(max_turn_text, 24) + 20)
            pr.draw_text(max_turn_text,
                         self.width - len_max_turn_text, 10,
                         24, pr.RAYWHITE)
            actual_turn_text = (
                f"Actual Turn: {self.drones_index}")
            len_actual_turn_text = (
                pr.measure_text(actual_turn_text, 24) + 20)
            pr.draw_text(actual_turn_text,
                         self.width - len_actual_turn_text, 40,
                         24, pr.RAYWHITE)
            if self.number_drone_move != []:
                move_count = self.number_drone_move[
                    self.drones_index]
                num_drone_move_txt = (
                    f"Number of drones move this turn: "
                    f"{move_count}")
            else:
                num_drone_move_txt = (
                    "Number of drones move this turn: 0")
            len_num_drone = (
                pr.measure_text(num_drone_move_txt, 24) + 20)
            pr.draw_text(num_drone_move_txt,
                         self.width - len_num_drone, 70, 24,
                         pr.RAYWHITE)
            nb_drones = self.data[0][0].nb_drones
            nb_drones_txt = f"Number of drones: {nb_drones}"
            len_nb_drones = (
                pr.measure_text(nb_drones_txt, 24) + 20)
            pr.draw_text(nb_drones_txt,
                         self.width - len_nb_drones, 100, 24,
                         pr.RAYWHITE)
            auto_animation_txt = f"Autoplay: {self.auto_play}"
            auto_anim_len = pr.measure_text(auto_animation_txt, 24) + 20
            pr.draw_text(auto_animation_txt, self.width - auto_anim_len,
                         130, 24, pr.RAYWHITE)
            self.draw_controls()
        pr.draw_fps(10, 10)

    def calculate_number_drone_move(self, path: list[Any]) -> None:
        self.number_drone_move.append(0)
        for drone_path in range(1, self.drones_index_max + 1):
            drone_move = 0
            for p in path:
                if drone_path < len(p):
                    position_current = p[drone_path]
                    position_before = p[drone_path - 1]
                    if position_before != position_current:
                        drone_move += 1
            self.number_drone_move.append(drone_move)

    def show_info_input(self) -> None:
        if pr.is_key_pressed(pr.KeyboardKey.KEY_I):
            if self.show_info is False:
                self.show_info = True
            else:
                self.show_info = False

    def gui_drones_id(self, path: list[Any]) -> None:
        i = 0
        for _ in path:
            try:
                id_text = f"ID: {i}"
                len_id_text = pr.measure_text(id_text, 24) + 20
                drone_pos = self.last_drones_position[i]
                world_pos = (
                    drone_pos.x, drone_pos.y + 1.5,
                    drone_pos.z)
                drone_screen_position = (
                    pr.get_world_to_screen(
                        world_pos, self.g_cam))
                rect = pr.Rectangle(
                    int(drone_screen_position.x - 10),
                    int(drone_screen_position.y - 5),
                    len_id_text, 30)
                pr.draw_rectangle(
                    int(rect.x), int(rect.y),
                    int(rect.width), int(rect.height),
                    pr.Color(0, 0, 0, 120))
                pr.draw_text(
                    id_text,
                    int(drone_screen_position.x),
                    int(drone_screen_position.y), 24,
                    pr.RAYWHITE)
                i += 1
            except IndexError:
                error_text = (
                    "Failed to find path with the map "
                    "choose try another one")
                font_size = 44
                len_error_text = pr.measure_text(
                    error_text, font_size)
                pr.draw_text(
                    error_text,
                    int((self.width - len_error_text) / 2),
                    int(self.height - font_size),
                    font_size, pr.RED)

    def gui_hub_id(self, data: list[Any]) -> None:
        for hub in data[0]:
            font_size = 16
            hub_world_pos = (
                int(hub.x) * 5, 2.0, int(hub.y) * 5)
            hub_screen_position = (
                pr.get_world_to_screen(
                    hub_world_pos, self.g_cam))
            hub_label = f"Hub: {hub.name}"
            type_label = f"Type: {hub.zone}"
            capacity_label = (
                f"Capacity: {hub.max_drones}")
            len_id_text = (pr.measure_text(
                hub_label, font_size) + 20)
            len_type_text = (pr.measure_text(
                type_label, font_size) + 20)
            len_capacity_text = (pr.measure_text(
                capacity_label, font_size) + 20)
            len_text = max(
                len_id_text, len_type_text,
                len_capacity_text)
            rect_x = int(
                hub_screen_position.x - (len_text / 2))
            rect = pr.Rectangle(
                rect_x, int(hub_screen_position.y - 5),
                len_text, font_size * 3 + 10)
            pr.draw_rectangle(
                int(rect.x), int(rect.y),
                int(rect.width), int(rect.height),
                pr.Color(0, 0, 0, 120))
            hub_info = (
                f"Hub: {hub.name}\n"
                f"Type: {hub.zone}\n"
                f"Capacity: {hub.max_drones}")
            pr.draw_text(
                hub_info,
                int(hub_screen_position.x -
                    (len_text / 2) + 10),
                int(hub_screen_position.y), font_size,
                pr.RAYWHITE)

    def get_random_loading_planet(self) -> None:
        self.loading_model[0] = self.planet_model[random.choice(list(self.planet_model.keys()))]
        self.loading_model[1] = self.planet_model[random.choice(list(self.planet_model.keys()))]
        self.loading_model[2] = self.planet_model[random.choice(list(self.planet_model.keys()))]

    def loading_screen(self) -> None:
        pr.draw_model_ex(
            self.planet_model["yellow"],
            pr.Vector3(0, 0, 0),
            pr.Vector3(0, 1, 0),
            self.planet_rotation,
            pr.Vector3(1.5, 1.5, 1.5),
            pr.WHITE,
        )
        pr.draw_model_ex(
            self.planet_model["orange"],
            pr.Vector3(5, 0, 0),
            pr.Vector3(0, 1, 0),
            self.planet_rotation,
            pr.Vector3(1.5, 1.5, 1.5),
            pr.WHITE,
        )
        pr.draw_model_ex(
            self.planet_model["magenta"],
            pr.Vector3(-5, 0, 0),
            pr.Vector3(0, 1, 0),
            self.planet_rotation,
            pr.Vector3(1.5, 1.5, 1.5),
            pr.WHITE,
        )
        self.planet_rotation_calc()

    def loading_screen_gui(self) -> None:
        font_size = 64
        text = f"Map: {self.data[2]} Loading..."
        len_text = pr.measure_text(text, font_size)
        pr.draw_text(text, int((self.width / 2) - len_text / 2), int(self.height / 1.5), font_size, pr.YELLOW)

    def frame_counter(self) -> None:
        self.current_frame += 1
        if self.current_frame > self.max_fps:
            self.current_frame = 0

    def load_planet_model(self) -> None:
        models = {
            "error": "assets/planet_error.gltf",
            "green": "assets/planet_green.gltf",
            "red": "assets/planet_red.gltf",
            "blue": "assets/planet_blue.gltf",
            "orange": "assets/planet_orange.gltf",
            "purple": "assets/planet_purple.gltf",
            "gold": "assets/planet_gold.gltf",
            "cyan": "assets/planet_cyan.gltf",
            "yellow": "assets/planet_yellow.gltf",
            "black": "assets/planet_black.gltf",
            "lime": "assets/planet_lime.gltf",
            "magenta": "assets/planet_magenta.gltf",
            "darkred": "assets/planet_darkred.gltf",
            "crimson": "assets/planet_crimson.gltf",
            "maroon": "assets/planet_maroon.gltf",
            "brown": "assets/planet_brown.gltf",
            "violet": "assets/planet_violet.gltf",
        }
        for color, path in models.items():
            self.planet_model[color] = pr.load_model(path)

    def unload_planet_model(self) -> None:
        for model in self.planet_model.values():
            pr.unload_model(model)

    def main_loop(self) -> None:
        drones_path: list[Any] = []
        temp_drones_path: list[Any] = []
        monitor = pr.get_current_monitor()
        self.max_fps = pr.get_monitor_refresh_rate(monitor)
        pr.set_target_fps(self.max_fps)
        res_loc = pr.get_shader_location(self.shader, "resolution")
        time_loc = pr.get_shader_location(self.shader, "time")
        font = pr.load_font("assets/PixelOperator.ttf")
        pr.gui_load_style("assets/genesis.rgs")
        self.spaceship_model = pr.load_model("assets/spaceship.gltf")
        self.load_planet_model()
        pr.gui_set_font(font)
        while not pr.window_should_close():
            self.dt = pr.get_frame_time()
            self.width = pr.get_screen_width()
            self.height = pr.get_screen_height()
            pr.set_shader_value(
                self.shader,
                res_loc,
                pr.Vector2(self.width, self.height),
                pr.ShaderUniformDataType.SHADER_UNIFORM_VEC2,
            )
            pr.set_shader_value(
                self.shader,
                time_loc,
                pr.ffi.new("float *", pr.get_time()),
                pr.ShaderUniformDataType.SHADER_UNIFORM_FLOAT,
            )
            pr.begin_drawing()
            pr.clear_background(pr.BLACK)
            pr.begin_shader_mode(self.shader)
            pr.draw_rectangle(0, 0, self.width, self.height, pr.WHITE)
            pr.end_shader_mode()
            if self.glob_state["Current"] == GlobalState.FIND:
                self.bellman = BellmanFord(self.data)
                self.thread_algo = threading.Thread(target=self.bellman.main_loop, args=(self.glob_state, temp_drones_path))
                self.thread_algo.start()
                self.glob_state["Current"] = GlobalState.THREAD
            pr.begin_mode_3d(self.g_cam)
            if self.glob_state["Current"] == GlobalState.THREAD:
                self.loading_screen()
            if self.glob_state["Current"] == GlobalState.TRANSIT:
                drones_path = temp_drones_path[0]
                if drones_path != []:
                    self.drones_index_max = len(drones_path[0]) - 1
                    self.init_drones_position(drones_path)
                    self.calculate_number_drone_move(drones_path)
                temp_drones_path.clear()
                self.glob_state["Current"] = GlobalState.SIMULATION
            if self.glob_state["Current"] == GlobalState.SIMULATION:
                self.mode3d_scene_manager(self.data)
                self.draw_drones(drones_path)
                self.auto_play_animation()
            pr.end_mode_3d()
            self.show_info_input()
            if self.glob_state["Current"] == GlobalState.THREAD:
                self.loading_screen_gui()
            if self.show_info is True:
                self.gui_drones_id(drones_path)
                self.gui_hub_id(self.data)
            self.gui_scene_manager()
            pr.end_drawing()
            self.frame_counter()
        pr.unload_shader(self.shader)
        pr.unload_font(font)
        self.unload_planet_model()
        pr.unload_model(self.spaceship_model)
        pr.close_window()
