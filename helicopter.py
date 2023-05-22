import time
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from map import Map

ICONS = "🔲💖💧"
IVONS = ".*#"
EMPTY = 0
HEART = 1
BUCKET = 2


class Helicopter:
    def __init__(self, map: "Map"):
        self.capacity, self.water = 1, 0
        self.max_health = 10
        self.health = self.max_health
        self.score = 0
        self.move_x, self.move_y = 0, 0
        self.moved = False
        self.stop_x, self.stop_y = True, True
        self.speed = 2
        self.last_step_time = 0
        self.map = map
        map.set_helicopter(self)

    def place(self, x, y):
        self.x, self.y = x, y

    def set_move_up(self):
        if self.move_y != -1:
            self.move_y = -1
            self.stop_y = False
            self.moved = False

    def set_move_down(self):
        if self.move_y != 1:
            self.move_y = 1
            self.stop_y = False
            self.moved = False

    def set_move_left(self):
        if self.move_x != -1:
            self.move_x = -1
            self.stop_x = False
            self.moved = False

    def set_move_right(self):
        if self.move_x != 1:
            self.move_x = 1
            self.stop_x = False
            self.moved = False

    def set_stop_x(self):
        if self.moved:
            self.move_x = 0
        self.stop_x = True

    def set_stop_y(self):
        if self.moved:
            self.move_y = 0
        self.stop_y = True

    def move(self):
        if 0 <= (self.x + self.move_x) < self.map.w:
            self.x += self.move_x
        if 0 <= (self.y + self.move_y) < self.map.h:
            self.y += self.move_y
        if self.stop_x:
            self.move_x = 0
        if self.stop_y:
            self.move_y = 0
        self.moved = True

    def process(self):
        current_time = time.time()
        if current_time >= self.last_step_time + 1 / self.speed:
            if (
                self.map.is_shop(self.x, self.y)
                and self.score >= self.map.get_upgrade_price()
            ):
                self.score -= self.map.get_upgrade_price()
                self.capacity += 1
                self.last_step_time = current_time
            if (
                self.map.is_hospital(self.x, self.y)
                and self.score >= self.map.get_heal_price()
                and self.health < self.max_health
            ):
                self.score -= self.map.get_heal_price()
                self.health += 1
                self.last_step_time = current_time
            if not (self.stop_x and self.stop_y) or not self.moved:
                self.move()
                self.last_step_time = current_time
            if self.stop_x:
                self.move_x = 0
            if self.stop_y:
                self.move_y = 0

    def print(self):
        health_str = (ICONS[HEART] * self.health) + (
            ICONS[EMPTY] * (self.max_health - self.health)
        )
        water_str = (ICONS[BUCKET] * self.water) + (
            ICONS[EMPTY] * (self.capacity - self.water)
        )
        result = f"Health: {health_str} Water: {water_str}  Score: {self.score}\n"
        result += f"move_x: {self.move_x} move_y: {self.move_y} moved: {self.moved} stop_x: {self.stop_x} stop_y: {self.stop_y}\n"
        return result
