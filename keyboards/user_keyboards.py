async def add_task_kb(data) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🏷 Добавить название",
                              callback_data="add_name")] if 'add_task_name' not in data else [],
        [InlineKeyboardButton(text="📝 Добавить описание",
                              callback_data="add_description"), ] if 'add_task_description' not in data else [],
        [InlineKeyboardButton(text="⌛️ Установить дедлайн",
                              callback_data="add_deadline"), ] if 'task_deadline' not in data else []

    ])

    return keyboard


async def update_task_kb(task_id: int | str) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='Изменить название', callback_data=f'change_task_param:{task_id}:name')],
        [InlineKeyboardButton(text='Изменить описание', callback_data=f'change_task_param:{task_id}:description')],
        [InlineKeyboardButton(text='Изменить дедлайн', callback_data=f'change_task_param:{task_id}:deadline_at')],
        [InlineKeyboardButton(text='Удалить', callback_data=f'delete_task:{task_id}')],
    ])

    return keyboard
