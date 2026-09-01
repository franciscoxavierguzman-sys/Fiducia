from datetime import UTC, datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class AssistantConversation(Base):
    __tablename__ = "assistant_conversations"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(160), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(UTC), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC), nullable=False)

    messages = relationship("AssistantMessage", back_populates="conversation")


class AssistantMessage(Base):
    __tablename__ = "assistant_messages"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    conversation_id: Mapped[int] = mapped_column(ForeignKey("assistant_conversations.id"), nullable=False, index=True)
    role: Mapped[str] = mapped_column(String(20), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    intent: Mapped[str | None] = mapped_column(String(80), nullable=True)
    provider: Mapped[str | None] = mapped_column(String(80), nullable=True)
    tools_used_json: Mapped[list | None] = mapped_column(JSON, nullable=True)
    sources_json: Mapped[list | None] = mapped_column(JSON, nullable=True)
    safety_events_json: Mapped[list | None] = mapped_column(JSON, nullable=True)
    metadata_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(UTC), nullable=False)

    conversation = relationship("AssistantConversation", back_populates="messages")
