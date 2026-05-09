class Hub:
    def __init__(self, name: str, x: int, y: int, color: str="none", max_drones: int=1, type_hub: str="normal", nb_drones: int=0):
        self.name = name
        self.x = x
        self.y = y
        self.color = color
        self.max_drones = max_drones
        self.type_hub = type_hub
        self.nb_drones = nb_drones

