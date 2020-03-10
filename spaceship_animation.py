import asyncio
from curses_tools import draw_frame, read_controls


async def animate_spaceship(canvas, row, column, space_ship_center_col,
                            frames, max_row, max_col, speed_row, speed_column):
    """"""

    while True:

        rows_direction, columns_direction, space_pressed = read_controls(
            canvas, speed_row, speed_column)

        row = row + rows_direction
        if row >= max_row:
            row -= speed_row
        elif row <= 1:
            row += speed_row

        column = column + columns_direction
        if column - space_ship_center_col >= max_col:
            column -= speed_column
        elif column + space_ship_center_col <= speed_column:
            column += speed_column

        for frame in frames:

            draw_frame(canvas, row, column - space_ship_center_col, frame)
            for _ in range(1):
                await asyncio.sleep(0)
            draw_frame(canvas, row, column - space_ship_center_col, frame,
                       negative=True)
