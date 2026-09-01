from __future__ import annotations

import logging
import time
from collections import defaultdict, deque
from dataclasses import dataclass
from threading import Lock
from uuid import uuid4

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response


logger = logging.getLogger("fiducia")


@dataclass
class RequestMetric:
    method: str
    path: str
    status_code: int
    duration_ms: float


class MetricsRegistry:
    def __init__(self, max_samples: int = 500) -> None:
        self._lock = Lock()
        self._samples: deque[RequestMetric] = deque(maxlen=max_samples)
        self._counts: dict[str, int] = defaultdict(int)

    def record(self, metric: RequestMetric) -> None:
        with self._lock:
            self._samples.append(metric)
            self._counts["requests_total"] += 1
            if metric.status_code >= 500:
                self._counts["errors_5xx"] += 1
            elif metric.status_code >= 400:
                self._counts["errors_4xx"] += 1

    def snapshot(self) -> dict:
        with self._lock:
            samples = list(self._samples)
            counts = dict(self._counts)
        durations = sorted(item.duration_ms for item in samples)
        return {
            "requests_total": counts.get("requests_total", 0),
            "errors_4xx": counts.get("errors_4xx", 0),
            "errors_5xx": counts.get("errors_5xx", 0),
            "sample_size": len(samples),
            "average_duration_ms": round(sum(durations) / len(durations), 2) if durations else 0,
            "p95_duration_ms": round(durations[int(len(durations) * 0.95) - 1], 2) if durations else 0,
            "max_duration_ms": round(max(durations), 2) if durations else 0,
        }


metrics_registry = MetricsRegistry()


class RequestContextMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        request_id = request.headers.get("X-Request-ID") or str(uuid4())
        request.state.request_id = request_id
        started = time.perf_counter()
        try:
            response = await call_next(request)
        except Exception:
            duration_ms = (time.perf_counter() - started) * 1000
            metrics_registry.record(RequestMetric(request.method, request.url.path, 500, duration_ms))
            logger.exception(
                "request_failed",
                extra={"request_id": request_id, "method": request.method, "path": request.url.path, "duration_ms": round(duration_ms, 2)},
            )
            raise
        duration_ms = (time.perf_counter() - started) * 1000
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "no-referrer"
        metrics_registry.record(RequestMetric(request.method, request.url.path, response.status_code, duration_ms))
        logger.info(
            "request_completed",
            extra={
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "status_code": response.status_code,
                "duration_ms": round(duration_ms, 2),
            },
        )
        return response
