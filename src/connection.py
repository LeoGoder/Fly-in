class Connection:
    def __init__(self, from_hub: str, to_hub: str, max_link_capacity: int = 1):
        self.from_hub = from_hub
        self.to_hub = to_hub
        self.max_link_capacity = max_link_capacity
