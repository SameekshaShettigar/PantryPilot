from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.agents.pantry_agent import run_pantry_agent
from app.core.auth import get_current_user
from app.db.dependencies import get_db
from app.models.user import User


class AgentChatRequest(BaseModel):
    message: str


class AgentChatResponse(BaseModel):
    response: str
    tools_used: list[str]


router = APIRouter(
    prefix="/agent",
    tags=["AI Agent"],
)


@router.post("/chat", response_model=AgentChatResponse)
def agent_chat(
    payload: AgentChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not payload.message.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Message cannot be empty",
        )

    try:
        result = run_pantry_agent(
            db=db,
            user_id=current_user.id,
            user_message=payload.message,
        )
        return result
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Agent execution error: {str(exc)}",
        ) from exc
