# Freedom Intelligent Routing Engine (F.I.R.E.)

AI-powered system for automatic ticket analysis and smart manager assignment in off-hours support operations.

## Team

- Yerlan
- Asyat
- Max
- Arsen

## Problem

Customer tickets arrive after working hours and must be processed fast, consistently, and fairly.
The challenge requires:

- AI enrichment of each ticket (type, sentiment, priority, language, summary, geo-normalization)
- Strict business-rule routing (skills, position constraints, language handling, office matching)
- Load-balanced assignment between eligible managers
- Persisted results in PostgreSQL
- Web UI for operations visibility
- Star task: AI assistant that builds analytics from natural language prompts

## Our Solution

We built a 3-service architecture:

- `pipeline-service` performs ticket enrichment and classification
- `backend` applies business rules, assigns managers, and exposes APIs
- `front` provides dashboards, ticket tools, and AI assistant interface

This separation keeps processing logic, orchestration, and UI independent for easier scaling and maintenance.

## How It Works

1. Ticket enters pipeline (single JSON or CSV batch).
2. AI pipeline extracts:
   - ticket type
   - sentiment
   - urgency score (priority)
   - language
   - short summary + recommendation
   - normalized geo data
3. Backend applies routing rules:
   - VIP/Priority -> only managers with `VIP` skill
   - data-change cases -> only `Глав спец`
   - KZ/ENG tickets -> manager must have matching language skill
   - unknown/foreign addresses -> balanced split between Astana/Almaty
4. Final assignee selected with load-aware round-robin among best candidates.
5. Result is stored in PostgreSQL and displayed in UI.

## Star Task: Analytics Assistant

Backend includes an AI analytics agent:

- natural language query -> structured DSL
- DSL -> safe SQL (allowlisted fields, SELECT-only validation)
- SQL result -> chart spec + summary

Example query:

`Show distribution of ticket types by city for last 30 days`

## Repository Structure

```text
.
├── backend/            # FastAPI + assignment rules + analytics agent
├── pipeline-service/   # NLP/ML pipeline graph and enrichment nodes
├── front/              # Next.js UI
├── docs/               # challenge materials and sample data
├── scripts/linux/      # Ubuntu run scripts
├── docker-compose.yml  # infra/services for local environment
└── .env.example        # safe env template
```

## Tech Stack

- Backend: FastAPI, SQLAlchemy, PostgreSQL, Ollama integration
- Pipeline: Python, LangGraph, modular nodes for NLP/geo/OCR
- Frontend: Next.js, React, TypeScript
- Infra: Docker Compose

## Quick Start (Ubuntu)

1. Create local env:

```bash
cp .env.example .env
```

2. Install dependencies:

```bash
bash scripts/linux/setup_dev.sh
```

3. Start infrastructure:

```bash
bash scripts/linux/start_infra.sh
```

4. Run services in separate terminals:

```bash
bash scripts/linux/run_backend.sh
bash scripts/linux/run_pipeline.sh --sample
bash scripts/linux/run_front.sh
```

5. Open:

- Frontend: `http://localhost:3000`
- Backend API docs: `http://localhost:8001/docs`

## Notes

- `.env` is intentionally ignored and must not be committed.
- Use `PIPELINE_OLLAMA_MODEL` and `AI_AGENT_OLLAMA_MODEL` to configure models independently.
