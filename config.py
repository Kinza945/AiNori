import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()


def _require_env(name: str, default: str | None = None) -> str:
    value = os.getenv(name, default)
    if value is None or value == "":
        raise RuntimeError(f"Ожидается переменная окружения {name}")
    return value


@dataclass(slots=True)
class Settings:
    bot_token: str = _require_env("BOT_TOKEN")
    database_url: str = os.getenv("DATABASE_URL", "postgresql+asyncpg://postgres:postgres@db:5432/postgres")
    redis_url: str | None = os.getenv("REDIS_URL")

    shikimori_client_id: str = _require_env("SHIKIMORI_CLIENT_ID")
    shikimori_client_secret: str = _require_env("SHIKIMORI_CLIENT_SECRET")
    shikimori_redirect_uri: str = _require_env("SHIKIMORI_REDIRECT_URI")

    encryption_secret: str = _require_env("FERNET_SECRET")

    webhook_url: str | None = os.getenv("WEBHOOK_URL")
    webhook_path: str = os.getenv("WEBHOOK_PATH", "/telegram/webhook")
    webhook_secret: str | None = os.getenv("WEBHOOK_SECRET")
    http_host: str = os.getenv("HTTP_HOST", "0.0.0.0")
    http_port: int = int(os.getenv("HTTP_PORT", "8080"))


def load_settings() -> Settings:
    return Settings()


settings = load_settings()
