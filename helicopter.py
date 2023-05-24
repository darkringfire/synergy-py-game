import time
from typing import TYPE_CHECKING
from conf import *
import utils as u

if TYPE_CHECKING:
    from map import Map


class Helicopter:
    def __init__(self, map: "Map"):
        self.capacity, self.water = CAPACITY, START_WATER
        self.max_health = MAX_HEALTH
        self.health = START_HEALTH
        self.score = START_SCORE
        self.speed = SPEED

        self.healing_price = HEAL_PRICE
        self.upgrade_price = UPGRADE_PRICE

        self.invincibility_delay = INVINCIBILITY_DELAY
        self.fill_delay = FILL_DELAY
        self.upgrade_delay = UPGRADE_DELAY
        self.heal_delay = HEAL_DELAY

        self.move_x, self.move_y = 0, 0
        self.last_process_time = time.time()
        self.invincibility_time = self.invincibility_delay
        self.step_time = 0
        self.filling_time = 0
        self.upgrading_time = 0
        self.healing_time = 0

        self.map = map
        map.set_helicopter(self)

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

    def process(self):
        current_time = time.time()
        tick_time = current_time - self.last_process_time
        self.last_process_time = current_time

        self.process_douse()
        self.process_refill(tick_time)
        self.process_upgrade(tick_time)
        self.process_heal(tick_time)
        self.process_move(tick_time)
        self.process_invincible(tick_time)

    def process_douse(self):
        if self.map.is_fire(self.x, self.y) and self.water > 0:
            self.water -= 1
            self.map.douse_fire(self.x, self.y)

    def process_refill(self, tick_time):
        if self.map.is_water(self.x, self.y) and self.water < self.capacity:
            if self.filling_time < self.fill_delay:
                self.filling_time += tick_time
            else:
                self.water += 1
                self.filling_time = 0
        else:
            self.filling_time = 0

    def process_upgrade(self, tick_time):
        if self.map.is_shop(self.x, self.y) and self.score >= int(self.upgrade_price):
            if self.upgrading_time < self.upgrade_delay:
                self.upgrading_time += tick_time
            else:
                self.score -= int(self.upgrade_price)
                self.upgrade()
                self.map.upgrade()
                self.upgrading_time = 0
        else:
            self.upgrading_time = 0

    def process_heal(self, tick_time):
        if (
            self.map.is_hospital(self.x, self.y)
            and self.health < self.max_health
            and self.score >= int(self.healing_price)
        ):
            if self.healing_time < self.heal_delay:
                self.healing_time += tick_time
            else:
                self.score -= int(self.healing_price)
                self.health += 1
                self.healing_time = 0
        else:
            self.healing_time = 0

    def process_move(self, tick_time):
        if self.step_time > 0:
            self.step_time -= tick_time
        if self.step_time <= 0 and (self.need_to_move()):
            self.move()
            self.step_time = 1 / self.speed

    def move(self):
        if 0 <= (self.x + self.move_x) < self.map.w:
            self.x += self.move_x
        if 0 <= (self.y + self.move_y) < self.map.h:
            self.y += self.move_y

    def process_invincible(self, tick_time):
        if self.invincibility_time > 0:
            self.invincibility_time -= tick_time

    def need_to_move(self):
        return self.move_x != 0 or self.move_y != 0

    def status(self):
        result: str = ""
        result += self.status_score()

        bar_len = max(self.max_health, self.capacity)
        result += self.status_health(bar_len)
        result += self.status_water(bar_len)
        result += self.status_actions()

        if DEBUG:
            result += self.status_debug

        return result

    def status_score(self):
        return f"{TILES[GEM]}{self.score} \n"

    def status_actions(self):
        result = ""
        if 0 < self.filling_time < self.fill_delay:
            result += u.progress_bar(
                self.fill_delay, self.filling_time, TILES, WATER, mul=10
            )
        elif 0 < self.upgrading_time < self.upgrade_delay:
            result += u.progress_bar(
                self.upgrade_delay, self.upgrading_time, TILES, UPGADE, mul=10
            )
        elif 0 < self.healing_time < self.heal_delay:
            result += u.progress_bar(
                self.heal_delay, self.healing_time, TILES, HEART, mul=10
            )
        else:
            result += "Nothing to do"
        result += "\n"
        return result

    def status_debug(self):
        result = "Invincibility: "
        result += u.progress_bar(
            self.invincibility_delay,
            self.invincibility_time,
            TILES,
            INVINCIBLE,
            mul=2,
        )
        result += f" (Delay: {self.invincibility_delay:.2f})\n"

        result += "Waiting: "
        result += u.progress_bar(
            1 / self.speed, self.step_time, TILES, HELICOPTER, mul=10
        )
        result += f" (Speed: {self.speed:.2f}, delay {1 / self.speed :.2f})\n"
        return result

    def status_health(self, bar_len):
        result = ""
        health_tile = HEART
        if self.invincibility_time > 0:
            health_tile = INVINCIBLE
        # health_bar = health_tile * self.health
        # health_bar += TILES[EMPTY] * (self.max_health - self.health)
        health_bar = u.progress_bar(self.max_health, self.health, TILES, health_tile)
        result += health_bar + TILES[SPACE] * (bar_len - len(health_bar))
        result += f" | {TILES[HEART]}: {TILES[GEM]}{int(self.healing_price)}\n"
        return result

    def status_water(self, bar_len):
        result = ""
        water_str = TILES[WATER] * self.water
        water_str += TILES[EMPTY] * (self.capacity - self.water)
        result += water_str + TILES[SPACE] * (bar_len - len(water_str))
        result += f" | {TILES[WATER]}: {TILES[CLOCK]}{self.fill_delay:.2f}s"
        result += f" | {TILES[UPGADE]}: {TILES[GEM]}{int(self.upgrade_price)}\n"
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
