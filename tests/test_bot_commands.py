import asyncio

from ainori.bot.app import build_bot_app
from ainori.services.recommendation import RecommendationService


class DummyService(RecommendationService):
    def __init__(self, responses):
        self._responses = responses

    async def recommend(self, query: str, temperature: float = 0.5):
        return self._responses.get(query, {})


def create_bot(responses):
    service = DummyService(responses)
    return build_bot_app(service)


def test_start_command_provides_greeting():
    bot = create_bot({})

    message = asyncio.run(bot.dispatch("/start"))

    assert message.replies == [
        "Привет! Я помогу подобрать аниме. Используй /menu чтобы узнать, что я умею."
    ]


def test_menu_command_lists_options():
    bot = create_bot({})

    message = asyncio.run(bot.dispatch("/menu"))

    assert "Доступные команды" in message.replies[0]


def test_recommend_command_requires_query():
    bot = create_bot({})

    message = asyncio.run(bot.dispatch("/recommend"))

    assert message.replies == [
        "Укажите, что хотите посмотреть после команды /recommend."
    ]


def test_recommend_command_returns_suggestion():
    bot = create_bot({"shonen": {"name": "Naruto"}})

    message = asyncio.run(bot.dispatch("/recommend shonen"))

    assert message.replies == ["Попробуйте посмотреть: Naruto"]


def test_unknown_command_is_handled():
    bot = create_bot({})

    message = asyncio.run(bot.dispatch("/unknown"))

    assert message.replies == ["Неизвестная команда."]
