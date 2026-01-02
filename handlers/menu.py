import datetime as dt

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from db import get_tokens, save_tokens
from shikimori import refresh_access_token

router = Router()


def _format_expiration(expires_at: dt.datetime) -> str:
    return expires_at.astimezone(dt.timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")


@router.message(Command("status"))
async def token_status(message: Message) -> None:
    tokens = await get_tokens(message.from_user.id)
    if tokens is None:
        await message.answer("Связка с Shikimori не найдена. Нажмите /start, чтобы авторизоваться.")
        return
    remaining = int((tokens.expires_at - dt.datetime.now(tz=dt.timezone.utc)).total_seconds())
    await message.answer(
        "Shikimori подключен.\n"
        f"Токен действует до {_format_expiration(tokens.expires_at)} (осталось {remaining // 60} минут)."
    )


@router.message(Command("refresh"))
async def refresh_token(message: Message) -> None:
    tokens = await get_tokens(message.from_user.id)
    if tokens is None:
        await message.answer("Нет сохраненных токенов. Авторизуйтесь через /start.")
        return
    refreshed = await refresh_access_token(tokens.refresh_token)
    await save_tokens(
        telegram_id=message.from_user.id,
        access_token=refreshed.access_token,
        refresh_token=refreshed.refresh_token,
        expires_at=refreshed.expires_at,
        scope=refreshed.scope,
    )
    await message.answer("Токен обновлен и сохранен.")
