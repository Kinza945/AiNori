from dataclasses import dataclass
from random import Random
from typing import List

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from settings import settings_repo

router = Router(name="recommendation")


@dataclass
class RecommendationService:
    """Simple recommender that mixes standard and experimental titles."""

    random: Random
    standard_titles: List[str]
    experimental_titles: List[str]

    def generate(self, user_id: int, total: int = 6) -> list[str]:
        settings = settings_repo.get(user_id)
        temperature = max(0.0, min(settings.temperature, 1.0))
        experimental_quota = max(1, round(total * temperature))
        standard_quota = max(total - experimental_quota, 0)

        standard_pool = self.standard_titles.copy()
        experimental_pool = self.experimental_titles.copy()
        self.random.shuffle(standard_pool)
        self.random.shuffle(experimental_pool)

        recommendations: list[str] = []
        recommendations.extend(standard_pool[:standard_quota])
        recommendations.extend(experimental_pool[:experimental_quota])
        self.random.shuffle(recommendations)
        return recommendations[:total]


service = RecommendationService(
    random=Random(),
    standard_titles=[
        "Звёздные хроники",
        "Путь героя",
        "Тихий океан приключений",
        "Дом на холме",
        "Клуб исследователей",
    ],
    experimental_titles=[
        "Сны киберсада",
        "Нити вероятности",
        "Сборщик штормов",
        "Долина отражений",
        "Фрактальная симфония",
    ],
)


@router.message(Command("recommend"))
async def recommend(message: Message) -> None:
    picks = service.generate(message.from_user.id)
    await message.answer("\n".join(f"• {title}" for title in picks))
