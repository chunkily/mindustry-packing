from copy import deepcopy
from collections import deque
from datetime import datetime as dt


EMPTY = 0
ORE = 1
EXIT = 2
WALL = 3
MINER_TL = 4
MINER_TR = 5
MINER_BL = 6
MINER_BR = 7

tile_to_code = {
    ".": EMPTY,
    "#": ORE,
    "E": EXIT,
    "X": WALL,
    "┌": MINER_TL,
    "┐": MINER_TR,
    "└": MINER_BL,
    "┘": MINER_BR,
}

# Invert the dictionary
code_to_tile = {v: k for k, v in tile_to_code.items()}


class board:
    def __init__(self, tiles, height, width, miners, score, exit_):
        self.tiles = tiles
        self.height = height
        self.width = width
        self.miners = miners
        self.score = score
        self.exit = exit_

    def __repr__(self):
        lines = []
        for l in self.tiles:
            lines.append("".join([code_to_tile[x] for x in l]))

        return "\n".join(lines)

    def __hash__(self):
        return hash(repr(self))

    def __eq__(self, other):
        return self.tiles == other.tiles

    def get_ore_coords(self):
        for x in range(2, self.width - 3):
            for y in range(2, self.height - 3):
                if self.tiles[y][x] == ORE:
                    yield x, y

    def check_path(self):
        """Returns True if all miners have a direct path to the exit, False otherwise."""
        tiles = deepcopy(self.tiles)

        # Flood fill exit tile
        q = deque()
        q.append(self.exit)
        while q:
            x, y = q.pop()
            if x > 0:
                if tiles[y][x - 1] <= ORE:  # Either EMPTY or ORE
                    tiles[y][x - 1] = EXIT
                    q.append((x - 1, y))
            if x < self.width - 1:
                if tiles[y][x + 1] <= ORE:
                    tiles[y][x + 1] = EXIT
                    q.append((x + 1, y))
            if y > 0:
                if tiles[y - 1][x] <= ORE:
                    tiles[y - 1][x] = EXIT
                    q.append((x, y - 1))
            if y < self.height - 1:
                if tiles[y + 1][x] <= ORE:
                    tiles[y + 1][x] = EXIT
                    q.append((x, y + 1))

        # Check that each miner has an adjacent exit
        for x, y in self.miners:
            # .12.
            # 8┌┐3
            # 7└┘4
            # .65.
            e1 = tiles[y - 1][x + 0] == EXIT
            e2 = tiles[y - 1][x + 1] == EXIT
            e3 = tiles[y + 0][x + 2] == EXIT
            e4 = tiles[y + 1][x + 2] == EXIT
            e5 = tiles[y + 2][x + 1] == EXIT
            e6 = tiles[y + 2][x + 0] == EXIT
            e7 = tiles[y + 1][x - 1] == EXIT
            e8 = tiles[y + 0][x - 1] == EXIT
            # if this miner does not have an adjacent exit, return False
            if not (e1 or e2 or e3 or e4 or e5 or e6 or e7 or e8):
                return False

        return True

    def add_miner(self, x, y):
        """Return a new board after adding a miner at x,y.
        
        If invalid returns None instead.
        """
        tiles = self.tiles
        score = self.score

        miner_score = 0

        tl = tiles[y + 0][x + 0]
        tr = tiles[y + 0][x + 1]
        bl = tiles[y + 1][x + 0]
        br = tiles[y + 1][x + 1]

        tl_free = tl <= ORE  # Either EMPTY or ORE
        tr_free = tr <= ORE
        bl_free = bl <= ORE
        br_free = br <= ORE

        if tl_free and tr_free and bl_free and br_free:
            miner_score += tl == ORE
            miner_score += tr == ORE
            miner_score += bl == ORE
            miner_score += br == ORE
            # if miner_score == 0:
            #     return None

            tiles = deepcopy(self.tiles)
            miners = deepcopy(self.miners)
            tiles[y + 0][x + 0] = MINER_TL
            tiles[y + 1][x + 0] = MINER_BL
            tiles[y + 0][x + 1] = MINER_TR
            tiles[y + 1][x + 1] = MINER_BR
        else:
            return None

        miner = (x, y)

        miners.append(miner)
        score += miner_score
        return board(tiles, self.height, self.width, miners, score, self.exit)


with open("input.txt") as f:
    lines = f.readlines()

exit_coords = None

tiles = []
for y, line in enumerate(lines):
    oline = []
    for x, tile in enumerate(line.strip()):
        code = tile_to_code[tile]
        oline.append(code)
        if code == EXIT:
            exit_coords = (x, y)

    tiles.append(oline)

if exit_coords is None:
    raise ValueError("Input has no exit.")

height = len(tiles)
width = len(tiles[0])

b = board(tiles, height, width, [], 0, exit_coords)

seen = set()
highest_score = 0
highest_score_miners = 0

search = deque()
search.append(b)

start_time = dt.now()

while search:
    nxt = search.pop()
    for ore_x, ore_y in nxt.get_ore_coords():
        for x, y in [
            (ore_x + 0, ore_y + 0),
            (ore_x - 1, ore_y + 0),
            (ore_x + 0, ore_y - 1),
            (ore_x - 1, ore_y - 1),
        ]:
            nxt_board = nxt.add_miner(x, y)
            if nxt_board is None or nxt_board in seen:
                continue
            seen.add(nxt_board)
            if nxt_board.check_path():
                search.append(nxt_board)
                num_miners = len(nxt_board.miners)
                score = nxt_board.score

                if score > highest_score:
                    highest_score = score
                    highest_score_miners = num_miners
                    print(f"patches covered:{score}, number of miners:{num_miners}")
                    print(nxt_board)
                elif score == highest_score and num_miners <= highest_score_miners:
                    highest_score_miners = num_miners
                    print(f"patches covered:{score}, number of miners:{num_miners}")
                    print(nxt_board)

duration = dt.now() - start_time
print(f"Took {duration} to finish.")
