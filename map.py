# 🟩🌳🌊🏥🏭🔥🚁🟩🌳🌊🏥🏭🔥🚁🟩🌳🌊🏥🏭🔥🚁
# 0 - empty
# 1 - tree
# 2 - water
# 3 - hospital
# 4 - workshop
# 5 - fire
# 6 - helicopter

import time
from utils import rand_coord
from utils import rand_dir
from utils import get_dir_coords
from utils import rand_bool
from clouds import Clouds
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from helicopter import Helicopter

TILES = ["🔲", "🟩", "🟦", "🌳", "🏥", "🏭", "🔥", "🚁", "⚪", "⚡"]
# TILES = " .T~HS*XO!"
FRAME = 0
EMPTY = 1
WATER = 2
TREE = 3
HOSPITAL = 4
WORKSHOP = 5
FIRE = 6
HELICOPTER = 7
CLOUD = 8
THUNDER = 9

GROW_DELAY = 5
GROW_TREE_N = 10
FIRE_DELAY = 20
FIRES_N = 5
TREE_BONUS = 100
BURN_PENALTY = 1


class Map:
    def __init__(self, w, h):
        self.w = w
        self.h = h
        self.cells = [[EMPTY for _ in range(w)] for _ in range(h)]
        self.generate_forest(0.3)
        self.generate_river()
        self.generate_river()
        self.grnerate_hospital()
        self.generate_workshop()
        self.clouds = Clouds(w, h)
        self.helicopter = None

        self.grow_delay = GROW_DELAY
        self.fire_delay = FIRE_DELAY
        self.tree_bonus = TREE_BONUS
        self.burn_penalty = BURN_PENALTY
        self.grow_tree_n = GROW_TREE_N
        self.fires_n = FIRES_N

        self.last_fire, self.last_grow = 0, 0

    def set_helicopter(self, helicopter: "Helicopter"):
        self.helicopter = helicopter
        helicopter.place(*rand_coord(self.w, self.h))

    def generate_river(self, length=None):
        if length is None:
            length = (self.w + self.h) // 2
        x, y = rand_coord(self.w, self.h)
        direction = rand_dir()
        while length > 0:
            self.cells[y][x] = WATER
            dx, dy = get_dir_coords(direction)
            if self.check_bounds(x + dx, y + dy):
                length -= 1
                x, y = x + dx, y + dy
            direction = rand_dir(direction)

    def generate_forest(self, probability):
        for i in range(self.h):
            for j in range(self.w):
                if rand_bool(probability):
                    self.cells[i][j] = TREE

    def grnerate_hospital(self):
        while True:
            x, y = rand_coord(self.w, self.h)
            if self.cells[y][x] == EMPTY:
                self.cells[y][x] = HOSPITAL
                break

    def generate_workshop(self):
        while True:
            x, y = rand_coord(self.w, self.h)
            if self.cells[y][x] == EMPTY:
                self.cells[y][x] = WORKSHOP
                break

    def grow_tree(self):
        x, y = rand_coord(self.w, self.h)
        if self.cells[y][x] == EMPTY:
            self.cells[y][x] = TREE

    def grow_trees(self):
        for _ in range(int(self.grow_tree_n)):
            self.grow_tree()

    def fire_tree(self):
        x, y = rand_coord(self.w, self.h)
        if self.cells[y][x] == TREE:
            self.cells[y][x] = FIRE

    def update_fire(self):
        for i in range(self.h):
            for j in range(self.w):
                if self.cells[i][j] == FIRE:
                    self.cells[i][j] = EMPTY
                    self.helicopter.score -= int(self.burn_penalty)
                    if self.helicopter.score < 0:
                        self.helicopter.score = 0
        [self.fire_tree() for _ in range(int(self.fires_n))]

    def render(self):
        screen: str = ""
        screen += TILES[FRAME] * (self.w + 2) + "\n"
        for i in range(self.h):
            screen += TILES[FRAME]
            for j in range(self.w):
                tile = self.cells[i][j]
                if self.helicopter.x == j and self.helicopter.y == i:
                    tile = HELICOPTER
                if self.clouds.is_cloudy(j, i):
                    tile = tile = CLOUD + self.clouds.cells[i][j] - 1
                screen += TILES[tile]
            screen += TILES[FRAME] + "\n"
        screen += TILES[FRAME] * (self.w + 2) + "\n"
        return screen

    def check_bounds(self, x, y):
        return 0 <= y < self.h and 0 <= x < self.w

    def process(self):
        current_time = time.time()
        if current_time >= self.last_fire + self.fire_delay:
            self.last_fire = current_time
            self.update_fire()
        if current_time >= self.last_grow + self.grow_delay:
            self.last_grow = current_time
            self.grow_trees()
        self.clouds.process(self.helicopter)

    def is_shop(self, x, y):
        return self.cells[y][x] == WORKSHOP

    def is_hospital(self, x, y):
        return self.cells[y][x] == HOSPITAL

    def is_water(self, x, y):
        return self.cells[y][x] == WATER

    def is_fire(self, x, y):
        return self.cells[y][x] == FIRE

    def douse_fire(self, x, y):
        self.cells[y][x] = TREE
        self.helicopter.score += int(self.tree_bonus)

    def upgrade(self):
        self.grow_delay *= 1.1
        self.burn_delay *= 0.9
        self.tree_bonus *= 1.2
        self.burn_penalty *= 1.5
        self.grow_tree_n *= 0.9
        self.fires_n *= 1.1
        self.clouds.upgrade()
