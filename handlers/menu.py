from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message

from keyboards import TEMPERATURE_PRESETS, temperature_keyboard
from settings import settings_repo

router = Router(name="menu")


class SettingsState(StatesGroup):
    temperature = State()


@router.message(Command("settings"))
async def open_settings(message: Message, state: FSMContext) -> None:
    await state.set_state(SettingsState.temperature)
    await message.answer(
        "Выберите температуру генерации рекомендаций:",
        reply_markup=temperature_keyboard(),
    )


@router.callback_query(SettingsState.temperature, F.data.startswith("temp:"))
async def set_temperature(callback: CallbackQuery, state: FSMContext) -> None:
    raw_value = callback.data.split(":", maxsplit=1)[1]
    try:
        temperature = float(raw_value)
    except ValueError:
        await callback.answer("Не удалось прочитать температуру", show_alert=True)
        return

    settings_repo.update_temperature(callback.from_user.id, temperature)
    await callback.message.edit_text(
        f"Температура установлена на {temperature:.1f}.\n"
        f"Доступные пресеты: {', '.join(f'{item:.1f}' for item in TEMPERATURE_PRESETS)}",
    )
    await callback.answer()
    await state.clear()
