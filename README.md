# F.I.R.E Challenge Monorepo

Ubuntu-first mono-repo with 3 services:

- `backend/` FastAPI API + analytics agent
- `pipeline-service/` ticket processing graph
- `front/` Next.js web UI

## Repository Structure

```text
.
├── backend/
├── pipeline-service/
├── front/
├── docs/
├── scripts/
│   └── linux/
├── docker-compose.yml
└── .env.example
```

## Quick Start (Ubuntu)

1. Copy env template:

```bash
cp .env.example .env
```

2. Install dependencies for all services:

```bash
bash scripts/linux/setup_dev.sh
```

3. Start infra dependencies:

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
- Backend docs: `http://localhost:8001/docs`

## GitHub Push

Run from repository root:

```bash
git add .
git commit -m "Initial clean Ubuntu-ready monorepo structure"
git branch -M main
git remote add origin <your-github-repo-url>  # skip if already set
git push -u origin main
```

If `.env` already exists locally, it stays untracked by `.gitignore`.
