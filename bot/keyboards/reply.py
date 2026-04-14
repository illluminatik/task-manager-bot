from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton


def main_menu() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📝 Добавить задачу")],
            [KeyboardButton(text="📋 Мои задачи"), KeyboardButton(text="🗑 Удалить задачу")],
        ],
        resize_keyboard=True,
    )


def priority_menu() -> InlineKeyboardMarkup:
    """Клавиатура выбора приоритета."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🟢 Low", callback_data="prio_low"),
            InlineKeyboardButton(text="🟡 Medium", callback_data="prio_medium"),
            InlineKeyboardButton(text="🔴 High", callback_data="prio_high")
        ]
    ])


def tasks_inline(tasks: list, prefix: str = "task_") -> InlineKeyboardMarkup:
    """Инлайн-кнопки со списком задач."""
    buttons = []
    for task in tasks:
        priority = task.get("priority", "medium")
        priority_emoji = {"low": "🟢", "medium": "🟡", "high": "🔴"}.get(priority, "⚪")
        deadline = f" | ⏰ {task['deadline'][:10]}" if task.get("deadline") else ""
        label = f"{priority_emoji} {task['title']}{deadline}"
        buttons.append([InlineKeyboardButton(text=label, callback_data=f"{prefix}{task['id']}")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def confirm_delete(task_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Да, удалить", callback_data=f"remove_{task_id}"),
            InlineKeyboardButton(text="❌ Отмена", callback_data="cancel"),
        ]
    ])
