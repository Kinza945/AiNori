from __future__ import annotations

import datetime as dt
from dataclasses import dataclass
from urllib.parse import urlencode

import aiohttp

from config import settings

BASE_URL = "https://shikimori.one"
AUTH_URL = f"{BASE_URL}/oauth/authorize"
TOKEN_URL = f"{BASE_URL}/oauth/token"


@dataclass(slots=True)
class TokenResponse:
    access_token: str
    refresh_token: str
    expires_in: int
    created_at: int
    scope: str | None

    @property
    def expires_at(self) -> dt.datetime:
        created = dt.datetime.fromtimestamp(self.created_at, tz=dt.timezone.utc)
        return created + dt.timedelta(seconds=self.expires_in)


def build_authorize_url(state: str) -> str:
    params = {
        "client_id": settings.shikimori_client_id,
        "redirect_uri": settings.shikimori_redirect_uri,
        "response_type": "code",
        "scope": "user_rates",
        "state": state,
    }
    return f"{AUTH_URL}?{urlencode(params)}"


async def _fetch_token(payload: dict[str, str]) -> TokenResponse:
    headers = {"User-Agent": "AiNoriBot/1.0"}
    async with aiohttp.ClientSession(headers=headers) as session:
        async with session.post(TOKEN_URL, data=payload) as response:
            response.raise_for_status()
            data = await response.json()
    return TokenResponse(
        access_token=data["access_token"],
        refresh_token=data["refresh_token"],
        expires_in=int(data["expires_in"]),
        created_at=int(data.get("created_at", dt.datetime.now(tz=dt.timezone.utc).timestamp())),
        scope=data.get("scope"),
    )


async def exchange_code(code: str) -> TokenResponse:
    payload = {
        "grant_type": "authorization_code",
        "client_id": settings.shikimori_client_id,
        "client_secret": settings.shikimori_client_secret,
        "code": code,
        "redirect_uri": settings.shikimori_redirect_uri,
    }
    return await _fetch_token(payload)


async def refresh_access_token(refresh_token: str) -> TokenResponse:
    payload = {
        "grant_type": "refresh_token",
        "client_id": settings.shikimori_client_id,
        "client_secret": settings.shikimori_client_secret,
        "refresh_token": refresh_token,
    }
    return await _fetch_token(payload)
