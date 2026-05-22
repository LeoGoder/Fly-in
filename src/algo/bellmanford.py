from hub import Hub
from global_state import GlobalState


class BellmanFord:
    def __init__(self, data: list) -> None:
        self.new_data: list = data.copy()
        self.all_hubs: list = self.new_data[0].copy()
        self.hub_connection: list = self.new_data[1].copy()
        self.hubs_dict: dict = {hub.name: hub for hub in self.all_hubs}
        self.final_path: list = []
        self.cost: int = 0

    def find_cost_hub(self, hub_name: str) -> int:
        hub = self.hubs_dict[hub_name]
        match hub:
            case "normal":
                return 1
            case "blocked":
                return 100000
            case "restricted":
                return 2
            case "priority":
                return 1
            case _:
                return 2

    def get_connection(self, hub_name: str) -> list:
        r_lst: list = []
        for connection in self.hub_connection:
            if hub_name in connection.from_hub:
                r_lst.append(connection.to_hub)
            if hub_name in connection.to_hub:
                r_lst.append(connection.from_hub)
        return r_lst

    def main_loop(self, global_state: dict) -> list:
        start_name = self.all_hubs[0].name
        end_name = self.all_hubs[-1].name
        nb_drones: int = self.all_hubs[0].nb_drones
        for i in range(nb_drones):
            costs = {hub.name: float('inf') for hub in self.all_hubs}
            costs[start_name] = 0
            parents = {hub.name: None for hub in self.all_hubs}
            for _ in range(len(self.all_hubs) - 1):
                for conn in self.hub_connection:
                    forward = (conn.from_hub, conn.to_hub)
                    backward = (conn.to_hub, conn.from_hub)
                    for actual_hub, neighbour_hub in [forward, backward]:
                        if costs[actual_hub] == float("inf"):
                            continue
                        new_cost = costs[actual_hub] + self.find_cost_hub(neighbour_hub)
                        if new_cost < costs[neighbour_hub]:
                            costs[neighbour_hub] = new_cost
                            parents[neighbour_hub] = actual_hub
        path = []
        current = end_name
        if parents[current] is not None or current == start_name:
            while current is not None:
                path.append(current)
                current = parents[current]
            path.reverse()
        global_state["Current"] = GlobalState.SIMULATION
        print(path)
        return path
