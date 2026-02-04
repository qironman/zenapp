# ZenApp - Mobile-First Markdown Book Editor with AI Agent

A PWA for writing books in Markdown where **AI is the writer** and **you are the director**.

## Quick Start

```bash
# Install
cd backend && python -m venv venv && source venv/bin/activate && pip install -e ".[dev]"
cd frontend && npm install

# Run backend (terminal 1)
cd backend && source venv/bin/activate && uvicorn app.main:app --reload --port 8001

# Run frontend (terminal 2)
cd frontend && npm run dev
```

Open **http://localhost:5173** on your phone or desktop browser.

## How It Works

1. **Select** a book and chapter
2. **Select text** you want to improve
3. **Tap "✨ AI Edit"** and describe what you want
4. **Review** the AI suggestion
5. **Revise** (give more feedback) or **Approve & Save**

The AI edits the actual markdown files on the backend - you just direct it.

## Project Structure

```
zenapp/
├── backend/           # FastAPI + LiteLLM
│   ├── app/
│   │   ├── routers/   # API endpoints
│   │   └── services/  # Business logic
│   └── data/books/    # Markdown storage
├── frontend/          # React + Vite + CodeMirror
│   └── src/
│       ├── components/
│       └── hooks/
├── SPEC.md            # Full specification
└── Makefile
```

## API Endpoints

- `GET /api/books` - List books
- `GET /api/books/{slug}` - Get book with chapters
- `GET /api/books/{book}/chapters/{chapter}` - Get chapter content
- `POST /api/agent/suggest` - Get AI edit suggestion (SSE)
- `POST /api/agent/revise` - Refine suggestion with feedback (SSE)
- `POST /api/agent/approve` - Save the edit to file

## Environment Variables

```bash
ANTHROPIC_API_KEY=sk-ant-...   # For Claude
OPENAI_API_KEY=sk-...          # For GPT-4o
```

Without API keys, the agent returns mock responses for testing.

## Features

- �� Mobile-first responsive design
- ✨ AI-powered text editing with streaming
- 📖 Book/chapter organization
- 🔄 Iterative refinement (suggest → revise → approve)
- 💾 Automatic file saving on approve
