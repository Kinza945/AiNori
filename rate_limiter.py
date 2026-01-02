import logging
import os
from dataclasses import dataclass

import redis

logger = logging.getLogger(__name__)


@dataclass
class RateLimiter:
    redis_client: redis.Redis
    limit: int = 30
    window_seconds: int = 60

    @classmethod
    def from_env(cls) -> "RateLimiter":
        redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
        limit = int(os.getenv("RATE_LIMIT", 30))
        window = int(os.getenv("RATE_LIMIT_WINDOW", 60))
        client = redis.Redis.from_url(redis_url)
        return cls(client, limit=limit, window_seconds=window)

    def allow(self, user_id: str) -> bool:
        """Return True if the user is under the limit, False otherwise."""

        key = f"rate_limit:{user_id}"
        with self.redis_client.pipeline() as pipe:
            pipe.incr(key, 1)
            pipe.expire(key, self.window_seconds)
            count, _ = pipe.execute()

        allowed = int(count) <= self.limit
        if not allowed:
            logger.warning("Rate limit exceeded for user_id=%s", user_id)
        return allowed
