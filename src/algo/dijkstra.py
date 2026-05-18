from hub import Hub

class Dijkstra:

    def __init__(self, data: list) -> None:
        self.hub_to_visit: list = data[0]
        self.hub_connection: list = data[1]
        self.data: list = data
        self.path: list = []
        self.lst_zone: list = ["normal", "blocked", "restricted", "priority"]

    def find_cost(self, hub: Hub) -> int:
        cost = 0
        match hub.zone:
            case "normal":
                cost += 1
            case "blocked":
                cost += 100000
            case "restricted":
                pass
            case "priority":
                pass
        return cost

    def main_loop(self) -> None:
        self.hub_to_visit.pop(0)
        i = 0
        while self.hub_to_visit != [] and self.hub_to_visit[i].type_hub != "end_hub":
            i += 1
