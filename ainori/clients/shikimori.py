"""Lightweight client for interacting with the Shikimori public API."""

from __future__ import annotations

import asyncio
import json
from dataclasses import dataclass
from typing import Any, Callable, List
from urllib import parse, request

JsonValue = dict[str, Any]


@dataclass
class _ResponseWrapper:
    body: bytes

    def read(self) -> bytes:  # pragma: no cover - compatibility helper
        return self.body

    def __enter__(self) -> "_ResponseWrapper":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        return None


class ShikimoriClient:
    """
    Minimal asynchronous Shikimori client.

    The client is intentionally dependency‑free so it can be tested without real
    network calls. An opener callable can be injected to fully mock HTTP
    responses.
    """

    def __init__(
        self,
        base_url: str = "https://shikimori.one/api",
        opener: Callable[[str], Any] | None = None,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self._opener: Callable[[str], Any] = opener or request.urlopen

    async def fetch_anime(self, anime_id: int) -> JsonValue:
        url = f"{self.base_url}/animes/{anime_id}"
        response = await asyncio.to_thread(self._request_json, url)
        if not isinstance(response, dict):
            raise RuntimeError("Unexpected Shikimori response type")
        return response

    async def search_anime(self, query: str, limit: int = 5) -> List[JsonValue]:
        params = parse.urlencode({"search": query, "limit": limit})
        url = f"{self.base_url}/animes?{params}"
        response = await asyncio.to_thread(self._request_json, url)
        if isinstance(response, list):
            return response
        return [response]

    def _request_json(self, url: str) -> JsonValue | List[JsonValue]:
        raw = self._request_bytes(url)
        try:
            return json.loads(raw.decode("utf-8"))
        except json.JSONDecodeError as exc:  # pragma: no cover - defensive
            raise RuntimeError("Invalid response from Shikimori") from exc

    def _request_bytes(self, url: str) -> bytes:
        with self._opener(url) as response:
            if hasattr(response, "read"):
                return response.read()
            if hasattr(response, "body"):
                return response.body
            raise RuntimeError("Opener must return a file-like object with 'read'")


__all__ = ["ShikimoriClient", "_ResponseWrapper"]
