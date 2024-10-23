import os
from os.path import join, dirname

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from dotenv import load_dotenv

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

bot = Bot(token=os.environ.get('BOT_TOKEN'))
dp = Dispatcher(storage=MemoryStorage())
