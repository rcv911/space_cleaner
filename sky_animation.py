import asyncio
import curses
from sleep import sleep


async def blink(canvas, row, column, blink_delay, symbol='*'):
    
    while True:

        # for _ in range(blink_delay):
        #     await asyncio.sleep(0)
        await sleep(blink_delay)

        canvas.addstr(row, column, symbol, curses.A_DIM)
        # for _ in range(20):
        #     await asyncio.sleep(0)
        await sleep(20)

        canvas.addstr(row, column, symbol)
        # for _ in range(3):
        #     await asyncio.sleep(0)
        await sleep(3)

        canvas.addstr(row, column, symbol, curses.A_BOLD)
        # for _ in range(5):
        #     await asyncio.sleep(0)
        await sleep(5)

        canvas.addstr(row, column, symbol)
        # for _ in range(3):
        #     await asyncio.sleep(0)
        await sleep(3)
