from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from keyboards import main_menu_keyboard

router = Router()


@router.message(Command("menu"))
async def handle_menu(message: Message) -> None:
    """Команда для явного показа меню."""
    await message.answer("Выберите действие:", reply_markup=main_menu_keyboard())
