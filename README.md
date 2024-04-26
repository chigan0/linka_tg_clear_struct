# Телеграм-бот на базе aiogram 3

Данный проект представляет собой телеграм-бота, разработанный с использованием библиотеки aiogram версии 3. Бот предназначен для обработки сообщений пользователей, выполнения различных задач и взаимодействия с базой данных. Ниже представлена подробная информация о структуре проекта и его основных компонентах.

## Описание

Проект представляет собой надстройку над фреймворком aiogram версии 3. Он включает в себя классы middleware и утилиты, а также административную панель и класс для подключения ко всем базам данных. По умолчанию используется база данных SQLite. Каждый пользователь, обратившийся к боту, записывается в базу данных. Также реализована трансинтернационализация, позволяющая переводить интерфейс на различные языки.

## Структура проекта

- **base**: базовые классы и функции для других модулей.
- **crud**: модуль для выполнения операций CRUD (Create, Read, Update, Delete) с данными в базе данных.
- **handlers**: обработчики для входящих сообщений и колбэков, определяющие логику ответа на запросы пользователей.
- **locale**: файлы локализации для перевода интерфейса на различные языки.
- **media**: модуль для работы с медиаконтентом, таким как изображения, аудио и видеофайлы.
- **middlewares**: промежуточные слои для предварительной обработки запросов перед их обработкой обработчиками.
- **models**: описания моделей базы данных.
- **states**: состояния пользователя для управления переходами между различными этапами взаимодействия с ботом.
- **utils**: вспомогательные функции и классы.
- **bot.py**: файл инициализации бота.
- **database.py**: драйвер для работы с базой данных.
- **router.py**: маршрутизатор для обработки входящих сообщений.
- **settings.py**: файл настроек проекта.

## Установка и запуск

### Требования

- Python 3.x
- Другие зависимости (если есть) указаны в файле `requirements.txt`.

### Установка зависимостей

```bash
pip install -r requirements.txt