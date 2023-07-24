import math
import os
import random
import time
import numpy as np


class Param:
    def __init__(self, init, k=1):
        self.init = init
        self.k = k

    def cast(self, value):
        return type(self.init)(value)


class PowerParam(Param):
    def v(self, level):
        return self.cast(self.init * math.pow(self.k, level - 1))


class LinearParam(Param):
    def v(self, level):
        return self.init + self.k * (level - 1)


DIRS = [
    (0, -1),
    (1, -1),
    (1, 0),
    (1, 1),
    (0, 1),
    (-1, 1),
    (-1, 0),
    (-1, -1),
]


def rand_dir(main_dir=None):
    if main_dir is None:
        return random.randint(0, len(DIRS) - 1)
    return (main_dir + random.randint(-1, 1)) % len(DIRS)


def dir_coord(dir_n):
    return DIRS[dir_n]


def rand_bool(probability):
    return random.random() < probability


def rand_coord(size: tuple):
    return tuple(map(lambda v: random.randint(0, v - 1), size))


def add_coord(coord1, coord2):
    return tuple(map(lambda x, y: x + y, coord1, coord2))


def eq_coord(coord1, coord2):
    return all(map(lambda x, y: x == y, coord1, coord2))


def limit_bounds(coord, size):
    return tuple(map(lambda c, s: max(0, min(c, s - 1)), coord, size))


def check_bounds(coord, size):
    return all(map(lambda c, s: 0 <= c < s, coord, size))


def cls():
    os.system("cls" if os.name == "nt" else "clear")


def progress_bar(total, value, tiles, v_tile, s_tile=0, mul=1) -> str:
    result = tiles[v_tile] * math.ceil(value * mul)
    result += tiles[s_tile] * (math.ceil(total * mul) - math.ceil(value * mul))
    return result


def tick(last_tick_time):
    current_time = time.time()
    return current_time - last_tick_time, current_time
