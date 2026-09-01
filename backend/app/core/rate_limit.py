from __future__ import annotations

import time
from collections import defaultdict, deque
from threading import Lock

from fastapi import HTTPException, Request, status


class InMemoryRateLimiter:
    def __init__(self) -> None:
        self._lock = Lock()
        self._hits: dict[str, deque[float]] = defaultdict(deque)

    def check(self, key: str, *, limit: int, window_seconds: int) -> None:
        now = time.monotonic()
        oldest = now - window_seconds
        with self._lock:
            hits = self._hits[key]
            while hits and hits[0] < oldest:
                hits.popleft()
            if len(hits) >= limit:
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail={"code": "RATE_LIMITED", "message": "Demasiados intentos. Espera un momento e intenta de nuevo."},
                )
            hits.append(now)


rate_limiter = InMemoryRateLimiter()


def client_rate_key(request: Request, scope: str) -> str:
    forwarded_for = request.headers.get("X-Forwarded-For", "")
    client_ip = forwarded_for.split(",")[0].strip() if forwarded_for else (request.client.host if request.client else "local")
    return f"{scope}:{client_ip}"
