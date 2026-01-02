from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from settings import settings_repo

router = Router(name="start")


@router.message(CommandStart())
async def handle_start(message: Message) -> None:
    settings_repo.get(message.from_user.id)
    await message.answer(
        "Привет! Я помогу подобрать тайтлы. "
        "Используй /settings чтобы изменить температуру рекомендаций."
    )
