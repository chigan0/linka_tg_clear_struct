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
from typing import Any, Optional, List, Tuple, Union, Dict  # Импорт типов данных для аннотации типов

# Функция для получения названия операционной системы
def get_os() -> str:
    return 'windows' if os.name == 'nt' else 'linux'


# Функция для генерации случайной строки заданной длины
def generate_random_string(length: int) -> str:
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))


# Функция для генерации случайного числа заданной длины
def generate_random_numbers(length: int) -> str:
    return ''.join(random.choices(string.digits, k=length))


# Функция для проверки, является ли значение целым числом
def is_int(val: Any) -> Optional[int]:
    try:
        return int(val)
    except ValueError:
        return None


# Функция для выполнения синхронной или асинхронной функции в зависимости от типа
def run_sync_or_async(func, *args, **kwargs):
    if asyncio.iscoroutinefunction(func):
        return asyncio.run(func(*args, **kwargs))
    else:
        return func(*args, **kwargs)


# Функция для создания директорий для медиа-файлов
def media_dir(dirs_: List[PosixPath]) -> None:
    """
    Создает директории для медиа-файлов.

    Args:
        dirs_: Список директорий для создания.
    """
    for dir_ in dirs_:
        assert isinstance(dir_, PosixPath), f"{type(dir_)} it should be {PosixPath}"
        if not os.path.isdir(dir_):
            os.mkdir(dir_)


# Функция для валидации URL
def validate_url(url: str) -> bool:
    """
    Проверяет, является ли URL валидным.

    Args:
        url: URL для проверки.

    Returns:
        bool: True, если URL валиден, иначе False.
    """
    pattern = re.compile(r'https?://(?:www\.)?[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}')
    return bool(pattern.match(url))


# Функция для очистки консоли операционной системы
def clear_console() -> None:
    """
    Очищает консоль операционной системы.
    """
    os_name: str = get_os()
    os.system('cls' if os_name == 'windows' else 'clear')


# Декоратор для измерения времени выполнения синхронной функции
def measure_time(func):
    """
    Декоратор для измерения времени выполнения синхронной функции.

    Args:
        func: Функция для измерения времени выполнения.

    Returns:
        Обернутая функция.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        print(f"Function '{func.__name__}' executed in {(end_time - start_time):.4f} seconds")
        return result
    return wrapper


# Декоратор для измерения времени выполнения асинхронной функции
def measure_time_async(func):
    """
    Декоратор для измерения времени выполнения асинхронной функции.

    Args:
        func: Асинхронная функция для измерения времени выполнения.

    Returns:
        Обернутая асинхронная функция.
    """
    @wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = time.time()
        result = await func(*args, **kwargs)
        end_time = time.time()
        print(f"Function '{func.__name__}' executed in {(end_time - start_time):.4f} seconds")
        return result
    return wrapper


# Функция для генерации случайного юзер-агента
def generate_random_user_agent() -> str:
    return random.choice(user_agents)


# Функция для выполнения асинхронной функции синхронно
def between_callback(func, *args):
    return asyncio.run(func(*args))


# Функция для загрузки данных из JSON файла
def load_json(file_path: str) -> dict:
    """
    Загружает данные из JSON файла.

    Args:
        file_path: Путь к JSON файлу.

    Returns:
        dict: Загруженные данные из файла.
    """
    with open(file_path, "r") as file:
        json_content = json.load(file)
    return json_content


# Функция для сохранения файла
def save_file(file_name: str, file_byte: bytes) -> None:
    """
    Сохраняет файл.

    Args:
        file_name: Название файла для сохранения.
        file_byte: Байты файла.
    """
    with open(file_name, 'wb') as file:
        file.write(file_byte.read())


# Функция для записи данных в JSON файл
def write_json_file(file_path: str, data_dict: dict) -> None:
    """
    Записывает данные в формате JSON в файл.

    Args:
        file_path: Путь к файлу, в который будет записан словарь в формате JSON.
        data_dict: Словарь данных для записи.
    """
    with open(file_path, 'w') as json_file:
        json.dump(data_dict, json_file, ensure_ascii=False, indent=2)  # indent для красивого форматирования, можно убрать, если не нужно


# Класс-синглтон для работы с языковыми файлами
class LangsSingleton:
    _instance = None

    def __init__(self, LANG_DIR: PosixPath, default_lang: str, languages: List[str]):
        assert isinstance(LANG_DIR, PosixPath), f"{type(LANG_DIR)} it should be {PosixPath}"

        self.LANG_FILE_NAME = 'trans'
        self.LANG_DIR = LANG_DIR
        self.default_lang = default_lang
        self.languages = languages

        self._initialized = True
        self._selected_lang = default_lang
        self._texts = {}
        self._default_trans = {
            "ru": {
                "Hello world": "***Привет Мир***\n",
                "Copy Msg": "`Скопировать сообщения`",
                "select_lang": "Выбрать язык",
                "select_lang_msg": "Выберите желаемый язык",
            },
            "kk": {
                "Hello world": "***Салем Алем***\n",
                "Copy Msg": "`Хабарламаларды көшіру`",
                "select_lang": "Тілді таңдау",
                "select_lang_msg": "Көмектескен тілді таңдау"
            },
            "en": {
                "Hello world": "***Hello world***\n",
                "Copy Msg": "`Copy Message`",
                "select_lang": "Select language",
                "select_lang_msg": "Choose your preferred language"
            }
        }

        self.text_init()

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(LangsSingleton, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def write_json_file(self, file_path: str, data_dict: dict) -> None:
        with open(file_path, 'w') as json_file:
            json.dump(data_dict, json_file, ensure_ascii=False, indent=2)

    def load_json(self, file_path: str) -> dict:
        with open(file_path, "r") as file:
            json_content = json.load(file)
        return json_content

    def check_lang_struct(self, lang_dir: PosixPath, languages: List[str]) -> None:
        if not os.path.isdir(lang_dir):
            os.mkdir(lang_dir)

        for lang in languages:
            lang_path: PosixPath = lang_dir / lang

            if not (os.path.isdir(lang_path)):
                os.mkdir(lang_path)

            if not (os.path.isfile(lang_path / f'{self.LANG_FILE_NAME}.json')):
                self.write_json_file(lang_path / f'{self.LANG_FILE_NAME}.json', self._default_trans[lang])

    def text_init(self) -> None:
        self.check_lang_struct(self.LANG_DIR, self.languages)

        for lang in self.languages:
            self._texts[lang] = self.load_json(self.LANG_DIR / lang / f"{self.LANG_FILE_NAME}.json")

    def get_text(self) -> Dict:
        return self._texts.get(self._selected_lang) or {}

    def get_languages(self) -> List[str]:
        return self.languages

    def set_lang(self, lang: str) -> None:
        self._selected_lang = lang

    def get_msg_key(self, key: str) -> Union[str, Dict]:
        return self._texts[self._selected_lang].get(key) or key
