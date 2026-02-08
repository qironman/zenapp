# ZenApp Takeover Plan

## Goal
Stabilize ZenApp as a reliable AI-assisted writing tool, then expand into a stronger author workflow (versioning, collaboration, publishing).

## Current State (Audit Summary)
The app already has a solid core flow: book/chapter management, markdown editing, AI suggestion/revision, image upload, and mobile-friendly UI.  
Key risks are mostly around security, reliability, and maintainability.

## Priority Backlog

### P0 - Fix Before Major Feature Work
1. Security hardening
- Replace hardcoded credentials in `backend/app/auth.py` with env/config-backed users.
- Require auth for prompt endpoints in `backend/app/routers/prompts.py`.
- Enforce strict slug validation in backend routes/services to prevent path traversal.

2. Save/session correctness
- Clarify or fix “Approve & Save” behavior in `frontend/src/App.tsx` and session lifecycle in `frontend/src/hooks/useAgent.ts`.
- Add explicit backend session expiry/cleanup in `backend/app/services/agent.py`.

3. Git/repo hygiene
- Stop tracking `frontend/node_modules` and `backend/venv` in git; clean repo history strategy can be decided separately.
- Align default ports/docs (`Makefile` vs `README`/Vite proxy currently inconsistent).

4. Test baseline
- Add backend API tests (`pytest`) for auth, books/chapters CRUD, agent session flow, and image upload validations.

### P1 - Reliability + UX Upgrades
1. Draft safety
- Autosave unsaved chapter drafts to IndexedDB; recover on reload/crash.
- Add “dirty state” route/close guards and clearer sync state.

2. Agent quality
- Replace fragile CLI output parsing with structured mode and robust error handling.
- Add model/provider selection UX and prompt templates management UI (create/edit/reorder).

3. Version history
- Show chapter revision timeline (git log-backed) and one-click restore.

### P2 - Product Expansion Features
1. Collaboration
- Comments/suggestions mode (inline notes anchored to ranges).
- Multi-user auth with roles (owner/editor/viewer).

2. Publishing
- Export pipelines: EPUB, PDF, and platform-specific markdown transforms.
- Image asset management panel (rename/reuse/delete, alt text support).

3. Writing acceleration
- Chapter-level AI operations: summarize chapter, continuity check, style consistency, glossary extraction.

## Suggested Execution Plan
1. Week 1: P0 security + repo cleanup + consistent run scripts.
2. Week 2: backend test suite + session/save correctness fixes.
3. Week 3: autosave/recovery + revision history viewer.
4. Week 4: agent UX upgrades + first export format (EPUB or PDF).

## Definition of “Takeover Complete”
- Reproducible local setup.
- No hardcoded secrets/credentials.
- Core APIs covered by tests.
- Stable edit/save/agent cycle with clear user feedback.
- Published roadmap with milestone tracking.
