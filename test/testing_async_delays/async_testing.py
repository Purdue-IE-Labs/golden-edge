import asyncio
import time

def write_tag(value: int) -> int:
    time.sleep(5)
    return value + 1

async def update_value(val):
    return val + 1

async def count_up(start: int, stop: int):
    val = start
    while val < stop:
        await asyncio.sleep(0.4) # this is necessary to give control over to the other task
        val = await update_value(val)
        print(val)
    return val

def network_call(my_num):
    print("blocking")
    time.sleep(my_num)
    print("done blocking")

async def main():
    # task2 = asyncio.create_task(count_up(5, 7))
    # task1 = asyncio.create_task(count_up(12, 14))
    # await task1
    # await task2

    # waits for all tasks to finish
    async with asyncio.TaskGroup() as tg:
        task1 = tg.create_task(count_up(5, 10))
        task2 = tg.create_task(count_up(12, 16))
        task3 = tg.create_task(count_up(24, 27))
    
    future = await asyncio.gather(count_up(2, 5), count_up(8, 10))
    print(future)

    task1 = asyncio.create_task(count_up(4, 6), name="foo")
    task2 = asyncio.create_task(count_up(8, 11), name="bar")
    done, pending = await asyncio.wait([task1, task2])
    print(done, pending)

    await asyncio.gather(
        asyncio.to_thread(network_call, my_num=2),
        asyncio.to_thread(network_call, 1),
        count_up(1, 10)
    )

    coro = asyncio.to_thread(network_call, 2)

    # await asyncio.open_connection()

    time.sleep(10)

    # coroutine won't be run until awaited
    await coro


asyncio.run(main())
