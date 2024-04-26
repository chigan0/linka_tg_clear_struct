import os  # Импорт модуля os для работы с операционной системой
import asyncio  # Импорт модуля asyncio для асинхронных операций
from typing import Callable, Dict, Any, Awaitable, Union  # Импорт типов данных для аннотации типов

from aiogram import BaseMiddleware  # Импорт базового мидлвара aiogram
from aiogram.types import CallbackQuery, Message  # Импорт типов данных CallbackQuery и Message из aiogram

from ..utils import base_func, select_lang, admin_panel, other_callback, LangsSingleton  # Импорт функций и класса из других модулей
from ..settings import settings  # Импорт настроек из другого модуля


class GeneralMiddleware(BaseMiddleware):
    """
    Общий базовый класс для мидлваров.
    """

    def __init__(self):
        """
        Инициализация класса.
        """
        self.latency = 0.01  # Задержка для асинхронных операций
        self.lang = LangsSingleton(settings.LANG_DIR, settings.DEFAULT_LANG, settings.LANGUAGES)  # Язык

    def set_texts(self, data: Dict[str, Any]) -> None:
        """
        Установка текстов на нужном языке.

        Args:
            data: Словарь с данными.
        """
        data['lang'] = self.lang  # Установка языка


# Внешний мидлвар для всех колбэков
class BaseMenuMiddleware(GeneralMiddleware):
    """
    Мидлвар для базового меню.
    """

    async def __call__(self,
                       handler: Callable[[CallbackQuery, Dict[str, Any]], Awaitable[Any]],
                       event: CallbackQuery,
                       data: Dict[str, Any],
                       ) -> Any:
        """
        Вызов мидлвара.

        Args:
            handler: Обработчик.
            event: Событие.
            data: Данные.

        Returns:
            Результат выполнения.
        """
        self.set_texts(data)  # Установка текстов

        callback_data_router = {  # Роутер для колбэков
            'base_menu': {'callback': base_func},
            'select_lang': {'callback': select_lang},
            'admin_panel': {'callback': admin_panel},
            'other_callback': {'callback': other_callback, 'only_event': True}
        }

        callback_name: str = event.data.split('__')[0]  # Имя колбэка
        callback_data = callback_data_router.get(callback_name)  # Получение данных для колбэка

        if callback_data is None:
            return await handler(event, data)

        callable_or_msg = event if callback_data.get('only_event') else event.message  # Определение колбэка
        callback = callback_data['callback']  # Функция колбэка

        try:
            await callback(callable_or_msg, bot=data['bot'], state=data['state'], lang=self.lang, change=True)

        except Exception as e:
            print(e)
            await callback(callable_or_msg, data['bot'], data['state'], lang=self.lang, change=False)


class LangsMiddleware(GeneralMiddleware):
    """
    Мидлвар для языков.
    """

    async def __call__(self,
                       handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
                       event: Message,
                       data: Dict[str, Any]
                       ) -> Any:
        """
        Вызов мидлвара.

        Args:
            handler: Обработчик.
            event: Событие.
            data: Данные.

        Returns:
            Результат выполнения.
        """
        self.set_texts(data)  # Установка текстов

        return await handler(event, data)


class SomeMiddleware(GeneralMiddleware):
    """
    Некоторый мидлвар.
    """

    album_data: dict = {}  # Данные альбома

    async def __call__(self,
                       handler: Callable[[Message, dict[str, Any]], Awaitable[Any]],
                       message: Message,
                       data: dict[str, Any]
                       ) -> Any:
        """
        Вызов мидлвара.

        Args:
            handler: Обработчик.
            message: Сообщение.
            data: Данные.

        Returns:
            Результат выполнения.
        """
        if not message.media_group_id:  # Если нет идентификатора медиагруппы
            await handler(message, data)  # Вызов обработчика
            return

        try:
            self.album_data[message.media_group_id].append(message)  # Добавление сообщения в альбом

        except KeyError:
            self.album_data[message.media_group_id] = [message]  # Создание нового альбома
            await asyncio.sleep(self.latency)  # Задержка

            data['_is_last'] = True  # Установка флага "последнего" сообщения
            data["album"] = self.album_data[message.media_group_id]  # Установка альбома в данные
            await handler(message, data)  # Вызов обработчика

        if message.media_group_id and data.get("_is_last"):  # Если это последнее сообщение в альбоме
            del self.album_data[message.media_group_id]  # Удаление альбома
            del data['_is_last']  # Удаление флага
