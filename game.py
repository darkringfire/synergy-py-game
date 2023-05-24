from map import Map
from helicopter import Helicopter
import time
import utils
from pynput import keyboard
from conf import *

MAP_SIZE = 20, 10

TICK_DELAY = 0.05

map = Map(*MAP_SIZE)
helicopter = Helicopter(map)

stop_game = False
pause_game = False


def on_press(key):
    if type(key) == keyboard.KeyCode:
        if key.char == "w":
            helicopter.set_move_up()
        elif key.char == "a":
            helicopter.set_move_left()
        elif key.char == "s":
            helicopter.set_move_down()
        elif key.char == "d":
            helicopter.set_move_right()
    else:
        if key == keyboard.Key.esc:
            global stop_game
            stop_game = True
        elif key == keyboard.Key.space:
            global pause_game
            pause_game = not pause_game


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
    if stop_game:
        utils.cls()
        print(f"Game stopped. Your score is {helicopter.score}")
        break

    if helicopter.is_dead():
        utils.cls()
        print(f"Game Over. Your score is {helicopter.score}")
        print("[Esc] to quit")
        time.sleep(0.5)
        continue

    if pause_game:
        utils.cls()
        print("Game paused.")
        print("[Space] to continue [Esc] to quit")
        time.sleep(0.5)
        continue

    tick_time = time.time()

    map.process()
    helicopter.process()
    screen = ""
    screen += f"Tick: {tick}\n"
    screen += f"{tick * TICK_DELAY:.2f}s\n"
    screen += helicopter.print()
    screen += map.render()
    screen += "[W/A/S/D] to move [Esc] to quit [Space] to pause\n"
    utils.cls()
    print(screen)

    tick_time = time.time() - tick_time
    if TICK_DELAY - tick_time > 0:
        time.sleep(TICK_DELAY - tick_time)
    tick += 1

listener.stop()
