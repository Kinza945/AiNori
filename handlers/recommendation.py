import json
import random
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import List, Optional

from aiogram import Router
from aiogram.filters import Command, Text
from aiogram.types import BotCommand, Message

router = Router()


CACHE_PATH = Path("data/recommendations.json")


@dataclass
class Recommendation:
    title: str
    description: str
    link: str
    poster: Optional[str] = None


STATIC_POOL: List[Recommendation] = [
    Recommendation(
        title="Cowboy Bebop",
        description="Неонуар, космический вестерн, джаз, охота за головами",
        link="https://www.imdb.com/title/tt0213338/",
        poster="https://m.media-amazon.com/images/M/MV5BMjI5OTE5NjcwNF5BMl5BanBnXkFtZTgwMzE3NDQxMTE@._V1_FMjpg_UX1000_.jpg",
    ),
    Recommendation(
        title="Odd Taxi",
        description="Детектив, слайс оф лайф, разговорное расследование, звериный город",
        link="https://www.crunchyroll.com/series/GYQWNXP5R/odd-taxi",
        poster="https://i.imgur.com/dk5eANd.jpeg",
    ),
    Recommendation(
        title="Monster",
        description="Триллер, расследование, моральные дилеммы, Европа 90-х",
        link="https://www.nautiljon.com/animes/monster.html",
        poster="https://i.imgur.com/EZ8pC9u.jpeg",
    ),
    Recommendation(
        title="Mushishi",
        description="Атмосферное, медитативное, сверхъестественное, этюды природы",
        link="https://anilist.co/anime/457/Mushishi/",
        poster="https://i.imgur.com/CKvMdIh.jpeg",
    ),
    Recommendation(
        title="Vinland Saga",
        description="Исторический эпос, викинги, становление героя, драма",
        link="https://www.netflix.com/title/81074668",
        poster="https://i.imgur.com/O3xcz4l.jpeg",
    ),
    Recommendation(
        title="Ping Pong The Animation",
        description="Спортдрама, сильный визуальный стиль, характеры через матч",
        link="https://www.funimation.com/shows/ping-pong-the-animation/",
        poster="https://i.imgur.com/BLN1zNQ.jpeg",
    ),
    Recommendation(
        title="From the New World",
        description="Антиутопия, психические силы, социальный эксперимент",
        link="https://www.imdb.com/title/tt2325989/",
        poster="https://i.imgur.com/06qSmz4.jpeg",
    ),
]


BOT_COMMANDS = [
    BotCommand(command="recommendations", description="Показать сохранённые рекомендации"),
    BotCommand(command="refresh", description="Пересобрать рекомендации и обновить кеш"),
]


def _ensure_cache_dir() -> None:
    CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)


def _load_cached() -> Optional[List[Recommendation]]:
    if not CACHE_PATH.exists():
        return None
    try:
        with CACHE_PATH.open("r", encoding="utf-8") as file:
            raw = json.load(file)
    except (OSError, json.JSONDecodeError):
        return None
    return [Recommendation(**item) for item in raw.get("items", [])]


def _save_cache(items: List[Recommendation]) -> None:
    _ensure_cache_dir()
    payload = {"items": [asdict(item) for item in items]}
    CACHE_PATH.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def _generate_new_set(limit: int = 5) -> List[Recommendation]:
    return random.sample(STATIC_POOL, k=min(limit, len(STATIC_POOL)))


def _format_recommendation(item: Recommendation) -> str:
    return f"<b>{item.title}</b> — {item.description}\n{item.link}"


async def _send_recommendations(message: Message, items: List[Recommendation], prefix: str) -> None:
    await message.answer(prefix)
    for item in items:
        text = _format_recommendation(item)
        if item.poster:
            await message.answer_photo(item.poster, caption=text)
        else:
            await message.answer(text)


@router.message(Command("recommendations"))
@router.message(Text(equals="Рекомендации", ignore_case=True))
async def cmd_recommendations(message: Message) -> None:
    cached = _load_cached()
    if cached:
        await _send_recommendations(message, cached, "Нашёл последние рекомендации в кеше:")
    else:
        fresh = _generate_new_set()
        _save_cache(fresh)
        await _send_recommendations(message, fresh, "Кеша нет, собрал новый список:")


@router.message(Command("refresh"))
@router.message(Text(equals="Рефреш", ignore_case=True))
async def cmd_refresh(message: Message) -> None:
    fresh = _generate_new_set()
    _save_cache(fresh)
    await _send_recommendations(message, fresh, "Обновил рекомендации и перезаписал кеш:")
