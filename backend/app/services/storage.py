"""File-based storage service for books and chapters."""
import json
import os
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Optional

DATA_DIR = Path(__file__).parent.parent.parent / "data" / "books"
REPO_ROOT = Path(__file__).parent.parent.parent.parent


def _slugify(text: str) -> str:
    """Convert text to URL-safe slug."""
    return text.lower().replace(" ", "-").replace("_", "-")


def ensure_data_dir():
    """Ensure the data directory exists."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)


# --- Books ---

def list_books() -> list[dict]:
    """List all books."""
    ensure_data_dir()
    books = []
    for book_dir in DATA_DIR.iterdir():
        if book_dir.is_dir():
            meta_file = book_dir / "book.json"
            if meta_file.exists():
                meta = json.loads(meta_file.read_text())
                books.append({"slug": book_dir.name, "title": meta.get("title", book_dir.name)})
    return books


def get_book(slug: str) -> Optional[dict]:
    """Get book metadata and chapters."""
    book_dir = DATA_DIR / slug
    meta_file = book_dir / "book.json"
    if not meta_file.exists():
        return None
    
    meta = json.loads(meta_file.read_text())
    chapters_dir = book_dir / "chapters"
    
    chapters = []
    chapter_order = meta.get("chapterOrder", [])
    
    # Add chapters in order
    for ch_slug in chapter_order:
        ch_file = chapters_dir / f"{ch_slug}.md"
        if ch_file.exists():
            # Extract title from first heading or use slug
            content = ch_file.read_text()
            title = ch_slug
            for line in content.split("\n"):
                if line.startswith("# "):
                    title = line[2:].strip()
                    break
            chapters.append({"slug": ch_slug, "title": title})
    
    # Add any chapters not in order
    if chapters_dir.exists():
        for ch_file in chapters_dir.glob("*.md"):
            ch_slug = ch_file.stem
            if ch_slug not in chapter_order:
                content = ch_file.read_text()
                title = ch_slug
                for line in content.split("\n"):
                    if line.startswith("# "):
                        title = line[2:].strip()
                        break
                chapters.append({"slug": ch_slug, "title": title})
    
    return {
        "slug": slug,
        "title": meta.get("title", slug),
        "author": meta.get("author"),
        "chapters": chapters,
    }


def create_book(title: str, author: str = "") -> dict:
    """Create a new book."""
    ensure_data_dir()
    slug = _slugify(title)
    book_dir = DATA_DIR / slug
    book_dir.mkdir(exist_ok=True)
    (book_dir / "chapters").mkdir(exist_ok=True)
    
    meta = {
        "title": title,
        "author": author,
        "createdAt": datetime.utcnow().isoformat() + "Z",
        "chapterOrder": [],
    }
    (book_dir / "book.json").write_text(json.dumps(meta, indent=2))
    return {"slug": slug, "title": title}


def delete_book(slug: str) -> bool:
    """Delete a book and all its chapters."""
    import shutil
    book_dir = DATA_DIR / slug
    if not book_dir.exists():
        return False
    shutil.rmtree(book_dir)
    return True


# --- Chapters ---

def get_chapter(book_slug: str, chapter_slug: str) -> Optional[dict]:
    """Get chapter content."""
    ch_file = DATA_DIR / book_slug / "chapters" / f"{chapter_slug}.md"
    if not ch_file.exists():
        return None
    
    stat = ch_file.stat()
    return {
        "content": ch_file.read_text(),
        "updatedAt": datetime.fromtimestamp(stat.st_mtime).isoformat() + "Z",
    }


def _git_commit_and_push(book_slug: str, chapter_slug: str, book_title: str = None):
    """Commit and push chapter changes to git."""
    try:
        # Get book title for better commit message
        if not book_title:
            meta_file = DATA_DIR / book_slug / "book.json"
            if meta_file.exists():
                meta = json.loads(meta_file.read_text())
                book_title = meta.get("title", book_slug)
            else:
                book_title = book_slug
        
        # Relative path from repo root
        ch_file_rel = f"backend/data/books/{book_slug}/chapters/{chapter_slug}.md"
        
        # Git add
        subprocess.run(
            ["git", "add", ch_file_rel],
            cwd=REPO_ROOT,
            check=True,
            capture_output=True,
        )
        
        # Git commit with descriptive message
        commit_msg = f"Update {book_title}/{chapter_slug}"
        subprocess.run(
            ["git", "commit", "-m", commit_msg],
            cwd=REPO_ROOT,
            check=True,
            capture_output=True,
        )
        
        # Git push
        subprocess.run(
            ["git", "push"],
            cwd=REPO_ROOT,
            check=True,
            capture_output=True,
        )
        
        return True
    except subprocess.CalledProcessError as e:
        # Log error but don't fail the save
        print(f"Git operation failed: {e}")
        return False


def save_chapter(book_slug: str, chapter_slug: str, content: str) -> dict:
    """Save chapter content and commit to git."""
    chapters_dir = DATA_DIR / book_slug / "chapters"
    chapters_dir.mkdir(parents=True, exist_ok=True)
    
    ch_file = chapters_dir / f"{chapter_slug}.md"
    ch_file.write_text(content)
    
    # Update chapter order if new
    book_title = None
    meta_file = DATA_DIR / book_slug / "book.json"
    if meta_file.exists():
        meta = json.loads(meta_file.read_text())
        book_title = meta.get("title", book_slug)
        if chapter_slug not in meta.get("chapterOrder", []):
            meta.setdefault("chapterOrder", []).append(chapter_slug)
            meta_file.write_text(json.dumps(meta, indent=2))
    
    # Commit and push to git
    git_success = _git_commit_and_push(book_slug, chapter_slug, book_title)
    
    return {
        "updatedAt": datetime.utcnow().isoformat() + "Z",
        "gitCommitted": git_success,
    }


def create_chapter(book_slug: str, title: str) -> dict:
    """Create a new chapter."""
    slug = _slugify(title)
    content = f"# {title}\n\n"
    save_chapter(book_slug, slug, content)
    return {"slug": slug}


def delete_chapter(book_slug: str, chapter_slug: str) -> bool:
    """Delete a chapter."""
    ch_file = DATA_DIR / book_slug / "chapters" / f"{chapter_slug}.md"
    if not ch_file.exists():
        return False
    ch_file.unlink()
    
    # Remove from order
    meta_file = DATA_DIR / book_slug / "book.json"
    if meta_file.exists():
        meta = json.loads(meta_file.read_text())
        if chapter_slug in meta.get("chapterOrder", []):
            meta["chapterOrder"].remove(chapter_slug)
            meta_file.write_text(json.dumps(meta, indent=2))
    
    return True


def reorder_chapters(book_slug: str, chapter_order: list[str]) -> bool:
    """Reorder chapters."""
    meta_file = DATA_DIR / book_slug / "book.json"
    if not meta_file.exists():
        return False
    
    meta = json.loads(meta_file.read_text())
    meta["chapterOrder"] = chapter_order
    meta_file.write_text(json.dumps(meta, indent=2))
    return True
