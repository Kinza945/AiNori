import asyncio
import json
from unittest.mock import Mock

from ainori.clients.shikimori import ShikimoriClient, _ResponseWrapper


def test_fetch_anime_uses_injected_opener():
    payload = {"id": 1, "name": "Naruto"}
    opener = Mock(return_value=_ResponseWrapper(json.dumps(payload).encode("utf-8")))
    client = ShikimoriClient(opener=opener)

    result = asyncio.run(client.fetch_anime(1))

    assert result == payload
    opener.assert_called_once_with("https://shikimori.one/api/animes/1")


def test_search_anime_returns_list_even_for_object():
    payload = {"id": 2, "name": "Bleach"}
    opener = Mock(return_value=_ResponseWrapper(json.dumps(payload).encode("utf-8")))
    client = ShikimoriClient(opener=opener)

    result = asyncio.run(client.search_anime("Bleach", limit=1))

    assert result == [payload]


def test_search_anime_with_multiple_results():
    payload = [{"id": 3, "name": "One Piece"}, {"id": 4, "name": "Gintama"}]
    opener = Mock(return_value=_ResponseWrapper(json.dumps(payload).encode("utf-8")))
    client = ShikimoriClient(opener=opener)

    result = asyncio.run(client.search_anime("pirate", limit=2))

    assert result == payload
    encoded_query = "search=pirate&limit=2"
    opener.assert_called_once_with(f"https://shikimori.one/api/animes?{encoded_query}")
