import sys  # Импорт модуля sys для работы с системными функциями
from typing import List, Union, Dict, Any  # Импорт типов данных для аннотации типов

from aiogram.dispatcher.dispatcher import Dispatcher  # Импорт класса Dispatcher из библиотеки aiogram

from .handlers import base, admin  # Импорт модулей обработчиков для базовых и административных функций
from .middlewares import LangsMiddleware  # Импорт промежуточного слоя для работы с языками


def global_router(dp: Dispatcher, router_middlewares: Dict[str, List[Any]] = {}) -> None:
    """
    Глобальный маршрутизатор, добавляющий обработчики из модулей base и admin.

    Args:
        dp (Dispatcher): Объект диспетчера aiogram.
        router_middlewares (Dict[str, List[Any]], optional): Словарь промежуточных слоев для обработчиков, 
            где ключ - имя модуля, значение - список промежуточных слоев.

    Returns:
        None
    """

    for app in [base, admin]:
        app_name = app.__name__.split('.')[-1]
        
        # Добавление промежуточного слоя для работы с языками к обработчикам сообщений
        app.router.message.middleware(LangsMiddleware())

        # Добавление пользовательских промежуточных слоев, если они указаны
        for middleware in router_middlewares.get(app_name) or []:
            app.router.message.middleware(middleware())

        # Включение обработчиков маршрутизатора в диспетчер
        dp.include_router(app.router)
