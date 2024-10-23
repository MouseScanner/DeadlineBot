import aiosqlite


class TasksDatabase:
    def __init__(self, db_name):
        self.db_name = db_name

    async def create_table(self):
        async with aiosqlite.connect(self.db_name) as db:
            await db.execute('''
                CREATE TABLE IF NOT EXISTS tasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    chat_id INTEGER,
                    name TEXT DEFAULT "Название задания не указано",
                    description TEXT DEFAULT "Описание задания не указано",
                    type TEXT DEFAULT "домашнее задание",
                    deadline_at INTEGER,
                    
                    created_by TEXT,
                    created_at INTEGER,
                    
                    last_edited_by TEXT DEFAULT "",
                    last_edited_at INTEGER DEFAULT 0,
                    
                    status TEXT DEFAULT "назначено"
                )
            ''')
            await db.commit()

    async def get_tasks(self) -> list:
        async with aiosqlite.connect(self.db_name) as db:
            async with db.execute('SELECT * FROM tasks ORDER BY deadline_at ASC') as cursor:
                return await cursor.fetchall()

    async def get_tasks_by_chat_id(self, chat_id: int) -> list:
        async with aiosqlite.connect(self.db_name) as db:
            async with db.execute('SELECT * FROM tasks WHERE chat_id = ? AND status != "zero" AND status != "удалено" ORDER BY deadline_at ASC', (chat_id, )) as cursor:
                return await cursor.fetchall()


    async def task_exists(self, id: int) -> bool:
        async with aiosqlite.connect(self.db_name) as db:
            async with db.execute('SELECT * FROM tasks WHERE id = ?',
                                  (id,)) as cursor:
                return await cursor.fetchone() is not None

    async def add(self, chat_id, name, description, type, deadline_at, created_by, created_at):
        async with aiosqlite.connect(self.db_name) as db:
            await db.execute(
                'INSERT INTO tasks (chat_id, name, description, type, deadline_at, created_by, created_at, last_edited_by, last_edited_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)',
                (chat_id, name, description, type, deadline_at, created_by, created_at, created_by, created_at))
            await db.commit()
            return (await (await db.execute(
                ("SELECT id FROM tasks ORDER BY id DESC LIMIT 1")
            )).fetchone())[0]

    async def set_status(self, id: int, value: str) -> None:
        async with aiosqlite.connect(self.db_name) as db:
            await db.execute('UPDATE tasks SET status = ? WHERE id = ?', (value, id))
            await db.commit()

    async def set_name(self, id: int, value: str) -> None:
        async with aiosqlite.connect(self.db_name) as db:
            await db.execute('UPDATE tasks SET name = ? WHERE id = ?', (value, id))
            await db.commit()

    async def set_description(self, id: int, value: str) -> None:
        async with aiosqlite.connect(self.db_name) as db:
            await db.execute('UPDATE tasks SET description = ? WHERE id = ?', (value, id))
            await db.commit()

    async def set_type(self, id: int, value: str) -> None:
        async with aiosqlite.connect(self.db_name) as db:
            await db.execute('UPDATE tasks SET type = ? WHERE id = ?', (value, id))
            await db.commit()

    async def set_deadline_at(self, id: int, value: int) -> None:
        async with aiosqlite.connect(self.db_name) as db:
            await db.execute('UPDATE tasks SET deadline_at = ? WHERE id = ?', (value, id))
            await db.commit()

    async def set_last_edited_at(self, id: int, value: int) -> None:
        async with aiosqlite.connect(self.db_name) as db:
            await db.execute('UPDATE tasks SET last_edited_at = ? WHERE id = ?', (value, id))
            await db.commit()

    async def set_last_edited_by(self, id: int, value: int) -> None:
        async with aiosqlite.connect(self.db_name) as db:
            await db.execute('UPDATE tasks SET last_edited_by = ? WHERE id = ?', (value, id))
            await db.commit()

    async def get_value(self, id: int, key: str):
        async with aiosqlite.connect(self.db_name) as db:
            async with db.execute(f'SELECT {key} FROM tasks WHERE id = ?',
                                  (id,)) as cursor:
                return (await cursor.fetchone())[0]


tasks_database = TasksDatabase('data/database.sqlite')
