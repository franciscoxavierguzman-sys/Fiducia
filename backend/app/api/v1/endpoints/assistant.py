from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.assistant import (
    AssistantCapability,
    AssistantChatRequest,
    AssistantChatResponse,
    AssistantConversationDetail,
    AssistantConversationRead,
    AssistantInfo,
)
from app.services import assistant as assistant_service

router = APIRouter()


@router.post("/chat", response_model=AssistantChatResponse)
def chat(payload: AssistantChatRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return assistant_service.chat(db, current_user, payload.message, payload.conversation_id)


@router.get("/conversations", response_model=list[AssistantConversationRead])
def conversations(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return assistant_service.list_conversations(db, current_user)


@router.get("/conversations/{conversation_id}", response_model=AssistantConversationDetail)
def conversation_detail(conversation_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return assistant_service.get_conversation(db, current_user, conversation_id)


@router.get("/capabilities", response_model=list[AssistantCapability])
def capabilities(current_user: User = Depends(get_current_user)):
    return assistant_service.capabilities_for_user(current_user)


@router.get("/info", response_model=AssistantInfo)
def info(_: User = Depends(get_current_user)):
    return assistant_service.assistant_info()
