import asyncio
import logging

from aiohttp import web
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.storage.redis import DefaultKeyBuilder, RedisStorage
from redis.asyncio import Redis

from config import settings
from db import init_db
from handlers.menu import router as menu_router
from handlers.start import router as start_router
from webserver import create_app

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def _build_storage() -> MemoryStorage | RedisStorage:
    if not settings.redis_url:
        return MemoryStorage()
    redis = Redis.from_url(settings.redis_url)
    return RedisStorage(redis=redis, key_builder=DefaultKeyBuilder(with_bot_id=True, with_destiny=True))


async def _run_polling(bot: Bot, dispatcher: Dispatcher, app: web.Application) -> None:
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, settings.http_host, settings.http_port)
    await site.start()
    logger.info("Запущен callback-сервер по адресу http://%s:%s", settings.http_host, settings.http_port)
    await dispatcher.start_polling(bot)


async def _run_webhook(bot: Bot, dispatcher: Dispatcher, app: web.Application) -> None:
    async def on_startup(_: web.Application) -> None:
        await bot.set_webhook(
            url=f"{settings.webhook_url}{settings.webhook_path}",
            secret_token=settings.webhook_secret,
            drop_pending_updates=True,
        )
        logger.info("Webhook настроен: %s", settings.webhook_url)

    async def on_shutdown(_: web.Application) -> None:
        await bot.delete_webhook(drop_pending_updates=True)
        logger.info("Webhook удален")

    app.on_startup.append(on_startup)
    app.on_shutdown.append(on_shutdown)
    web.run_app(app, host=settings.http_host, port=settings.http_port)


async def main() -> None:
    await init_db()
    storage = _build_storage()
    bot = Bot(token=settings.bot_token, parse_mode=ParseMode.HTML)
    dispatcher = Dispatcher(storage=storage)
    dispatcher.include_routers(start_router, menu_router)

    app = create_app(bot, dispatcher)

    if settings.webhook_url:
        await _run_webhook(bot, dispatcher, app)
    else:
        await _run_polling(bot, dispatcher, app)


if __name__ == "__main__":
    asyncio.run(main())
