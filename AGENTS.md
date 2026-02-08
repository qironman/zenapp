# Repository Guidelines

## Project Structure & Module Organization
- `backend/app/`: FastAPI backend (`main.py`, `routers/`, `services/`, `auth.py`).
- `backend/data/books/`: file-based content store (`book.json`, `chapters/*.md`, optional `images/`).
- `frontend/src/`: React + TypeScript app (`components/`, `hooks/`, `lib/`, `types.ts`).
- `frontend/dist/`: built frontend assets served by backend in production mode.
- `Makefile`: convenience targets for local development.

## Build, Test, and Development Commands
- Install deps:
  - `make install`
  - Or manually: `cd backend && pip install -e ".[dev]"`, `cd frontend && npm install`
- Run backend (recommended with frontend proxy): `cd backend && uvicorn app.main:app --reload --port 8001`
- Run frontend: `cd frontend && npm run dev` (Vite on `5173`, proxies `/api` to `8001`).
- Build frontend: `cd frontend && npm run build`
- Run both via Make: `make dev` (note: current `make backend` uses port `8000`).
- Clean artifacts: `make clean`

## Coding Style & Naming Conventions
- Python: follow PEP 8, 4-space indentation, snake_case for functions/variables, type hints where practical.
- TypeScript/React: follow existing style (2-space indentation, semicolons, single quotes, functional components + hooks).
- Naming:
  - Components: `PascalCase` (e.g., `AgentPanel.tsx`)
  - Hooks/utils: `camelCase` file names prefixed by intent (e.g., `useAgent.ts`, `retry.ts`)
- No repo-wide formatter/linter is currently configured; keep changes consistent with nearby code.

## Testing Guidelines
- Backend test stack is available via `pytest` + `pytest-asyncio` + `httpx`.
- Add backend tests under `backend/tests/` with `test_*.py` naming.
- Run tests: `cd backend && pytest`
- Frontend currently has no configured automated test runner; at minimum run `npm run build` and validate key flows manually.

## Commit & Pull Request Guidelines
- Follow existing commit style: short, imperative subjects (e.g., `Fix ...`, `Add ...`, `Update ...`).
- Keep one logical change per commit; include context in body when behavior changes.
- PRs should include:
  - What changed and why
  - How to verify (commands/steps)
  - Screenshots/GIFs for UI changes
  - Linked issue/task when applicable

## Security & Configuration Notes
- Configure secrets via environment variables (`JWT_SECRET`, model API keys); never commit secrets.
- Auth credentials are defined in `backend/app/auth.py` for local use.
- Saving chapters triggers backend git add/commit/push logic in `backend/app/services/storage.py`; test on the correct branch/remote.

## Agent Operational Memory
- After any code change in `backend/` or `frontend/`, automatically restart ZenApp backend before handing off.
- Keep runtime env vars set before restart (for example: `XHS_PUBLISH_WEBHOOK`, `XHS_PUBLISH_WEBHOOK_TOKEN`, `ZENAPP_PUBLIC_BASE_URL`).
- Preferred restart flow:
  - Stop existing backend on port `8001`.
  - Start `uvicorn app.main:app --host 0.0.0.0 --port 8001`.
  - Verify `GET /api/health` returns `{"status":"ok"}`.
