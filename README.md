# PlantWise AI

A growing-suitability assistant for crops and vegetables. Pick a plant, enter a
location, and the app compares the site's historical climate against that
plant's documented agronomic requirements — and explains the reasoning.

The suitability verdict is **not** a ratio or a score. It is a weighted,
rule-based assessment: each requirement (cold tolerance, heat tolerance, frost
risk, growing-window length, water balance, soil, sunlight) is evaluated
against a documented range and reported as pass / caution / fail / not
assessed, and the verdict is reached from those. Unknown values are reported as
unknown rather than guessed.

The project is deliberately honest about its limits: climate values are
climatological normals for a reanalysis grid cell, not a forecast, and a
positive verdict is a good signal, not a guarantee.

## Repository layout

- `backend/` — FastAPI application, SQLAlchemy persistence, climate + AI
  services, suitability engine, pytest suite.
- `frontend/` — Next.js 16 application (App Router, server components, Tailwind).

## Stack

- **Backend:** Python 3.13, FastAPI, Uvicorn, Pydantic v2, SQLAlchemy 2 (async,
  aiosqlite), httpx, pytest.
- **Frontend:** Node 24, Next.js 16.3.8, React 19, TypeScript, Tailwind CSS 4
  (PostCSS), react-leaflet.
- **External services (all optional, with graceful degradation):**
  - [Open-Meteo Historical Weather API](https://open-meteo.com/) — ERA5
    reanalysis normals (2015–2024) for the location.
  - [Open-Meteo Geocoding API](https://open-meteo.com/) — place name to
    coordinates (also works as a frontend proxy through `app/api/locations`).
  - [OpenRouter](https://openrouter.ai/) with a hosted open-weight model
    (Google Gemma 4 by default) — optional plain-language assistant. The
    backend calls an OpenAI-compatible endpoint; without an API key the
    assistant reports itself unavailable and everything else keeps working.

## Run it locally

### 1. Backend

```bash
cd backend
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
cp .env.example .env          # defaults are fine for a local run
.venv/bin/python -m uvicorn app.main:app --reload
```

On startup the database is created and seeded with **17 plant profiles and 90
documented cultivation regions** (`SEED_ON_STARTUP=true`; reseeding is
idempotent and never touches runtime data such as search counts).

The API is at `http://127.0.0.1:8000`, interactive docs at
`/docs`. Key endpoints:

- `GET /api/v1/health` · `GET /api/v1/health/assistant`
- `GET /api/v1/plants` (search/filter via `query`, `lifecycle`, `difficulty`,
  `tag`; when a query returns nothing it also returns `suggestions`) ·
  `GET /api/v1/plants/featured` · `GET /api/v1/plants/{slug}`
- `POST /api/v1/suitability` — `{"plant_slug", "location", "inputs"}`
  (pass `?explain=true` for the optional assistant explanation)
- `GET /api/v1/regions/plants` (plants with documented regions) ·
  `GET /api/v1/regions/{plant_slug}`
- `GET /api/v1/locations/search?q=...`
- `GET /api/v1/assistant/status` · `POST /api/v1/assistant/chat`

### 2. Frontend

```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:3000`. The frontend talks to the backend through
`PLANTWISE_API_URL` (server-side only; default `http://127.0.0.1:8000`).
Set it in `frontend/.env.local` if your backend runs elsewhere:

```
PLANTWISE_API_URL=http://127.0.0.1:8000
```

### 3. Optional: hosted assistant (OpenRouter)

The assistant is off by default because it needs an API key. The default model
is a free open-weight Google Gemma 4 variant served by OpenRouter — no local
download, no GPU required.

1. Create an account and generate a key at
   [openrouter.ai/settings/keys](https://openrouter.ai/settings/keys).
2. Create `backend/.env` (copied from `.env.example`) and set:

   ```bash
   OPENROUTER_API_KEY=sk-or-...
   # OPENROUTER_MODEL=google/gemma-4-26b-a4b-it:free   # default, or pick your own
   # OPENROUTER_FALLBACK_MODELS=nvidia/nemotron-3-super-120b-a12b:free,nvidia/nemotron-3.5-lightning:free
   ```

`backend/.env` is git-ignored. The key is read only by the backend and never
sent to the browser, logged, or returned in API responses.

**Chosen model — `google/gemma-4-26b-a4b-it:free`**

- Verified live at `https://openrouter.ai/api/v1/models` against the official
  catalog (free variant priced at \$0.00 prompt and completion).
- **Vendor / license:** Google's open-weights Gemma family; the specific
  Free Variant is one of the `:free` models bundled with the catalog. Model
  pages list each one's own terms.
- **Context:** 262,144 tokens (~256K), comfortably larger than the assistant's
  12-turn history window.
- **Limitations:** free models are rate-limited — roughly **50 requests/day**
  without purchased credits (1,000/day once you have bought ≥ \$10 of credits)
  and are "usually not suitable for production". The free pools are also
  *shared*, so a request can be rate-limited upstream by the provider (Google AI
  Studio) even when your own daily quota is untouched. Model IDs change over
  time; browse [openrouter.ai/models](https://openrouter.ai/models) and set
  `OPENROUTER_MODEL` to another free open-weight model if this one is removed
  or renamed.

**Model fallbacks.** `OPENROUTER_FALLBACK_MODELS` (comma separated) is passed to
OpenRouter as its `models` routing list, which is tried in order whenever the
primary model is rate-limited, down, or refuses. This keeps the assistant
answering during upstream congestion instead of surfacing a 429. The default
chain is Gemma 4 → `nvidia/nemotron-3-super-120b-a12b:free` →
`nvidia/nemotron-3.5-lightning:free` (both open-weight). The response's `model`
field reports which model actually answered.

- **How to check:** `GET /api/v1/assistant/status` live-probes the key with
  OpenRouter's `GET /api/v1/auth/key` endpoint.

Without a key, suitability results still work; only the assistant is
unavailable and the UI tells you so.

## Tests

```bash
cd backend
.venv/bin/python -m pytest
```

The suite is deterministic and network-free: it runs the suitability engine
against hand-built climate snapshots and verifies seeding idempotency against
an in-memory SQLite database. `pytest-asyncio` is pinned but not used — the
fixtures manage their own event loop.

## How a suitability check works

1. **Location.** A place name is geocoded; coordinates are validated.
2. **Climate.** A 10-year ERA5 archive series for the grid cell is fetched from
   Open-Meteo and cached for 30 days. Coldest/hottest months, frost days, and
   annual precipitation are derived.
3. **Assessment.** The plant's recorded requirements are compared against the
   climate and against the growing inputs you supply (soil, sunlight,
   irrigation). Each criterion produces an observed value, a requirement, a
   status, and an explanation.
4. **Verdict.** Criteria are combined by a documented weighted policy
   (methodology `v1.0.0`):

   | Criterion       | Weight | Boundary                        |
   |-----------------|--------|---------------------------------|
   | Cold tolerance  | 1.0    | coldest month mean min < `temp_min_c` |
   | Heat tolerance  | 1.0    | hottest month mean max > `temp_max_c` |
   | Frost risk      | 1.0    | `frost_tolerance` vs frost days |
   | Growing window  | 0.8    | months ≥ `temp_min_c` vs season length |
   | Water balance   | 0.8    | annual precipitation vs rainfall range, irrigation-aware |
   | Soil match      | 0.6    | declared soil texture vs preference |
   | Sunlight match  | 0.6    | declared position vs sunlight need |

   A hard failure is decisive only when the weight of passing evidence is
   outweighed (a 1.0- or 0.8-weight criterion failing tips the balance; two
   0.6-weight fails do not veto ten passes). Confidence reflects *coverage* —
   how many criteria could actually be evaluated — never a quality score.
   The verdict text never contains a percentage.

5. **Evidence.** Documented cultivation regions for the crop are shown as
   *evidence that the crop is grown somewhere comparable* — explicitly not as
   an endorsement of the queried location. The explanation toggle (when the
   assistant is available) reads the criteria and writes a plain-language walk
   through of the verdict.

## Degraded modes

| No API key / OpenRouter down | Geocoding down       | Climate archive down       |
|------------------------------|----------------------|----------------------------|
| assistant reports `unavailable`; `/suitability?explain` omits the explanation | location search fails with a clear reason; manual lat/lon entry still works | verdict is `insufficient_data` with an explicit "why" instead of a misleading answer |

## Data and references

Plant requirement envelopes are compiled from public references, primarily FAO
Ecocrop, USDA PLANTS, and the RHS — each profile records its own sources, which
are shown on the plant page. Climate data is ERA5 reanalysis via Open-Meteo
(`© OpenStreetMap contributors` attribution for the map tiles). The seed data
ships under `backend/app/services/seed_data.py`.