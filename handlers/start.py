from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from keyboards import main_menu_keyboard

router = Router()


@router.message(CommandStart())
async def handle_start(message: Message) -> None:
    """Приветствие и показ главного меню."""
    await message.answer(
        (
            "Привет! Я бот с рекомендациями аниме.\n"
            "Нажми кнопку ниже, чтобы получить список или обновить его."
        ),
        reply_markup=main_menu_keyboard(),
    )
