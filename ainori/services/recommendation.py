"""Recommendation service built on top of :class:`ShikimoriClient`."""

from __future__ import annotations

import math
import random
from typing import Any, List, Mapping, Sequence

from ainori.clients.shikimori import ShikimoriClient


class RecommendationService:
    def __init__(
        self, client: ShikimoriClient, rng: random.Random | None = None
    ) -> None:
        self._client = client
        self._rng = rng or random.Random()

    async def recommend(
        self, query: str, temperature: float = 0.5
    ) -> Mapping[str, Any]:
        candidates: Sequence[Mapping[str, Any]] = await self._client.search_anime(
            query, limit=10
        )
        if not candidates:
            return {}
        return self._select_candidate(candidates, temperature)

    def _select_candidate(
        self, candidates: Sequence[Mapping[str, Any]], temperature: float
    ) -> Mapping[str, Any]:
        if temperature <= 0:
            return candidates[0]
        if temperature >= 1:
            return self._rng.choice(candidates)

        weights = self._temperature_weights(len(candidates), temperature)
        index = self._rng.choices(range(len(candidates)), weights=weights, k=1)[0]
        return candidates[index]

    @staticmethod
    def _temperature_weights(size: int, temperature: float) -> List[float]:
        return [math.exp(-idx / max(temperature, 0.001)) for idx in range(size)]


__all__ = ["RecommendationService"]
