import asyncio
from time import sleep
from threading import Thread
from typing import List, Union

from aiogram import Bot, Dispatcher

from .models import UserBase  # Импорт модели пользователя
from .settings import settings, user_processes  # Импорт настроек и процессов пользователя
from .utils import clear_console, media_dir, LangsSingleton  # Импорт утилит
from .database import Database  # Импорт базы данных
from .router import global_router  # Импорт глобального роутера
from .middlewares import BaseMenuMiddleware, SomeMiddleware  # Импорт промежуточных слоев

async def bot_init( 
		bot_token: str,  # Токен бота для авторизации
		database_uri: str = f"sqlite+aiosqlite:///{settings.BASE_DIR / 'bot.db'}",  # URI базы данных
		db_echo: bool = True,  # Флаг вывода SQL-запросов в консоль
		super_users: List[Union[str, int]] = []
	) -> (Bot, Dispatcher):  # Функция возвращает объекты бота и диспетчера
	
	# Очистка консоли перед началом работы
	clear_console()
	
	# Инициализация базы данных с указанным URI
	database = Database(database_uri, [UserBase], db_echo)
	bot = Bot(token=bot_token, parse_mode='html')
	dp = Dispatcher()	
	
	# Получение информации о самом боте
	settings.ME = await bot.get_me()
	
	# Присвоение базы данных глобальной переменной
	settings.DATABASE = database
	settings.get_db = database.get_db
	settings.SUPER_USERS = super_users

	# Подключение глобального роутера для обработки входящих сообщений
	global_router(dp)  # {'report': [SomeMiddleware]}
	
	# Создание директории для медиафайлов, если ее еще не существует
	media_dir([settings.MEDIA_DIR])

	# Назначение внешнего промежуточного слоя для обработки колбэк-квери
	dp.callback_query.outer_middleware(BaseMenuMiddleware())
		
	# Инициализация моделей базы данных перед началом работы
	await database.init_models()
	
	return bot, dp
