import asyncio
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from aiogram import Bot, Dispatcher
from bot.handlers import start, tasks
from bot.scheduler import setup_scheduler
from dotenv import load_dotenv


load_dotenv()

async def main():
    token = os.getenv("BOT_TOKEN")
    if not token:
        print("❌ ОШИБКА: BOT_TOKEN не найден в .env!")
        return

    print("🔹 Запуск бота...")
    try:
        bot = Bot(token=token)
        dp = Dispatcher()

        dp.include_router(start.router)
        dp.include_router(tasks.router)

        print("🔹 Настройка планировщика...")
        scheduler = setup_scheduler(bot)
        scheduler.start()

        print("✅ Бот успешно запущен и слушает сообщения!")
        await dp.start_polling(bot)
    except Exception as e:
        print(f"❌ КРИТИЧЕСКАЯ ОШИБКА ПРИ ЗАПУСКЕ: {e}")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("🛑 Бот остановлен вручную.")
    except Exception as e:
        print(f"❌ Ошибка asyncio: {e}")
