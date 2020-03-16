import asyncio


async def sleep(tics=1):
    for _ in range(tics, 0, -1):
        await asyncio.sleep(0)
