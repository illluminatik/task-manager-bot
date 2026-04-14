# Task Manager Bot 📝

Современный менеджер задач в Telegram с использованием **FastAPI**, **Aiogram 3** и **PostgreSQL**.

## Архитектура
Проект разделен на два независимых сервиса:
1. **API (Backend)**: Обрабатывает логику задач, работает с базой данных через SQLAlchemy (Async).
2. **Bot (Frontend)**: Интерфейс в Telegram, общается с API через защищенные запросы.

## Технологии
- **Python 3.12**
- **Aiogram 3** (Telegram Bot framework)
- **FastAPI** (REST API)
- **SQLAlchemy 2.0** (ORM)
- **PostgreSQL 15** (Database)
- **Docker** (Контейнеризация БД)
- **Apscheduler** (Напоминания о дедлайнах)

## Запуск проекта

### 1. Подготовка окружения
Создайте файл `.env` в корневой папке на основе `.env.example` и заполните свои данные:
```text
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5433/taskdb
BOT_TOKEN=ваш_токен_бота
API_AUTH_TOKEN=ваш_секретный_ключ_api
API_URL=http://127.0.0.1:8000
```

### 2. Запуск базы данных (Docker)
```bash
docker run -d --name task_db -p 5433:5432 -e POSTGRES_USER=user -e POSTGRES_PASSWORD=password -e POSTGRES_DB=taskdb postgres:15
```

### 3. Установка зависимостей
```bash
pip install -r requirements.txt
```

### 4. Запуск сервисов
Запустите API в одном терминале:
```bash
uvicorn api.main:app --reload
```

Запустите Бота в другом терминале:
```bash
python bot/main.py
```

## Функционал
- ✅ Добавление задач с выбором приоритета (low, medium, high).
- 📅 Указание дедлайнов.
- 📋 Просмотр списка активных задач.
- ✅ Отметка задач как выполненных.
- 🗑 Полное удаление задач.
- 🔔 Автоматические уведомления о просроченных дедлайнах (раз в час).
