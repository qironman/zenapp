"""Publishing API router."""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from ..auth import get_current_user
from ..services import publisher

router = APIRouter(prefix="/api/publish", tags=["publish"])


class PublishRequest(BaseModel):
    force: bool = False


@router.get("/xiaohongshu/{book_slug}/{chapter_slug}")
def get_xiaohongshu_status(
    book_slug: str,
    chapter_slug: str,
    user: str = Depends(get_current_user),
):
    """Get publish status for a chapter."""
    try:
        return publisher.get_xiaohongshu_status(book_slug, chapter_slug)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/xiaohongshu/{book_slug}/{chapter_slug}")
def publish_chapter_to_xiaohongshu(
    book_slug: str,
    chapter_slug: str,
    req: PublishRequest,
    user: str = Depends(get_current_user),
):
    """Publish chapter as a Xiaohongshu post or update if already published."""
    try:
        return publisher.publish_xiaohongshu(book_slug, chapter_slug, force=req.force)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
