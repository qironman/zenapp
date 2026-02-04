"""Chapters API router."""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List

from ..services import storage
from ..auth import get_current_user

router = APIRouter(prefix="/api/books/{book_slug}/chapters", tags=["chapters"])


class SaveChapterRequest(BaseModel):
    content: str


class CreateChapterRequest(BaseModel):
    title: str


class ReorderChaptersRequest(BaseModel):
    order: List[str]


@router.get("/{chapter_slug}")
def get_chapter(book_slug: str, chapter_slug: str, user: str = Depends(get_current_user)):
    """Get chapter content."""
    chapter = storage.get_chapter(book_slug, chapter_slug)
    if not chapter:
        raise HTTPException(status_code=404, detail="Chapter not found")
    return chapter


@router.put("/{chapter_slug}")
def save_chapter(book_slug: str, chapter_slug: str, req: SaveChapterRequest, user: str = Depends(get_current_user)):
    """Save chapter content."""
    return storage.save_chapter(book_slug, chapter_slug, req.content)


@router.post("")
def create_chapter(book_slug: str, req: CreateChapterRequest, user: str = Depends(get_current_user)):
    """Create a new chapter."""
    return storage.create_chapter(book_slug, req.title)


@router.delete("/{chapter_slug}")
def delete_chapter(book_slug: str, chapter_slug: str, user: str = Depends(get_current_user)):
    """Delete a chapter."""
    if not storage.delete_chapter(book_slug, chapter_slug):
        raise HTTPException(status_code=404, detail="Chapter not found")
    return {"status": "deleted"}


@router.patch("/reorder")
def reorder_chapters(book_slug: str, req: ReorderChaptersRequest, user: str = Depends(get_current_user)):
    """Reorder chapters."""
    if not storage.reorder_chapters(book_slug, req.order):
        raise HTTPException(status_code=404, detail="Book not found")
    return {"status": "reordered"}
