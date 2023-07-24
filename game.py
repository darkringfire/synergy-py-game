from map import Map
import time
from pynput import keyboard
import conf as c
import utils as u
import saver
from reprint import output

MAP_SIZE = (20, 20)

TICK_DELAY = 0.1

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

game_paused = True
u.cls()
print(
    """
You need to move your helicopter to douse trees before they are burned.
You can fill your tank with water if helicopter is above rivers.
You can douse fire if there is water in the tank.
You can upgrade your helicopter in the workshop.
Upgrading increases the level, tank capacity, speed of helicopter,
and also increase difficulty of the game:
decrease trees spawning, increase fire frequency, increase burned tree penalty.

[Space] to continue
"""
)
while game_paused:
    time.sleep(0.5)

game_stoped = False
u.cls()

tick = 0
last_tick_time = time.time()
with output(initial_len=0) as output_lines:
    while True:
        loop_start = time.time()
        if game_stoped:
            saver.save(SAVEFILE, game_map.dump())
            output_lines.clear()
            output_lines.append(
                f"Game stopped. Your level is {game_map.helicopter.level}. Your score is {game_map.helicopter.score}"
            )
            break

        if game_map.helicopter.is_dead():
            output_lines.clear()
            output_lines.append(f"Game Over. Your level is {game_map.helicopter.level}")
            output_lines.append("[Esc] Save and exit")
            time.sleep(0.5)
            continue

        if game_paused:
            output_lines.clear()
            output_lines.append(
                f"Game paused. Your level is {game_map.helicopter.level}. Your score is {game_map.helicopter.score}"
            )
            output_lines.append("[Space] to continue [F5] to save [F6] to load [Esc] save and exit")
            while game_paused and not game_stoped:
                time.sleep(0.5)
            last_tick_time = time.time()
            continue

        tick_time, last_tick_time = u.tick(last_tick_time)

        game_map.process(tick_time)

        screen = []
        if c.DEBUG:
            screen.append(f"{c.T.i[c.T.CLOCK]}{tick * TICK_DELAY:.2f}s Tick: {tick} Tick time: {tick_time:.2f}s")
        screen.extend(game_map.helicopter.status())
        screen.extend(game_map.render())
        screen.append("[W/A/S/D] to move [Esc] save and exit [Space] to pause [F5] to save [F6] to load")
        for i in range(0, len(screen)):
            if i > len(output_lines)-1:
                output_lines.append(screen[i])
            elif output_lines[i] != screen[i]:
                output_lines[i] = screen[i]

        loop_time = time.time() - loop_start
        if TICK_DELAY - loop_time > 0:
            time.sleep(TICK_DELAY - loop_time)
        tick += 1

listener.stop()
