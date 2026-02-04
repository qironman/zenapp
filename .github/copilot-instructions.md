# Copilot Instructions for ZenApp

## Overview

Mobile-first markdown book editor where **AI is the writer, user is the director**.

## Tech Stack

- **Frontend**: React + Vite + TypeScript + CodeMirror 6
- **Backend**: Python + FastAPI + LiteLLM
- **Storage**: File-based (`data/books/{book-slug}/chapters/*.md`)

## Commands

```bash
# Backend
cd backend && source venv/bin/activate
uvicorn app.main:app --reload --port 8001

# Frontend
cd frontend && npm run dev
```

## Core Workflow

1. User **selects text** (read-only editor)
2. User **enters prompt** → `POST /api/agent/suggest`
3. Agent **streams suggestion** (SSE: delta → done → session)
4. User can:
   - **Revise**: `POST /api/agent/revise` with more feedback
   - **Approve**: `POST /api/agent/approve` → saves to file
   - **Discard**: clears UI state, start fresh

## API

```
POST /api/agent/suggest   { bookSlug, chapterSlug, selectionStart, selectionEnd, prompt }
POST /api/agent/revise    { sessionId, prompt }
POST /api/agent/approve   { sessionId, bookSlug, chapterSlug }
```

## Key Files

```
backend/app/services/agent.py    # LLM + session management
backend/app/services/storage.py  # File CRUD
backend/app/routers/agent.py     # Agent endpoints
frontend/src/hooks/useAgent.ts   # Agent hook
frontend/src/components/AgentPanel.tsx  # UI
```

## Session State

Backend keeps `PendingEdit` in memory:
- `original_content`, `selection_start/end`
- `current_suggestion`, `prompt_history`

Revisions build on prompt history for better context.

## Environment

```bash
ANTHROPIC_API_KEY=...  # Claude
OPENAI_API_KEY=...     # GPT-4o
```

Without keys → mock responses for testing.
