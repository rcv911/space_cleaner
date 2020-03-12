import time
import curses
import random
from fire_animation import fire
from curses_tools import get_frame_size
from sky_animation import blink
from spaceship_animation import animate_spaceship

TIC_TIMEOUT = 0.1


def load_frame(file):
    with open(file, 'r') as f:
        frame = f.read()
    return frame


def build_game(canvas):
    """ main draw """
    # sky config
    star_qty = 113
    left_space = 2
    blink_value = 10
    star_symbols = '+*.:'

    # spaceship move speed config
    ship_speed_row = 1  # Y
    ship_speed_column = 4  # X

    # fire speed config
    fire_speed_row = -1.5
    fire_speed_column = 0

    frame1 = load_frame('animation/rocket_frame_1.txt')
    frame2 = load_frame('animation/rocket_frame_2.txt')
    frames = [frame1, frame2]

    canvas.nodelay(True)
    canvas.border()
    curses.curs_set(False)

    max_row, max_column = canvas.getmaxyx()
    center_row = max_row // 2
    center_col = max_column // 2

    frame_row, frame_column = get_frame_size(frames[0])
    ship_center_col = frame_column / 2

    border_row = max_row - frame_row
    border_column = max_column - frame_column

    coroutines = list()
    for star in range(star_qty):
        row = random.randint(left_space, max_row - left_space)
        column = random.randint(left_space, max_column - left_space)
        symbol = random.choice(star_symbols)
        blink_delay = random.randint(0, blink_value)
        coroutines.append(blink(canvas, row, column, blink_delay, symbol))

    ship = animate_spaceship(canvas, center_row,  center_col, ship_center_col,
                             frames, border_row, border_column,
                             ship_speed_row, ship_speed_column)
    coroutines.append(ship)

    shoot_fire = fire(canvas, center_row, center_col, fire_speed_row,
                      fire_speed_column)
    coroutines.append(shoot_fire)

    while coroutines:

        for coroutine in coroutines.copy():
            try:
                coroutine.send(None)
            except StopIteration:
                coroutines.remove(coroutine)

        canvas.refresh()
        time.sleep(TIC_TIMEOUT)
