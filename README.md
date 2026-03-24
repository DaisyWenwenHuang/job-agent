# Job Application Agent

An autonomous job hunting agent that scrapes LinkedIn and Indeed daily, uses Claude AI to score job fit against your resume, and applies on your behalf with one click.

**Live Demo → [your-railway-url.railway.app](https://your-app.railway.app)**

---

## Features

- **Scrapes LinkedIn + Indeed** daily for Data Scientist, ML/AI Engineer, and Data Engineer roles
- **AI-powered matching** — Claude reads your resume and scores every job 0–100 with reasoning
- **Review dashboard** — approve or reject jobs before any application is sent
- **Auto-apply** — Playwright fills LinkedIn Easy Apply and Indeed Quick Apply forms automatically
- **Configurable** — all filters (roles, location, seniority, score threshold) editable in the UI
- **Run history** — full logs of every agent run

## Tech Stack

| Layer | Tech |
|---|---|
| Backend | Python · FastAPI · SQLite · APScheduler |
| Scraping | Playwright · playwright-stealth |
| AI Matching | Claude AI (Anthropic SDK) |
| Frontend | React · TypeScript · Vite · Tailwind CSS |
| Deploy | Docker · Railway |

## Architecture

```
┌─────────────────────────────────────────┐
│              Daily Pipeline             │
│  LinkedIn/Indeed → Claude Score → DB    │
└────────────────────┬────────────────────┘
                     │
          ┌──────────▼──────────┐
          │   FastAPI Backend   │
          │  /api/jobs          │
          │  /api/runs          │
          │  /api/config        │
          └──────────┬──────────┘
                     │
          ┌──────────▼──────────┐
          │   React Dashboard   │
          │  Review → Approve   │
          │  → Auto-Apply       │
          └─────────────────────┘
```

## Quick Start (Local)

1. **Clone & configure**
   ```bash
   git clone https://github.com/DaisyWenwenHuang/job-agent.git
   cd job-agent
   cp .env.example .env
   # Fill in your ANTHROPIC_API_KEY, LinkedIn/Indeed credentials, and RESUME_FILE_PATH
   ```

2. **Run with Docker**
   ```bash
   docker compose up --build
   ```

3. Open `http://localhost:8000`

## Local Dev (without Docker)

```bash
# Backend
python -m venv .venv && source .venv/bin/activate
pip install -r backend/requirements.txt
playwright install chromium
python scripts/init_db.py
uvicorn backend.main:app --reload

# Frontend (separate terminal)
cd frontend && npm install && npm run dev
```

## Deploy to Railway

1. Push this repo to GitHub
2. Create a new project at [railway.app](https://railway.app) → "Deploy from GitHub"
3. Add a **Volume** → mount path `/app/backend/data`
4. Set environment variables (see `.env.example`):
   - `ANTHROPIC_API_KEY`
   - `LINKEDIN_EMAIL` / `LINKEDIN_PASSWORD`
   - `INDEED_EMAIL` / `INDEED_PASSWORD`
   - `RESUME_BASE64` — base64-encoded resume: `base64 -i resume.pdf`
   - `DEMO_MODE=true` (optional — seeds demo data, disables real applies)
5. Railway auto-deploys on every push to `main`

## Configuration

Edit filters anytime in the **Settings** tab of the dashboard, or directly in `backend/data/job_config.json`:

```json
{
  "target_roles": ["Data Scientist", "ML Engineer", "..."],
  "location": { "city": "Redmond", "state": "WA", "max_miles_onsite": 20 },
  "min_claude_score": 60,
  "apply_automatically": false
}
```

## Project Structure

```
job-agent/
├── backend/
│   ├── core/          # Config, DB, scheduler
│   ├── models/        # SQLAlchemy ORM models
│   ├── api/           # FastAPI routers
│   ├── scrapers/      # LinkedIn + Indeed Playwright scrapers
│   ├── appliers/      # Easy Apply + Quick Apply handlers
│   └── services/      # Resume parser, Claude matcher, pipeline
├── frontend/          # React dashboard (Vite + TypeScript + Tailwind)
├── scripts/           # DB init, test scraper, demo seed
├── Dockerfile         # Multi-stage build
└── docker-compose.yml
```

---

Built by [Daisy Huang](https://www.daisyhuangds.com) · [GitHub](https://github.com/DaisyWenwenHuang/job-agent)
