from typing import Any
from global_state import GlobalState


class BellmanFord:
    def __init__(self, data: list[Any]) -> None:
        self.new_data: list[Any] = data.copy()
        self.all_hubs: list[Any] = self.new_data[0].copy()
        self.hub_connection: list[Any] = self.new_data[1].copy()
        self.hubs_dict: dict[str, Any] = {hub.name: hub for hub
                                          in self.all_hubs}
        self.final_path: list[Any] = []
        self.cost: int = 0
        self.RED_PRINT: str = "\033[91m"
        self.RESET_PRINT: str = "\033[0m"

    def find_cost_hub(self, hub_name: str) -> int | float:
        hub = self.hubs_dict[hub_name]
        match hub.zone:
            case "normal":
                return 1
            case "blocked":
                return float("inf")
            case "restricted":
                return 2
            case "priority":
                return 1
            case _:
                return 1

    def get_connection(self, hub_name: str) -> list[Any]:
        r_lst: list[Any] = []
        for connection in self.hub_connection:
            if hub_name in connection.from_hub:
                r_lst.append(connection.to_hub)
            if hub_name in connection.to_hub:
                r_lst.append(connection.from_hub)
        return r_lst

    def fill_path(self, path: list[Any]) -> list[Any]:
        len_max = 0
        for p in path:
            temp_len = len(p)
            if temp_len > len_max:
                len_max = temp_len
        for p in path:
            while len(p) < len_max:
                p.append(p[-1])

        return path

    def get_max_len(self, path: list[Any]) -> int:
        return_max = 0
        for p in path:
            temp_len = len(p)
            if temp_len > return_max:
                return_max = temp_len
        return return_max

    def output_file(self, path: list[Any]) -> None:
        max_len = self.get_max_len(path)
        i = 1
        try:
            with open("Simulation_output.txt", 'w') as f:
                while i < max_len - 1:
                    y = 0
                    for p in path:
                        if i < len(p):
                            if p[i - 1] != p[i]:
                                f.write(f"D{y}-{p[i]} ")
                        y += 1
                    f.write("\n")
                    i += 1
        except (PermissionError, FileNotFoundError, IndexError) as e:
            print(f"{self.RED_PRINT}Caught Error while creating "
                  f"output file: {e}{self.RESET_PRINT}")

    def main_loop(self, global_state: dict[str, Any]) -> list[Any]:
        start_name = self.all_hubs[0].name
        end_name = self.all_hubs[-1].name
        nb_drones: int = self.all_hubs[0].nb_drones
        max_drones: int = self.hubs_dict[start_name].max_drones
        path: list[Any] = [[] for _ in range(nb_drones)]
        timed_path: list[Any] = [[] for _ in range(nb_drones)]
        reservation: dict[Any, int] = {}
        connection_reservation: dict[Any, int] = {}
        for i in range(nb_drones):
            costs = {hub.name: float('inf') for hub in self.all_hubs}
            costs[start_name] = 0
            parents = {hub.name: None for hub in self.all_hubs}
            priorities = {hub.name: 0 for hub in self.all_hubs}
            for _ in range(len(self.all_hubs) - 1):
                for conn in self.hub_connection:
                    forward = (conn.from_hub, conn.to_hub)
                    backward = (conn.to_hub, conn.from_hub)
                    max_connection_capacity = conn.max_link_capacity
                    for actual_hub, neighbour_hub in [forward, backward]:
                        if self.find_cost_hub(neighbour_hub) == float("inf"):
                            continue
                        if costs[actual_hub] == float("inf"):
                            continue
                        max_capacity = self.hubs_dict[neighbour_hub].max_drones
                        travel_cost = self.find_cost_hub(neighbour_hub)
                        # waiting capabilities
                        waiting_turn = 0
                        max_waiting_turn = nb_drones * 5
                        valid_path = False
                        while waiting_turn < int(max_waiting_turn):
                            departure_turn = costs[actual_hub] + waiting_turn
                            if waiting_turn > 0:
                                if actual_hub == start_name:
                                    current_cap = max_drones * 1
                                else:
                                    current_cap = (
                                        self.hubs_dict[actual_hub].max_drones
                                    )
                                if (
                                    reservation.get(
                                        (actual_hub, departure_turn), 0
                                    )
                                    >= int(current_cap)
                                ):
                                    break
                            arrival_turn = departure_turn + travel_cost
                            if (
                                self.hubs_dict[neighbour_hub].zone ==
                                "restricted"
                            ):
                                hub_ok = all(
                                    reservation.get(
                                        (neighbour_hub, departure_turn + t), 0
                                    ) < int(max_capacity)
                                    for t in range(1, int(travel_cost) + 1)
                                )
                            else:
                                hub_ok = reservation.get(
                                    (neighbour_hub, arrival_turn),
                                    0,
                                ) < int(max_capacity)
                            connection_ok = all(connection_reservation.get(
                                ((actual_hub, neighbour_hub),
                                 departure_turn + t),
                                0, ) < int(max_connection_capacity)
                                for t in range(int(travel_cost))
                            )
                            if hub_ok and connection_ok:
                                valid_path = True
                                break
                            waiting_turn += 1
                        if waiting_turn >= int(max_waiting_turn):
                            continue
                        if not valid_path:
                            continue
                        new_cost = (
                            costs[actual_hub]
                            + travel_cost
                            + waiting_turn
                        )
                        is_priority = (
                            1
                            if self.hubs_dict[neighbour_hub].zone == "priority"
                            else 0
                        )
                        new_priority = priorities[actual_hub] + is_priority
                        if (
                            new_cost < costs[neighbour_hub]
                            or (
                                new_cost == costs[neighbour_hub]
                                and new_priority > priorities[neighbour_hub]
                            )
                        ):
                            costs[neighbour_hub] = new_cost
                            priorities[neighbour_hub] = new_priority
                            parents[neighbour_hub] = actual_hub

            # Reconstruct path
            current = end_name
            if parents[current] is not None or current == start_name:
                while current is not None:
                    path[i].append(current)
                    current = parents[current]
                path[i].reverse()
            if path[i]:
                for j, hub in enumerate(path[i]):
                    timed_path[i].append(hub)
                    if j < len(path[i]) - 1:
                        next_hub = path[i][j + 1]
                        travel_cost = self.find_cost_hub(next_hub)
                        wait = costs[next_hub] - costs[hub] - travel_cost
                        for _ in range(int(wait)):
                            timed_path[i].append(hub)
                        for _ in range(int(travel_cost) - 1):
                            timed_path[i].append(next_hub)

            # Update reservation
            if timed_path[i]:
                for turn, hub in enumerate(timed_path[i]):
                    reservation[(hub, turn)] = (
                        reservation.get((hub, turn), 0) + 1
                    )
                for turn in range(len(timed_path[i]) - 1):
                    current_hub = timed_path[i][turn]
                    next_hub = timed_path[i][turn + 1]

                    if current_hub != next_hub:
                        t_cost = self.find_cost_hub(next_hub)
                        departure_turn = turn + 1 - t_cost
                        for t in range(int(t_cost)):
                            connection_reservation[
                                ((current_hub, next_hub), departure_turn + t)
                            ] = connection_reservation.get(
                                ((current_hub, next_hub), departure_turn + t),
                                0,
                            ) + 1

        visual_path = [path.copy() for path in timed_path]
        for i in range(nb_drones):
            for turn in range(1, len(visual_path[i])):
                prev_node = visual_path[i][turn - 1]
                curr_node = visual_path[i][turn]

                if (
                    isinstance(prev_node, str)
                    and isinstance(curr_node, str)
                    and prev_node != curr_node
                ):
                    if self.hubs_dict[curr_node].zone == "restricted":
                        conn_obj = None

                        for conn in self.hub_connection:
                            if (
                                (
                                    conn.from_hub == prev_node
                                    and conn.to_hub == curr_node
                                )
                                or (
                                    conn.to_hub == prev_node
                                    and conn.from_hub == curr_node
                                )
                            ):
                                conn_obj = conn
                                break
                        if conn_obj:
                            prev_x = int(self.hubs_dict[prev_node].x)
                            curr_x = int(self.hubs_dict[curr_node].x)
                            conn_obj.x = (prev_x + curr_x) / 2
                            prev_y = int(self.hubs_dict[prev_node].y)
                            curr_y = int(self.hubs_dict[curr_node].y)
                            conn_obj.y = (prev_y + curr_y) / 2
                            visual_path[i][turn] = conn_obj

        self.fill_path(visual_path)
        self.output_file(timed_path)
        global_state["Current"] = GlobalState.SIMULATION
        return visual_path
