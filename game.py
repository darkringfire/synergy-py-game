from map import Map
from helicopter import Helicopter
from clouds import Clouds
import time
import utils
from pynput import keyboard

MAP_SIZE = 20, 10

TICK_DELAY = 0.05

map = Map(*MAP_SIZE)
helicopter = Helicopter(map)


def on_press(key):
    try:
        if key.char == "w":
            helicopter.set_move_up()
        elif key.char == "a":
            helicopter.set_move_left()
        elif key.char == "s":
            helicopter.set_move_down()
        elif key.char == "d":
            helicopter.set_move_right()
    except AttributeError:
        pass


def on_release(key):
    global move_x, move_y
    try:
        if key.char in ["a", "d"]:
            helicopter.set_stop_x()
        elif key.char in ["w", "s"]:
            helicopter.set_stop_y()
    except AttributeError:
        pass


listener = keyboard.Listener(on_press=on_press, on_release=on_release)

listener.start()

tick = 0
tick_time = 0
while True:
    tick_time = time.time()

    map.process()
    helicopter.process()
    screen = ""
    screen += f"Tick: {tick}\n"
    screen += f"{tick * TICK_DELAY:.2f}s\n"
    screen += helicopter.print()
    screen += map.render()
    utils.cls()
    print(screen)

    tick_time = time.time() - tick_time
    if TICK_DELAY - tick_time > 0:
        time.sleep(TICK_DELAY - tick_time)
    tick += 1
