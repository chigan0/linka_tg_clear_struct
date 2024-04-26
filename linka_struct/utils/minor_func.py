import os  # Импорт модуля os для работы с операционной системой
import re  # Импорт модуля re для работы с регулярными выражениями
import time  # Импорт модуля time для работы со временем
import json  # Импорт модуля json для работы с JSON данными
import random  # Импорт модуля random для генерации случайных значений
import string  # Импорт модуля string для работы с символьными строками
import asyncio  # Импорт модуля asyncio для асинхронного программирования
from functools import wraps  # Импорт функции wraps из модуля functools
from pathlib import Path, PosixPath  # Импорт классов Path и PosixPath из модуля pathlib
from multiprocessing import Process, Manager  # Импорт классов Process и Manager из модуля multiprocessing
from typing import Any, Optional, List, Tuple, Union, Dict, Callable, Set  # Импорт типов данных для аннотации типов

import aiogram  # Импорт модуля aiogram для работы с Telegram Bot API
from aiogram import Router, Bot, types, F  # Импорт классов Router, Bot, types, F из модуля aiogram
from aiogram.types import user, Message, CallbackQuery, FSInputFile, InputMediaPhoto, InputMediaAudio, InputMediaDocument, InputMediaVideo, InputFile, ContentType as CT  # Импорт классов user, Message, CallbackQuery, FSInputFile, InputMediaPhoto, InputMediaAudio, InputMediaDocument, InputMediaVideo, InputFile, ContentType из модуля aiogram.types
from aiogram.fsm.context import FSMContext  # Импорт класса FSMContext из модуля aiogram.fsm.context
from aiogram.filters import Command, StateFilter  # Импорт классов Command, StateFilter из модуля aiogram.filters
from aiogram.enums.chat_member_status import ChatMemberStatus  # Импорт перечисления ChatMemberStatus из модуля aiogram.enums.chat_member_status
from aiogram.exceptions import TelegramForbiddenError, TelegramMigrateToChat  # Импорт исключений TelegramForbiddenError, TelegramMigrateToChat из модуля aiogram.exceptions

from ..settings import settings, user_processes  # Импорт настроек и процессов пользователя
from ..utils import inline_keyboard, run_sync_or_async  # Импорт вспомогательных функций
# from ..database__sqlite import get_db  # Импорт функции get_db из модуля database__sqlite
from ..crud import User, user_by_tg_id, add_user, get_all_groups  # Импорт функций CRUD
from ..states import AdminState  # Импорт состояния AdminState

# Функция для отправки ответа пользователю
async def send_answer(message: Message, change: bool, msg: str, keyboard=None, parse_mode='html'):
    if change:
        return await message.edit_text(msg, reply_markup=keyboard, parse_mode=parse_mode)
    return await message.answer(msg, reply_markup=keyboard, parse_mode=parse_mode)


# Асинхронный декоратор для обработки ошибок в функциях
async def funcs_middlewares(func: Callable, *args, **kwargs):
    try:
        await func(*args, **kwargs)
    except Exception as e:
        print(e)


# Функция для смены языка интерфейса
async def switch_lang(value: Any, callback: CallbackQuery, bot: Bot, state: FSMContext, lang: dict, change: bool = True):
    lang.set_lang(value)
    await funcs_middlewares(base_func, callback.message, bot, state, lang, True)


# Функция для сортировки медиафайлов по типам
def file_sort(medias: List[str]) -> Dict[str, str]:
    file_rules: Dict[str, List[str]] = {
        'audio': ['mp3', 'wav', 'ogg', 'flac', 'aac'],
        'video': ['mp4', 'avi', 'mkv', 'mov', 'wmv'],
        'photo': ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'tiff'],
    }
    sort_result: Dict[str, List[str]] = {file_type: [] for file_type in [*['document'], *file_rules.keys()]}

    for file in medias:
        file_type = 'document'

        for key, value in file_rules.items():
            if file.split('.')[-1] in value:
                file_type = key

        sort_result[file_type].append(file)

    return sort_result


# Функция для выбора языка
async def select_lang(message: Message, bot: Bot, state: FSMContext, lang: dict, change: bool = True):
    await send_answer(
        message,
        change,
        lang.get_msg_key('select_lang_msg'),
        inline_keyboard(
            {l.upper(): f'other_callback__set_lang__{l}' for l in lang.get_languages()},
            row=3
        ),
        'Markdown'
    )


# Функция для обработки других колбэков
async def other_callback(callback: CallbackQuery, bot: Bot, state: FSMContext, lang: dict, change: bool = True):
    funcs = {
        'set_lang': switch_lang,
    }

    if len(callback.data.split('__')) != 3:
        return

    key, value = callback.data.split('__')[1:]
    func = funcs.get(key)

    if func is None:
        return
    await func(value, callback, bot, state, lang, change)


# Функция для отображения базового меню
async def base_func(message: Message, bot: Bot, state: FSMContext, lang: dict, change: bool = True):
    user_data: user.User = message.chat

    if user_data.type in ['group', 'supergroup']:
        answer_msg = lang.get_msg_key('Group msg').format(group_title=user_data.title)
        keyboard: Dict[str, str] = {
            lang.get_msg_key('select_lang'): "select_lang",
        }

    if user_data.type == 'private':
        async with settings.get_db(True) as session:
            user: Optional[User] = await user_by_tg_id(user_data.id, session)

            if user is None:
                user = add_user(user_data, session)

        keyboard: Dict[str, str] = {
            lang.get_msg_key('select_lang'): "select_lang",
        }

        menu_msg: str = f"{lang.get_msg_key('Hello world').format(username=user_data.first_name)}\n\n" \
                        f"{lang.get_msg_key('Copy Msg').format(botname=settings.ME.first_name.title())}"

    await state.set_state(None)
    await send_answer(
        message,
        change,
        menu_msg,
        inline_keyboard(keyboard, row=3),
        'Markdown'
    )


# Функция для отображения админской панели
async def admin_panel(message: Message, bot: Bot, state: FSMContext, lang: dict, change: bool = True):
    user_data: user.User = message.chat.first_name

    await state.set_state(AdminState.base_menu)
    await send_answer(
        message,
        change,
        lang.get_msg_key('Admin panel Welcome MSG').format(name=user_data),
        inline_keyboard({lang.get_msg_key('Base menu'): 'base_menu'}),
        'Markdown'
    )


# Функция для отправки длинных сообщений
async def send_logn_msg(*args, **kwargs):
    max_message_length: int = 4094
    correct_chhats, failed_chats = set(), set()

    for chunk in [kwargs['text_message'][i:i + max_message_length] for i in range(0, len(kwargs['text_message']), max_message_length)]:
        kwargs['text_message'] = chunk
        correct, failed = await send_media_to_usr(**kwargs)

        correct_chhats.union(correct)
        failed_chats.union(failed)

    return correct_chhats, failed_chats


# Функция для отправки медиафайлов
async def send_media_to_usr(
        bot: Bot,
        chats_id: Optional[List[Union[str, int]]] = [],
        media_key: Optional[str] = None,
        media_paths: Optional[List[str]] = None,
        caption: Optional[str] = None,
        reply_to_message_id: Optional[Union[str, int]] = None,
        text_message: Optional[str] = None,
        parse_mode: str = 'html'
) -> Set[Union[str, int]]:
    """
    Отправляет медиафайлы или текстовые сообщения в указанные чаты.

    Args:
        bot (Bot): Экземпляр бота для отправки сообщений.
        chats_id (Optional[List[Union[str, int]]]): Список идентификаторов чатов.
            Если не указан, используются все групповые чаты из базы данных.
        media_key (Optional[str]): Ключ медиафайла. Определяет тип медиафайла (photo, audio, video, document).
        media_paths (Optional[List[str]]): Список путей к медиафайлам для отправки.
        caption (Optional[str]): Подпись к медиафайлам.
        reply_to_message_id (Optional[Union[str, int]]): Идентификатор сообщения, на которое нужно ответить.
        text_message (Optional[str]): Текстовое сообщение для отправки.
        parse_mode (str): Режим разбора текста. По умолчанию 'html'.

    Returns:
        Set[Union[str, int]]: Множество идентификаторов чатов, в которых не удалось отправить сообщение.
    """

    max_message_length: int = 4096
    tasks: Set[asyncio.Task] = set()
    correct_chhats: Dict[str, str] = {}
    failed_chats: Set[Union[str, int]] = set()  # Список чатов, в которых не удалось отправить сообщение

    # Проверка аргументов
    assert isinstance(chats_id, list), f"{type(chats_id)} is not a List"
    assert text_message is not None or media_paths is not None, "Either text_message or media_paths must be provided"

    # Если не указаны чаты, берем их из базы данных
    if len(chats_id) == 0:
        async with settings.get_db(True) as session:
            chats_id = [chat[0].chat_id for chat in await get_all_groups(session)]

    # Отправка текстового сообщения
    if text_message is not None:
        if len(text_message) > max_message_length:
            return await send_logn_msg(
                bot=bot,
                chats_id=chats_id,
                media_key=media_key,
                media_paths=media_paths,
                caption=caption,
                reply_to_message_id=reply_to_message_id,
                text_message=text_message,
                parse_mode=parse_mode
            )
        # Добавить исключения

        for chat_id in chats_id:
            tasks.add(bot.send_message(
                chat_id,
                text_message,
                reply_to_message_id=reply_to_message_id,
                parse_mode=parse_mode
            ))

    # Отправка медиафайла
    elif media_key is not None:
        assert isinstance(media_paths, list), f"{type(media_paths)} is not a list"

        media_params: Dict[str, Dict[str, Union[Callable, Type]]] = {
            'photo': {'single_func': bot.send_photo, 'media': InputMediaPhoto},
            'audio': {'single_func': bot.send_audio, 'media': InputMediaAudio},
            'video': {'single_func': bot.send_video, 'media': InputMediaVideo},
            'document': {'single_func': bot.send_document, 'media': InputMediaDocument},
        }

        assert media_key in media_params.keys(), f"{media_key} is not supported"

        media_data = media_params[media_key]
        medias = [FSInputFile(path) for path in media_paths]
        single_func = media_data['single_func']
        media_callback = media_data['media']

        # Отправка одиночного медиафайла
        if len(medias) < 2:
            for chat_id in chats_id:
                tasks.add(single_func(
                    chat_id,
                    medias[-1],
                    caption=caption,
                    reply_to_message_id=reply_to_message_id,
                ))

        # Отправка группы медиафайлов
        else:
            medias = [media_callback(media=media, caption=caption) for media in medias]

            for chat_id in chats_id:
                for media_slice in range(0, len(medias), 9):
                    media_group = medias[media_slice:media_slice + 9]

                    tasks.add(bot.send_media_group(
                        chat_id=chat_id,
                        media=media_group,
                        reply_to_message_id=reply_to_message_id,
                    ))

    # Ожидание результатов и сохранение неудачных попыток
    results = await asyncio.gather(*tasks, return_exceptions=True)

    for idx, result in enumerate(results):
        if isinstance(result, Exception):
            failed_chats.add(chats_id[idx])
        else:
            correct_chhats[chats_id[idx]] = result.message_id if type(result) is not list else result[0].message_id

    return correct_chhats, failed_chats
