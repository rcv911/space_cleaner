import time
import curses
import random
from curses_tools import get_frame_size
from sky_animation import blink
from sleep import sleep
import asyncio
from curses_tools import draw_frame, read_controls
from physics import update_speed
from obstacles import Obstacle, show_obstacles
# from spaceship_animation import animate_spaceship
# from space_garbage import fly_garbage
# from fire_animation import fire


TIC_TIMEOUT = 0.1


def load_frame(file):
    with open(file, 'r') as f:
        frame = f.read()
    return frame


async def fire(canvas, start_row, start_column, rows_speed=-0.3,
               columns_speed=0):
    """Display animation of gun shot. Direction and speed can be specified."""

    row, column = start_row, start_column

    canvas.addstr(round(row), round(column), '*')
    await asyncio.sleep(0)

    canvas.addstr(round(row), round(column), 'O')
    await asyncio.sleep(0)
    canvas.addstr(round(row), round(column), ' ')

    row += rows_speed
    column += columns_speed

    symbol = '-' if columns_speed else '|'

    rows, columns = canvas.getmaxyx()
    max_row, max_column = rows - 1, columns - 1

    curses.beep()

    while 0 < row < max_row and 0 < column < max_column:
        canvas.addstr(round(row), round(column), symbol)
        await asyncio.sleep(0)
        canvas.addstr(round(row), round(column), ' ')

        for obst in obstacles:
            if obst.has_collision(row, column):
                obstacles_in_last_collisions.append(obst)
                return

        row += rows_speed
        column += columns_speed


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

        if space_pressed:
            shoot_fire = fire(canvas, row, column,
                              fire_speed_row, fire_speed_column)
            coroutines.append(shoot_fire)

        for frame in frames:
            draw_frame(canvas, row, column - space_ship_center_col, frame)
            await asyncio.sleep(0)
            draw_frame(canvas, row, column - space_ship_center_col, frame,
                       negative=True)


async def fly_garbage(canvas, column, garbage_frame, speed=0.5):
    """
    Animate garbage, flying from top to bottom. Сolumn position will stay
    same, as specified on start.
    """
    rows_number, columns_number = canvas.getmaxyx()

    column = max(column, 0)
    column = min(column, columns_number - 1)

    row = 0
    garbage_row, garbage_column = get_frame_size(garbage_frame)

    while row < rows_number:

        draw_frame(canvas, row, column, garbage_frame)
        obstacles.append(Obstacle(row, column, garbage_row, garbage_column))
        await asyncio.sleep(0)
        draw_frame(canvas, row, column, garbage_frame, negative=True)
        obstacles.pop(0)

        # for obst in obstacles_in_last_collisions:
        #     return obst

        row += speed


async def fill_orbit_with_garbage(canvas, frames, max_column, left_space):

    while True:
        column = random.randint(0, max_column - left_space)

        trash = fly_garbage(canvas, column, random.choice(frames), speed=0.5)
        coroutines.append(trash)

        await sleep(random.randint(0, 30))


def build_game(canvas):
    """ main draw """
    global coroutines, obstacles, obstacles_in_last_collisions
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

    obstacles = list()
    obstacles_in_last_collisions = list()

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

    fill = fill_orbit_with_garbage(canvas, garbage_frames, max_column,
                                   left_space)
    coroutines.append(fill)

    obst = show_obstacles(canvas, obstacles)
    coroutines.append(obst)

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
