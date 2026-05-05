from global_state import GlobalState


class Parsing:
    def __init__(self) -> None:
        pass

    def is_comments(self, line_splits: list) -> bool:
        if '#' in line_splits:
            return False
        return True

    def check_file(self, path: str, global_state: dict) -> None:
        data: dict = {}
        try:
            with open(path, 'r') as f:
                for line in f.readlines():
                    line_split = line.split()
                    if self.is_comments == False:
                        continue
                    print(line_split)
        except (FileNotFoundError, PermissionError, UnicodeDecodeError) as e:
            print(f"Caught error {e}")
        global_state["Current"] = GlobalState.SIMULATION

