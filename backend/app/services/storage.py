"""File-based storage service for books and chapters."""
import json
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Optional

DATA_DIR = Path(__file__).parent.parent.parent / "data" / "books"
REPO_ROOT = Path(__file__).parent.parent.parent.parent


def _slugify(text: str) -> str:
    """Convert text to URL-safe slug."""
    return text.lower().replace(" ", "-").replace("_", "-")


def _extract_heading_slug(content: str, fallback_slug: str) -> str:
    """Derive chapter slug from first markdown heading."""
    for line in content.splitlines():
        stripped = line.strip()
        if stripped.startswith("# "):
            heading = stripped[2:].strip()
            if heading:
                return _slugify(heading)
            break
    return fallback_slug


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

    book_meta_path = f"backend/data/books/{slug}/book.json"
    commit_msg = f"Add book {title}"
    git_success = _git_commit_and_push([book_meta_path], commit_msg)

    return {"slug": slug, "title": title, "gitCommitted": git_success}


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


def _run_git(args: list[str]) -> subprocess.CompletedProcess:
    """Run git command in repo root."""
    return subprocess.run(
        ["git", *args],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


def _is_missing_pathspec(stderr: str) -> bool:
    lowered = stderr.lower()
    return "pathspec" in lowered and ("did not match any file" in lowered or "did not match any files" in lowered)


def _git_commit_and_push(paths: list[str], commit_msg: str) -> bool:
    """Stage selected paths, commit (if changed), and push."""
    try:
        for path in paths:
            add_result = _run_git(["add", "-A", "--", path])
            if add_result.returncode != 0:
                err = add_result.stderr.strip()
                if _is_missing_pathspec(err):
                    continue
                print(f"Git add failed: {err}")
                return False

        # Nothing staged means file content didn't change.
        staged_result = _run_git(["diff", "--cached", "--quiet"])
        if staged_result.returncode == 0:
            return True

        commit_result = _run_git(["commit", "-m", commit_msg])
        if commit_result.returncode != 0:
            print(f"Git commit failed: {commit_result.stderr.strip()}")
            return False

        push_result = _run_git(["push"])
        if push_result.returncode != 0:
            print(f"Git push failed: {push_result.stderr.strip()}")
            return False

        return True
    except Exception as e:
        # Log error but don't fail the save
        print(f"Git operation failed: {e}")
        return False


def save_chapter(book_slug: str, chapter_slug: str, content: str) -> dict:
    """Save chapter content and commit to git."""
    chapters_dir = DATA_DIR / book_slug / "chapters"
    chapters_dir.mkdir(parents=True, exist_ok=True)

    old_slug = chapter_slug
    target_slug = _extract_heading_slug(content, chapter_slug)
    target_file = chapters_dir / f"{target_slug}.md"
    old_file = chapters_dir / f"{old_slug}.md"

    # Avoid overwriting another chapter when heading-generated slug collides.
    if target_slug != old_slug and target_file.exists():
        target_slug = old_slug
        target_file = old_file

    chapter_is_new = not old_file.exists() and not target_file.exists()
    did_move = target_slug != old_slug and old_file.exists()

    if did_move:
        old_file.rename(target_file)

    target_file.write_text(content)

    # Update chapter order and metadata.
    book_title = None
    meta_file = DATA_DIR / book_slug / "book.json"
    meta_changed = False
    if meta_file.exists():
        meta = json.loads(meta_file.read_text())
        book_title = meta.get("title", book_slug)
        order = list(meta.get("chapterOrder", []))

        if target_slug != old_slug:
            order = [target_slug if slug == old_slug else slug for slug in order]
            meta_changed = True

        if target_slug not in order:
            order.append(target_slug)
            meta_changed = True

        if meta_changed:
            meta["chapterOrder"] = order
            meta_file.write_text(json.dumps(meta, indent=2))

    renamed = target_slug != old_slug
    action = "Rename" if renamed else ("Add" if chapter_is_new else "Update")
    if renamed:
        commit_msg = f"Rename {book_title or book_slug}/{old_slug} -> {target_slug}"
    else:
        commit_msg = f"{action} {book_title or book_slug}/{target_slug}"

    target_path = f"backend/data/books/{book_slug}/chapters/{target_slug}.md"
    old_path = f"backend/data/books/{book_slug}/chapters/{old_slug}.md"
    meta_path = f"backend/data/books/{book_slug}/book.json"

    # Commit and push chapter + metadata updates, including old path for rename/delete staging.
    commit_paths = [target_path, meta_path]
    if did_move:
        commit_paths.append(old_path)
    git_success = _git_commit_and_push(commit_paths, commit_msg)
    
    return {
        "updatedAt": datetime.utcnow().isoformat() + "Z",
        "gitCommitted": git_success,
        "chapterSlug": target_slug,
        "renamed": renamed,
    }


def create_chapter(book_slug: str, title: str) -> dict:
    """Create a new chapter."""
    slug = _slugify(title)
    content = f"# {title}\n\n"
    result = save_chapter(book_slug, slug, content)
    return {
        "slug": result.get("chapterSlug", slug),
        "gitCommitted": result.get("gitCommitted", False),
    }


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

    meta_path = f"backend/data/books/{book_slug}/book.json"
    chapter_path = f"backend/data/books/{book_slug}/chapters/{chapter_slug}.md"
    _git_commit_and_push(
        [chapter_path, meta_path],
        f"Delete {book_slug}/{chapter_slug}",
    )

    return True


def reorder_chapters(book_slug: str, chapter_order: list[str]) -> bool:
    """Reorder chapters."""
    meta_file = DATA_DIR / book_slug / "book.json"
    if not meta_file.exists():
        return False
    
    meta = json.loads(meta_file.read_text())
    meta["chapterOrder"] = chapter_order
    meta_file.write_text(json.dumps(meta, indent=2))

    meta_path = f"backend/data/books/{book_slug}/book.json"
    _git_commit_and_push(
        [meta_path],
        f"Reorder chapters in {book_slug}",
    )

    return True
