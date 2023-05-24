import pprint
from map import Map
import time
import utils
from pynput import keyboard
from conf import *
import utils as u
import saver

MAP_SIZE = 20, 10

TICK_DELAY = 0.05

SAVEFILE = "save.json"

def init():
    global map, helicopter
    map = Map(*MAP_SIZE)
    helicopter = map.helicopter

init()

game_stoped = False
game_paused = False


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
            global game_stoped
            game_stoped = True
        elif key == keyboard.Key.space:
            global game_paused
            game_paused = not game_paused
        elif key == keyboard.Key.f5:
            # TODO: Save
            saver.save(SAVEFILE, map.export())
        elif key == keyboard.Key.f6:
            # TODO Load
            init()
            map.import_(saver.load(SAVEFILE))



def on_release(key):
    global move_x, move_y
    if type(key) == keyboard.KeyCode:
        if key.char in ["a", "d"]:
            helicopter.set_stop_x()
        elif key.char in ["w", "s"]:
            helicopter.set_stop_y()


listener = keyboard.Listener(on_press=on_press, on_release=on_release, suppress=True)

listener.start()

tick = 0
last_tick_time = time.time()
while True:
    loop_start = time.time()
    if game_stoped:
        utils.cls()
        print(f"Game stopped. Your score is {helicopter.score}")
        break

    if helicopter.is_dead():
        utils.cls()
        print(f"Game Over. Your score is {helicopter.score}")
        print("[Esc] to quit")
        time.sleep(0.5)
        continue

    if game_paused:
        utils.cls()
        print("Game paused.")
        if DEBUG:
            pprint.pprint(map.export(), width=100)
        print("[Space] to continue [F5] to save [F6] to load [Esc] to quit")
        while game_paused and not game_stoped:
            time.sleep(0.5)
        last_tick_time = time.time()
        continue

    tick_time, last_tick_time = u.tick(last_tick_time)

    map.process(tick_time)

    screen = ""
    if DEBUG:
        screen += f"Tick: {tick}\n"
        screen += f"Tick time: {tick_time:.2f}s\n"
        screen += f"{TILES[CLOCK]}{tick * TICK_DELAY:.2f}s\n"
    screen += helicopter.status()
    screen += map.render()
    screen += "[W/A/S/D] to move [Esc] to quit [Space] to pause [F5] to save [F6] to load\n"
    utils.cls()
    print(screen)

    loop_time = time.time() - loop_start
    if TICK_DELAY - loop_time > 0:
        time.sleep(TICK_DELAY - loop_time)
    tick += 1

listener.stop()
