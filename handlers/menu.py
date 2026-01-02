from __future__ import annotations

from ainori.bot.app import BotMessage


async def handle_menu(message: BotMessage) -> None:
    await message.answer("Доступные команды: /start, /menu, /recommend <поиск>.")
