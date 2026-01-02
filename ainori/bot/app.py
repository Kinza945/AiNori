"""Minimal bot application used for integration-style tests."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Awaitable, Callable, Dict, List

from ainori.services.recommendation import RecommendationService

Handler = Callable[["BotMessage"], Awaitable[None]]


@dataclass
class BotMessage:
    text: str
    replies: List[str] = field(default_factory=list)

    async def answer(self, text: str) -> None:
        self.replies.append(text)


class BotApp:
    """Simple dispatcher inspired by aiogram command handlers."""

    def __init__(self, recommendation_service: RecommendationService) -> None:
        self.recommendation_service = recommendation_service
        self._handlers: Dict[str, Handler] = {}

    def command(self, name: str) -> Callable[[Handler], Handler]:
        def decorator(func: Handler) -> Handler:
            self._handlers[name] = func
            return func

        return decorator

    async def dispatch(self, text: str) -> BotMessage:
        if not text.startswith("/"):
            raise ValueError("Bot commands must start with '/'")
        name, *_ = text.lstrip("/").split(maxsplit=1)
        message = BotMessage(text=text)
        handler = self._handlers.get(name)
        if handler is None:
            await message.answer("Неизвестная команда.")
            return message
        await handler(message)
        return message

    async def send_recommendation(self, message: BotMessage, query: str) -> None:
        recommendation = await self.recommendation_service.recommend(query)
        if not recommendation:
            await message.answer("Не удалось найти аниме по запросу.")
            return
        title = recommendation.get("name") or recommendation.get("russian") or "Аниме"
        await message.answer(f"Попробуйте посмотреть: {title}")


def build_bot_app(service: RecommendationService) -> BotApp:
    from handlers import menu, recommendation, start

    app = BotApp(service)

    @app.command("start")
    async def start_cmd(message: BotMessage) -> None:  # pragma: no cover - thin wrapper
        await start.handle_start(message)

    @app.command("menu")
    async def menu_cmd(message: BotMessage) -> None:  # pragma: no cover - thin wrapper
        await menu.handle_menu(message)

    @app.command("recommend")
    async def recommend_cmd(
        message: BotMessage,
    ) -> None:  # pragma: no cover - thin wrapper
        query = message.text[len("/recommend") :].strip() or ""
        await recommendation.handle_recommendation(app, message, query)

    return app


__all__ = ["BotApp", "BotMessage", "build_bot_app"]
