from __future__ import annotations

from src.services.gemini_limiter import GeminiRateLimiter


def test_cached_run_avoids_repeating_operation():
    calls = []
    limiter = GeminiRateLimiter(requests_per_minute=15, cache_ttl=60)

    def operation():
        calls.append(1)
        return "answer"

    assert limiter.cached_run("same-question", operation) == "answer"
    assert limiter.cached_run("same-question", operation) == "answer"
    assert len(calls) == 1


def test_different_cache_keys_are_independent():
    calls = []
    limiter = GeminiRateLimiter(requests_per_minute=15, cache_ttl=60)

    def operation():
        calls.append(1)
        return len(calls)

    assert limiter.cached_run("question-a", operation) == 1
    assert limiter.cached_run("question-b", operation) == 2
    assert len(calls) == 2
