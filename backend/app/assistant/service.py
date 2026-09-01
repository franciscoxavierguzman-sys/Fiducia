from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.assistant import ASSISTANT_VERSION
from app.assistant.prompt import build_prompt
from app.assistant.providers import DeterministicAssistantProvider, provider_from_environment
from app.assistant.router import extract_integer, extract_remittance_number, route_intent
from app.assistant.tools import ensure_tool_allowed, tool_registry
from app.assistant.types import AssistantContext, MAX_MESSAGE_CHARS, MAX_TOOLS_PER_REQUEST
from app.models.assistant import AssistantConversation, AssistantMessage
from app.models.user import User
from app.services.audit import log_audit_event


INTENT_TOOLS = {
    "GENERAL_HELP": ["get_support_article"],
    "MY_REMITTANCES": ["get_my_remittances"],
    "REMITTANCE_STATUS": ["get_remittance_status"],
    "REMITTANCE_FEES": ["get_remittance_fee"],
    "BI_OVERVIEW": ["get_bi_overview"],
    "BI_CORRIDORS": ["get_top_corridors"],
    "BI_CUSTOMERS": ["get_bi_customers"],
    "FORECAST_SUMMARY": ["get_forecast_summary"],
    "RISK_QUEUE": ["get_risk_queue"],
    "RISK_EXPLANATION": ["get_risk_assessment"],
    "BLOCKCHAIN_TRACE": ["get_blockchain_trace"],
    "BLOCKCHAIN_VERIFY": ["verify_blockchain_evidence"],
    "OUT_OF_SCOPE": [],
}


def assistant_info() -> dict[str, Any]:
    provider = provider_from_environment()
    health = provider.health_check()
    return {
        "provider": provider.provider_type,
        "provider_status": health["status"],
        "fallback_enabled": True,
        "version": ASSISTANT_VERSION,
        "max_message_chars": MAX_MESSAGE_CHARS,
        "max_tools_per_request": MAX_TOOLS_PER_REQUEST,
    }


def capabilities_for_user(user: User) -> list[dict[str, Any]]:
    return [
        {"name": tool.name, "description": tool.description, "allowed_roles": tool.allowed_roles}
        for tool in tool_registry().values()
        if user.role.name in tool.allowed_roles
    ]


def list_conversations(db: Session, user: User) -> list[AssistantConversation]:
    return list(
        db.scalars(
            select(AssistantConversation)
            .where(AssistantConversation.user_id == user.id, AssistantConversation.is_active.is_(True))
            .order_by(AssistantConversation.updated_at.desc(), AssistantConversation.id.desc())
        )
    )


def get_conversation(db: Session, user: User, conversation_id: int) -> AssistantConversation:
    conversation = db.scalars(
        select(AssistantConversation)
        .options(joinedload(AssistantConversation.messages))
        .where(AssistantConversation.id == conversation_id, AssistantConversation.user_id == user.id, AssistantConversation.is_active.is_(True))
    ).unique().first()
    if conversation is None:
        log_audit_event(db, user_id=user.id, action="ASSISTANT_ACCESS_DENIED", entity="assistant_conversation", entity_id=str(conversation_id), metadata={})
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"code": "ASSISTANT_CONVERSATION_NOT_FOUND", "message": "Conversacion no encontrada"})
    conversation.messages.sort(key=lambda item: item.created_at)
    return conversation


def chat(db: Session, user: User, message: str, conversation_id: int | None = None) -> dict[str, Any]:
    clean_message = message.strip()
    if len(clean_message) > MAX_MESSAGE_CHARS:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail={"code": "ASSISTANT_MESSAGE_TOO_LONG", "message": "Mensaje demasiado largo"})

    conversation = get_conversation(db, user, conversation_id) if conversation_id else _create_conversation(db, user, clean_message)
    intent = route_intent(clean_message)
    user_message = AssistantMessage(
        conversation_id=conversation.id,
        role="user",
        content=clean_message,
        intent=intent.intent,
        safety_events_json=intent.safety_events,
        metadata_json={"confidence": intent.confidence},
    )
    db.add(user_message)
    db.flush()
    log_audit_event(db, user_id=user.id, action="ASSISTANT_MESSAGE_RECEIVED", entity="assistant_conversation", entity_id=str(conversation.id), metadata={"intent": intent.intent})

    context = _build_context(db, user, clean_message, intent.intent, intent.safety_events)
    build_prompt(context)
    response = _generate_with_fallback(db, user, context)
    now = datetime.now(UTC)
    assistant_message = AssistantMessage(
        conversation_id=conversation.id,
        role="assistant",
        content=response.answer,
        intent=intent.intent,
        provider=response.provider,
        tools_used_json=context.tools_used,
        sources_json=context.sources,
        safety_events_json=intent.safety_events,
        metadata_json={"model": response.model, "source_types": sorted({source["type"] for source in context.sources}), "generated_at": now.isoformat()},
    )
    db.add(assistant_message)
    conversation.updated_at = now
    db.flush()
    log_audit_event(
        db,
        user_id=user.id,
        action="ASSISTANT_RESPONSE_GENERATED",
        entity="assistant_message",
        entity_id=str(assistant_message.id),
        metadata={"intent": intent.intent, "provider": response.provider, "tools_used": context.tools_used},
    )
    db.commit()
    db.refresh(assistant_message)
    return {
        "conversation_id": conversation.id,
        "message_id": assistant_message.id,
        "answer": response.answer,
        "intent": intent.intent,
        "provider": response.provider,
        "tools_used": context.tools_used,
        "sources": _client_safe_sources(context.sources, user),
        "source_types": sorted({source["type"] for source in context.sources}),
        "warnings": response.warnings,
        "generated_at": now,
    }


def _create_conversation(db: Session, user: User, message: str) -> AssistantConversation:
    title = message[:80] or "Nueva conversacion"
    conversation = AssistantConversation(user_id=user.id, title=title)
    db.add(conversation)
    db.flush()
    log_audit_event(db, user_id=user.id, action="ASSISTANT_CONVERSATION_CREATED", entity="assistant_conversation", entity_id=str(conversation.id), metadata={})
    return conversation


def _build_context(db: Session, user: User, question: str, intent: str, safety_events: list[str]) -> AssistantContext:
    registry = tool_registry()
    tools_used: list[str] = []
    sources: list[dict[str, Any]] = []
    data: dict[str, Any] = {}
    warnings: list[str] = []
    inputs = {"query": question, "remittance_number": extract_remittance_number(question), "assessment_id": extract_integer(question)}
    if safety_events:
        warnings.extend(safety_events)

    for tool_name in INTENT_TOOLS.get(intent, [])[:MAX_TOOLS_PER_REQUEST]:
        tool = registry[tool_name]
        try:
            ensure_tool_allowed(tool, user)
        except HTTPException:
            log_audit_event(db, user_id=user.id, action="ASSISTANT_ACCESS_DENIED", entity="assistant_tool", entity_id=tool_name, metadata={"intent": intent})
            warnings.append("ACCESS_DENIED")
            continue
        result = tool.handler(db, user, inputs)
        tools_used.append(tool.name)
        sources.extend(result.pop("sources", []))
        data.update(result)
        log_audit_event(db, user_id=user.id, action="ASSISTANT_TOOL_USED", entity="assistant_tool", entity_id=tool.name, metadata={"intent": intent})

    return AssistantContext(intent=intent, user_role=user.role.name, question=question, data=data, tools_used=tools_used, sources=sources, warnings=warnings)


def _generate_with_fallback(db: Session, user: User, context: AssistantContext):
    provider = provider_from_environment()
    try:
        return provider.generate(context)
    except Exception as exc:
        log_audit_event(db, user_id=user.id, action="ASSISTANT_PROVIDER_FAILED", entity="assistant_provider", entity_id=provider.provider_type, metadata={"error": str(exc)})
        return DeterministicAssistantProvider().generate(context)


def _client_safe_sources(sources: list[dict[str, Any]], user: User) -> list[dict[str, Any]]:
    if user.role.name == "CLIENT":
        return [{"type": source["type"], "label": source.get("title") or "Datos de FIDUCIA"} for source in sources]
    return sources
