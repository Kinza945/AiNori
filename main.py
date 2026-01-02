import logging
import os
from typing import Any, Dict

from dotenv import load_dotenv

from monitoring import RATE_LIMIT_REJECTIONS, init_metrics_server, init_sentry_from_env, record_latency
from rate_limiter import RateLimiter
from security import configure_logging, load_bot_token

load_dotenv()


def handle_update(user_id: str, payload: Dict[str, Any], rate_limiter: RateLimiter) -> None:
    """Example request handler with rate limiting and metrics."""

    with record_latency():
        if not rate_limiter.allow(user_id):
            RATE_LIMIT_REJECTIONS.inc()
            return

        logging.info("Processing update for user_id=%s", user_id)
        # Token never logged: sanitized by logging filter.
        logging.debug("Payload keys: %s", list(payload))


def bootstrap() -> None:
    # Configure logging before anything else to avoid leaking secrets.
    configure_logging([
        os.getenv("BOT_TOKEN"),
        os.getenv("BOT_TOKEN_ENC"),
        os.getenv("FERNET_KEY"),
    ])

    init_sentry_from_env()
    init_metrics_server()

    bot_token = load_bot_token()
    logging.info("Bot token loaded and decrypted")

    rate_limiter = RateLimiter.from_env()
    logging.info(
        "Rate limiter configured: limit=%s, window_seconds=%s",
        rate_limiter.limit,
        rate_limiter.window_seconds,
    )

    # Example usage; in a real bot, integrate with the bot framework.
    sample_payload = {"action": "ping"}
    handle_update(user_id="demo", payload=sample_payload, rate_limiter=rate_limiter)


if __name__ == "__main__":
    bootstrap()
