from hub import Hub
from global_state import GlobalState

class BellmanFord:
    def __init__(self, data: list) -> None:
        self.new_data: list = data.copy()
        self.all_hubs: list = self.new_data[0].copy()
        self.hub_connection: list = self.new_data[1].copy()
        self.final_path: list = []
        self.cost: int = 0

    def find_cost(self, hub: Hub) -> None:
        match hub.zone:
            case "normal":
                self.cost += 1
            case "blocked":
                self.cost += 100000
            case "restricted":
                self.cost += 2
            case "priority":
                self.cost += 1

    def get_connection(self, hub_name: str) -> list:
        r_lst: list = []
        for connection in self.hub_connection:
            if hub_name in connection.from_hub:
                r_lst.append(connection.to_hub)
            if hub_name in connection.to_hub:
                r_lst.append(connection.from_hub)
        return r_lst

    def main_loop(self, global_state: dict) -> None:
        costs = {hub.name: float('inf') for hub in self.all_hubs}
        print(costs)
        nb_drones: int = self.all_hubs[0].nb_drones
        for i in range(nb_drones):
            for _ in range(len(self.all_hubs) - 1):
                for conn in self.hub_connection:
                    pass
        global_state["Current"] = GlobalState.SIMULATION

