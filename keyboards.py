from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def main_menu_keyboard() -> InlineKeyboardMarkup:
    """Главное меню с базовыми действиями."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📋 Рекомендации", callback_data="recommendations")],
            [InlineKeyboardButton(text="🔄 Обновить", callback_data="refresh")],
            [InlineKeyboardButton(text="🎛 Температура", callback_data="temperature_menu")],
        ]
    )


def temperature_keyboard(selected: float) -> InlineKeyboardMarkup:
    """Клавиатура для выбора температуры рекомендаций."""
    options = [0.0, 0.25, 0.5, 0.75, 1.0]
    rows = []
    for value in options:
        suffix = " ✅" if value == selected else ""
        rows.append(
            [
                InlineKeyboardButton(
                    text=f"{value:.2f}{suffix}", callback_data=f"temperature:{value}"
                )
            ]
        )
    rows.append([InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_menu")])
    return InlineKeyboardMarkup(inline_keyboard=rows)
