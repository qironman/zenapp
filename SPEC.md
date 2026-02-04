# ZenApp — Mobile-First Markdown Book Editor with AI Agent

## 1. Overview

A **mobile-first PWA** for writing books in Markdown with AI-powered editing assistance. The **agent is the writer**; the **user is the director**.

### Tech Stack
- **Frontend**: React + Vite + TypeScript + CodeMirror 6
- **Backend**: Python + FastAPI
- **Storage**: File-based (`data/books/{book-slug}/chapters/*.md`)
- **Agent**: Multi-provider (OpenAI, Anthropic) via LiteLLM

### Core Concept
- User **views and selects** text (read-only editor)
- User **directs** the AI with prompts
- Agent **suggests** edits (streaming)
- User **revises** or **approves**
- Agent **saves** approved edits to file

---

## 2. Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Mobile Browser                        │
│  ┌─────────────────┐  ┌─────────────────────────────┐   │
│  │   React App     │  │       IndexedDB             │   │
│  │  - CodeMirror 6 │  │  - content cache (offline)  │   │
│  │  - Book picker  │  │                             │   │
│  │  - Agent panel  │  └─────────────────────────────┘   │
│  └────────┬────────┘                                    │
└───────────┼─────────────────────────────────────────────┘
            │ REST API + SSE
            ▼
┌─────────────────────────────────────────────────────────┐
│                   FastAPI Backend                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐   │
│  │ Books API    │  │ Agent API    │  │  File Store  │   │
│  │ Chapters API │  │ (LiteLLM)    │  │  data/books/ │   │
│  └──────────────┘  └──────────────┘  └──────────────┘   │
└─────────────────────────────────────────────────────────┘
```

---

## 3. User Flow

```
┌─────────────────────────────────────────────────────────┐
│  1. Select Book    →  2. Select Chapter  →  3. View     │
└─────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────┐
│  4. Select Text  →  5. Enter Prompt  →  6. "Suggest"    │
└─────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────┐
│                   7. View Suggestion                     │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐    │
│  │ Approve │  │ Revise  │  │ Discard │  │  Close  │    │
│  │ & Save  │  │         │  │         │  │         │    │
│  └────┬────┘  └────┬────┘  └────┬────┘  └────┬────┘    │
│       ↓            ↓            ↓            ↓          │
│    Save to     New prompt    Clear &      Close        │
│    file &      → revised     start        panel        │
│    reload      suggestion    fresh                     │
└─────────────────────────────────────────────────────────┘
```

---

## 4. Data Model

### File Structure
```
data/books/
├── my-novel/
│   ├── book.json
│   └── chapters/
│       ├── 01-introduction.md
│       └── 02-getting-started.md
└── another-book/
    ├── book.json
    └── chapters/
        └── 01-chapter-one.md
```

### book.json
```json
{
  "title": "My Novel",
  "author": "Author Name",
  "createdAt": "2024-01-15T10:00:00Z",
  "chapterOrder": ["01-introduction", "02-getting-started"]
}
```

---

## 5. API Endpoints

### Books
```
GET    /api/books                    → [{ slug, title }]
POST   /api/books                    → { slug, title }
GET    /api/books/{slug}             → { slug, title, chapters }
DELETE /api/books/{slug}             → 204
```

### Chapters
```
GET    /api/books/{book}/chapters/{chapter}   → { content, updatedAt }
PUT    /api/books/{book}/chapters/{chapter}   → { updatedAt }
POST   /api/books/{book}/chapters             → { slug }
DELETE /api/books/{book}/chapters/{chapter}   → 204
```

### Agent
```
POST /api/agent/suggest
Request: {
  "bookSlug": "my-novel",
  "chapterSlug": "01-introduction",
  "selectionStart": 100,
  "selectionEnd": 250,
  "prompt": "make this more concise"
}
Response: SSE stream
  event: delta    → { "text": "partial..." }
  event: done     → { "replacement": "full text" }
  event: session  → { "sessionId": "uuid" }

POST /api/agent/revise
Request: { "sessionId": "uuid", "prompt": "make it shorter" }
Response: SSE stream (same format)

POST /api/agent/approve
Request: { "sessionId": "uuid", "bookSlug": "...", "chapterSlug": "..." }
Response: { "status": "applied", "updatedAt": "..." }
→ Saves edit to file
```

---

## 6. Agent Session

The backend maintains **pending edit sessions** in memory:

```python
class PendingEdit:
    original_content: str      # Full chapter content
    selection_start: int       # Selection range
    selection_end: int
    original_text: str         # Selected text
    current_suggestion: str    # Latest suggestion
    prompt_history: list[str]  # All prompts for context
```

- **suggest**: Creates new session with initial suggestion
- **revise**: Updates session with refined suggestion (uses prompt history)
- **approve**: Applies `current_suggestion` to file, clears session
- **discard**: Client clears UI state (session expires on backend)

---

## 7. Project Structure

```
zenapp/
├── backend/
│   ├── pyproject.toml
│   ├── app/
│   │   ├── main.py              # FastAPI entry
│   │   ├── routers/
│   │   │   ├── books.py         # Book CRUD
│   │   │   ├── chapters.py      # Chapter CRUD
│   │   │   └── agent.py         # suggest/revise/approve
│   │   └── services/
│   │       ├── storage.py       # File operations
│   │       └── agent.py         # LLM + session management
│   └── data/books/              # Markdown storage
├── frontend/
│   ├── package.json
│   ├── src/
│   │   ├── App.tsx              # Main app
│   │   ├── App.css              # Styles
│   │   ├── components/
│   │   │   ├── BookPicker.tsx   # Book dropdown
│   │   │   ├── ChapterList.tsx  # Chapter sidebar
│   │   │   ├── Editor.tsx       # CodeMirror (read-only)
│   │   │   └── AgentPanel.tsx   # Prompt + suggestion UI
│   │   ├── hooks/
│   │   │   ├── useBooks.ts      # Fetch books
│   │   │   ├── useChapter.ts    # Fetch chapter
│   │   │   └── useAgent.ts      # Agent interactions
│   │   └── lib/
│   │       └── api.ts           # API client
│   └── vite.config.ts
├── SPEC.md
├── README.md
└── Makefile
```

---

## 8. Development

```bash
# Install
cd backend && python -m venv venv && source venv/bin/activate && pip install -e ".[dev]"
cd frontend && npm install

# Run
cd backend && source venv/bin/activate && uvicorn app.main:app --reload --port 8000
cd frontend && npm run dev

# Or use Makefile
make install
make dev
```

### Environment Variables
```bash
ANTHROPIC_API_KEY=sk-ant-...   # For Claude
OPENAI_API_KEY=sk-...          # For GPT-4o
```

Without keys, agent returns mock responses.

---

## 9. Mobile UX

- **Full-screen editor** by default
- **Swipe right** → chapter sidebar
- **Select text** → floating "✨ AI Edit" button appears
- **Bottom sheet** → agent prompt/suggestion panel
- **Touch-optimized** controls

---

## 10. Future Enhancements

- [ ] PWA manifest for installable app
- [ ] Git integration for version history
- [ ] Multiple LLM provider selection in UI
- [ ] Offline queue for agent requests
- [ ] Chapter reordering drag-and-drop
- [ ] Export to PDF/EPUB
