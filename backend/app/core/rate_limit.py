from collections import defaultdict, deque
from time import monotonic


class InMemoryRateLimiter:
    def __init__(self):
        self._hits: dict[str, deque[float]] = defaultdict(deque)

    def allow(self, key: str, limit: int, window_seconds: int) -> bool:
        now = monotonic()
        bucket = self._hits[key]
        while bucket and bucket[0] <= now - window_seconds:
            bucket.popleft()
        if len(bucket) >= limit:
            return False
        bucket.append(now)
        return True


registration_limiter = InMemoryRateLimiter()
login_limiter = InMemoryRateLimiter()
