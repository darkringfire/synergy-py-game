import time
from typing import TYPE_CHECKING
from conf import *

if TYPE_CHECKING:
    from map import Map

ICONS = ["🔲", "💖", "🧱", "💧"]
IVONS = ".*#"
EMPTY = 0
HEART = 1
SHIELD = 2
WATER = 3

FILL_DELAY = 1
UPGRADE_DELAY = 1
HEAL_DELAY = 1
INVINCIBILITY_DELAY = 5

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

        self.map = map
        map.set_helicopter(self)
        self.last_process_time = time.time()

        self.healing_price = HEAL_PRICE
        self.upgrade_price = UPGRADE_PRICE
        self.invincibility_delay = INVINCIBILITY_DELAY

        self.invincibility_time = self.invincibility_delay
        self.step_delay = 0
        self.filling_time = 0
        self.upgrading_time = 0
        self.healing_time = 0

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
        tick_time = current_time - self.last_process_time
        self.last_process_time = current_time

        # Dousing
        if self.map.is_fire(self.x, self.y) and self.water > 0:
            self.water -= 1
            self.map.douse_fire(self.x, self.y)

        # Filling
        if self.map.is_water(self.x, self.y) and self.water < self.capacity:
            if self.filling_time < FILL_DELAY:
                self.filling_time += tick_time
            else:
                self.water += 1
                self.filling_time = 0
        else:
            self.filling_time = 0

        # Upgrading
        if self.map.is_shop(self.x, self.y) and self.score >= int(self.upgrade_price):
            if self.upgrading_time < UPGRADE_DELAY:
                self.upgrading_time += tick_time
            else:
                self.score -= int(self.upgrade_price)
                self.upgrade()
                self.map.upgrade()
                self.upgrading_time = 0
        else:
            self.upgrading_time = 0

        # Healing
        if (
            self.map.is_hospital(self.x, self.y)
            and self.health < self.max_health
            and self.score >= int(self.healing_price)
        ):
            if self.healing_time < HEAL_DELAY:
                self.healing_time += tick_time
            else:
                self.score -= int(self.healing_price)
                self.health += 1
                self.healing_time = 0
        else:
            self.healing_time = 0

        # Moving
        if self.step_delay > 0:
            self.step_delay -= tick_time
        if self.step_delay <= 0 and (self.need_to_move()):
            self.move()
            self.step_delay = 1 / self.speed

        # Invincible
        if self.invincibility_time > 0:
            self.invincibility_time -= tick_time

    def need_to_move(self):
        return self.move_x != 0 or self.move_y != 0

    def print(self):
        health_icon = ICONS[HEART]
        if self.invincibility_time > 0:
            health_icon = ICONS[SHIELD]
        health_str = health_icon * self.health + (
            ICONS[EMPTY] * (self.max_health - self.health)
        )
        water_str = (ICONS[WATER] * self.water) + (
            ICONS[EMPTY] * (self.capacity - self.water)
        )
        result = f"Health: {health_str} Water: {water_str} Speed: {self.speed:.2f} Score: {self.score}\n"
        result += f"Upgrade price: {int(self.upgrade_price)} Healing price: {int(self.healing_price)}\n"
        result += "Invincible: " + "<" * int(self.invincibility_time * 10) + "\n"
        result += "Action: "
        if 0 < self.filling_time < FILL_DELAY:
            result += "Filling: " + "<" * int((FILL_DELAY - self.filling_time) * 10)
        elif 0 < self.upgrading_time < UPGRADE_DELAY:
            result += "Upgrading: " + "<" * int(
                (UPGRADE_DELAY - self.upgrading_time) * 10
            )
        elif 0 < self.healing_time < HEAL_DELAY:
            result += "Healing: " + "<" * int((HEAL_DELAY - self.healing_time) * 10)
        else:
            result += "None"
        result += "\n"
        result += "Waiting: " + "<" * int(self.step_delay * 10) + "\n"
        return result

    def hit(self):
        if self.invincibility_time <= 0:
            self.health -= 1
            self.invincibility_time = self.invincibility_delay

    def is_dead(self):
        return self.health <= 0

    def upgrade(self):
        self.capacity += 1
        self.speed += 0.2
        self.upgrade_price *= 1.5
        self.invincibility_delay *= 0.9
