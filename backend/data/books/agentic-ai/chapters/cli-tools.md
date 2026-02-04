# Cli Tools

## github copilot
Use small, purpose-built `.md` files as reusable “prompt cards” you can paste into Copilot Chat/Copilot CLI to keep requests consistent and reduce back-and-forth.
Recommended `.md` prompt cards
- `docs/copilot/overview.md`: project one‑pager (what it is, what it isn’t, key terminology)
- `docs/copilot/dev-setup.md`: how to run, test, lint, build; common env vars
- `docs/copilot/architecture.md`: high-level components, boundaries, data flow
- `docs/copilot/conventions.md`: naming, folder layout, error handling, logging, commit style
- `docs/copilot/api-patterns.md`: request/response shapes, pagination, auth, status codes
- `docs/copilot/db.md`: migrations workflow, schema notes, seed data, gotchas
- `docs/copilot/recipes.md`: “how do I…” snippets (add endpoint, add job, add config, add test)
What each card should contain
- Goal: what Copilot should optimize for (correctness, minimal diff, backward compatibility)
- Constraints: languages, frameworks, “don’t touch” areas, performance or security requirements
- Commands: the exact commands to run for tests/build/lint
- File map: the 5–10 most important directories/files and what they contain
- Examples: 1–2 small examples of preferred patterns (error handling, logging, response shape)
- Acceptance checks: a short checklist of what “done” means
Useful tips
- Be explicit about output: “return a unified diff” / “only the edited text” / “list steps then code”
- Include paths and scope: “only change `src/foo` and `tests/foo`”
- Provide a minimal repro and expected behavior when debugging
- Ask for options when unsure: “give 2 approaches with tradeoffs, then pick one”
- Keep prompt cards short and stable; update them when conventions or tooling changes
