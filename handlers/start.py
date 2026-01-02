from __future__ import annotations

from ainori.bot.app import BotMessage


async def handle_start(message: BotMessage) -> None:
    await message.answer(
        "Привет! Я помогу подобрать аниме. Используй /menu чтобы узнать, что я умею."
    )
