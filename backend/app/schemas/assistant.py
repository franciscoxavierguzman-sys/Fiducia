from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class AssistantChatRequest(BaseModel):
    conversation_id: int | None = None
    message: str = Field(min_length=1, max_length=3000)


class AssistantChatResponse(BaseModel):
    conversation_id: int
    message_id: int
    answer: str
    intent: str
    provider: str
    tools_used: list[str]
    sources: list[dict[str, Any]]
    source_types: list[str]
    warnings: list[str]
    generated_at: datetime


class AssistantMessageRead(BaseModel):
    id: int
    role: str
    content: str
    intent: str | None
    provider: str | None
    tools_used_json: list | None
    sources_json: list | None
    created_at: datetime

    model_config = {"from_attributes": True}


class AssistantConversationRead(BaseModel):
    id: int
    title: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class AssistantConversationDetail(AssistantConversationRead):
    messages: list[AssistantMessageRead]


class AssistantCapability(BaseModel):
    name: str
    description: str
    allowed_roles: list[str]


class AssistantInfo(BaseModel):
    provider: str
    provider_status: str
    fallback_enabled: bool
    version: str
    max_message_chars: int
    max_tools_per_request: int
