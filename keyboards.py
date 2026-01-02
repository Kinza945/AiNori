from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

TEMPERATURE_PRESETS: tuple[float, ...] = (0.1, 0.3, 0.5, 0.8, 1.0)


def temperature_keyboard() -> InlineKeyboardMarkup:
    """Preset buttons for choosing the recommendation temperature."""

    buttons = [
        [InlineKeyboardButton(text=f"{preset:.1f}", callback_data=f"temp:{preset:.1f}")]
        for preset in TEMPERATURE_PRESETS
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)
