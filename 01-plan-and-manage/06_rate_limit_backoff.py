# Run: uv run python 01-plan-and-manage/06_rate_limit_backoff.py
# Practice-question coverage: Q17, Q125.
"""429 handling — exponential backoff + jitter using `tenacity`.

Retry only on rate-limit / transient errors. Respect the `Retry-After` header
when the service tells you when to come back.
"""
import logging
from email.utils import parsedate_to_datetime
from datetime import datetime, timezone

from openai import APIConnectionError, RateLimitError
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_random_exponential,
    before_sleep_log,
)
from tenacity.wait import wait_base

from _shared.config import settings
from _shared.openai_client import openai_client

logging.basicConfig(level=logging.WARNING)
log = logging.getLogger("backoff")


def retry_after_seconds(error: Exception, fallback: float) -> float:
    """Prefer a bounded service retry hint over the exponential fallback."""
    headers = getattr(getattr(error, "response", None), "headers", {}) or {}
    raw_ms = headers.get("retry-after-ms")
    if raw_ms:
        try:
            return min(max(float(raw_ms) / 1000, 0), 60)
        except ValueError:
            pass

    raw_seconds = headers.get("retry-after")
    if raw_seconds:
        try:
            return min(max(float(raw_seconds), 0), 60)
        except ValueError:
            try:
                delay = (
                    parsedate_to_datetime(raw_seconds).astimezone(timezone.utc)
                    - datetime.now(timezone.utc)
                ).total_seconds()
                return min(max(delay, 0), 60)
            except (TypeError, ValueError):
                pass
    return fallback


class wait_retry_after_or_exponential(wait_base):
    def __init__(self) -> None:
        self._fallback = wait_random_exponential(multiplier=1, max=60)

    def __call__(self, retry_state) -> float:
        error = retry_state.outcome.exception() if retry_state.outcome else None
        fallback = self._fallback(retry_state)
        return retry_after_seconds(error, fallback) if error else fallback


# Only retry transient errors (429, connection drops).
# Never retry 404/400/401 — those are bugs, not transient failures.
@retry(
    reraise=True,
    retry=retry_if_exception_type((RateLimitError, APIConnectionError)),
    wait=wait_retry_after_or_exponential(),
    stop=stop_after_attempt(6),
    before_sleep=before_sleep_log(log, logging.WARNING),
)
def _ask(client, prompt: str) -> str:
    r = client.responses.create(model=settings().default_model, input=prompt)
    return r.output_text


def main() -> None:
    client = openai_client()
    # Fire a few requests back-to-back — with jitter the retry cadence stays sane
    # even under heavy contention.
    for i in range(5):
        print(f"[req {i}] {_ask(client, f'One-sentence fact about number {i}.')}")


if __name__ == "__main__":
    main()
