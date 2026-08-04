# Run: uv run python 01-plan-and-manage/06_rate_limit_backoff.py
"""429 handling — exponential backoff + jitter using `tenacity`.

Retry only on rate-limit / transient errors. Respect the `Retry-After` header
when the service tells you when to come back.
"""
import logging

from openai import APIConnectionError, RateLimitError
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_random_exponential,
    before_sleep_log,
)

from _shared.config import settings
from _shared.openai_client import openai_client

logging.basicConfig(level=logging.WARNING)
log = logging.getLogger("backoff")

# Only retry transient errors (429, connection drops).
# Never retry 404/400/401 — those are bugs, not transient failures.
@retry(
    reraise=True,
    retry=retry_if_exception_type((RateLimitError, APIConnectionError)),
    wait=wait_random_exponential(multiplier=1, max=60),
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
