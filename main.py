from collections import deque
from copy import deepcopy
from datetime import datetime as dt

import numpy as np

EMPTY = 0
ORE = 1
EXIT = 2
WALL = 3
MINER_TL = 4
MINER_TR = 5
MINER_BL = 6
MINER_BR = 7

CHAR_TO_TILE = {
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
TILE_TO_CHAR = {v: k for k, v in CHAR_TO_TILE.items()}

MINER_ARR = np.array([[MINER_TL, MINER_TR], [MINER_BL, MINER_BR]])

# Adjacent index modifiers
# .12.
# 8┌┐3
# 7└┘4
# .65.
MINER_ADJ_IND_Y = np.array([-1, -1, 0, 1, 2, 2, 1, 0])
MINER_ADJ_IND_X = np.array([0, 1, 2, 2, 1, 0, -1, -1])


class board:
    def __init__(self, tiles, height, width, miners, score, exit_):
        self.tiles = tiles
        self.height = height
        self.width = width
        self.miners = miners
        self.score = score
        self.exit = exit_

    def __repr__(self):
        lines = (
            "".join([TILE_TO_CHAR[self.tiles[y, x]] for x in range(0, self.width)])
            for y in range(0, self.height)
        )
        return "\n".join(lines)

    def __hash__(self):
        return hash(tuple(self.tiles.flat))

    def __eq__(self, other):
        return np.array_equal(self.tiles, other.tiles)

    def check_path(self):
        """Returns True if all miners have a direct path to the exit, False otherwise."""
        tiles = self.tiles.copy()

        # Flood fill exit tile
        q = deque()
        q.append(self.exit)
        while q:
            x, y = q.pop()
            if x > 0:
                if tiles[y, x - 1] <= ORE:  # Either EMPTY or ORE
                    tiles[y, x - 1] = EXIT
                    q.append((x - 1, y))
            if x < self.width - 1:
                if tiles[y, x + 1] <= ORE:
                    tiles[y, x + 1] = EXIT
                    q.append((x + 1, y))
            if y > 0:
                if tiles[y - 1, x] <= ORE:
                    tiles[y - 1, x] = EXIT
                    q.append((x, y - 1))
            if y < self.height - 1:
                if tiles[y + 1, x] <= ORE:
                    tiles[y + 1, x] = EXIT
                    q.append((x, y + 1))

        # Check that each miner has an adjacent exit
        for x, y in self.miners:
            iy = MINER_ADJ_IND_Y + y
            ix = MINER_ADJ_IND_X + x

            if not np.any(tiles[iy, ix] == EXIT):
                # if this miner does not have an adjacent exit, return False
                return False

        return True

    def add_miner(self, x, y):
        """Return a new board after adding a miner at x,y.
        
        If invalid returns None instead.
        """
        miner_section = self.tiles[y : y + 2, x : x + 2]

        is_ore = miner_section == ORE
        is_empty = miner_section == EMPTY

        if not np.all(is_ore | is_empty):
            return None

        tiles = self.tiles.copy()
        tiles[y : y + 2, x : x + 2] = MINER_ARR

        miners = self.miners.copy()
        miners.append((x, y))

        score = self.score + np.sum(is_ore)

        return board(tiles, self.height, self.width, miners, score, self.exit)


def main(lines):
    height = len(lines)
    width = len(lines[0].strip())

    exit_coords = None
    ores = []

    tiles = np.zeros((height, width), dtype="int")

    for y, line in enumerate(lines):
        for x, char in enumerate(line.strip()):
            tile = CHAR_TO_TILE[char]
            tiles[y, x] = tile
            if tile == ORE:
                ores.append((x, y))
            elif tile == EXIT:
                exit_coords = (x, y)

    if exit_coords is None:
        raise ValueError("Input has no exit.")

    b = board(tiles, height, width, [], 0, exit_coords)

    seen = set()
    highest_score = 0
    highest_score_miners = 0

    search = deque()
    search.append(b)

    start_time = dt.now()

    while search:
        nxt = search.pop()
        gen = (
            (ore_x, ore_y) for ore_x, ore_y in ores if nxt.tiles[ore_y][ore_x] == ORE
        )
        for ore_x, ore_y in gen:
            for x, y in [
                (ore_x - 1, ore_y - 1),
                (ore_x + 0, ore_y - 1),
                (ore_x - 1, ore_y + 0),
                (ore_x + 0, ore_y + 0),
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


if __name__ == "__main__":
    with open("input.txt") as f:
        lines = f.readlines()
    main(lines)
