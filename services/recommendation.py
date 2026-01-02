"""Recommendation pipeline built on top of Shikimori data."""
from __future__ import annotations

import logging
import random
from collections import Counter
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, Iterable, List, Optional, Sequence, Set

from clients.shikimori import ShikimoriClient, extract_genre_names

logger = logging.getLogger(__name__)


@dataclass
class Recommendation:
    """Lightweight recommendation payload for persistence in the DB."""

    user_id: int
    anime_id: int
    score: float
    reason: str
    payload: Dict[str, Any]
    created_at: datetime


@dataclass
class UserProfile:
    """Aggregated user preference profile built from user rates."""

    rated_ids: Set[int]
    favorite_genres: Counter
    anchor_anime_ids: List[int]


class RecommendationService:
    """Generate anime recommendations based on user history."""

    def __init__(
        self,
        client: ShikimoriClient,
        *,
        min_score: int = 7,
        genre_weight: float = 1.0,
        temperature: float = 0.2,
    ) -> None:
        self.client = client
        self.min_score = min_score
        self.genre_weight = genre_weight
        self.temperature = temperature

    def _build_profile(
        self,
        user_rates: Sequence[Dict[str, Any]],
        details_by_anime: Dict[int, Dict[str, Any]],
    ) -> UserProfile:
        rated_ids: Set[int] = set()
        genre_counter: Counter = Counter()
        anchor_anime_ids: List[int] = []

        for rate in user_rates:
            anime_id = int(rate.get("target_id"))
            rated_ids.add(anime_id)
            score = rate.get("score")
            details = details_by_anime.get(anime_id) or {}
            genres = extract_genre_names(details)
            if score:
                genre_counter.update(genres)
            if score and score >= self.min_score:
                anchor_anime_ids.append(anime_id)

        return UserProfile(
            rated_ids=rated_ids,
            favorite_genres=genre_counter,
            anchor_anime_ids=anchor_anime_ids,
        )

    def _extract_related_anime(self, details: Dict[str, Any]) -> List[int]:
        candidates: Set[int] = set()
        for key in ("similar", "similar_animes", "related"):
            raw_items = details.get(key)
            if not raw_items:
                continue
            for item in raw_items:
                if isinstance(item, dict) and item.get("id"):
                    candidates.add(int(item["id"]))
        return list(candidates)

    def _score_candidates(
        self,
        candidate_ids: Iterable[int],
        details_by_anime: Dict[int, Dict[str, Any]],
        profile: UserProfile,
        *,
        temperature: Optional[float] = None,
    ) -> List[Recommendation]:
        temp = self.temperature if temperature is None else temperature
        recommendations: List[Recommendation] = []
        now = datetime.utcnow()

        for anime_id in candidate_ids:
            if anime_id in profile.rated_ids:
                continue
            details = details_by_anime.get(anime_id, {})
            genres = extract_genre_names(details)
            genre_score = sum(profile.favorite_genres.get(genre, 0) for genre in genres)
            random_bonus = random.random() * temp
            total_score = genre_score * self.genre_weight + random_bonus
            reason = "Жанровое совпадение" if genre_score else "Исследование каталога"
            recommendations.append(
                Recommendation(
                    user_id=0,
                    anime_id=anime_id,
                    score=total_score,
                    reason=reason,
                    payload={
                        "genres": genres,
                        "genre_score": genre_score,
                        "random_bonus": random_bonus,
                    },
                    created_at=now,
                )
            )
        recommendations.sort(key=lambda rec: rec.score, reverse=True)
        return recommendations

    def recommend(
        self,
        *,
        user_id: int,
        access_token: str,
        limit: int = 10,
        temperature: Optional[float] = None,
    ) -> List[Recommendation]:
        """Generate a list of recommendations for the provided user.

        The pipeline fetches user rates, builds a preference profile, collects
        related titles for every highly rated show, scores them using genre
        overlap, and finally mixes in randomness controlled by `temperature`.
        """

        user_rates = list(
            self.client.fetch_user_rates(access_token=access_token, user_id=user_id)
        )
        details_by_anime: Dict[int, Dict[str, Any]] = {}
        for rate in user_rates:
            anime_id = int(rate.get("target_id"))
            if anime_id not in details_by_anime:
                details_by_anime[anime_id] = self.client.fetch_anime_details(
                    access_token, anime_id
                )

        profile = self._build_profile(user_rates, details_by_anime)

        candidate_ids: Set[int] = set()
        for anime_id in profile.anchor_anime_ids:
            details = details_by_anime.get(anime_id) or {}
            candidate_ids.update(self._extract_related_anime(details))

        logger.info(
            "Profile built for user %s: %s favorite genres, %s anchors",
            user_id,
            len(profile.favorite_genres),
            len(profile.anchor_anime_ids),
        )

        scored = self._score_candidates(
            candidate_ids, details_by_anime, profile, temperature=temperature
        )

        for rec in scored:
            rec.user_id = user_id
        return scored[:limit]
