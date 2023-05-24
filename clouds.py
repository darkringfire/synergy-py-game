from utils import rand_coord
from utils import rand_bool
import time
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from helicopter import Helicopter
    from map import Map

UPDATE_DELAY = 10

EMPTY = 0
CLOUD = 1
THUNDER = 2


class Clouds:
    def __init__(self, map: "Map"):
        self.map = map
        self.cells = [[EMPTY for _ in range(map.w)] for _ in range(map.h)]
        self.update()
        self.update_time = 0
        self.update_delay = UPDATE_DELAY

    def process(self, helicopter: "Helicopter", tick_time):
        self.update_time += tick_time
        if self.update_time >= self.update_delay:
            self.update()
            self.update_time = 0
        if self.is_thunder(helicopter.x, helicopter.y):
            helicopter.hit()

    def is_thunder(self, x, y):
        return self.cells[y][x] == THUNDER

    def is_empty(self, x, y):
        return self.cells[y][x] == EMPTY

    def is_cloudy(self, x, y):
        return self.cells[y][x] != EMPTY

    def update(self, clouds_probability=0.1, thunder_probability=0.1):
        for i in range(self.map.h):
            for j in range(self.map.w):
                self.cells[i][j] = EMPTY
                if rand_bool(clouds_probability):
                    self.cells[i][j] = CLOUD
                    if rand_bool(thunder_probability):
                        self.cells[i][j] = THUNDER

    def upgrade(self):
        # TODO: Implement Clouds upgrade
        pass
