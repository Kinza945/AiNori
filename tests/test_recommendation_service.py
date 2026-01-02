import asyncio
import random
from unittest.mock import AsyncMock

from ainori.services.recommendation import RecommendationService


def test_recommend_returns_first_for_cold_temperature():
    client = AsyncMock()
    client.search_anime.return_value = [
        {"id": 1, "name": "A"},
        {"id": 2, "name": "B"},
    ]
    service = RecommendationService(client, rng=random.Random(42))

    result = asyncio.run(service.recommend("ninja", temperature=0))

    assert result["name"] == "A"


def test_recommend_returns_random_for_hot_temperature():
    client = AsyncMock()
    client.search_anime.return_value = [
        {"id": 1, "name": "A"},
        {"id": 2, "name": "B"},
    ]
    service = RecommendationService(client, rng=random.Random(1))

    result = asyncio.run(service.recommend("ninja", temperature=1))

    assert result["name"] in {"A", "B"}


def test_recommend_weights_are_temperature_sensitive():
    client = AsyncMock()
    client.search_anime.return_value = [
        {"id": 1, "name": "A"},
        {"id": 2, "name": "B"},
        {"id": 3, "name": "C"},
    ]
    rng = random.Random(0)
    service = RecommendationService(client, rng=rng)

    cold_pick = asyncio.run(service.recommend("ninja", temperature=0.1))
    hot_pick = asyncio.run(service.recommend("ninja", temperature=0.9))

    assert cold_pick["name"] == "A"
    assert hot_pick["name"] in {"A", "B", "C"}
