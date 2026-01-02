from __future__ import annotations

from ainori.bot.app import BotApp, BotMessage


async def handle_recommendation(app: BotApp, message: BotMessage, query: str) -> None:
    if not query:
        await message.answer("Укажите, что хотите посмотреть после команды /recommend.")
        return
    await app.send_recommendation(message, query)
