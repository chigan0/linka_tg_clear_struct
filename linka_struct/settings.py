import os  # Импорт модуля os для работы с операционной системой
from pathlib import Path, PosixPath  # Импорт классов Path и PosixPath для работы с путями
from multiprocessing import Process, Manager  # Импорт классов Process и Manager для работы с многопроцессорностью
from typing import Dict, List, Union, Tuple, Optional, Set, Any, Callable  # Импорт типов данных для аннотации типов

from pydantic_settings import BaseSettings  # Импорт базовых настроек Pydantic
from aiogram.types import user  # Импорт типа данных пользователя из библиотеки aiogram


class Settings(BaseSettings):
    """
    Класс настроек приложения.
    """

    PROJECT_NAME: str = 'linka_struct'  # Название проекта
    ME: Optional[user.User] = None  # Пользователь "я"
    BASE_DIR: Path = Path(__file__).resolve().parent.parent.joinpath(PROJECT_NAME)  # Базовая директория проекта
    
    # REDIS_DSN: str = "redis://localhost"
    SUPER_USERS: List[Union[int, str]] = []  # Список суперпользователей
    DATABASE: Optional[Any] = None  # База данных
    get_db: Optional[Callable] = None  # Функция получения базы данных

    # Параметры языков
    DEFAULT_LANG: str = "ru"  # Язык по умолчанию
    LANG_DIR: PosixPath = BASE_DIR / 'locale'  # Директория с языковыми файлами
    LANGUAGES: List[str] = ['ru', 'kk', 'en']  # Доступные языки

    # Параметры медиафайлов
    MEDIA_DIR: PosixPath = BASE_DIR / 'media'  # Директория медиафайлов


settings = Settings()  # Создание экземпляра настроек
user_processes = {}  # Словарь процессов пользователя
