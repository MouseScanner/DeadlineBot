async def send_deadline_reminder(task, status, dif, time_frame, new_status, time_text, bot, tasks_database, chat_ids):
    if time_frame[0] < dif <= time_frame[1] and status != new_status:
        await bot.send_message(
            chat_id=task[1],
            text=f"⚠️ Напоминание о дедлайне!\n\nЧерез менее, чем <b>{time_text}</b> подходит к концу дедлайн задания №{task[0]}.\n\n<i>{task[2]}\n\n{task[3]}</i>",
            parse_mode="HTML"
        )
        await tasks_database.set_status(task[0], new_status)
        if new_status == "3days":
            chat_ids.append(task[1])


async def check_task_deadlines(task, status, dif, bot, tasks_database, chat_ids):
    await send_deadline_reminder(task, status, dif, (24 * 60 * 60, 24 * 60 * 60 * 3), '3days', '3 дня', bot,
                                 tasks_database, chat_ids)
    await send_deadline_reminder(task, status, dif, (12 * 60 * 60, 24 * 60 * 60), '1day', '1 день', bot, tasks_database,
                                 chat_ids)
    await send_deadline_reminder(task, status, dif, (3 * 60 * 60, 12 * 60 * 60), 'halfday', '12 часов', bot,
                                 tasks_database, chat_ids)
    await send_deadline_reminder(task, status, dif, (1 * 60 * 60, 3 * 60 * 60), '3hours', '3 часа', bot, tasks_database,
                                 chat_ids)
    await send_deadline_reminder(task, status, dif, (1, 1 * 60 * 60), '1hour', '1 час', bot, tasks_database, chat_ids)

    if dif <= 1 and status != 'zero':
        await bot.send_message(
            chat_id=task[1],
            text=f"✅ Подошел конец дедлайна задания №{task[0]}.\n\n<i>{task[2]}\n\n{task[3]}</i>",
            parse_mode="HTML"
        )
        await tasks_database.set_status(task[0], "zero")
