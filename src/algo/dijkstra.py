class Dijkstra:
    
    def __init__(self, data: list) -> None:
        self.hub_to_visit: list = data
        self.data: list = data
        self.path: list = []

    def find_cost(self) -> None:
        cost = 1

    def main_loop(self) -> None:
        self.hub_to_visit.pop(0)
        i = 0
        while self.hub_to_visit != [] and self.hub_to_visit[i].type_hub != "end_hub":
            
            i += 1

