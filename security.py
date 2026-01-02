import logging
import os
import re
from typing import Iterable, List

from cryptography.fernet import Fernet, InvalidToken


class SensitiveDataFilter(logging.Filter):
    """Filter that redacts configured secrets from log messages."""

    def __init__(self, secrets: Iterable[str]):
        super().__init__()
        # Remove empty values and precompile regex for speed
        self._patterns: List[re.Pattern[str]] = [
            re.compile(re.escape(secret)) for secret in secrets if secret
        ]

    def filter(self, record: logging.LogRecord) -> bool:  # pragma: no cover - small wrapper
        message = str(record.getMessage())
        for pattern in self._patterns:
            message = pattern.sub("[REDACTED]", message)
        record.msg = message
        return True


def configure_logging(secrets: Iterable[str]) -> None:
    """Configure logging with secrets redacted from output."""

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )
    logger = logging.getLogger()
    logger.addFilter(SensitiveDataFilter(secrets))


def _get_fernet() -> Fernet:
    key = os.getenv("FERNET_KEY")
    if not key:
        raise RuntimeError("FERNET_KEY is required to decrypt tokens")
    try:
        return Fernet(key.encode())
    except ValueError as exc:  # pragma: no cover - invalid key guarded by runtime
        raise RuntimeError("Invalid FERNET_KEY format") from exc


def decrypt_token(encrypted_token: str) -> str:
    """Decrypt a token encrypted with Fernet using the key from env."""

    fernet = _get_fernet()
    try:
        return fernet.decrypt(encrypted_token.encode()).decode()
    except InvalidToken as exc:  # pragma: no cover - runtime guard
        raise RuntimeError("Failed to decrypt token; check FERNET_KEY and value") from exc


def load_bot_token() -> str:
    """Load and decrypt the bot token from environment variables."""

    encrypted_token = os.getenv("BOT_TOKEN_ENC")
    if encrypted_token:
        return decrypt_token(encrypted_token)

    plain_token = os.getenv("BOT_TOKEN")
    if plain_token:
        return plain_token

    raise RuntimeError("Bot token not found in environment")


def encrypt_token(token: str) -> str:
    """Helper to encrypt a token for storage in BOT_TOKEN_ENC."""

    return _get_fernet().encrypt(token.encode()).decode()
