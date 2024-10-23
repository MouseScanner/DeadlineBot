import asyncio
import datetime

import aioschedule as aioschedule

from handlers import user_handlers

from loguru import logger

from data.config import bot, dp
from data.methods.tasks import tasks_database
from utils.scheduler import check_task_deadlines


async def on_startup():
    logger.info("Bot is starting up.")


async def on_shutdown():
    logger.info("Bot is shutting down.")


async def check_deadlines():
    now = int(datetime.datetime.now().timestamp())
    chat_ids = []
    for task in await tasks_database.get_tasks():
        deadline_at = task[5]
        task_chat_id = task[1]

        if task_chat_id in chat_ids:
            continue

        dif = deadline_at - now

        status = task[-1]

        if status == 'удалено':
            continue

        await check_task_deadlines(task, status, dif, bot, tasks_database, chat_ids)


async def scheduler():
    tasks = []
    while True:
        asyncio.create_task(check_deadlines())
        await asyncio.sleep(10)


async def main():
    await tasks_database.create_table()
    logger.info("Tasks data base is enabled.")
    dp.include_router(user_handlers.router)
    logger.info("User handlers is connected.")
    asyncio.create_task(scheduler())
    logger.info("Scheduler is started.")
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
