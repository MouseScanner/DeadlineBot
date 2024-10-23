import datetime
import html

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery, FSInputFile, InlineKeyboardMarkup, InlineKeyboardButton

from data import config
from data.config import bot
from data.methods.tasks import tasks_database

from loguru import logger

import utils
from keyboards.user_keyboards import add_task_kb, update_task_kb

router = Router()


@router.message(Command('start', ignore_case=True))
async def start_handler(message: Message, state: FSMContext):
    await message.reply('''📌 Устанавливайте напоминания о ваших дедлайнах прямо в беседе!

Для добавления задания введите команду <code>/добавить</code> и следуйте дальнейшей инструкции по добавлению нового задания.

Для того, чтобы посмотреть список всех дедлайнов необходимо ввести команду <code>/список</code>. Каждый из них расположен в порядке наименьшего остатка времени до конца сдачи задания.

Для редактирования информации о задании используйте уникальный номер задания, которые находится в списке.
К примеру,
<i>Уникальный номер: 1
Задание: Проект по микроэкономике
Описание: Вычислить 1+2</i>

В панель редактирования задания можно перейти с помощью команды <code>/изменить номер_задания</code> (к примеру, /изменить 1) или через панель в списке заданий.''',
                        parse_mode='HTML')


class AddTaskStates(StatesGroup):
    get_task_name = State()
    get_task_description = State()
    get_task_deadline = State()


@router.message(Command('добавить', ignore_case=True))
async def get_task_name_handler(message: Message, state: FSMContext):
    await state.clear()

    data = await state.get_data()

    keyboard = await add_task_kb(data)

    await message.reply('''📖 Вы перешли в панель добавления заданий.

Вам необходимо заполнить необходимые данные для заполнения дедлайны. Выберите в том порядке, в котором вам удобно.''',
                        parse_mode='HTML', reply_markup=keyboard)


@router.callback_query(lambda clb: clb.data == 'add_name')
async def add_task_name_handler(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()

    keyboard = await add_task_kb(data)

    await callback.message.answer('''Введите, пожалуйста, название задания.''',
                                  parse_mode='HTML', reply_markup=keyboard)
    await callback.answer()
    await state.set_state(AddTaskStates.get_task_name)


@router.callback_query(lambda clb: clb.data == 'add_deadline')
async def add_task_deadline_handler(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()

    keyboard = await add_task_kb(data)

    await callback.message.answer('''Пожалуйста, укажите дату <b>дедлайна</b> задачи.

<b>Как можно записать</b>: 
20.12.2023 = 20.12.2023 0:00
20.12.2023 23:59 = 20.12.2023 23:59 
завтра = ну, получается, завтра
сегодня 23:59

🔎 Пример: <i>20.12.2023 23:59</i>.''',
                                  parse_mode='HTML', reply_markup=keyboard)
    await callback.answer()
    await state.set_state(AddTaskStates.get_task_deadline)


@router.callback_query(lambda clb: clb.data == 'add_description')
async def add_task_desc_handler(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()

    keyboard = await add_task_kb(data)

    await callback.message.answer('''Пожалуйста, введите <b>описание</b> задачи.

🔎 Пример: <i>Расписать план выполнения проектов, а также распределить пункт каждому из участников.</i>''',
                                  parse_mode='HTML', reply_markup=keyboard)
    await callback.answer()
    await state.set_state(AddTaskStates.get_task_description)


@router.message(AddTaskStates.get_task_name)
async def get_task_description_handler(message: Message, state: FSMContext):
    task_name = message.text

    if not 3 <= len(task_name) <= 150:
        await message.reply(
            '🚫 Название задания должно содержать от 3 до 150 символов. Пожалуйста, соблюдайте ограничения.\n\nВведите еще раз название задания.')
        return

    await message.reply(f'''✏️ Вы внесли название: <i>{html.escape(task_name)}</i>''',
                        parse_mode='HTML')

    await state.update_data({"add_task_name": task_name})

    data = await state.get_data()

    if not ('add_task_description' in data and 'add_task_name' in data and 'add_task_deadline' in data):
        keyboard = await add_task_kb(data)

        await message.answer('''📖 Вы перешли в панель добавления заданий.

            Вам необходимо заполнить необходимые данные для заполнения дедлайны. Выберите в том порядке, в котором вам удобно.''',
                             parse_mode='HTML', reply_markup=keyboard)
        return

    name = data['add_task_name']
    description = data['add_task_description']
    data = data['add_task_deadline']

    task_id = await tasks_database.add(message.chat.id, name, description, "задание",
                                       int(datetime.datetime.strptime(data, '%d.%m.%Y %H:%M').timestamp()),
                                       message.from_user.username,
                                       int(datetime.datetime.now().timestamp()))

    keyboard = await update_task_kb(task_id)

    await message.answer(f'''✅ Вы успешно добавили задание.

    Уникальный номер: <code>{task_id}</code>

    Название: <b>{name}</b>
    Описание: <b>{description}</b>

    ❗️ Дедлайн: {datetime.datetime.strptime(data, '%d.%m.%Y %H:%M')}''',
                         parse_mode='HTML', reply_markup=keyboard)

    await state.clear()


@router.message(AddTaskStates.get_task_description)
async def get_task_deadline_handler(message: Message, state: FSMContext):
    task_description = message.text

    if not 3 <= len(task_description) <= 2048:
        await message.reply(
            '🚫 Описание задания должно содержать от 3 до 2048 символов. Пожалуйста, соблюдайте ограничения.\n\nВведите еще раз название задания.')
        return

    await message.reply(f'''✏️ Вы внесли описание.''',
                        parse_mode='HTML')

    await state.update_data({"add_task_description": task_description})

    data = await state.get_data()

    if not ('add_task_description' in data and 'add_task_name' in data and 'add_task_deadline' in data):
        keyboard = await add_task_kb(data)

        await message.answer('''📖 Вы перешли в панель добавления заданий.

            Вам необходимо заполнить необходимые данные для заполнения дедлайны. Выберите в том порядке, в котором вам удобно.''',
                             parse_mode='HTML', reply_markup=keyboard)
        return

    name = data['add_task_name']
    description = data['add_task_description']
    data = data['add_task_deadline']

    task_id = await tasks_database.add(message.chat.id, name, description, "задание",
                                       int(datetime.datetime.strptime(data, '%d.%m.%Y %H:%M').timestamp()),
                                       message.from_user.username,
                                       int(datetime.datetime.now().timestamp()))

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='Изменить название', callback_data=f'change_task_param:{task_id}:name')],
        [InlineKeyboardButton(text='Изменить описание', callback_data=f'change_task_param:{task_id}:description')],
        [InlineKeyboardButton(text='Изменить дедлайн', callback_data=f'change_task_param:{task_id}:deadline_at')],
        [InlineKeyboardButton(text='Удалить', callback_data=f'delete_task:{task_id}')],
    ])
    await message.answer(f'''✅ Вы успешно добавили задание.

    Уникальный номер: <code>{task_id}</code>

    Название: <b>{name}</b>
    Описание: <b>{description}</b>

    ❗️ Дедлайн: {datetime.datetime.strptime(data, '%d.%m.%Y %H:%M')}''',
                         parse_mode='HTML', reply_markup=keyboard)

    await state.clear()


@router.message(AddTaskStates.get_task_deadline)
async def get_task_deadline_handler(message: Message, state: FSMContext):
    task_deadline = message.text.lower()

    is_success, result = utils.convert_input_date(task_deadline)

    if not is_success:
        await message.reply(
            f'🚫 Неверно задано время дедлайна: {result}', parse_mode='HTML')
        return

    await state.update_data({"add_task_deadline": result})

    data = await state.get_data()

    if not ('add_task_description' in data and 'add_task_name' in data and 'add_task_deadline' in data):
        keyboard = await add_task_kb(data)

        await message.answer('''📖 Вы перешли в панель добавления заданий.

        Вам необходимо заполнить необходимые данные для заполнения дедлайны. Выберите в том порядке, в котором вам удобно.''',
                             parse_mode='HTML', reply_markup=keyboard)
        return

    name = data['add_task_name']
    description = data['add_task_description']
    data = data['add_task_deadline']

    task_id = await tasks_database.add(message.chat.id, name, description, "задание",
                                       int(datetime.datetime.strptime(data, '%d.%m.%Y %H:%M').timestamp()),
                                       message.from_user.username,
                                       int(datetime.datetime.now().timestamp()))

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='Изменить название', callback_data=f'change_task_param:{task_id}:name')],
        [InlineKeyboardButton(text='Изменить описание', callback_data=f'change_task_param:{task_id}:description')],
        [InlineKeyboardButton(text='Изменить дедлайн', callback_data=f'change_task_param:{task_id}:deadline_at')],
        [InlineKeyboardButton(text='Удалить', callback_data=f'delete_task:{task_id}')],
    ])
    await message.answer(f'''✅ Вы успешно добавили задание.

Уникальный номер: <code>{task_id}</code>

Название: <b>{name}</b>
Описание: <b>{description}</b>

❗️ Дедлайн: {datetime.datetime.strptime(data, '%d.%m.%Y %H:%M')}''',
                         parse_mode='HTML', reply_markup=keyboard)

    await state.clear()


@router.message(
    lambda msg: msg is not None and (
            msg.text.startswith('/изменить') or msg.text.startswith('/задание') or msg.text.startswith('/з ')))
async def change_task_handler(message: Message, state: FSMContext):
    args = message.text.split()

    if len(args) != 2:
        await message.reply(
            f'🚫 Неверный формат команды. Используйте <code>/изменить уникальный_номер_задания</code>',
            parse_mode='HTML')
        return

    cmd, task_id = args

    if not task_id.isdigit():
        await message.reply(
            f'🚫 Номер задания должен включать в себя только число. Используйте <code>/изменить уникальный_номер_задания</code>',
            parse_mode='HTML')
        return

    if not (await tasks_database.task_exists(task_id)):
        await message.reply(
            f'🚫 Номер задания не найден в системе. Перепроверьте ввод.', parse_mode='HTML')
        return

    if (await tasks_database.get_value(task_id, 'chat_id')) != message.chat.id:
        await message.reply(
            f'🚫 Номер задания не найден в этом чате. Перепроверьте ввод.', parse_mode='HTML')
        return

    if (await tasks_database.get_value(task_id, 'status')) == "удалено":
        await message.reply(
            f'🚫 Данное задание было завершено и удалено.', parse_mode='HTML')
        return

    name = await tasks_database.get_value(task_id, 'name')
    description = await tasks_database.get_value(task_id, 'description')
    created_by = await tasks_database.get_value(task_id, 'created_by')
    created_at = await tasks_database.get_value(task_id, 'created_at')
    last_edited_by = await tasks_database.get_value(task_id, 'last_edited_by')
    last_edited_at = await tasks_database.get_value(task_id, 'last_edited_at')
    deadline = datetime.datetime.fromtimestamp(await tasks_database.get_value(task_id, 'deadline_at'))

    now = datetime.datetime.now()

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='Изменить название', callback_data=f'change_task_param:{task_id}:name')],
        [InlineKeyboardButton(text='Изменить описание', callback_data=f'change_task_param:{task_id}:description')],
        [InlineKeyboardButton(text='Изменить дедлайн', callback_data=f'change_task_param:{task_id}:deadline_at')],
        [InlineKeyboardButton(text='Удалить', callback_data=f'delete_task:{task_id}')],
    ])
    if not last_edited_at:
        await message.answer(f'''🏷 УН: <code>{task_id}</code>
<b>{html.escape(name)}</b>
{html.escape(description)}

<i>Добавлен @{created_by}, {datetime.datetime.fromtimestamp(created_at).strftime('%d.%m.%Y %H:%M')}</i>

До конца дедлайна осталось: {utils.seconds_to_string(int((deadline - now).seconds) + 24 * 60 * 60 * (deadline - now).days)} ({deadline.strftime('%d.%m.%Y %H:%M')})''',
                             parse_mode='HTML', reply_markup=keyboard)

        await state.clear()
    else:
        await message.answer(f'''🏷 УН: <code>{task_id}</code>
<b>{html.escape(name)}</b>
{html.escape(description)}

<i>Добавлен @{created_by}, {datetime.datetime.fromtimestamp(created_at).strftime('%d.%m.%Y %H:%M')}</i>
<i>Последний раз отредактировал @{last_edited_by}, {datetime.datetime.fromtimestamp(last_edited_at).strftime('%d.%m.%Y %H:%M')}</i>

До конца дедлайна осталось: {utils.seconds_to_string(int((deadline - now).seconds) + 24 * 60 * 60 * (deadline - now).days)} ({deadline.strftime('%d.%m.%Y %H:%M')})''',
                             parse_mode='HTML', reply_markup=keyboard)


class ChangeParamStates(StatesGroup):
    get_new_value = State()


@router.callback_query(lambda clb: clb.data.startswith('change_task_param:'))
async def change_param_task_handler(clb: CallbackQuery, state: FSMContext):
    cmd, task_id, param_name = clb.data.split(':')
    task_id = int(task_id)
    display_names = {
        'name': 'название',
        'description': 'описание',
        'deadline_at': 'дедлайн'
    }
    await state.update_data({"change_param_name": param_name, "change_task_id": task_id})
    await clb.answer()

    if param_name == 'deadline_at':
        await clb.message.answer(
            f'''Текущее(/ий) {display_names[param_name]}: <i>{html.escape(datetime.datetime.fromtimestamp(await tasks_database.get_value(task_id, param_name)).strftime('%d.%m.%Y %H:%M'))}</i>

        На что хотите изменить?''', parse_mode='HTML')
    else:
        await clb.message.answer(
            f'''Текущее(/ий) {display_names[param_name]}: <i>{html.escape(str(await tasks_database.get_value(task_id, param_name)))}</i>
    
    На что хотите изменить?''', parse_mode='HTML')
    await state.set_state(ChangeParamStates.get_new_value)


@router.message(ChangeParamStates.get_new_value)
async def get_param_task_handler(message: Message, state: FSMContext):
    new_val = message.text

    data = await state.get_data()
    task_id = data['change_task_id']
    param_name = data['change_param_name']

    if param_name == 'deadline_at':
        task_deadline = new_val

        is_success, result = utils.convert_input_date(task_deadline)

        if not is_success:
            await message.reply(
                f'🚫 Неверно задано время дедлайна: {result}.\nВведите еще раз', parse_mode='HTML')
            return
        await tasks_database.set_deadline_at(task_id,
                                             int(datetime.datetime.strptime(result, '%d.%m.%Y %H:%M').timestamp()))
        await message.answer(
            f'''Вы изменили дедлайн на <b>{html.escape(result)}</b>''', parse_mode='HTML')
        await state.clear()
        return

    display_names = {
        'name': 'название',
        'description': 'описание',
        'deadline_at': 'дедлайн'
    }
    if param_name == 'name':
        await tasks_database.set_name(task_id, new_val)
    elif param_name == 'description':
        await tasks_database.set_description(task_id, new_val)

    await tasks_database.set_last_edited_by(task_id, message.from_user.username)
    await tasks_database.set_last_edited_at(task_id, int(datetime.datetime.now().timestamp()))

    await message.answer(
        f'''Вы изменили <i>{display_names[param_name]}</i> на <code>{new_val}</code>''', parse_mode='HTML')
    await state.clear()


@router.callback_query(lambda clb: clb.data.startswith('delete_task:'))
async def change_param_task_handler(clb: CallbackQuery, state: FSMContext):
    cmd, task_id = clb.data.split(':')

    task_id = int(task_id)

    if not (await tasks_database.task_exists(task_id)):
        await clb.message.answer("Данное задание было удалено.")
        return
    created_by = (await tasks_database.get_value(task_id, 'created_by'))

    if created_by != clb.from_user.username:
        await clb.message.answer(f"Данное задание было создано @{created_by}. Только автор может удалить задание.")
        return
    await clb.answer()
    await tasks_database.set_status(task_id, 'удалено')
    await clb.message.answer(f"Вы удалили задание №{task_id}.")


@router.message(F.text.startswith('/список'))
async def change_task_handler(message: Message, state: FSMContext):
    args = message.text.split()

    if len(args) != 1:
        await message.reply(
            f'🚫 Неверный формат команды. Используйте <code>/список<code>',
            parse_mode='HTML')
        return

    chat_tasks = await tasks_database.get_tasks_by_chat_id(message.chat.id)

    msg = '⤵️ Для просмотра подробности задания используйте <code>/задание уникальный_номер</code>\n\n'
    now = datetime.datetime.now()
    for chat_task in chat_tasks:
        deadline = datetime.datetime.fromtimestamp(chat_task[5])
        msg += f'''[№<b>{chat_task[0]}</b>] <b>{html.escape(chat_task[2])}</b>
❗️ До конца дедлайна осталось: {utils.seconds_to_string(int((deadline - now).seconds) + 24 * 60 * 60 * (deadline - now).days)} ({deadline.strftime('%d.%m.%Y %H:%M')})
'''
    await message.answer(msg, parse_mode='HTML')
