# Loktra AI

**AI-powered constituency intelligence & civic-governance platform.**

Citizens report civic issues (text / voice / image, multilingual). The AI validates
governance relevance, categorises the issue, scores its priority against a **sample
government-style dataset** (demo data — not real government data), routes it to the
correct constituency, and gives MPs and officers decision support to resolve it.

This repository is a monorepo with two apps:

| App | Path | Stack |
|-----|------|-------|
| **Backend** | [`backend/`](backend/) | FastAPI · SQLAlchemy 2 · SQLite · Pydantic v2 · JWT · pluggable Gemini / rule-based AI |
| **Frontend** | [`loktra-ai-frontend/`](loktra-ai-frontend/) | React 18 · Vite · Tailwind · React Router · Recharts · Leaflet · Framer Motion |

---

## Quick start

Run the two apps in separate terminals. The backend serves the API on `:8000`;
the frontend dev server runs on `:5173` and proxies `/api` and `/uploads` to it.

### 1. Backend

```bash
cd backend
python -m venv .venv && source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt

python -m app.db.init_db          # create + seed the demo database
uvicorn app.main:app --reload     # https://loktra-production.up.railway.app (interactive docs at /docs)
```

The backend boots with **no API key and no `.env`** — it uses a deterministic
rule-based AI provider by default. To enable live Gemini analysis:

```bash
cp .env.example .env              # then set GEMINI_API_KEY and AI_PROVIDER=gemini
pip install google-genai
```

If a Gemini call ever fails (quota, network, bad JSON) the request transparently
falls back to the rule-based provider, so the API never errors out because of the model.

### 2. Frontend

```bash
cd loktra-ai-frontend
npm install
npm run dev                       # http://localhost:5173
```

Leave `VITE_API_BASE_URL` empty for local dev — the Vite proxy (see
`vite.config.js`) forwards API calls to the backend on `:8000` with no CORS friction.
Set it to an absolute URL for production builds.

---

## Demo logins

The seeded database ships with one account per role:

| Role        | Email                        | Password    | Scope             |
|-------------|------------------------------|-------------|-------------------|
| Super Admin | admin@loktra.ai              | admin123    | everything        |
| MP/Admin    | mp@loktra.ai                 | mp123456    | Goregaon          |
| Officer     | officer@loktra.ai            | officer123  | Goregaon          |
| Citizen     | citizen@loktra.ai            | citizen123  | own complaints    |
| MP (demo 2) | mp.hyd@loktra.ai             | mp123456    | Serilingampally   |
| Officer (2) | officer.hyd@loktra.ai        | officer123  | Serilingampally   |

---

## How it works

### The complaint pipeline

A citizen submission flows through the AI layer before it reaches a human:

1. **Relevance guard** — rejects non-governance content.
2. **Analysis** — categorises the issue and detects language (Unicode script).
3. **Priority scoring** — transparent `0–100`:

   ```
   score = base(urgency) + emergency_boost + dataset_adjustment
   ```

   Sample-dataset scores are `0–100` (higher = better existing infrastructure),
   so a **low** dataset score raises priority — worse infrastructure means greater
   need. Each complaint stores the full breakdown in `ai_reason`.

4. **Routing** — the complaint is scoped to the correct constituency and surfaced
   to that constituency's officer / MP.

### Pluggable AI (`backend/app/ai/`)

The app depends only on the `AIProvider` interface; a factory picks the
implementation from config (`AI_PROVIDER` = `auto` | `gemini` | `fallback`):

- **GeminiProvider** — `google-genai`, imported lazily, with per-call fallback.
- **FallbackProvider** — offline rules: keyword banks + Unicode script detection.

Swapping the provider changes nothing else in the codebase.

### Visibility (enforced at the query level)

Role scoping happens inside `complaint_service.visible_query()`, so out-of-scope
complaints never leave the database:

- **Citizen** → only their own submissions
- **Officer** → complaints assigned to them or in their constituency
- **MP** → only their constituency
- **Super Admin** → everything

Fetching an out-of-scope complaint returns **404** (not 403), so existence isn't
leaked across constituencies.

---

## Repository layout

```
loktra-ai-backend/
├── backend/                     FastAPI service (see backend/README.md for detail)
│   └── app/
│       ├── core/                config, security (bcrypt + JWT), dependencies (RBAC)
│       ├── db/                  Base, metadata, session, init_db (seed)
│       ├── models/              SQLAlchemy models (users, location tree, complaints…)
│       ├── schemas/             Pydantic v2 request/response models
│       ├── ai/                  pluggable AI layer (provider, analyzer, priority…)
│       ├── services/            business logic (auth, complaints, assignment, dashboard)
│       ├── api/v1/              routers: auth, locations, complaints, officer, mp, admin, datasets
│       └── main.py              app factory (CORS, static /uploads, create_all, router)
│
├── loktra-ai-frontend/          React + Vite SPA
│   └── src/
│       ├── api/                 axios client + one module per backend area
│       ├── context/             AuthContext (JWT session)
│       ├── routes/              ProtectedRoute (role-gated routing)
│       ├── components/          layout, charts, map, and reusable UI primitives
│       ├── pages/               per-role screens (citizen, officer, mp, admin)
│       └── lib/                 constants, hooks (speech input, page header)
│
├── docs/                        (placeholder for project docs)
├── CLAUDE.md                    guidelines for AI coding assistants working here
└── README.md                    this file
```

---

## Verify it works

```bash
cd backend
python -m app.db.init_db                          # seed
PYTHONPATH=. python tests/integration_check.py    # 27 end-to-end checks
```

---

## Key API endpoints

| Method | Path                                             | Who         |
|--------|--------------------------------------------------|-------------|
| POST   | `/api/v1/auth/register` · `/login`               | public      |
| GET    | `/api/v1/locations/{states,districts,…}`         | public      |
| POST   | `/api/v1/complaints` (multipart)                 | citizen     |
| GET    | `/api/v1/complaints` · `/{id}` · `/track/{code}` | scoped      |
| POST   | `/api/v1/officer/complaints/{id}/verify` · `/status` · `/note` | officer |
| GET    | `/api/v1/mp/dashboard` · `/mp/officers`          | MP          |
| POST   | `/api/v1/mp/complaints/{id}/assign`              | MP          |
| GET    | `/api/v1/admin/summary`                          | super admin |
| CRUD   | `/api/v1/admin/*` · `/api/v1/datasets/*`         | super admin |

Full interactive docs at `/docs` once the backend is running.

---

## Notes

- `init_db` **DROPS and recreates** tables for a clean, deterministic demo — do not
  run it against data you want to keep.
- Uploaded media is stored under `backend/uploads/` and served at `/uploads/...`.
  Swap `app/utils/file_storage.py` for S3/GCS without touching services.
- Nothing in this repo is committed with real secrets: `.env`, `*.db`, and uploads
  are git-ignored. Change `JWT_SECRET_KEY` before any non-local deployment.
- See [`backend/README.md`](backend/README.md) for deeper backend documentation.
