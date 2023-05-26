import numpy as np
import utils as u
from typing import TYPE_CHECKING
# from conf import *
import conf as c

if TYPE_CHECKING:
    from helicopter import Helicopter
    from map import Map


class Clouds:
    EMPTY = 0
    CLOUD = 1
    THUNDER = 2

    def __init__(self, map: "Map"):
        self.cells = np.full(map.cells.shape, Clouds.EMPTY)
        self.update_time = 0
        self.update_delay = None
        self.clouds_probability = None
        self.thunder_probability = None

    def process(self, helicopter: "Helicopter", tick_time):
        self.update_time += tick_time
        if self.update_time >= self.update_delay:
            self.update()
            self.update_time = 0
        if self.is_thunder(helicopter.coord):
            helicopter.hit()

    def is_clear(self, coord):
        return self.cells.item(coord) == Clouds.EMPTY

    def is_cloudy(self, coord):
        return self.cells.item(coord) == Clouds.CLOUD

    def is_thunder(self, coord):
        return self.cells.item(coord) == Clouds.THUNDER

    def update(self):
        for coord in np.ndindex(self.cells.shape):
            self.cells.itemset(coord, Clouds.EMPTY)
            if u.rand_bool(self.clouds_probability):
                self.cells.itemset(coord, Clouds.CLOUD)
                if u.rand_bool(self.thunder_probability):
                    self.cells.itemset(coord, Clouds.THUNDER)

    def apply_level(self, level):
        self.update_delay = c.Params.clouds_delay.v(level)
        self.clouds_probability = c.Params.clouds_probability.v(level)
        self.thunder_probability = c.Params.thunder_probability.v(level)

    # TODO: Implement Saving and loading
    def dump(self):
        return {
            "cells": self.cells.tolist(),
            "update_time": self.update_time,
        }

    def load(self, data: dict):
        self.cells = np.asarray(data["cells"])
        self.update_time = data["update_time"]
