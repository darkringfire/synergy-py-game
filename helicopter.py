import time
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from map import Map

ICONS = "🔲💖💧"
IVONS = ".*#"
EMPTY = 0
HEART = 1
BUCKET = 2

FILL_DELAY = 1
UPGRADE_DELAY = 1
HEAL_DELAY = 1

UPGRADE_PRICE = 1000
HEAL_PRICE = 500

class Helicopter:
    def __init__(self, map: "Map"):
        self.capacity, self.water = 1, 0
        self.max_health = 10
        self.health = 3
        self.score = 0
        self.move_x, self.move_y = 0, 0
        self.speed = 1
        (
            self.last_step_time,
            self.last_fill_time,
            self.last_upgrade_time,
            self.last_heal_time,
        ) = (0, 0, 0, 0)
        self.map = map
        map.set_helicopter(self)

        self.heal_price = HEAL_PRICE
        self.upgrade_price = UPGRADE_PRICE

    def place(self, x, y):
        self.x, self.y = x, y

    def set_move_up(self):
        self.move_y = -1

    def set_move_down(self):
        self.move_y = 1

    def set_move_left(self):
        self.move_x = -1

    def set_move_right(self):
        self.move_x = 1

    def set_stop_x(self):
        self.move_x = 0

    def set_stop_y(self):
        self.move_y = 0

    def move(self):
        if 0 <= (self.x + self.move_x) < self.map.w:
            self.x += self.move_x
        if 0 <= (self.y + self.move_y) < self.map.h:
            self.y += self.move_y

    def process(self):
        current_time = time.time()

        if self.map.is_fire(self.x, self.y) and self.water > 0:
            self.water -= 1
            self.map.douse_fire(self.x, self.y)

        if (
            current_time >= self.last_fill_time + FILL_DELAY
            and self.map.is_water(self.x, self.y)
            and self.water < self.capacity
        ):
            self.water += 1
            self.last_fill_time = current_time

        if (
            current_time >= self.last_upgrade_time + UPGRADE_DELAY
            and self.map.is_shop(self.x, self.y)
            and self.score >= int(self.upgrade_price)
        ):
            self.score -= int(self.upgrade_price)
            self.upgrade()
            self.map.upgrade()
            self.last_upgrade_time = current_time

        if (
            current_time >= self.last_heal_time + HEAL_DELAY
            and self.map.is_hospital(self.x, self.y)
            and self.score >= int(self.heal_price)
            and self.health < self.max_health
        ):
            self.score -= int(self.heal_price)
            self.health += 1
            self.last_heal_time = current_time

        if current_time >= self.last_step_time + 1 / self.speed and (
            self.move_x != 0 or self.move_y != 0
        ):
            self.move()
            self.last_step_time = current_time

    def print(self):
        health_str = (ICONS[HEART] * self.health) + (
            ICONS[EMPTY] * (self.max_health - self.health)
        )
        water_str = (ICONS[BUCKET] * self.water) + (
            ICONS[EMPTY] * (self.capacity - self.water)
        )
        result = f"Health: {health_str} Water: {water_str} Speed: {self.speed:.2f} Score: {self.score}\n"
        result += f"Upgrade price: {int(self.upgrade_price)}\n"
        return result

    def hit(self):
        if self.health > 0:
            self.health -= 1

    def is_dead(self):
        return self.health <= 0
    def upgrade(self):
        self.capacity += 1
        self.speed += 0.1
        self.upgrade_price *= 1.5