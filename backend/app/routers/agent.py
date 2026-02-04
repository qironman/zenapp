"""Agent API router for AI-powered editing."""
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Literal, Optional

from ..services import agent, storage
from ..auth import get_current_user

router = APIRouter(prefix="/api/agent", tags=["agent"])


class AgentSuggestRequest(BaseModel):
    bookSlug: str
    chapterSlug: str
    selectionStart: int
    selectionEnd: int
    prompt: str
    provider: Optional[Literal["anthropic", "openai"]] = "anthropic"
    content: Optional[str] = None  # Optional: use this content instead of fetching from storage


class AgentReviseRequest(BaseModel):
    sessionId: str
    prompt: str  # Additional feedback for revision
    provider: Optional[Literal["anthropic", "openai"]] = "anthropic"


class ApproveEditRequest(BaseModel):
    sessionId: str
    bookSlug: str
    chapterSlug: str


@router.post("/suggest")
async def get_suggestion(req: AgentSuggestRequest, user: str = Depends(get_current_user)):
    """
    Get initial AI edit suggestion for selected text.
    
    Returns Server-Sent Events:
    - event: delta - partial response text
    - event: done - final replacement text
    - event: session - session ID for revision/approval
    - event: error - error message
    """
    # Use provided content if available, otherwise fetch from storage
    if req.content is not None:
        content = req.content
    else:
        chapter = storage.get_chapter(req.bookSlug, req.chapterSlug)
        if not chapter:
            raise HTTPException(status_code=404, detail="Chapter not found")
        content = chapter["content"]
    
    return StreamingResponse(
        agent.get_edit_suggestion(
            content,
            req.selectionStart,
            req.selectionEnd,
            req.prompt,
            req.provider,
        ),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "Connection": "keep-alive"},
    )


@router.post("/revise")
async def revise_suggestion(req: AgentReviseRequest, user: str = Depends(get_current_user)):
    """
    Revise an existing suggestion with additional feedback.
    
    Keeps the same session but generates a new suggestion based on:
    - Original text
    - Previous prompts
    - Current suggestion
    - New revision feedback
    """
    return StreamingResponse(
        agent.revise_suggestion(req.sessionId, req.prompt, req.provider),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "Connection": "keep-alive"},
    )


@router.post("/approve")
async def approve_edit(req: ApproveEditRequest, user: str = Depends(get_current_user)):
    """
    Approve and apply the current suggestion.
    
    The agent saves the edit to the file on the backend.
    """
    new_content = agent.apply_edit(req.sessionId)
    if new_content is None:
        raise HTTPException(status_code=404, detail="Edit session not found or expired")
    
    result = storage.save_chapter(req.bookSlug, req.chapterSlug, new_content)
    
    return {
        "status": "applied",
        "updatedAt": result["updatedAt"],
    }
