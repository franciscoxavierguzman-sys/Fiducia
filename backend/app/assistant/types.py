from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


MAX_MESSAGE_CHARS = 3000
MAX_TOOLS_PER_REQUEST = 3


@dataclass(frozen=True)
class IntentResult:
    intent: str
    confidence: float
    safety_events: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class AssistantContext:
    intent: str
    user_role: str
    question: str
    data: dict[str, Any]
    tools_used: list[str]
    sources: list[dict[str, Any]]
    warnings: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class ProviderResponse:
    answer: str
    provider: str
    model: str
    warnings: list[str] = field(default_factory=list)
