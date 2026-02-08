# Xiaohongshu Publishing

ZenApp now supports chapter-based Xiaohongshu publishing with update semantics:

- First publish of a chapter: `create`
- Publish again after edits: `update` (same post mapping)
- Publish again with no changes: returns `No content changes since last publish.`

## How It Works

- Source of truth: each chapter markdown file (`backend/data/books/{book}/chapters/{chapter}.md`)
- Images: markdown image refs are extracted and sent as URLs
- Mapping store: `backend/data/publish/xiaohongshu_state.json`
  - Keeps `book/chapter -> postId/postUrl/contentHash/lastPublishedAt`

## API

- `GET /api/publish/xiaohongshu/{bookSlug}/{chapterSlug}`
  - Returns publish status and whether an update is needed.
- `POST /api/publish/xiaohongshu/{bookSlug}/{chapterSlug}`
  - Body: `{ "force": false }`
  - Creates first post mapping or updates existing mapping.

## Frontend

In edit mode, use the floating `📮 Publish 小红书` button:

- If not published yet: `Publish 小红书`
- If published and changed: `Update 小红书`
- If published and unchanged: `Re-publish 小红书`

You must save chapter changes first before publishing.

## Real Auto-Publish Integration (Webhook)

Set environment variables for backend:

```bash
export XHS_PUBLISH_WEBHOOK="https://your-automation-endpoint/publish"
export XHS_PUBLISH_WEBHOOK_TOKEN="same-secret-as-webhook"
export ZENAPP_PUBLIC_BASE_URL="https://your-zenapp-domain"
```

ZenApp sends JSON payload:

```json
{
  "platform": "xiaohongshu",
  "operation": "create|update",
  "bookSlug": "...",
  "chapterSlug": "...",
  "postId": "...",
  "title": "...",
  "content": "...",
  "imageUrls": ["..."],
  "localImagePaths": ["..."],
  "contentHash": "..."
}
```

## Local Playwright Bridge

A runnable webhook bridge is included at:

- `backend/xhs_webhook/server.py`
- Setup guide: `backend/xhs_webhook/README.md`

It automates Xiaohongshu creator UI using a persistent login profile.

Your webhook should return:

```json
{
  "postId": "xhs-note-id",
  "postUrl": "https://www.xiaohongshu.com/explore/...",
  "status": "published",
  "message": "ok"
}
```
