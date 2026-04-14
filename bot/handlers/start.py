from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message
from bot.keyboards.reply import main_menu

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer(
        f"Привет, {message.from_user.first_name}! 👋\n\n"
        "Я твой менеджер задач. Вот что я умею:\n"
        "📝 <b>Добавить задачу</b> — создать новую задачу\n"
        "📋 <b>Мои задачи</b> — список активных задач\n"
        "🗑 <b>Удалить</b> — удалить задачу\n\n"
        "Выбери действие 👇",
        parse_mode="HTML",
        reply_markup=main_menu(),
    )