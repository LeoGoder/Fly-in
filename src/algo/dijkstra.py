from hub import Hub
from global_state import GlobalState

class Dijkstra:

    def __init__(self, data: list) -> None:
        self.new_data: list = data.copy()
        self.hub_to_visit: list = self.new_data[0].copy()
        self.hub_connection: list = self.new_data[1].copy()
        self.final_path: list = []
        self.lst_zone: list = ["normal", "blocked", "restricted", "priority"]
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
        print(f"len hub to visit {len(self.hub_to_visit)}")
        while self.hub_to_visit != [] and self.hub_to_visit[0].type_hub != "end_hub":
            connection = self.get_connection(self.hub_to_visit[0].name)
            print(f"connection for {self.hub_to_visit[0].name}: {connection}")

            self.hub_to_visit.pop(0)
        global_state["Current"] = GlobalState.SIMULATION
