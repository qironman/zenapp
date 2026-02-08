# Xiaohongshu Webhook Bridge (Playwright)

This service receives publish payloads from ZenApp and automates Xiaohongshu creator page actions.

## 1. Install Dependencies

Use your backend venv:

```bash
cd backend
source venv/bin/activate
pip install playwright
playwright install chromium
```

## 2. Bootstrap Login Session (one-time / when expired)

```bash
cd /home/ytian/git/zenapp
backend/venv/bin/python -m backend.xhs_webhook.login
```

This opens a browser with persistent profile at `backend/data/xhs_profile`.
Scan QR and finish login on the creator site, then press Enter in terminal.

## 3. Start Webhook Server

```bash
cd /home/ytian/git/zenapp
export XHS_WEBHOOK_TOKEN="replace-with-long-random-secret"
export XHS_HEADLESS=false
backend/venv/bin/uvicorn backend.xhs_webhook.server:app --host 127.0.0.1 --port 9009
```

## 4. Connect ZenApp Backend to Webhook

In another terminal:

```bash
cd /home/ytian/git/zenapp
export XHS_PUBLISH_WEBHOOK="http://127.0.0.1:9009/publish"
export XHS_PUBLISH_WEBHOOK_TOKEN="replace-with-long-random-secret"
export ZENAPP_PUBLIC_BASE_URL="https://your-zenapp-domain"
cd backend
source venv/bin/activate
uvicorn app.main:app --reload --port 8001
```

`ZENAPP_PUBLIC_BASE_URL` must be a URL Xiaohongshu can access to fetch images.

## 5. Use from ZenApp UI

- Open chapter in edit mode
- Save chapter
- Click `📮 Publish 小红书`

First publish runs `create`, subsequent publishes run `update` (same post ID).

## Notes

- If Xiaohongshu asks for captcha/human verification, browser automation may pause/fail.
- Update requires a valid remote `postId`.
- If first publish succeeds but `postId` was not auto-detected, bind it manually:

```bash
curl -X POST "http://127.0.0.1:9009/bind" \
  -H "Content-Type: application/json" \
  -H "X-Webhook-Token: replace-with-long-random-secret" \
  -d '{
    "bookSlug":"老田游记",
    "chapterSlug":"古龙英雄王",
    "postId":"<xhs-note-id>",
    "postUrl":"https://www.xiaohongshu.com/explore/<xhs-note-id>"
  }'
```

- Webhook state is stored at `backend/data/xhs_webhook/state.json`.
