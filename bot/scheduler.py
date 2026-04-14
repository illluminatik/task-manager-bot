from apscheduler.schedulers.asyncio import AsyncIOScheduler
from aiogram import Bot
from core.database import async_session
from core.crud import get_overdue_tasks


async def send_reminders(bot: Bot):
    async with async_session() as session:
        tasks = await get_overdue_tasks(session)
        for task in tasks:
            try:
                await bot.send_message(
                    chat_id=task.user.telegram_id,
                    text=(
                        f"⚠️ Задача просрочена!\n\n"
                        f"📝 <b>{task.title}</b>\n"
                        f"Дeдлайн был: {task.deadline.strftime('%d.%m.%Y')}"
                    ),
                    parse_mode="HTML",
                )
            except Exception:
                pass


def setup_scheduler(bot: Bot) -> AsyncIOScheduler:
    scheduler = AsyncIOScheduler()
    scheduler.add_job(
        send_reminders,
        trigger="interval",
        hours=1,
        args=[bot],
    )
    return scheduler