import utils as u
from clouds import Clouds
from conf import *
import numpy as np

from helicopter import Helicopter


class Map:
    def __init__(self, size: tuple[int]):
        self.cells = np.full(size, T.GROUND)
        self.generate_forest(0.3)
        self.generate_river()
        self.generate_river()
        self.grnerate_hospital()
        self.generate_workshop()
        self.clouds = Clouds(self)
        self.helicopter = Helicopter(self)

        self.apply_level(self.helicopter.level)
        self.clouds.apply_level(self.helicopter.level)

        self.burning_time, self.growing_time = self.burn_delay, 0.0

    def generate_river(self, length=None):
        if length is None:
            length = sum(self.cells.shape) // 2
        coord = u.rand_coord(self.cells.shape)
        dir = u.rand_dir()
        while length > 0:
            self.cells.itemset(coord, T.RIVER)
            new_coord = u.add_coord(coord, u.dir_coord(dir))
            if u.check_bounds(new_coord, self.cells.shape):
                length -= 1
                coord = new_coord
            dir = u.rand_dir(dir)

    def generate_forest(self, probability):
        for coord in np.ndindex(self.cells.shape):
            if u.rand_bool(probability):
                self.cells.itemset(coord, T.TREE)

    def grnerate_hospital(self):
        for _ in range(self.cells.size):
            coord = u.rand_coord(self.cells.shape)
            if self.is_ground(coord):
                self.cells.itemset(coord, T.HOSPITAL)
                break

    def generate_workshop(self):
        for _ in range(self.cells.size):
            coord = u.rand_coord(self.cells.shape)
            if self.is_ground(coord):
                self.cells.itemset(coord, T.WORKSHOP)
                break

    def grow_tree(self):
        coord = u.rand_coord(self.cells.shape)
        if self.is_ground(coord):
            self.cells.itemset(coord, T.TREE)

    def grow_trees(self):
        for _ in range(self.grow_tree_n):
            self.grow_tree()

    def fire_tree(self):
        coord = u.rand_coord(self.cells.shape)
        if self.is_tree(coord):
            self.cells.itemset(coord, T.FIRE)

    def update_fire(self):
        for coord in np.ndindex(self.cells.shape):
            if self.is_fire(coord):
                self.cells.itemset(coord, T.GROUND)
                self.helicopter.score -= self.burn_penalty
                if self.helicopter.score < 0:
                    self.helicopter.hit()
                    self.helicopter.score = 0
        [self.fire_tree() for _ in range(self.fires_n)]

    def render(self):
        screen: str = ""

        if DEBUG:
            screen += self.status_debug()

        screen += "\n" + self.render_field()
        return screen

    def render_field(self):
        w, h = self.cells.shape
        screen = T.i[T.EMPTY] * (w + 2) + "\n"
        for y in range(h):
            screen += T.i[T.EMPTY]
            for x in range(w):
                coord = (x, y)
                tile = self.cells.item(coord)
                if self.clouds.is_cloudy(coord):
                    tile = T.CLOUD
                elif self.clouds.is_thunder(coord):
                    tile = T.THUNDER
                elif self.helicopter.is_on(coord):
                    tile = T.HELICOPTER
                screen += T.i[tile]
            screen += T.i[T.EMPTY] + "\n"
        screen += T.i[T.EMPTY] * (w + 2) + "\n"
        return screen

    def status_debug(self):
        # Grow progress
        screen = u.progress_bar(self.grow_delay, self.growing_time, T.i, T.TREE)
        screen += f" ({T.i[T.GEM]}{int(self.tree_bonus)})\n"
        # Burn progress
        screen += u.progress_bar(self.burn_delay, self.burning_time, T.i, T.FIRE)
        screen += f" ({T.i[T.LOSE]}{int(self.burn_penalty)})\n"
        return screen

    def process(self, tick_time):
        self.burning_time += tick_time
        self.growing_time += tick_time
        if self.burning_time >= self.burn_delay:
            self.burning_time = 0
            self.update_fire()
        if self.growing_time >= self.grow_delay:
            self.growing_time = 0
            self.grow_trees()
        self.clouds.process(self.helicopter, tick_time)
        self.helicopter.process(tick_time)

    def is_ground(self, coord: tuple[int, int]):
        return self.cells.item(coord) == T.GROUND

    def is_tree(self, coord: tuple[int, int]):
        return self.cells.item(coord) == T.TREE

    def is_shop(self, coord: tuple[int, int]):
        return self.cells.item(coord) == T.WORKSHOP

    def is_hospital(self, coord: tuple[int, int]):
        return self.cells.item(coord) == T.HOSPITAL

    def is_river(self, coord: tuple[int, int]):
        return self.cells.item(coord) == T.RIVER

    def is_fire(self, coord: tuple[int, int]):
        return self.cells.item(coord) == T.FIRE

    def douse_fire(self, coord: tuple[int, int]):
        if self.is_fire(coord):
            self.cells.itemset(coord, T.TREE)
            self.helicopter.score += self.tree_bonus

    def apply_level(self, level):
        self.grow_delay = Params.grow_delay.v(level)
        self.burn_delay = Params.burn_delay.v(level)
        self.tree_bonus = Params.tree_bonus.v(level)
        self.burn_penalty = Params.burn_penalty.v(level)
        self.grow_tree_n = Params.grow_tree_n.v(level)
        self.fires_n = Params.fires_n.v(level)
        self.clouds.apply_level(level)

    # TODO: Implement dump and load
    def dump(self):
        return {
            "cells": self.cells.tolist(),
            "clouds": self.clouds.dump(),
            "helicopter": self.helicopter.dump(),
            "burning_time": self.burning_time,
            "growing_time": self.growing_time,
        }

    def load(self, data):
        self.cells = np.asarray(data["cells"])

        self.helicopter.load(data["helicopter"])
        self.clouds.load(data["clouds"])

        self.burning_time = data["burning_time"]
        self.growing_time = data["growing_time"]

        self.apply_level(self.helicopter.level)
        self.clouds.apply_level(self.helicopter.level)
