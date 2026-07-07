# CLAUDE.md

Guidance for AI coding assistants working in this repository. **Part A** is project
context specific to Loktra AI. **Part B** is general behavioral guidelines.

---

# Part A — Project Context

## What this is

**Loktra AI** — an AI-powered constituency intelligence & civic-governance platform.
Citizens report civic issues (text / voice / image, multilingual); the AI validates
governance relevance, categorises, scores priority against government datasets, routes
to the correct constituency, and gives MPs/officers decision support.

Monorepo with two apps:

- **`backend/`** — FastAPI · SQLAlchemy 2 · SQLite · Pydantic v2 · JWT · pluggable Gemini/rule-based AI
- **`loktra-ai-frontend/`** — React 18 · Vite · Tailwind · React Router · Recharts · Leaflet · Framer Motion

See `README.md` (root) and `backend/README.md` for full documentation.

## Common commands

```bash
# Backend (from backend/)
python -m app.db.init_db                          # DROP + recreate + seed the demo DB
uvicorn app.main:app --reload                     # serve API on :8000, docs at /docs
PYTHONPATH=. python tests/integration_check.py    # 27 end-to-end checks (run after seeding)

# Frontend (from loktra-ai-frontend/)
npm run dev                                        # Vite dev server on :5173 (proxies /api, /uploads)
npm run build
```

## Environment & platform notes

- Primary dev platform is **Windows** — the shell is PowerShell. Activate the venv with
  `.venv\Scripts\activate`. Paths in this repo use backslashes on disk.
- The app boots with **no `.env` and no API key**: config defaults live in
  `backend/app/core/config.py` and every value has a safe local default.
- AI provider is selected by `AI_PROVIDER` (`auto` | `gemini` | `fallback`). Gemini
  calls fall back to the rule-based provider at runtime on any failure — never let a
  model error surface as an API error.

## Architecture conventions (follow these)

- **Backend layering:** `api/v1` (routers) → `services` (business logic) → `models` /
  `db`. Keep request/response shapes in `schemas/` (Pydantic v2). Don't put business
  logic in routers.
- **AI is behind an interface.** The app depends only on the `AIProvider` interface
  (`app/ai/provider.py`); orchestration wrappers (`relevance_guard`, `analyzer`,
  `language`) and the pure `priority` engine sit on top. Add capabilities without
  coupling callers to a concrete provider.
- **Visibility is enforced at the query level** in `complaint_service.visible_query()`,
  not in the router. Out-of-scope complaints return **404, not 403**, so existence
  isn't leaked across constituencies. Preserve this when touching complaint reads.
- **Priority scoring is transparent and explainable** (`score = base(urgency) +
  emergency_boost + dataset_adjustment`, `0–100`). The full breakdown is stored in
  each complaint's `ai_reason`. Keep it deterministic and auditable.
- **File storage is abstracted** behind `app/utils/file_storage.py` so it can be
  swapped for S3/GCS without touching services.
- **Frontend:** one axios module per backend area under `src/api/`; auth/session in
  `src/context/AuthContext.jsx`; role-gated routing via `src/routes/ProtectedRoute.jsx`;
  per-role screens under `src/pages/{citizen,officer,mp,admin}/`.

## Gotchas

- `init_db` **drops all tables** — never run it against data you want to keep.
- Secrets and generated files are git-ignored (`.env`, `*.db`, `backend/uploads/*`).
  Change `JWT_SECRET_KEY` before any non-local deployment.
- This working tree is **not a git repository**.

---

# Part B — Behavioral Guidelines

Behavioral guidelines to reduce common LLM coding mistakes.

**Tradeoff:** These guidelines bias toward caution over speed. For trivial tasks, use judgment.

## 1. Think Before Coding

**Don't assume. Don't hide confusion. Surface tradeoffs.**

Before implementing:
- State your assumptions explicitly. If uncertain, ask.
- If multiple interpretations exist, present them - don't pick silently.
- If a simpler approach exists, say so. Push back when warranted.
- If something is unclear, stop. Name what's confusing. Ask.

## 2. Simplicity First

**Minimum code that solves the problem. Nothing speculative.**

- No features beyond what was asked.
- No abstractions for single-use code.
- No "flexibility" or "configurability" that wasn't requested.
- No error handling for impossible scenarios.
- If you write 200 lines and it could be 50, rewrite it.

Ask yourself: "Would a senior engineer say this is overcomplicated?" If yes, simplify.

## 3. Surgical Changes

**Touch only what you must. Clean up only your own mess.**

When editing existing code:
- Don't "improve" adjacent code, comments, or formatting.
- Don't refactor things that aren't broken.
- Match existing style, even if you'd do it differently.
- If you notice unrelated dead code, mention it - don't delete it.

When your changes create orphans:
- Remove imports/variables/functions that YOUR changes made unused.
- Don't remove pre-existing dead code unless asked.

The test: Every changed line should trace directly to the user's request.

## 4. Goal-Driven Execution

**Define success criteria. Loop until verified.**

Transform tasks into verifiable goals:
- "Add validation" → "Write tests for invalid inputs, then make them pass"
- "Fix the bug" → "Write a test that reproduces it, then make it pass"
- "Refactor X" → "Ensure tests pass before and after"

For multi-step tasks, state a brief plan:
```
1. [Step] → verify: [check]
2. [Step] → verify: [check]
3. [Step] → verify: [check]
```

Strong success criteria let you loop independently. Weak criteria ("make it work") require constant clarification.

---

**These guidelines are working if:** fewer unnecessary changes in diffs, fewer rewrites due to overcomplication, and clarifying questions come before implementation rather than after mistakes.
