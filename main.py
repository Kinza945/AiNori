import asyncio
import logging
import os

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from dotenv import load_dotenv

from handlers import menu, recommendation, start

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN не найден. Проверь файл .env")


async def main() -> None:
    """Запустить Telegram-бота с зарегистрированными роутерами."""
    logging.basicConfig(level=logging.INFO)
    bot = Bot(BOT_TOKEN, parse_mode=ParseMode.HTML)
    dp = Dispatcher()
    dp.include_router(start.router)
    dp.include_router(menu.router)
    dp.include_router(recommendation.router)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
