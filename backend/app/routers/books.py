"""Books API router."""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel

from ..services import storage
from ..auth import get_current_user

router = APIRouter(prefix="/api/books", tags=["books"])


class CreateBookRequest(BaseModel):
    title: str
    author: str = ""


@router.get("")
def list_books(user: str = Depends(get_current_user)):
    """List all books."""
    return storage.list_books()


@router.post("")
def create_book(req: CreateBookRequest, user: str = Depends(get_current_user)):
    """Create a new book."""
    return storage.create_book(req.title, req.author)


@router.get("/{slug}")
def get_book(slug: str, user: str = Depends(get_current_user)):
    """Get book details with chapters."""
    book = storage.get_book(slug)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    return book


@router.delete("/{slug}")
def delete_book(slug: str, user: str = Depends(get_current_user)):
    """Delete a book."""
    if not storage.delete_book(slug):
        raise HTTPException(status_code=404, detail="Book not found")
    return {"status": "deleted"}
