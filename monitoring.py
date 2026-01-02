import logging
import os
from contextlib import contextmanager
from typing import Iterator

from prometheus_client import Counter, Summary, start_http_server
import sentry_sdk

logger = logging.getLogger(__name__)

REQUEST_LATENCY = Summary(
    "bot_request_latency_seconds", "Latency of incoming bot updates"
)
ERROR_COUNTER = Counter(
    "bot_processing_errors_total", "Count of errors while processing updates"
)
RATE_LIMIT_REJECTIONS = Counter(
    "bot_rate_limit_rejections_total", "Number of requests blocked by rate limiting"
)


def init_sentry_from_env() -> None:
    dsn = os.getenv("SENTRY_DSN")
    if not dsn:
        logger.info("Sentry DSN not configured; skipping Sentry init")
        return

    sentry_sdk.init(
        dsn=dsn,
        traces_sample_rate=float(os.getenv("SENTRY_TRACES_SAMPLE_RATE", 0.1)),
    )
    logger.info("Sentry initialized")


def init_metrics_server() -> None:
    port = int(os.getenv("METRICS_PORT", 9000))
    start_http_server(port)
    logger.info("Prometheus metrics server started on port %s", port)


@contextmanager
def record_latency() -> Iterator[None]:
    with REQUEST_LATENCY.time():
        try:
            yield
        except Exception:
            ERROR_COUNTER.inc()
            raise
