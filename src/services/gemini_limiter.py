from __future__ import annotations

import threading
import time
from collections import deque
from functools import wraps
from typing import Callable, TypeVar

T = TypeVar("T")


class GeminiRateLimiter:
    """Process-local sliding-window limiter for Gemini free-tier requests."""

    def __init__(self, requests_per_minute: int = 15, max_retries: int = 3, cache_ttl: int = 300):
        if requests_per_minute < 1:
            raise ValueError("requests_per_minute must be positive")
        self.interval = 60.0
        self.limit = requests_per_minute
        self.max_retries = max_retries
        self.cache_ttl = cache_ttl
        self._timestamps: deque[float] = deque()
        self._cache: dict[str, tuple[float, T]] = {}
        self._lock = threading.Lock()

    def acquire(self) -> None:
        while True:
            with self._lock:
                now = time.monotonic()
                while self._timestamps and now - self._timestamps[0] >= self.interval:
                    self._timestamps.popleft()
                if len(self._timestamps) < self.limit:
                    self._timestamps.append(now)
                    return
                wait_for = self.interval - (now - self._timestamps[0])
            time.sleep(max(wait_for, 0.01))

    def run(self, operation: Callable[[], T]) -> T:
        for attempt in range(self.max_retries + 1):
            self.acquire()
            try:
                return operation()
            except Exception as exc:
                if "429" not in str(exc) or attempt >= self.max_retries:
                    raise
                time.sleep(min(2 ** attempt, 30))
        raise RuntimeError("Gemini operation did not complete")

    def cached_run(self, cache_key: str, operation: Callable[[], T]) -> T:
        now = time.monotonic()
        with self._lock:
            cached = self._cache.get(cache_key)
            if cached and now - cached[0] < self.cache_ttl:
                return cached[1]
            if cached:
                self._cache.pop(cache_key, None)
        result = self.run(operation)
        with self._lock:
            self._cache[cache_key] = (time.monotonic(), result)
        return result

    def limited(self, operation: Callable[..., T]) -> Callable[..., T]:
        @wraps(operation)
        def wrapped(*args, **kwargs):
            return self.run(lambda: operation(*args, **kwargs))

        return wrapped
