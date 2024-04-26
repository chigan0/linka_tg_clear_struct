from typing import Union, List, Dict, Optional, Tuple  # Импорт типов данных для аннотации типов

from sqlalchemy import Column, String, Integer, Boolean, BigInteger, ForeignKey, DateTime, Text  # Импорт классов и функций из библиотеки SQLAlchemy
from sqlalchemy.orm import relationship, Session  # Импорт классов и функций из библиотеки SQLAlchemy
from sqlalchemy.orm import declarative_base  # Импорт функции declarative_base из библиотеки SQLAlchemy
from sqlalchemy.orm import DeclarativeMeta  # Импорт класса DeclarativeMeta из библиотеки SQLAlchemy

UserBase: DeclarativeMeta = declarative_base()  # Создание базового класса для описания моделей SQLAlchemy


class User(UserBase):
    """
    Модель пользователя.
    """
    __tablename__ = "user"  # Название таблицы в базе данных

    id = Column(Integer, primary_key=True)  # Поле идентификатора пользователя
    user_tg_id = Column(String(25), unique=True, nullable=False)  # Поле идентификатора пользователя в Telegram
    first_name = Column(String(65), unique=False, nullable=False)  # Поле имени пользователя
    last_name = Column(String(65), unique=False, nullable=True)  # Поле фамилии пользователя
    language_code = Column(String(10), nullable=True)  # Поле языкового кода пользователя
    username = Column(String(40), unique=True, nullable=True)  # Поле юзернейма пользователя
    phone_number = Column(String(20), unique=True, nullable=True)  # Поле номера телефона пользователя
    date_created = Column(DateTime)  # Поле даты создания записи о пользователе

    def __repr__(self) -> str:
        """
        Метод возвращающий строковое представление объекта.
        """
        return self.first_name  # Возвращает имя пользователя


class ActiveGroups(UserBase):
    """
    Модель активных групп.
    """
    __tablename__ = 'active_groups'  # Название таблицы в базе данных

    id = Column(Integer, primary_key=True)  # Поле идентификатора группы
    chat_id = Column(String(25), unique=True, nullable=False)  # Поле идентификатора чата
    title = Column(String(326), nullable=False)  # Поле названия группы
    group_type = Column(String(76), nullable=False)  # Поле типа группы

    def __repr__(self) -> str:
        """
        Метод возвращающий строковое представление объекта.
        """
        return f"{self.title} - {self.group_type}"  # Возвращает строку с названием и типом группы
