

class Parsing:
    def __init__(self) -> None:
        pass

    def is_comments(self) -> None:
        pass

    def check_file(self) -> None:
        # temp need to know how i pass the map choose
        with open("maps/easy/01_linear_path.txt", 'r') as f:
            for line in f.readline():
                line_split = line.split()
                print(line_split)
