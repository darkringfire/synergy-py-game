import time
import utils as u
from clouds import Clouds
from typing import TYPE_CHECKING
from conf import *


from helicopter import Helicopter


class Map:
    def __init__(self, w, h):
        self.w = w
        self.h = h
        self.cells = [[GROUND for _ in range(w)] for _ in range(h)]
        self.generate_forest(0.3)
        self.generate_river()
        self.generate_river()
        self.grnerate_hospital()
        self.generate_workshop()
        self.clouds = Clouds(self)
        self.helicopter = Helicopter(self)
        self.helicopter.place(*u.rand_coord(self.w, self.h))

        self.grow_delay = GROW_DELAY
        self.burn_delay = BURN_DELAY
        self.tree_bonus = TREE_BONUS
        self.burn_penalty = BURN_PENALTY
        self.grow_tree_n = GROW_TREE_N
        self.fires_n = FIRES_N

        self.burning_time, self.growing_time = BURN_DELAY, 0
        self.last_process_time = time.time()

    def generate_river(self, length=None):
        if length is None:
            length = (self.w + self.h) // 2
        x, y = u.rand_coord(self.w, self.h)
        direction = u.rand_dir()
        while length > 0:
            self.cells[y][x] = RIVER
            dx, dy = u.get_dir_coords(direction)
            if self.check_bounds(x + dx, y + dy):
                length -= 1
                x, y = x + dx, y + dy
            direction = u.rand_dir(direction)

    def generate_forest(self, probability):
        for i in range(self.h):
            for j in range(self.w):
                if u.rand_bool(probability):
                    self.cells[i][j] = TREE

    def grnerate_hospital(self):
        while True:
            x, y = u.rand_coord(self.w, self.h)
            if self.cells[y][x] == GROUND:
                self.cells[y][x] = HOSPITAL
                break

    def generate_workshop(self):
        while True:
            x, y = u.rand_coord(self.w, self.h)
            if self.cells[y][x] == GROUND:
                self.cells[y][x] = WORKSHOP
                break

    def grow_tree(self):
        x, y = u.rand_coord(self.w, self.h)
        if self.cells[y][x] == GROUND:
            self.cells[y][x] = TREE

    def grow_trees(self):
        for _ in range(int(self.grow_tree_n)):
            self.grow_tree()

    def fire_tree(self):
        x, y = u.rand_coord(self.w, self.h)
        if self.cells[y][x] == TREE:
            self.cells[y][x] = FIRE

    def update_fire(self):
        for i in range(self.h):
            for j in range(self.w):
                if self.cells[i][j] == FIRE:
                    self.cells[i][j] = GROUND
                    self.helicopter.score -= int(self.burn_penalty)
                    if self.helicopter.score < 0:
                        self.helicopter.score = 0
        [self.fire_tree() for _ in range(int(self.fires_n))]

    def render(self):
        screen: str = ""

        if DEBUG:
            screen += self.render_debug()

        screen += "\n" + self.render_field()
        return screen

    def render_field(self):
        screen = TILES[EMPTY] * (self.w + 2) + "\n"
        for i in range(self.h):
            screen += TILES[EMPTY]
            for j in range(self.w):
                tile = self.cells[i][j]
                if self.helicopter.x == j and self.helicopter.y == i:
                    tile = HELICOPTER
                if self.clouds.is_cloudy(j, i):
                    tile = tile = CLOUD + self.clouds.cells[i][j] - 1
                screen += TILES[tile]
            screen += TILES[EMPTY] + "\n"
        screen += TILES[EMPTY] * (self.w + 2) + "\n"
        return screen

    def render_debug(self):
        # Grow progress
        screen = u.progress_bar(self.grow_delay, self.growing_time, TILES, TREE)
        screen += f" ({TILES[GEM]}{int(self.tree_bonus)})\n"
        # Burn progress
        screen += u.progress_bar(self.burn_delay, self.burning_time, TILES, FIRE)
        screen += f" ({TILES[LOSE]}{int(self.burn_penalty)})\n"
        return screen

    def check_bounds(self, x, y):
        return 0 <= y < self.h and 0 <= x < self.w

    def process(self):
        current_time = time.time()
        tick_time = current_time - self.last_process_time
        self.last_process_time = current_time
        self.burning_time += tick_time
        self.growing_time += tick_time
        if self.burning_time >= self.burn_delay:
            self.burning_time = 0
            self.update_fire()
        if self.growing_time >= self.grow_delay:
            self.growing_time = 0
            self.grow_trees()
        self.clouds.process(self.helicopter)

    def is_shop(self, x, y):
        return self.cells[y][x] == WORKSHOP

    def is_hospital(self, x, y):
        return self.cells[y][x] == HOSPITAL

    def is_river(self, x, y):
        return self.cells[y][x] == RIVER

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
