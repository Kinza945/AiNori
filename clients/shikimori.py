"""Shikimori API client helpers."""
from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Optional

import requests

logger = logging.getLogger(__name__)


@dataclass
class TokenSet:
    """Represents OAuth tokens returned by Shikimori.

    Attributes:
        access_token: Access token for authorized API calls.
        refresh_token: Refresh token for renewing access.
        expires_in: Number of seconds until the token expires.
        created_at: Epoch timestamp when the token was issued.
    """

    access_token: str
    refresh_token: str
    expires_in: int
    created_at: int


class ShikimoriClient:
    """Tiny wrapper around the Shikimori API.

    The client intentionally avoids maintaining any shared state so it can be
    reused by background workers or request handlers without side effects.
    """

    def __init__(
        self,
        client_id: str,
        client_secret: str,
        redirect_uri: str,
        base_url: str = "https://shikimori.one",
        session: Optional[requests.Session] = None,
    ) -> None:
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.base_url = base_url.rstrip("/")
        self.session = session or requests.Session()
        self.session.headers.update(
            {
                "User-Agent": "AiNoriBot/1.0",
                "Accept": "application/json",
            }
        )

    def _url(self, path: str) -> str:
        return f"{self.base_url}{path}"

    def _auth_headers(self, access_token: str) -> Dict[str, str]:
        return {"Authorization": f"Bearer {access_token}"}

    def refresh_token(self, refresh_token: str) -> TokenSet:
        """Refresh OAuth tokens using the provided refresh token."""

        payload = {
            "grant_type": "refresh_token",
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "refresh_token": refresh_token,
            "redirect_uri": self.redirect_uri,
        }
        url = self._url("/oauth/token")
        logger.debug("Refreshing token via %s", url)
        response = self.session.post(url, data=payload)
        response.raise_for_status()
        data = response.json()
        return TokenSet(
            access_token=data["access_token"],
            refresh_token=data["refresh_token"],
            expires_in=int(data.get("expires_in", 0)),
            created_at=int(data.get("created_at", 0)),
        )

    def fetch_user_rates(
        self,
        access_token: str,
        user_id: int,
        limit: int = 50,
        status: Optional[str] = None,
    ) -> Iterable[Dict[str, Any]]:
        """Yield user rates for the given user.

        The method transparently walks through all available pages. Records are
        yielded as returned by the API without additional normalization to avoid
        accidental data loss when new fields appear on the backend.
        """

        page = 1
        headers = self._auth_headers(access_token)
        while True:
            params: Dict[str, Any] = {
                "user_id": user_id,
                "target_type": "Anime",
                "page": page,
                "limit": limit,
            }
            if status:
                params["status"] = status
            url = self._url("/api/v2/user_rates")
            logger.debug("Fetching user rates page %s via %s", page, url)
            response = self.session.get(url, params=params, headers=headers)
            response.raise_for_status()
            chunk: List[Dict[str, Any]] = response.json()
            if not chunk:
                break
            for item in chunk:
                yield item
            if len(chunk) < limit:
                break
            page += 1

    def fetch_anime_details(self, access_token: str, anime_id: int) -> Dict[str, Any]:
        """Return detailed anime information for the provided id."""

        url = self._url(f"/api/animes/{anime_id}")
        logger.debug("Fetching anime #%s details via %s", anime_id, url)
        response = self.session.get(url, headers=self._auth_headers(access_token))
        response.raise_for_status()
        return response.json()


def extract_genre_names(anime_details: Dict[str, Any]) -> List[str]:
    """Safely extract genre names from an anime details payload."""

    genres = anime_details.get("genres") or []
    names: List[str] = []
    for genre in genres:
        if isinstance(genre, dict):
            name = genre.get("russian") or genre.get("name")
            if name:
                names.append(name)
    return names
