from __future__ import annotations

import logging

from aiohttp import web
from aiogram import Bot, Dispatcher
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application

from config import settings
from db import save_tokens
from shikimori import exchange_code

logger = logging.getLogger(__name__)


async def oauth_callback(request: web.Request) -> web.StreamResponse:
    bot: Bot = request.app["bot"]
    code = request.query.get("code")
    state = request.query.get("state")
    if not code or not state:
        return web.Response(text="code/state отсутствуют", status=400)

    try:
        telegram_id = int(state)
    except ValueError:
        return web.Response(text="Некорректный state", status=400)

    try:
        tokens = await exchange_code(code)
        await save_tokens(
            telegram_id=telegram_id,
            access_token=tokens.access_token,
            refresh_token=tokens.refresh_token,
            expires_at=tokens.expires_at,
            scope=tokens.scope,
        )
    except Exception as exc:  # pragma: no cover - в проде логируем
        logger.exception("Ошибка при обмене кода Shikimori: %s", exc)
        return web.Response(text="Не удалось обменять код. Проверьте логи сервера.", status=500)

    await bot.send_message(telegram_id, "Готово! Токены Shikimori сохранены.")
    return web.Response(text="Авторизация завершена, вернитесь в Telegram.")


def create_app(bot: Bot, dispatcher: Dispatcher) -> web.Application:
    app = web.Application()
    app["bot"] = bot
    app.router.add_get("/oauth/callback", oauth_callback)

    if settings.webhook_url:
        handler = SimpleRequestHandler(dispatcher=dispatcher, bot=bot, secret_token=settings.webhook_secret)
        handler.register(app, path=settings.webhook_path)
        setup_application(app, dispatcher, bot=bot)

    return app
