

class Parsing:
    def __init__(self, path: str) -> None:
        self.file_path = path

    def is_comments(self) -> None:
        pass

    def check_file(self) -> None:
        with open(self.file_path, 'r') as f:
            for line in f.readline():
                line_split = line.split()
                print(line_split)
