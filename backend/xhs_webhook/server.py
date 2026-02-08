"""Webhook bridge for Xiaohongshu publishing via browser automation."""
from __future__ import annotations

import hashlib
import json
import logging
import os
import re
import threading
import time
from pathlib import Path
from typing import Literal, Optional
from urllib.parse import parse_qs, urlparse

from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel, Field
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
from playwright.sync_api import sync_playwright

APP_TITLE = "ZenApp Xiaohongshu Webhook"

PROFILE_DIR = Path(os.getenv("XHS_PROFILE_DIR", "backend/data/xhs_profile"))
STATE_FILE = Path(os.getenv("XHS_WEBHOOK_STATE_FILE", "backend/data/xhs_webhook/state.json"))

WEBHOOK_TOKEN = os.getenv("XHS_WEBHOOK_TOKEN", "").strip()
HEADLESS = os.getenv("XHS_HEADLESS", "false").strip().lower() in {"1", "true", "yes"}
if not HEADLESS and not os.getenv("DISPLAY", "").strip():
    # Auto-fallback in server environments without X11/Wayland.
    HEADLESS = True
ALLOW_INTERACTIVE_LOGIN = os.getenv("XHS_ALLOW_INTERACTIVE_LOGIN", "true").strip().lower() in {"1", "true", "yes"}
LOGIN_WAIT_SECONDS = int(os.getenv("XHS_LOGIN_WAIT_SECONDS", "180"))
ACTION_TIMEOUT_MS = int(os.getenv("XHS_ACTION_TIMEOUT_MS", "90000"))
WEBHOOK_URL_PUBLIC_BASE = os.getenv("XHS_NOTE_URL_BASE", "https://www.xiaohongshu.com/explore").rstrip("/")

PUBLISH_URL = os.getenv("XHS_PUBLISH_URL", "https://creator.xiaohongshu.com/publish/publish")
EDIT_URL_TEMPLATE = os.getenv("XHS_EDIT_URL_TEMPLATE", "https://creator.xiaohongshu.com/publish/publish?noteId={post_id}")

IMAGE_EXT_RE = re.compile(r"\.(jpg|jpeg|png|webp|gif|heic)$", re.IGNORECASE)
EXPLORE_URL_RE = re.compile(r"https?://www\.xiaohongshu\.com/explore/([0-9a-zA-Z]+)", re.IGNORECASE)
NOTE_URL_RE = re.compile(
    r"https?://www\.xiaohongshu\.com/(?:explore|discovery/item)/([0-9a-zA-Z]+)",
    re.IGNORECASE,
)

TITLE_SELECTORS = [
    "textarea[placeholder*='标题']",
    "input[placeholder*='标题']",
    "input[placeholder*='添加标题']",
    "textarea[placeholder*='添加标题']",
    "input[placeholder*='填写标题']",
    "textarea[placeholder*='填写标题']",
    "div[contenteditable='true'][data-placeholder*='标题']",
]

CONTENT_SELECTORS = [
    ".tiptap.ProseMirror",
    ".ProseMirror[contenteditable='true']",
    "div[contenteditable='true'][data-placeholder*='正文']",
    "div[contenteditable='true'][data-placeholder*='内容']",
    "textarea[placeholder*='正文']",
    "textarea[placeholder*='内容']",
    "div[contenteditable='true'][role='textbox']",
]

UPLOAD_INPUT_SELECTORS = [
    "input.upload-input[type='file']",
    "input[type='file'][accept*='image']",
    "input[type='file']",
]

IMAGE_TAB_SELECTORS = [
    "div.creator-tab:has-text('上传图文')",
    "[role='tab']:has-text('上传图文')",
    "button:has-text('上传图文')",
]

PUBLISH_BUTTON_SELECTORS = [
    "button:has-text('发布')",
    "button:has-text('立即发布')",
    "button:has-text('发布笔记')",
]

UPDATE_BUTTON_SELECTORS = [
    "button:has-text('更新')",
    "button:has-text('保存')",
    "button:has-text('发布')",
]

LOGIN_INDICATOR_SELECTORS = [
    "text=扫码登录",
    "text=登录",
    "input[placeholder*='手机号']",
]


class PublishPayload(BaseModel):
    platform: Literal["xiaohongshu"]
    operation: Literal["create", "update"]
    bookSlug: str
    chapterSlug: str
    postId: Optional[str] = None
    title: str
    content: str
    imageUrls: list[str] = Field(default_factory=list)
    localImagePaths: list[str] = Field(default_factory=list)
    contentHash: str


class PublishResponse(BaseModel):
    postId: str
    postUrl: Optional[str] = None
    status: str
    message: str


class BindRequest(BaseModel):
    bookSlug: str
    chapterSlug: str
    postId: str
    postUrl: Optional[str] = None


app = FastAPI(title=APP_TITLE, version="0.1.0")
PUBLISH_LOCK = threading.Lock()
logger = logging.getLogger("xhs_webhook")


def _is_local_fallback_post_id(post_id: str | None) -> bool:
    return bool(post_id and post_id.startswith("local-"))


def _resolve_remote_post_id(*values: str | None) -> str | None:
    for value in values:
        if value and not _is_local_fallback_post_id(value):
            return value
    return None


def _make_local_post_id(payload: PublishPayload) -> str:
    seed = f"{payload.bookSlug}:{payload.chapterSlug}:{payload.contentHash}"
    return "local-" + hashlib.sha256(seed.encode("utf-8")).hexdigest()[:12]


def _read_state() -> dict:
    if not STATE_FILE.exists():
        return {"posts": {}}
    try:
        return json.loads(STATE_FILE.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {"posts": {}}


def _write_state(state: dict) -> None:
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    STATE_FILE.write_text(json.dumps(state, indent=2, ensure_ascii=False), encoding="utf-8")


def _state_key(payload: PublishPayload) -> str:
    return f"{payload.bookSlug}/{payload.chapterSlug}"


def _is_logged_in(page) -> bool:
    current_url = page.url or ""
    if "creator.xiaohongshu.com" not in current_url:
        return False
    lowered_url = current_url.lower()
    if "login" in lowered_url or "passport" in lowered_url:
        return False

    for selector in LOGIN_INDICATOR_SELECTORS:
        try:
            locator = page.locator(selector).first
            if locator.count() > 0 and locator.is_visible(timeout=300):
                return False
        except Exception:
            continue

    editor_selectors = TITLE_SELECTORS + CONTENT_SELECTORS + UPLOAD_INPUT_SELECTORS
    for selector in editor_selectors:
        try:
            if page.locator(selector).count() > 0:
                return True
        except Exception:
            continue
    return False


def _wait_for_login(page) -> None:
    if _is_logged_in(page):
        return

    if HEADLESS:
        raise RuntimeError(
            "Xiaohongshu login required in webhook profile. "
            "Run `python -m backend.xhs_webhook.login` on a machine with display, then retry."
        )

    if not ALLOW_INTERACTIVE_LOGIN:
        raise RuntimeError(
            "Xiaohongshu login required. Run `python -m backend.xhs_webhook.login` first."
        )

    deadline = time.time() + LOGIN_WAIT_SECONDS
    while time.time() < deadline:
        if _is_logged_in(page):
            return
        page.wait_for_timeout(1000)

    raise RuntimeError(
        f"Login not completed within {LOGIN_WAIT_SECONDS}s. "
        "Please run `python -m backend.xhs_webhook.login` to bootstrap session."
    )


def _goto_operation_page(page, payload: PublishPayload, update_post_id: str | None) -> None:
    if payload.operation == "update" and update_post_id:
        target_url = EDIT_URL_TEMPLATE.format(post_id=update_post_id)
    else:
        target_url = PUBLISH_URL

    page.goto(target_url, wait_until="domcontentloaded", timeout=ACTION_TIMEOUT_MS)
    page.wait_for_timeout(1000)


def _is_in_viewport(page, locator) -> bool:
    box = locator.bounding_box()
    if not box:
        return False
    viewport = page.viewport_size or {"width": 1280, "height": 720}
    return (
        box["width"] > 0
        and box["height"] > 0
        and box["x"] >= 0
        and box["y"] >= 0
        and (box["x"] + box["width"]) <= (viewport["width"] + 2)
        and (box["y"] + box["height"]) <= (viewport["height"] + 2)
    )


def _switch_to_image_post_tab(page) -> None:
    for selector in IMAGE_TAB_SELECTORS:
        locator = page.locator(selector)
        try:
            count = locator.count()
        except Exception:
            continue
        for idx in range(count):
            tab = locator.nth(idx)
            try:
                if not tab.is_visible(timeout=400):
                    continue
                if not _is_in_viewport(page, tab):
                    continue
                tab.click(timeout=5000)
                page.wait_for_timeout(1500)
                return
            except Exception:
                continue

    # If editor fields already exist, treat tab switch as unnecessary.
    for selector in TITLE_SELECTORS + CONTENT_SELECTORS:
        try:
            if page.locator(selector).count() > 0:
                return
        except Exception:
            continue

    raise RuntimeError("Could not switch to image post tab ('上传图文').")


def _wait_for_editor_ready(page) -> None:
    deadline = time.time() + 45
    while time.time() < deadline:
        for selector in TITLE_SELECTORS + CONTENT_SELECTORS:
            locator = page.locator(selector)
            try:
                if locator.count() > 0 and locator.first.is_visible(timeout=300):
                    return
            except Exception:
                continue
        page.wait_for_timeout(500)
    raise RuntimeError(f"Image editor fields did not appear on {page.url}.")


def _fill_with_selectors(page, selectors: list[str], value: str, label: str) -> None:
    for selector in selectors:
        locator = page.locator(selector).first
        try:
            if locator.count() == 0:
                continue
            if not locator.is_visible(timeout=1200):
                continue
            locator.click()
            try:
                locator.fill(value)
                return
            except Exception:
                # Rich-text editor path: clear then insert plain text.
                page.keyboard.press("Control+A")
                page.keyboard.press("Backspace")
                page.keyboard.insert_text(value)
            return
        except Exception:
            continue

    raise RuntimeError(f"Could not find {label} input field on {page.url}.")


def _upload_images(page, local_paths: list[str]) -> None:
    normalized_paths = [str(Path(p)) for p in local_paths if Path(p).exists()]
    if not normalized_paths:
        return

    for selector in UPLOAD_INPUT_SELECTORS:
        locator = page.locator(selector).first
        try:
            if locator.count() == 0:
                continue
            locator.set_input_files(normalized_paths)
            page.wait_for_timeout(2000)
            return
        except Exception:
            continue

    raise RuntimeError("Could not find image upload input on publish page.")


def _click_publish(page, payload: PublishPayload) -> None:
    button_selectors = UPDATE_BUTTON_SELECTORS if payload.operation == "update" else PUBLISH_BUTTON_SELECTORS
    for selector in button_selectors:
        locator = page.locator(selector)
        try:
            count = locator.count()
            for idx in range(count):
                button = locator.nth(idx)
                if not button.is_visible(timeout=500):
                    continue
                disabled = button.get_attribute("disabled")
                aria_disabled = button.get_attribute("aria-disabled")
                if disabled is not None or aria_disabled in {"true", "1"}:
                    continue
                button.click()
                page.wait_for_timeout(5000)
                return
        except Exception:
            continue

    raise RuntimeError("Could not find a clickable publish/update button.")


def _extract_note_id_and_url(page) -> tuple[Optional[str], Optional[str]]:
    current_url = page.url or ""
    parsed = urlparse(current_url)
    qs = parse_qs(parsed.query)
    for key in ("noteId", "note_id", "id"):
        value = qs.get(key, [])
        if value and value[0]:
            note_id = value[0]
            return note_id, f"{WEBHOOK_URL_PUBLIC_BASE}/{note_id}"

    html = page.content()
    match = NOTE_URL_RE.search(html)
    if match:
        note_id = match.group(1)
        return note_id, match.group(0)

    return None, None


def _publish_via_browser(payload: PublishPayload) -> PublishResponse:
    PROFILE_DIR.mkdir(parents=True, exist_ok=True)
    state = _read_state()
    state_key = _state_key(payload)
    state_entry = state.setdefault("posts", {}).get(state_key, {})
    remote_update_post_id = _resolve_remote_post_id(payload.postId, state_entry.get("postId"))

    if payload.operation == "update" and not remote_update_post_id:
        raise RuntimeError(
            "Update requested but remote postId is unavailable. "
            "Please publish once with detectable postId or bind it manually."
        )

    with sync_playwright() as playwright:
        def _launch_context(headless_value: bool):
            return playwright.chromium.launch_persistent_context(
                user_data_dir=str(PROFILE_DIR),
                headless=headless_value,
                args=["--disable-blink-features=AutomationControlled"],
            )

        try:
            browser_context = _launch_context(HEADLESS)
        except Exception as exc:
            message = str(exc).lower()
            if (not HEADLESS) and (
                "missing x server" in message
                or "$display" in message
                or "x11" in message
                or "no authorisation" in message
            ):
                try:
                    browser_context = _launch_context(True)
                except Exception as retry_exc:
                    raise RuntimeError(
                        "Webhook cannot start browser in headed mode and headless fallback also failed."
                    ) from retry_exc
            else:
                if "processsingleton" in message or "singletonlock" in message:
                    raise RuntimeError(
                        "XHS profile is locked by another browser session. "
                        "Close `python -m backend.xhs_webhook.login` (and related Chromium processes), then retry."
                    ) from exc
                if "missing x server" in message or "$display" in message or "x11" in message:
                    raise RuntimeError(
                        "Webhook is running in headed mode without a display server. "
                        "Set XHS_HEADLESS=true and restart the webhook."
                    ) from exc
                raise
        try:
            page = browser_context.pages[0] if browser_context.pages else browser_context.new_page()
            page.set_default_timeout(ACTION_TIMEOUT_MS)
            captured_note_id: str | None = None
            captured_note_url: str | None = None

            def _capture_publish_response(resp) -> None:
                nonlocal captured_note_id, captured_note_url
                if captured_note_id:
                    return
                url = resp.url or ""
                if "edith.xiaohongshu.com" not in url:
                    return
                if "/web_api/sns/v2/note" not in url:
                    return
                logger.info("Observed publish API response: %s (status=%s)", url, resp.status)
                try:
                    body = resp.json()
                except Exception:
                    return
                if not isinstance(body, dict):
                    return

                share_link = body.get("share_link")
                if isinstance(share_link, str) and share_link:
                    match = NOTE_URL_RE.search(share_link)
                    if match:
                        captured_note_id = match.group(1)
                        captured_note_url = match.group(0)

                data = body.get("data")
                if isinstance(data, dict):
                    note_id = data.get("id") or data.get("note_id")
                    if isinstance(note_id, str) and note_id:
                        captured_note_id = note_id
                        if not captured_note_url:
                            captured_note_url = share_link or f"{WEBHOOK_URL_PUBLIC_BASE}/{note_id}"
                        logger.info("Captured note id from publish API: %s", captured_note_id)

            page.on("response", _capture_publish_response)

            _goto_operation_page(page, payload, remote_update_post_id)
            _wait_for_login(page)
            if payload.operation == "create":
                _switch_to_image_post_tab(page)
            _upload_images(page, payload.localImagePaths)
            _wait_for_editor_ready(page)
            _fill_with_selectors(page, TITLE_SELECTORS, payload.title, "title")
            _fill_with_selectors(page, CONTENT_SELECTORS, payload.content, "content")
            _click_publish(page, payload)

            note_id, note_url = _extract_note_id_and_url(page)
            note_id = note_id or captured_note_id
            note_url = note_url or captured_note_url
        except PlaywrightTimeoutError as exc:
            raise RuntimeError(f"Playwright timeout during publish: {exc}") from exc
        finally:
            browser_context.close()

    resolved_post_id = note_id or remote_update_post_id or _make_local_post_id(payload)
    resolved_post_url = note_url or state_entry.get("postUrl")

    status = "published" if note_id else "published_unverified"
    message = (
        "Published and extracted note ID."
        if note_id
        else "Publish action completed but note ID could not be auto-detected. Using fallback postId."
    )

    state["posts"][state_key] = {
        "postId": resolved_post_id,
        "postUrl": resolved_post_url,
        "lastOperation": payload.operation,
        "updatedAt": int(time.time()),
        "lastContentHash": payload.contentHash,
    }
    _write_state(state)

    return PublishResponse(
        postId=resolved_post_id,
        postUrl=resolved_post_url,
        status=status,
        message=message,
    )


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "service": APP_TITLE}


@app.post("/bind")
def bind_post_id(req: BindRequest, x_webhook_token: str | None = Header(default=None)) -> dict:
    if WEBHOOK_TOKEN and x_webhook_token != WEBHOOK_TOKEN:
        raise HTTPException(status_code=401, detail="Invalid webhook token")

    if _is_local_fallback_post_id(req.postId):
        raise HTTPException(status_code=400, detail="postId must be remote id, not local-*")

    state = _read_state()
    key = f"{req.bookSlug}/{req.chapterSlug}"
    previous = state.setdefault("posts", {}).get(key, {})
    state["posts"][key] = {
        **previous,
        "postId": req.postId,
        "postUrl": req.postUrl or previous.get("postUrl"),
        "updatedAt": int(time.time()),
    }
    _write_state(state)
    return {"status": "bound", "key": key, "postId": req.postId, "postUrl": req.postUrl}


@app.post("/publish", response_model=PublishResponse)
def publish(
    payload: PublishPayload,
    x_webhook_token: str | None = Header(default=None),
):
    if payload.platform != "xiaohongshu":
        raise HTTPException(status_code=400, detail="Unsupported platform")

    if WEBHOOK_TOKEN and x_webhook_token != WEBHOOK_TOKEN:
        raise HTTPException(status_code=401, detail="Invalid webhook token")

    usable_local_paths: list[str] = [p for p in payload.localImagePaths if Path(p).exists()]
    if payload.localImagePaths:
        missing = [p for p in payload.localImagePaths if not Path(p).exists()]
        if missing:
            # Do not fail hard when some images are missing; keep best-effort publish.
            usable_local_paths = [p for p in payload.localImagePaths if Path(p).exists()]

    if not usable_local_paths and payload.imageUrls:
        non_image_urls = [u for u in payload.imageUrls if not IMAGE_EXT_RE.search(u)]
        if non_image_urls:
            raise HTTPException(status_code=400, detail=f"Unsupported image URL(s): {non_image_urls}")

    if not PUBLISH_LOCK.acquire(blocking=False):
        raise HTTPException(status_code=409, detail="Another publish task is in progress. Please wait.")

    try:
        payload_dict = payload.model_dump()
        payload_dict["localImagePaths"] = usable_local_paths
        return _publish_via_browser(PublishPayload(**payload_dict))
    except RuntimeError as exc:
        logger.exception("Publish runtime error")
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    except Exception as exc:
        logger.exception("Unexpected webhook failure")
        raise HTTPException(
            status_code=502,
            detail=f"Unexpected webhook failure: {type(exc).__name__}: {exc}",
        ) from exc
    finally:
        PUBLISH_LOCK.release()
