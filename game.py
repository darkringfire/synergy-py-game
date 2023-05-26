from map import Map
import time
import utils
from pynput import keyboard
import conf as c
import utils as u
import saver

MAP_SIZE = (20, 10)

TICK_DELAY = 0.05

SAVEFILE = "save.json"

game_map = Map(MAP_SIZE)

# TODO: Loading
# game_map.load(saver.load(SAVEFILE))

game_stoped = False
game_paused = False


def on_press(key):
    global game_map
    try:
        if type(key) == keyboard.KeyCode:
            if key.char == "w":
                game_map.helicopter.set_move_up()
            elif key.char == "a":
                game_map.helicopter.set_move_left()
            elif key.char == "s":
                game_map.helicopter.set_move_down()
            elif key.char == "d":
                game_map.helicopter.set_move_right()
        else:
            if key == keyboard.Key.esc:
                global game_stoped
                game_stoped = True
            elif key == keyboard.Key.space:
                global game_paused
                game_paused = not game_paused
            elif key == keyboard.Key.f5:
                saver.save(SAVEFILE, game_map.dump())
                pass
            elif key == keyboard.Key.f6:
                # TODO: Loading
                game_map.load(saver.load(SAVEFILE))
                pass
            elif key == keyboard.Key.f9:
                game_map = Map(MAP_SIZE)
            elif key == keyboard.Key.f12:
                c.DEBUG = not c.DEBUG
    except Exception as e:
        print(f"\n\n{e}\n\n")
        pass


def on_release(key):
    if type(key) == keyboard.KeyCode:
        if key.char in ["a", "d"]:
            game_map.helicopter.set_stop_x()
        elif key.char in ["w", "s"]:
            game_map.helicopter.set_stop_y()


listener = keyboard.Listener(on_press=on_press, on_release=on_release, suppress=True)

listener.start()

# DEBUG
# game_map.helicopter.set_move_up()

tick = 0
last_tick_time = time.time()
while True:
    loop_start = time.time()
    if game_stoped:
        saver.save(SAVEFILE, game_map.dump())
        utils.cls()
        print(f"Game stopped. Your level is {game_map.helicopter.level}. Your score is {game_map.helicopter.score}")
        break

    if game_map.helicopter.is_dead():
        utils.cls()
        print(f"Game Over. Your level is {game_map.helicopter.level}")
        print("[Esc] Save and exit")
        time.sleep(0.5)
        continue

    if game_paused:
        utils.cls()
        print(f"Game paused. Your level is {game_map.helicopter.level}. Your score is {game_map.helicopter.score}")
        print("[Space] to continue [F5] to save [F6] to load [Esc] save and exit")
        while game_paused and not game_stoped:
            time.sleep(0.5)
        last_tick_time = time.time()
        continue

    tick_time, last_tick_time = u.tick(last_tick_time)

    game_map.process(tick_time)

    screen = ""
    if c.DEBUG:
        screen += f"{c.T.i[c.T.CLOCK]}{tick * TICK_DELAY:.2f}s Tick: {tick} Tick time: {tick_time:.2f}s\n"
    screen += game_map.helicopter.status()
    screen += game_map.render()
    screen += "[W/A/S/D] to move [Esc] save and exit [Space] to pause [F5] to save [F6] to load\n"
    utils.cls()
    print(screen)

    loop_time = time.time() - loop_start
    if TICK_DELAY - loop_time > 0:
        time.sleep(TICK_DELAY - loop_time)
    tick += 1

listener.stop()
