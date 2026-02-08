"""Publishing service for chapter-based social publishing."""
import hashlib
import json
import os
import re
from datetime import datetime
from pathlib import Path
from typing import Any
from urllib import error, parse, request

BOOKS_DIR = Path(__file__).parent.parent.parent / "data" / "books"
STATE_FILE = Path(__file__).parent.parent.parent / "data" / "publish" / "xiaohongshu_state.json"
WEBHOOK_URL = os.getenv("XHS_PUBLISH_WEBHOOK", "").strip()
WEBHOOK_TOKEN = os.getenv("XHS_PUBLISH_WEBHOOK_TOKEN", "").strip()
PUBLIC_BASE_URL = os.getenv("ZENAPP_PUBLIC_BASE_URL", "http://localhost:8001").rstrip("/")

MARKDOWN_IMAGE_RE = re.compile(r"!\[[^\]]*]\(([^)]+)\)")
HTML_IMAGE_RE = re.compile(r"<img[^>]+src=['\"]([^'\"]+)['\"]", re.IGNORECASE)
IMAGE_ONLY_LINE_RE = re.compile(r"^!\[[^\]]*]\([^)]+\)\s*$")
IMAGE_EXT_RE = re.compile(r"\.(jpg|jpeg|png|webp|gif|heic)$", re.IGNORECASE)


def _utc_now() -> str:
    return datetime.utcnow().isoformat() + "Z"


def _is_remote_post_id(post_id: str | None) -> bool:
    return bool(post_id) and (not str(post_id).startswith("local-"))


def _ensure_safe_path(base_dir: Path, child_path: Path) -> Path:
    base_resolved = base_dir.resolve()
    child_resolved = child_path.resolve()
    try:
        child_resolved.relative_to(base_resolved)
    except ValueError as exc:
        raise ValueError("Invalid path") from exc
    return child_resolved


def _chapter_file(book_slug: str, chapter_slug: str) -> Path:
    chapters_dir = BOOKS_DIR / book_slug / "chapters"
    file_path = chapters_dir / f"{chapter_slug}.md"
    return _ensure_safe_path(chapters_dir, file_path)


def _load_state() -> dict[str, Any]:
    if not STATE_FILE.exists():
        return {"posts": {}}
    try:
        raw = json.loads(STATE_FILE.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {"posts": {}}
    posts = raw.get("posts", {})
    if not isinstance(posts, dict):
        posts = {}
    return {"posts": posts}


def _save_state(state: dict[str, Any]) -> None:
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    STATE_FILE.write_text(json.dumps(state, indent=2, ensure_ascii=False), encoding="utf-8")


def _chapter_key(book_slug: str, chapter_slug: str) -> str:
    return f"{book_slug}/{chapter_slug}"


def _normalize_markdown_url(url: str) -> str:
    cleaned = url.strip()
    if cleaned.startswith("<") and cleaned.endswith(">"):
        cleaned = cleaned[1:-1].strip()
    if ' "' in cleaned:
        cleaned = cleaned.split(' "', 1)[0]
    if " '" in cleaned:
        cleaned = cleaned.split(" '", 1)[0]
    return cleaned.strip()


def _extract_image_refs(content: str) -> list[str]:
    refs: list[str] = []
    seen = set()

    for match in MARKDOWN_IMAGE_RE.finditer(content):
        ref = _normalize_markdown_url(match.group(1))
        if ref and ref not in seen:
            seen.add(ref)
            refs.append(ref)

    for match in HTML_IMAGE_RE.finditer(content):
        ref = match.group(1).strip()
        if ref and ref not in seen:
            seen.add(ref)
            refs.append(ref)

    return refs


def _image_ref_to_public_url(book_slug: str, image_ref: str) -> str:
    if image_ref.startswith(("http://", "https://")):
        return image_ref

    if image_ref.startswith("/"):
        return f"{PUBLIC_BASE_URL}{image_ref}"

    if image_ref.startswith("./"):
        image_ref = image_ref[2:]

    if image_ref.startswith("api/"):
        return f"{PUBLIC_BASE_URL}/{image_ref}"

    if "/" not in image_ref and IMAGE_EXT_RE.search(image_ref):
        return f"{PUBLIC_BASE_URL}/api/books/{book_slug}/images/{image_ref}"

    return f"{PUBLIC_BASE_URL}/{image_ref.lstrip('/')}"


def _image_ref_to_local_path(book_slug: str, image_ref: str) -> str | None:
    parsed = parse.urlparse(image_ref)
    path = parsed.path if parsed.scheme else image_ref

    if not path.startswith("/api/books/"):
        return None

    parts = path.split("/")
    # ['', 'api', 'books', '{book}', 'images', '{filename}']
    if len(parts) < 6 or parts[4] != "images":
        return None

    ref_book = parts[3]
    filename = parts[5]
    if ref_book != book_slug:
        return None

    images_dir = BOOKS_DIR / book_slug / "images"
    local_path = _ensure_safe_path(images_dir, images_dir / filename)
    if not local_path.exists():
        return None
    return str(local_path)


def _extract_title_and_body(content: str, chapter_slug: str) -> tuple[str, str]:
    title = chapter_slug
    body_lines: list[str] = []
    title_found = False

    for line in content.splitlines():
        stripped = line.strip()
        if not title_found and stripped.startswith("# "):
            maybe_title = stripped[2:].strip()
            title = maybe_title or chapter_slug
            title_found = True
            continue

        if IMAGE_ONLY_LINE_RE.match(stripped):
            continue
        if stripped.lower().startswith("<img "):
            continue

        if stripped.startswith("#"):
            body_lines.append(re.sub(r"^#+\s*", "", stripped))
        else:
            body_lines.append(line)

    body = "\n".join(body_lines).strip()
    return title, body


def _build_chapter_payload(book_slug: str, chapter_slug: str) -> dict[str, Any]:
    chapter_path = _chapter_file(book_slug, chapter_slug)
    if not chapter_path.exists():
        raise FileNotFoundError("Chapter not found")

    content = chapter_path.read_text(encoding="utf-8")
    title, body = _extract_title_and_body(content, chapter_slug)
    image_refs = _extract_image_refs(content)
    image_urls = [_image_ref_to_public_url(book_slug, ref) for ref in image_refs]
    local_image_paths = [path for path in (_image_ref_to_local_path(book_slug, ref) for ref in image_refs) if path]

    hash_input = json.dumps(
        {"title": title, "content": body, "images": image_urls},
        ensure_ascii=False,
        sort_keys=True,
    )
    content_hash = hashlib.sha256(hash_input.encode("utf-8")).hexdigest()

    return {
        "title": title,
        "content": body,
        "imageUrls": image_urls,
        "localImagePaths": local_image_paths,
        "contentHash": content_hash,
    }


def _post_webhook(payload: dict[str, Any]) -> dict[str, Any]:
    data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    headers = {"Content-Type": "application/json"}
    if WEBHOOK_TOKEN:
        headers["X-Webhook-Token"] = WEBHOOK_TOKEN

    req = request.Request(
        WEBHOOK_URL,
        data=data,
        headers=headers,
        method="POST",
    )
    try:
        with request.urlopen(req, timeout=120) as resp:
            body = resp.read().decode("utf-8", errors="ignore").strip()
            if not body:
                return {}
            parsed = json.loads(body)
            if isinstance(parsed, dict):
                return parsed
            return {}
    except error.HTTPError as exc:
        detail = f"{exc.code} {exc.reason}"
        try:
            error_body = exc.read().decode("utf-8", errors="ignore").strip()
            if error_body:
                detail = f"{detail}: {error_body}"
        except Exception:
            pass
        raise RuntimeError(f"Failed to publish via webhook: {detail}") from exc
    except (error.URLError, TimeoutError, json.JSONDecodeError) as exc:
        raise RuntimeError(f"Failed to publish via webhook: {exc}") from exc


def get_xiaohongshu_status(book_slug: str, chapter_slug: str) -> dict[str, Any]:
    payload = _build_chapter_payload(book_slug, chapter_slug)
    state = _load_state()
    key = _chapter_key(book_slug, chapter_slug)
    entry = state["posts"].get(key, {})

    post_id = entry.get("postId")
    published = _is_remote_post_id(post_id)
    needs_update = (not published) or (entry.get("contentHash") != payload["contentHash"])

    return {
        "platform": "xiaohongshu",
        "bookSlug": book_slug,
        "chapterSlug": chapter_slug,
        "published": published,
        "needsUpdate": needs_update,
        "postId": post_id,
        "postUrl": entry.get("postUrl"),
        "lastPublishedAt": entry.get("lastPublishedAt"),
        "lastOperation": entry.get("lastOperation"),
        "status": entry.get("status", "never_published"),
        "webhookConfigured": bool(WEBHOOK_URL),
        "preview": {
            "title": payload["title"],
            "content": payload["content"],
            "imageCount": len(payload["imageUrls"]),
            "imageUrls": payload["imageUrls"],
        },
    }


def publish_xiaohongshu(book_slug: str, chapter_slug: str, force: bool = False) -> dict[str, Any]:
    payload = _build_chapter_payload(book_slug, chapter_slug)
    state = _load_state()
    key = _chapter_key(book_slug, chapter_slug)
    previous = state["posts"].get(key, {})

    previous_post_id = previous.get("postId")
    remote_post_id = previous_post_id if _is_remote_post_id(previous_post_id) else None
    has_changes = previous.get("contentHash") != payload["contentHash"]
    operation = "update" if remote_post_id else "create"

    if remote_post_id and not has_changes and not force:
        status = get_xiaohongshu_status(book_slug, chapter_slug)
        status["message"] = "No content changes since last publish."
        return status

    webhook_payload = {
        "platform": "xiaohongshu",
        "operation": operation,
        "bookSlug": book_slug,
        "chapterSlug": chapter_slug,
        "postId": remote_post_id,
        "title": payload["title"],
        "content": payload["content"],
        "imageUrls": payload["imageUrls"],
        "localImagePaths": payload["localImagePaths"],
        "contentHash": payload["contentHash"],
    }

    remote_status = "prepared"
    post_url = previous.get("postUrl")
    message = "Prepared publish payload. Set XHS_PUBLISH_WEBHOOK for real auto-publish."
    post_id = remote_post_id or f"local-{payload['contentHash'][:12]}"

    if WEBHOOK_URL:
        remote = _post_webhook(webhook_payload)
        post_id = str(remote.get("postId") or post_id)
        post_url = remote.get("postUrl") or post_url
        remote_status = str(remote.get("status") or "published")
        message = str(remote.get("message") or "Published via webhook.")

    now = _utc_now()
    state["posts"][key] = {
        "postId": post_id,
        "postUrl": post_url,
        "contentHash": payload["contentHash"],
        "lastPublishedAt": now,
        "lastOperation": operation,
        "status": remote_status,
    }
    _save_state(state)

    result = get_xiaohongshu_status(book_slug, chapter_slug)
    result["operation"] = operation
    result["message"] = message
    return result
