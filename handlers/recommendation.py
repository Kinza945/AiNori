import random
from collections import defaultdict
from typing import Dict, List, Tuple

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message

from keyboards import main_menu_keyboard, temperature_keyboard

router = Router()

# Простые данные для демонстрации; в реальном проекте вместо этого будет вызов API.
Anime = Tuple[str, str, str]
RECOMMENDATIONS: List[Anime] = [
    (
        "Vinland Saga",
        "Исторический экшен о становлении викинга Торфинна, месть и выбор пути.",
        "https://shikimori.one/animes/39535-vinland-saga",
    ),
    (
        "Made in Abyss",
        "Путешествие в Безду: дружба, тайны древних технологий и испытания героям.",
        "https://shikimori.one/animes/34599-made-in-abyss",
    ),
    (
        "Mushishi",
        "Спокойные истории о Гинко, исследующем загадочных существ муши.",
        "https://shikimori.one/animes/457-mushishi",
    ),
    (
        "Baccano!",
        "Нелинейный криминальный экшен про бессмертных, гангстеров и алхимию.",
        "https://shikimori.one/animes/2251-baccano",
    ),
    (
        "Hyouka",
        "Школьный клуб расследует бытовые загадки, балансируя между интригой и бытом.",
        "https://shikimori.one/animes/12189-hyouka",
    ),
    (
        "Samurai Champloo",
        "Роуд-муви о самураях с хип-хоп эстетикой и яркими персонажами.",
        "https://shikimori.one/animes/205-samurai-champloo",
    ),
    (
        "Barakamon",
        "Тёплая история каллиграфа на острове о творчестве, дружбе и поиске себя.",
        "https://shikimori.one/animes/22789-barakamon",
    ),
    (
        "Mononoke",
        "Визуально экспериментальное аниме о таинственном лекаре и ёкаях.",
        "https://shikimori.one/animes/2246-mononoke",
    ),
]

user_temperature: Dict[int, float] = defaultdict(lambda: 0.5)


def pick_recommendations(temperature: float, limit: int = 5) -> List[Anime]:
    """Сформировать список рекомендаций с учётом температуры."""
    base = RECOMMENDATIONS.copy()
    random.shuffle(base)
    cutoff = max(1, int(limit * (1 - temperature)))
    core = base[:cutoff]
    remaining = [item for item in base if item not in core]
    noise = random.sample(remaining, k=min(limit - len(core), len(remaining)))
    result = core + noise
    return result[:limit]


def format_recommendations(recs: List[Anime]) -> str:
    """Отформатировать рекомендации для вывода."""
    lines = []
    for title, desc, url in recs:
        lines.append(f"<b>{title}</b>\n{desc}\n<a href='{url}'>Открыть на Shikimori</a>")
    return "\n\n".join(lines)


@router.message(Command("recommendations"))
async def recommendations_command(message: Message) -> None:
    """Ответить списком рекомендаций по команде."""
    temperature = user_temperature[message.from_user.id]
    recs = pick_recommendations(temperature)
    await message.answer(
        format_recommendations(recs),
        disable_web_page_preview=False,
        reply_markup=main_menu_keyboard(),
    )


@router.callback_query(F.data == "recommendations")
async def recommendations_callback(call: CallbackQuery) -> None:
    """Показать рекомендации при нажатии на кнопку меню."""
    temperature = user_temperature[call.from_user.id]
    recs = pick_recommendations(temperature)
    await call.message.edit_text(
        format_recommendations(recs),
        disable_web_page_preview=False,
        reply_markup=main_menu_keyboard(),
    )
    await call.answer("Подобрал новые тайтлы")


@router.callback_query(F.data == "refresh")
async def refresh_recommendations(call: CallbackQuery) -> None:
    """Обновить выдачу рекомендаций."""
    temperature = user_temperature[call.from_user.id]
    recs = pick_recommendations(temperature)
    await call.message.edit_text(
        format_recommendations(recs),
        disable_web_page_preview=False,
        reply_markup=main_menu_keyboard(),
    )
    await call.answer("Рекомендации обновлены")


@router.callback_query(F.data == "temperature_menu")
async def temperature_menu(call: CallbackQuery) -> None:
    """Показать выбор температуры."""
    current = user_temperature[call.from_user.id]
    await call.message.edit_text(
        "Выберите температуру — чем ниже, тем смелее подборка:",
        reply_markup=temperature_keyboard(current),
    )
    await call.answer()


@router.callback_query(F.data.startswith("temperature:"))
async def set_temperature(call: CallbackQuery) -> None:
    """Сохранить температуру и показать новые рекомендации."""
    value = float(call.data.split(":", maxsplit=1)[1])
    user_temperature[call.from_user.id] = value
    recs = pick_recommendations(value)
    await call.message.edit_text(
        format_recommendations(recs),
        disable_web_page_preview=False,
        reply_markup=main_menu_keyboard(),
    )
    await call.answer(f"Температура установлена: {value:.2f}")


@router.callback_query(F.data == "back_to_menu")
async def back_to_menu(call: CallbackQuery) -> None:
    """Вернуться к главному меню без изменения состояния."""
    await call.message.edit_text("Выберите действие:", reply_markup=main_menu_keyboard())
    await call.answer()
