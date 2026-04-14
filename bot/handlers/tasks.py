import aiohttp
import os
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from bot.keyboards.reply import main_menu, tasks_inline, confirm_delete, priority_menu
from dotenv import load_dotenv

load_dotenv()

router = Router()
API_URL = os.getenv("API_URL", "http://127.0.0.1:8000")
API_AUTH_TOKEN = os.getenv("API_AUTH_TOKEN")

class AddTask(StatesGroup):
    title = State()
    priority = State()
    deadline = State()

# ───── API Helpers ─────

async def fetch_tasks(telegram_id: int, only_active: bool = True):
    headers = {"X-API-Token": API_AUTH_TOKEN}
    try:
        async with aiohttp.ClientSession(headers=headers) as session:
            async with session.get(
                f"{API_URL}/tasks/{telegram_id}",
                params={"only_active": str(only_active).lower()},
                timeout=5
            ) as resp:
                if resp.status == 200:
                    return await resp.json()
                elif resp.status == 401:
                    return "AUTH_ERROR"
                return "SERVER_ERROR"
    except Exception:
        return "CONNECTION_ERROR"

async def post_task(telegram_id: int, data: dict):
    headers = {"X-API-Token": API_AUTH_TOKEN}
    try:
        async with aiohttp.ClientSession(headers=headers) as session:
            async with session.post(
                f"{API_URL}/tasks/{telegram_id}",
                json=data,
                timeout=5
            ) as resp:
                if resp.status == 200:
                    return await resp.json()
                elif resp.status == 401:
                    return "AUTH_ERROR"
                return "SERVER_ERROR"
    except Exception:
        return "CONNECTION_ERROR"

async def complete_task(telegram_id: int, task_id: int):
    headers = {"X-API-Token": API_AUTH_TOKEN}
    try:
        async with aiohttp.ClientSession(headers=headers) as session:
            async with session.patch(
                f"{API_URL}/tasks/{telegram_id}/{task_id}/done",
                timeout=5
            ) as resp:
                if resp.status == 200:
                    return await resp.json()
                elif resp.status == 401:
                    return "AUTH_ERROR"
                return "SERVER_ERROR"
    except Exception:
        return "CONNECTION_ERROR"

async def remove_task(telegram_id: int, task_id: int):
    headers = {"X-API-Token": API_AUTH_TOKEN}
    try:
        async with aiohttp.ClientSession(headers=headers) as session:
            async with session.delete(
                f"{API_URL}/tasks/{telegram_id}/{task_id}",
                timeout=5
            ) as resp:
                if resp.status == 200:
                    return "SUCCESS"
                elif resp.status == 401:
                    return "AUTH_ERROR"
                return "SERVER_ERROR"
    except Exception:
        return "CONNECTION_ERROR"

# ───── Handlers ─────

@router.message(F.text == "📝 Добавить задачу")
async def ask_title(message: Message, state: FSMContext):
    await state.set_state(AddTask.title)
    await message.answer("Введи название задачи:")

@router.message(AddTask.title)
async def ask_priority(message: Message, state: FSMContext):
    await state.update_data(title=message.text)
    await state.set_state(AddTask.priority)
    await message.answer("Выбери приоритет задачи:", reply_markup=priority_menu())

@router.callback_query(AddTask.priority, F.data.startswith("prio_"))
async def set_priority(callback: CallbackQuery, state: FSMContext):
    priority = callback.data.split("_")[1]
    await state.update_data(priority=priority)
    await state.set_state(AddTask.deadline)
    await callback.message.edit_text(f"Выбран приоритет: {priority.capitalize()}\nТеперь укажи дедлайн (ДД.ММ.ГГГГ) или отправь /skip:")
    await callback.answer()

@router.message(AddTask.deadline)
async def save_task(message: Message, state: FSMContext):
    deadline = None
    if message.text != "/skip":
        try:
            from datetime import datetime
            parsed_date = datetime.strptime(message.text, "%d.%m.%Y")
            if parsed_date.date() < datetime.now().date():
                await message.answer("❌ Введи актуальную дату (ДД.ММ.ГГГГ):")
                return
            deadline = parsed_date.isoformat()
        except ValueError:
            await message.answer("Неверный формат даты. Попробуй ДД.ММ.ГГГГ:")
            return

    data = await state.get_data()
    data["deadline"] = deadline
    await state.clear()

    res = await post_task(message.from_user.id, data)
    if res == "AUTH_ERROR":
        await message.answer("🔐 Ошибка авторизации.", reply_markup=main_menu())
    elif isinstance(res, str):
        await message.answer("📡 Сервер API недоступен.", reply_markup=main_menu())
    else:
        await message.answer(
            f"✅ Задача <b>{res['title']}</b> добавлена!",
            parse_mode="HTML",
            reply_markup=main_menu()
        )

@router.message(F.text == "📋 Мои задачи")
async def list_tasks(message: Message):
    res = await fetch_tasks(message.from_user.id)
    if res == "AUTH_ERROR":
        await message.answer("🔐 Ошибка авторизации.")
    elif isinstance(res, str):
        await message.answer("📡 Ошибка связи с сервером.")
    elif not res:
        await message.answer("У тебя пока нет активных задач 🎉")
    else:
        await message.answer(
            f"Твои активные задачи ({len(res)}):",
            reply_markup=tasks_inline(res),
        )

@router.callback_query(F.data.startswith("task_"))
async def mark_done(callback: CallbackQuery):
    task_id = int(callback.data.split("_")[1])
    res = await complete_task(callback.from_user.id, task_id)
    if isinstance(res, str):
        await callback.answer("❌ Ошибка при выполнении.")
    else:
        await callback.message.edit_text(
            f"✅ Задача <b>{res['title']}</b> выполнена!",
            parse_mode="HTML"
        )
    await callback.answer()

@router.message(F.text == "🗑 Удалить задачу")
async def choose_delete(message: Message):
    res = await fetch_tasks(message.from_user.id, only_active=True)
    if isinstance(res, str) or not res:
        await message.answer("Нет активных задач для удаления!")
        return
    await message.answer(
        "Выбери активную задачу для удаления:",
        reply_markup=tasks_inline(res, prefix="delete_")
    )

@router.callback_query(F.data.startswith("delete_"))
async def confirm_delete_cb(callback: CallbackQuery):
    task_id = int(callback.data.split("_")[1])
    await callback.message.edit_text("Точно удалить эту задачу?", reply_markup=confirm_delete(task_id))
    await callback.answer()

@router.callback_query(F.data.startswith("remove_"))
async def perform_remove(callback: CallbackQuery):
    task_id = int(callback.data.split("_")[1])
    res = await remove_task(callback.from_user.id, task_id)
    if res == "SUCCESS":
        await callback.message.edit_text("🗑 Задача удалена!")
    else:
        await callback.answer("❌ Ошибка при удалении.")
    await callback.answer()

@router.callback_query(F.data == "cancel")
async def cancel_cb(callback: CallbackQuery):
    await callback.message.edit_text("Отменено ✋")
    await callback.answer()
