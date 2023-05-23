from utils import rand_coord
from utils import rand_bool
import time
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from helicopter import Helicopter

HIT_DELAY = 1
UPDATE_DELAY = 10

EMPTY = 0
CLOUD = 1
THUNDER = 2


class Clouds:
    def __init__(self, w, h):
        self.w = w
        self.h = h
        self.cells = [[EMPTY for _ in range(w)] for _ in range(h)]
        self.update()
        self.last_hit_time, self.last_update_time = 0, 0

    def process(self, helicopter: "Helicopter"):
        current_time = time.time()
        if current_time >= self.last_update_time + UPDATE_DELAY:
            self.update()
            self.last_update_time = current_time
        if (
            current_time >= self.last_hit_time + HIT_DELAY
            and self.cells[helicopter.y][helicopter.x] == THUNDER
        ):
            self.last_hit_time = current_time
            helicopter.hit()

    def is_empty(self, x, y):
        return self.cells[y][x] == EMPTY

    def is_cloudy(self, x, y):
        return self.cells[y][x] != EMPTY

    def update(self, clouds_probability=0.1, thunder_probability=0.1):
        for i in range(self.h):
            for j in range(self.w):
                self.cells[i][j] = EMPTY
                if rand_bool(clouds_probability):
                    self.cells[i][j] = CLOUD
                    if rand_bool(thunder_probability):
                        self.cells[i][j] = THUNDER
