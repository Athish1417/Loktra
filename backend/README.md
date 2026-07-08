# Loktra AI — Backend

AI-powered constituency intelligence & civic-governance platform. Citizens report
civic issues (text / voice / image, multilingual); the AI validates governance
relevance, categorises, scores priority using a **sample government-style dataset**
(demo data, not real government data), routes to the correct constituency, and gives
MPs decision support.

FastAPI · SQLAlchemy · SQLite · Pydantic v2 · JWT · pluggable Gemini/rule-based AI.

---

## Quick start

```bash
cd backend
python -m venv .venv && source .venv/bin/activate      # (Windows: .venv\Scripts\activate)
pip install -r requirements.txt

python -m app.db.init_db          # create + seed the demo database
uvicorn app.main:app --reload     # https://loktra-production.up.railway.app  (docs at /docs)
```

The app runs with **no API key** — it uses a deterministic rule-based AI provider
by default. To enable live Gemini analysis:

```bash
cp .env.example .env
# set GEMINI_API_KEY=... and (optionally) AI_PROVIDER=gemini
pip install google-genai
```

If a Gemini call ever fails at runtime (quota, network, bad JSON), the request
transparently falls back to the rule-based provider — the API never errors out
because of the model.

## Demo logins

| Role        | Email                        | Password    | Scope             |
|-------------|------------------------------|-------------|-------------------|
| Super Admin | admin@loktra.ai              | admin123    | everything        |
| MP/Admin    | mp@loktra.ai                 | mp123456    | Goregaon          |
| Officer     | officer@loktra.ai            | officer123  | Goregaon          |
| Citizen     | citizen@loktra.ai            | citizen123  | own complaints    |
| MP (demo 2) | mp.hyd@loktra.ai             | mp123456    | Serilingampally   |
| Officer (2) | officer.hyd@loktra.ai        | officer123  | Serilingampally   |

The second Serilingampally pair exists so cross-constituency visibility is easy to demo.

## Verify it works

```bash
python -m app.db.init_db          # seed
PYTHONPATH=. python tests/integration_check.py   # 27 end-to-end checks
```

---

## Architecture

```
app/
├── core/          config, security (bcrypt + JWT), dependencies (RBAC)
├── db/            base_class (Base), base (metadata), session, init_db (seed)
├── models/        SQLAlchemy models (users, location tree, complaints, datasets...)
├── schemas/       Pydantic v2 request/response models
├── ai/            pluggable AI layer (see below)
├── services/      business logic (auth, complaint pipeline, assignment, dashboard)
├── api/v1/        routers: auth, locations, complaints, officer, mp, admin, datasets
└── main.py        app factory (CORS, static /uploads, create_all, router)
```

### Pluggable AI (`app/ai/`)

The app depends only on the `AIProvider` interface. A factory picks the
implementation from config:

- **GeminiProvider** — google-genai, imported lazily, per-call fallback.
- **FallbackProvider** — offline rules: keyword banks + Unicode script detection.

Orchestration wrappers (`relevance_guard`, `analyzer`, `language`) and the pure
`priority` engine sit on top, so swapping the provider changes nothing else.

### Priority scoring

Transparent, explainable `0–100`:

```
score = base(urgency) + emergency_boost + dataset_adjustment
```

Sample-dataset scores are `0–100` (higher = better infrastructure), so a
**low** relevant score raises priority (worse existing infra → greater need). Each
complaint stores the full breakdown in `ai_reason`. The dataset is a **Sample
Government-Style Dataset** — demo values only, structured so real sources
(data.gov.in / Census India) can be imported later.

### Visibility (enforced at the query level)

Role scoping happens inside `complaint_service.visible_query()`, so out-of-scope
complaints never leave the database:

- **Citizen** → only their own submissions
- **Officer** → complaints assigned to them or in their constituency
- **MP** → only their constituency
- **Super Admin** → everything

Fetching an out-of-scope complaint returns **404** (not 403), so existence isn't
leaked across constituencies.

## Key API endpoints

| Method | Path                                        | Who         |
|--------|---------------------------------------------|-------------|
| POST   | `/api/v1/auth/register` · `/login`          | public      |
| GET    | `/api/v1/locations/{states,districts,...}`  | public      |
| POST   | `/api/v1/complaints` (multipart)            | citizen     |
| GET    | `/api/v1/complaints` · `/{id}` · `/track/{code}` | scoped |
| POST   | `/api/v1/officer/complaints/{id}/verify` · `/status` · `/note` | officer |
| GET    | `/api/v1/mp/dashboard` · `/officers`        | MP          |
| POST   | `/api/v1/mp/complaints/{id}/assign`         | MP          |
| GET    | `/api/v1/admin/summary`                     | super admin |
| CRUD   | `/api/v1/admin/*`, `/api/v1/datasets/*`     | super admin |

Complaint statuses: `Submitted → Verified → Assigned → Work Started → Completed`,
plus `Rejected`. `/officer/.../note` adds a timeline note without changing status;
`/mp/officers` lists the officers an MP can assign within their constituency;
`/admin/summary` returns platform totals with state-wise and constituency-wise
breakdowns.

Full interactive docs at `/docs` once running.

## Real government datasets (Phase 4)

The app runs on a clearly-labelled **Sample Government-Style Dataset** by default.
To use real official data, drop downloaded files into `backend/datasets/`:

```
datasets/
  census/     # Census population data
  lgd/        # LGD villages / local directory
  pincode/    # All-India PIN Code directory
  nfhs/       # NFHS district / state factsheets
  election/   # ECI constituency summary / result reports (2024, etc.)
  imports/    # anything else
```

`.csv`, `.xlsx`, and `.xls` are supported. The importer does **not** assume exact
file or column names. It reads **all sheets**, detects the real header row past any
title/notes rows, **skips blank rows**, detects columns robustly (e.g.
`Total Population` → population), skips invalid rows, and never crashes on messy or
partial files. Data files here are git-ignored; see `datasets/README.md`.

**Import flow (Super Admin):**

| Method | Path | Purpose |
|--------|------|---------|
| GET    | `/api/v1/datasets/files`          | list detected dataset files |
| POST   | `/api/v1/datasets/preview`        | `{path, source_type}` → sheets, columns, detected fields, sample rows |
| POST   | `/api/v1/datasets/import-file`    | `{path, source_type, is_official, replace, ...}` → import into DB |
| GET    | `/api/v1/datasets/sources`        | provenance log (record counts + status) |
| DELETE | `/api/v1/datasets/sources/{id}`   | delete a source + its records (safely re-labels mode) |
| GET    | `/api/v1/datasets/source`         | current **Dataset Mode** (Sample vs Official) |

Re-importing the **same file** is skipped (`status: skipped_duplicate`) unless you
pass `replace=true`, which deletes the old rows and re-imports. Verify an import via
`GET /datasets/sources` (record count + `import_status`); `GET /datasets/source`
flips to **"Official Government Dataset Imported"** once a file imports with
`is_official=true`. Sample data is never labelled official; deleting the last
official source drops mode back to sample.

**What the AI uses today:** the priority engine uses **real Census population** for a
complaint's district when imported (via `population_records`), and falls back safely
to the sample constituency dataset otherwise — so scoring never breaks on missing or
partial data. When Census / NFHS / Election records match the complaint's area, the
AI assessment notes *"Priority enhanced using imported … dataset context."* LGD, PIN
code, NFHS, and election records are stored (`lgd_location_records`, `pincode_records`,
`nfhs_records`, `election_constituency_records`) for location intelligence.

## Notes

- `init_db` DROPS and recreates tables for a clean, deterministic demo.
- Uploaded media is stored under `uploads/` and served at `/uploads/...`.
  Swap `app/utils/file_storage.py` for S3/GCS without touching services.
- CORS defaults allow the Vite dev server (`localhost:5173`).
