import time
import curses
import random
from curses_tools import get_frame_size
from sky_animation import blink
# from spaceship_animation import animate_spaceship
from space_garbage import fly_garbage
from sleep import sleep
import asyncio
from curses_tools import draw_frame, read_controls
from physics import update_speed
from fire_animation import fire


TIC_TIMEOUT = 0.1
# coroutines = list()


def load_frame(file):
    with open(file, 'r') as f:
        frame = f.read()
    return frame


async def animate_spaceship(canvas, row, column, space_ship_center_col,
                            frames, max_row, max_col, speed_row, speed_column,
                            fire_speed_row, fire_speed_column):
    """
    Обновляет spaceship_frame, но не трогает canvas и draw_frame
    """
    global spaceship_frame

    spaceship_frame = await run_spaceship(canvas, row, column,
                                          space_ship_center_col, frames,
                                          max_row, max_col, speed_row,
                                          speed_column, fire_speed_row,
                                          fire_speed_column)


async def run_spaceship(canvas, row, column, space_ship_center_col,
                        frames, max_row, max_col, speed_row, speed_column,
                        fire_speed_row, fire_speed_column):
    """
    Управляет положением корабля и рисует его на экране
    """
    while True:

        row_speed = column_speed = 0

        rows_direction, columns_direction, space_pressed = read_controls(
            canvas, speed_row, speed_column)

        row_speed, column_speed = update_speed(row_speed, column_speed,
                                               rows_direction,
                                               columns_direction)

        row = row + rows_direction + row_speed
        if row >= max_row:
            row -= speed_row
        elif row <= 1:
            row += speed_row

        column = column + columns_direction + column_speed
        if column - space_ship_center_col >= max_col:
            column -= speed_column
        elif column + space_ship_center_col <= speed_column:
            column += speed_column

        shoot_fire = fire(canvas, row, column,
                          fire_speed_row, fire_speed_column)
        coroutines.append(shoot_fire)

        for frame in frames:
            draw_frame(canvas, row, column - space_ship_center_col, frame)
            await asyncio.sleep(0)
            draw_frame(canvas, row, column - space_ship_center_col, frame,
                       negative=True)


async def fill_orbit_with_garbage(canvas, frames, max_column, left_space):

    while True:
        column = random.randint(0, max_column - left_space)
        trash = fly_garbage(canvas, column, random.choice(frames), speed=0.5)
        coroutines.append(trash)
        await sleep(random.randint(0, 10))


def build_game(canvas):
    """ main draw """
    global coroutines
    # sky config
    star_qty = 113
    left_space = 2
    blink_value = 10
    star_symbols = '+*.:'

    # spaceship move speed config
    ship_speed_row = 1  # Y
    ship_speed_column = 1  # X

    # fire speed config
    fire_speed_row = -2.0
    fire_speed_column = 0

    spaceship_files = [
        'animation/rocket_frame_1.txt',
        'animation/rocket_frame_2.txt'
    ]
    spaceship_frames = list()
    for file in spaceship_files:
        spaceship_frames.append(load_frame(file))

    garbage_files = [
        'animation/trash_small.txt',
        'animation/trash_large.txt',
        'animation/trash_xl.txt',
        'animation/lamp.txt',
        'animation/hubble.txt',
        'animation/duck.txt',
    ]

    garbage_frames = list()
    for file in garbage_files:
        garbage_frames.append(load_frame(file))

    canvas.nodelay(True)
    canvas.border()
    curses.curs_set(False)

    max_row, max_column = canvas.getmaxyx()
    center_row = max_row // 2
    center_col = max_column // 2

    frame_row, frame_column = get_frame_size(spaceship_frames[0])
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
                             spaceship_frames, border_row, border_column,
                             ship_speed_row, ship_speed_column,
                             fire_speed_row, fire_speed_column)
    coroutines.append(ship)

    # shoot_fire = fire(canvas, center_row, center_col, fire_speed_row,
    #                   fire_speed_column)
    # coroutines.append(shoot_fire)

    fill = fill_orbit_with_garbage(canvas, garbage_frames, max_column,
                                   left_space)
    coroutines.append(fill)

    # game engine
    custom_event_loop(canvas)


def custom_event_loop(canvas):

    while coroutines:

        for coroutine in coroutines.copy():
            try:
                coroutine.send(None)
            except StopIteration:
                coroutines.remove(coroutine)

        canvas.refresh()
        time.sleep(TIC_TIMEOUT)
