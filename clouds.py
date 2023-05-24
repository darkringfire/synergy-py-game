from utils import rand_bool
from typing import TYPE_CHECKING
from conf import *

if TYPE_CHECKING:
    from helicopter import Helicopter
    from map import Map


class Clouds:
    EMPTY = 0
    CLOUD = 1
    THUNDER = 2

    def __init__(self, map: "Map"):
        self.map = map
        self.cells = [[Clouds.EMPTY for _ in range(map.w)] for _ in range(map.h)]
        self.update()
        self.update_time = 0
        self.update_delay = CLOUDS_DELAY

    def process(self, helicopter: "Helicopter", tick_time):
        self.update_time += tick_time
        if self.update_time >= self.update_delay:
            self.update()
            self.update_time = 0
        if self.is_thunder(helicopter.x, helicopter.y):
            helicopter.hit()

    def is_clear(self, x, y):
        return self.cells[y][x] == Clouds.EMPTY

    def is_cloudy(self, x, y):
        return self.cells[y][x] == Clouds.CLOUD

    def is_thunder(self, x, y):
        return self.cells[y][x] == Clouds.THUNDER

    def update(self, clouds_probability=0.1, thunder_probability=0.1):
        for i in range(self.map.h):
            for j in range(self.map.w):
                self.cells[i][j] = Clouds.EMPTY
                if rand_bool(clouds_probability):
                    self.cells[i][j] = Clouds.CLOUD
                    if rand_bool(thunder_probability):
                        self.cells[i][j] = Clouds.THUNDER

    def upgrade(self):
        # TODO: Implement Clouds upgrade
        pass
