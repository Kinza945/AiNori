import asyncio
import os

from aiogram import Bot, Dispatcher
from dotenv import load_dotenv

from handlers.menu import router as menu_router
from handlers.recommendation import router as recommendation_router
from handlers.start import router as start_router

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN не найден. Проверь файл .env")


def create_dispatcher() -> Dispatcher:
    dispatcher = Dispatcher()
    dispatcher.include_router(start_router)
    dispatcher.include_router(menu_router)
    dispatcher.include_router(recommendation_router)
    return dispatcher


async def main() -> None:
    bot = Bot(BOT_TOKEN)
    dp = create_dispatcher()
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
