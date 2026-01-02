from dataclasses import dataclass
from typing import Dict


@dataclass
class Settings:
    """User configuration for recommendation generation."""

    temperature: float = 0.3


class SettingsRepository:
    """In-memory storage for user settings.

    This is intentionally simple for the prototype bot and can be replaced
    by persistent storage in the future.
    """

    def __init__(self) -> None:
        self._settings: Dict[int, Settings] = {}

    def get(self, user_id: int) -> Settings:
        return self._settings.setdefault(user_id, Settings())

    def update_temperature(self, user_id: int, temperature: float) -> Settings:
        settings = self.get(user_id)
        settings.temperature = temperature
        return settings


settings_repo = SettingsRepository()
