from typing import TYPE_CHECKING, Any
from conf import *
import utils as u

if TYPE_CHECKING:
    from map import Map


class Helicopter:
    def __init__(self, map: "Map"):
        self.map = map
        self.apply_level(1)
        self.health = HEALTH_INIT
        self.score = SCORE_INIT
        self.water = WATER_INIT

        self.move_coord = (0, 0)
        self.step_time = 0.0
        self.filling_time = 0.0
        self.upgrading_time = 0.0
        self.healing_time = 0.0

        self.coord: tuple[int, int] = u.rand_coord(map.cells.shape)

    def apply_level(self, level):
        self.level = level
        self.max_health = Params.max_health.v(level)
        self.capacity = Params.capacity.v(level)
        self.speed = Params.speed.v(level)
        self.healing_price = Params.healing_price.v(level)
        self.upgrade_price = Params.upgrade_price.v(level)
        self.safe_delay = Params.safe_delay.v(level)
        self.fill_delay = Params.fill_delay.v(level)
        self.upgrade_delay = Params.upgrade_delay.v(level)
        self.heal_delay = Params.heal_delay.v(level)
        self.safe_time = self.safe_delay

    def place(self, coord):
        self.coord = coord

    def is_on(self, coord: tuple[int, int]) -> bool:
        return self.coord == coord

    def set_move_up(self):
        self.move_coord = (self.move_coord[0], -1)

    def set_move_down(self):
        self.move_coord = (self.move_coord[0], 1)

    def set_move_left(self):
        self.move_coord = (-1, self.move_coord[1])

    def set_move_right(self):
        self.move_coord = (1, self.move_coord[1])

    def set_stop_x(self):
        self.move_coord = (0, self.move_coord[1])

    def set_stop_y(self):
        self.move_coord = (self.move_coord[0], 0)

    def process(self, tick_time):
        self.process_douse()
        self.process_refill(tick_time)
        self.process_upgrade(tick_time)
        self.process_heal(tick_time)
        self.process_move(tick_time)
        self.process_invincible(tick_time)

    def process_douse(self):
        if self.map.is_fire(self.coord) and self.water > 0:
            self.water -= 1
            self.map.douse_fire(self.coord)

    def process_refill(self, tick_time):
        if self.map.is_river(self.coord) and self.water < self.capacity:
            if self.filling_time < self.fill_delay:
                self.filling_time += tick_time
            else:
                self.water += 1
                self.filling_time = 0
        else:
            self.filling_time = 0

    def process_upgrade(self, tick_time):
        if self.map.is_shop(self.coord) and self.score >= self.upgrade_price:
            if self.upgrading_time < self.upgrade_delay:
                self.upgrading_time += tick_time
            else:
                self.score -= self.upgrade_price
                self.apply_level(self.level + 1)
                self.map.apply_level(self.level)
                self.upgrading_time = 0
        else:
            self.upgrading_time = 0

    def process_heal(self, tick_time):
        if (
            self.map.is_hospital(self.coord)
            and self.health < self.max_health
            and self.score >= self.healing_price
        ):
            if self.healing_time < self.heal_delay:
                self.healing_time += tick_time
            else:
                self.score -= self.healing_price
                self.health += 1
                self.healing_time = 0
        else:
            self.healing_time = 0

    def process_move(self, tick_time):
        if self.step_time > 0:
            self.step_time -= tick_time
        if self.step_time <= 0 and self.need_to_move():
            self.move()
            self.step_time = 1 / self.speed

    def move(self):
        self.coord = u.limit_bounds(
            u.add_coord(self.coord, self.move_coord), self.map.cells.shape
        )

    def process_invincible(self, tick_time):
        if self.safe_time > 0:
            self.safe_time -= tick_time

    def need_to_move(self):
        return not u.eq_coord(self.move_coord, (0, 0))

    def status(self) -> list[str]:
        result: list[str] = []
        result.append(self.status_score())

        bar_len = max(self.max_health, self.capacity)
        result.append(self.status_health(bar_len))
        result.append(self.status_water(bar_len))
        result.append(self.status_actions())

        if DEBUG:
            result.extend(self.status_debug())

        return result

    def status_score(self) -> str:
        result = ""
        result += f"{T.i[T.LEVEL]}{self.level} | {T.i[T.GEM]}{self.score} "
        result += f" | {T.i[T.UPGRADE]}: {T.i[T.GEM]}{int(self.upgrade_price)}"
        return result

    def status_actions(self) -> str:
        result = ""
        if 0 < self.filling_time < self.fill_delay:
            result += u.progress_bar(
                self.fill_delay, self.filling_time, T.i, T.WATER, mul=10
            )
        elif 0 < self.upgrading_time < self.upgrade_delay:
            result += u.progress_bar(
                self.upgrade_delay, self.upgrading_time, T.i, T.UPGRADE, mul=10
            )
        elif 0 < self.healing_time < self.heal_delay:
            result += u.progress_bar(
                self.heal_delay, self.healing_time, T.i, T.HEART, mul=10
            )
        else:
            result += "Nothing to do"
        return result

    def status_debug(self) -> list[str]:
        result = ["Invincibility: "]
        result.append(
            u.progress_bar(
                self.safe_delay,
                self.safe_time,
                T.i,
                T.SAFE,
                mul=2,
            )
            + f" (Delay: {self.safe_delay:.2f})"
        )

        result.append(
            "Waiting: "
            + u.progress_bar(1 / self.speed, self.step_time, T.i, T.HELICOPTER, mul=10)
            + f" (Speed: {self.speed:.2f}, delay {1 / self.speed :.2f})"
        )
        return result

    def status_health(self, bar_len) -> str:
        result = ""
        health_tile = T.HEART
        if self.safe_time > 0:
            health_tile = T.SAFE
        health_bar = u.progress_bar(self.max_health, self.health, T.i, health_tile)
        result += health_bar + T.i[T.SPACE] * (bar_len - len(health_bar))
        result += f" | {T.i[T.HEART]}: {T.i[T.GEM]}{int(self.healing_price)}"
        return result

    def status_water(self, bar_len) -> str:
        result = ""
        water_str = T.i[T.WATER] * self.water
        water_str += T.i[T.EMPTY] * (self.capacity - self.water)
        result += water_str + T.i[T.SPACE] * (bar_len - len(water_str))
        result += f" | {T.i[T.WATER]}: {T.i[T.CLOCK]}{self.fill_delay:.2f}s"
        return result

    def hit(self):
        if self.safe_time <= 0:
            self.health -= 1
            self.safe_time = self.safe_delay

    def is_dead(self) -> bool:
        return self.health <= 0

    # TODO: Implement dump and load
    def dump(self) -> dict[str, Any]:
        return {
            "level": self.level,
            "health": self.health,
            "score": self.score,
            "water": self.water,
            "x": self.coord[0],
            "y": self.coord[1],
            "filling_time": self.filling_time,
            "upgrading_time": self.upgrading_time,
            "healing_time": self.healing_time,
        }

    def load(self, data):
        self.apply_level(data["level"])

        self.health = data["health"]
        self.score = data["score"]
        self.water = data["water"]
        self.coord = (data["x"], data["y"])
        self.filling_time = data["filling_time"]
        self.upgrading_time = data["upgrading_time"]
        self.healing_time = data["healing_time"]
