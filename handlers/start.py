from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message) -> None:
    await message.answer(
        "Привет! Я соберу для тебя рекомендации. Используй команду «Рекомендации» для просмотра или «Рефреш» чтобы обновить список."
    )
