from copy import deepcopy
from collections import deque


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

    def check_path(self):
        tiles = deepcopy(self.tiles)

        # Flood fill exit tile
        q = deque()
        q.append(self.exit)
        while q:
            x, y = q.pop()
            if x > 0:
                if tiles[y][x - 1] in [EMPTY, ORE]:
                    tiles[y][x - 1] = EXIT
                    q.append((x - 1, y))
            if x < self.width - 1:
                if tiles[y][x + 1] in [EMPTY, ORE]:
                    tiles[y][x + 1] = EXIT
                    q.append((x + 1, y))
            if y > 0:
                if tiles[y - 1][x] in [EMPTY, ORE]:
                    tiles[y - 1][x] = EXIT
                    q.append((x, y - 1))
            if y < self.height - 1:
                if tiles[y + 1][x] in [EMPTY, ORE]:
                    tiles[y + 1][x] = EXIT
                    q.append((x, y + 1))

        # Check that each miner has an adjacent exit
        for x, y in self.miners:
            #             #12#
            #             8MM3
            #             7MM4
            #             #65#
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

        free_tile_types = [EMPTY, ORE, EXIT]
        tl_free = tl in free_tile_types
        tr_free = tr in free_tile_types
        bl_free = bl in free_tile_types
        br_free = br in free_tile_types

        if tl_free and tr_free and bl_free and br_free:
            miner_score += tl == ORE
            miner_score += tr == ORE
            miner_score += bl == ORE
            miner_score += br == ORE
            if miner_score == 0:
                return None

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

while search:
    nxt = search.pop()
    for i in range(2, width - 3):
        for j in range(2, height - 3):
            nxt_board = nxt.add_miner(i, j)
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
                    print(f"patches covered: {score}, number of miners:{num_miners}")
                    print(nxt_board)
                elif score == highest_score and num_miners < highest_score_miners:
                    highest_score_miners = num_miners
                    print(f"patches covered: {score}, number of miners:{num_miners}")
                    print(nxt_board)
