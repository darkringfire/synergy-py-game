import math
import os
import random

DIRS = [(0, -1), (1, -1), (1, 0), (1, 1), (0, 1), (-1, 1), (-1, 0), (-1, -1)]


def rand_dir(main_dir=None):
    if main_dir is None:
        return random.randint(0, len(DIRS) - 1)
    return (main_dir + random.randint(-1, 1)) % len(DIRS)


def get_dir_coords(dir):
    return DIRS[dir]


def rand_bool(probability):
    return random.random() < probability


def rand_coord(w, h):
    x = random.randint(0, w - 1)
    y = random.randint(0, h - 1)
    return x, y


def cls():
    os.system("cls" if os.name == "nt" else "clear")


def progress_bar(total, value, tiles, v_tile, s_tile=0, mul=1):
    result = tiles[v_tile] * math.ceil(value * mul)
    result += tiles[s_tile] * (math.ceil(total * mul) - math.ceil(value * mul))
    return result
