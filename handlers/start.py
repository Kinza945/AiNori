from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message

from shikimori import build_authorize_url

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message) -> None:
    state = str(message.from_user.id)
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Авторизоваться в Shikimori", url=build_authorize_url(state))]
        ]
    )
    await message.answer(
        "Привет! Подключите Shikimori, чтобы бот мог работать с вашими списками.",
        reply_markup=keyboard,
    )
