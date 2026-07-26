from __future__ import annotations

from collections import defaultdict, deque
from dataclasses import dataclass
from threading import Lock
from time import time


@dataclass
class RateLimitResult:
    allowed: bool
    retry_after_seconds: int = 0


class RateLimiter:
    def __init__(self, requests_per_minute: int, burst: int) -> None:
        self._requests_per_minute = requests_per_minute
        self._burst = burst
        self._window_seconds = 60
        self._events: dict[str, deque[float]] = defaultdict(deque)
        self._lock = Lock()

    def check(self, key: str) -> RateLimitResult:
        now = time()
        limit = self._requests_per_minute + self._burst
        with self._lock:
            queue = self._events[key]
            while queue and now - queue[0] > self._window_seconds:
                queue.popleft()
            if len(queue) >= limit:
                retry_after = max(1, int(self._window_seconds - (now - queue[0])))
                return RateLimitResult(allowed=False, retry_after_seconds=retry_after)
            queue.append(now)
        return RateLimitResult(allowed=True)
