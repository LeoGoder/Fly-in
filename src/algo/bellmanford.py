from global_state import GlobalState


class BellmanFord:
    def __init__(self, data: list) -> None:
        self.new_data: list = data.copy()
        self.all_hubs: list = self.new_data[0].copy()
        self.hub_connection: list = self.new_data[1].copy()
        self.hubs_dict: dict = {hub.name: hub for hub in self.all_hubs}
        self.final_path: list = []
        self.cost: int = 0
        self.RED_PRINT: str = "\033[91m"
        self.RESET_PRINT: str = "\033[0m"

    def find_cost_hub(self, hub_name: str) -> int | float:
        hub = self.hubs_dict[hub_name]
        match hub.zone:
            case "normal":
                return 1
            case "blocked":
                return float('inf')
            case "restricted":
                return 2
            case "priority":
                return 1
            case _:
                return 1

    def get_connection(self, hub_name: str) -> list:
        r_lst: list = []
        for connection in self.hub_connection:
            if hub_name in connection.from_hub:
                r_lst.append(connection.to_hub)
            if hub_name in connection.to_hub:
                r_lst.append(connection.from_hub)
        return r_lst

    def fill_path(self, path: list) -> list:
        len_max = 0
        for p in path:
            temp_len = len(p)
            if temp_len > len_max:
                len_max = temp_len
        for p in path:
            while len(p) < len_max:
                p.append(p[-1])

        return path

    def get_max_len(self, path: list) -> int:
        return_max = 0
        for p in path:
            for dp in p:
                temp_len = len(dp)
                if temp_len > return_max:
                    return_max = temp_len
        return return_max

    def output_file(self, path: list) -> None:
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

    def main_loop(self, global_state: dict) -> list:
        start_name = self.all_hubs[0].name
        end_name = self.all_hubs[-1].name
        nb_drones: int = self.all_hubs[0].nb_drones
        max_drones: int = self.hubs_dict[start_name].max_drones
        path: list = [[] for _ in range(nb_drones)]
        timed_path: list = [[] for _ in range(nb_drones)]
        reservation: dict = {}
        connection_reservation: dict = {}
        for i in range(nb_drones):
            costs = {hub.name: float('inf') for hub in self.all_hubs}
            costs[start_name] = 0
            parents = {hub.name: None for hub in self.all_hubs}
            for _ in range(len(self.all_hubs) - 1):
                for conn in self.hub_connection:
                    forward = (conn.from_hub, conn.to_hub)
                    backward = (conn.to_hub, conn.from_hub)
                    max_connection_capacity = conn.max_link_capacity
                    for actual_hub, neighbour_hub in [forward, backward]:
                        if self.find_cost_hub(neighbour_hub) == float('inf'):
                            continue
                        if costs[actual_hub] == float("inf"):
                            continue
                        estimation_turn = (
                            costs[actual_hub]
                            + self.find_cost_hub(neighbour_hub)
                        )
                        futur_drones_neighbour = reservation.get(
                            (neighbour_hub, estimation_turn),
                            0,
                        )
                        max_capacity = self.hubs_dict[neighbour_hub].max_drones
                        travel_cost = self.find_cost_hub(neighbour_hub)
                        waiting_turn = 0
                        # waiting capabilities
                        waiting_turn = 0
                        max_waiting_turn = max_drones * 3
                        while waiting_turn < int(max_waiting_turn):
                            departure_turn = costs[actual_hub] + waiting_turn
                            arrival_turn = departure_turn + travel_cost
                            hub_ok = reservation.get(
                                (neighbour_hub, arrival_turn),
                                0,
                            ) < int(max_capacity)
                            connection_ok = all(connection_reservation.get(
                                ((actual_hub, neighbour_hub), departure_turn + t),
                                0, ) < int(max_connection_capacity)
                                for t in range(int(travel_cost))
                            )
                            if (
                                hub_ok and connection_ok
                            ):
                                break
                            waiting_turn += 1
                        if waiting_turn >= int(max_waiting_turn):
                            continue
                        new_cost = (
                            costs[actual_hub]
                            + travel_cost
                            + waiting_turn
                        )
                        if new_cost < costs[neighbour_hub]:
                            costs[neighbour_hub] = new_cost
                            parents[neighbour_hub] = actual_hub
            # Reconstruct path
            current = end_name
            if parents[current] is not None or current == start_name:
                while current is not None:
                    path[i].append(current)
                    current = parents[current]
                path[i].reverse()
            if path[i]:
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
                        for t in range(t_cost):
                            connection_reservation[
                                ((current_hub, next_hub), departure_turn + t)
                            ] = connection_reservation.get(
                                ((current_hub, next_hub), departure_turn + t),
                                0,
                            ) + 1
        print(timed_path)
        print(reservation)
        print(connection_reservation)
        self.fill_path(timed_path)
        self.output_file(timed_path)
        global_state["Current"] = GlobalState.SIMULATION
        return timed_path
