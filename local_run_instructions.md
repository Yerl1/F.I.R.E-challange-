# Local Run Instructions (Ubuntu/Linux)

This project is split into:

- infrastructure via Docker: `postgres`, `ollama`, `nominatim`
- app services run locally: `backend`, `pipeline-service`, `front`

## 1) Prepare environment

From repo root:

```bash
cp .env.example .env
```

Adjust `.env` values if needed.

## 2) Install dependencies

```bash
bash scripts/linux/setup_dev.sh
```

This sets up:
- `backend/.venv`
- `pipeline-service/.venv`
- `front/node_modules`

## 3) Start infrastructure

```bash
bash scripts/linux/start_infra.sh
```

## 4) Run services (separate terminals)

Terminal A:

```bash
bash scripts/linux/run_backend.sh
```

Terminal B:

```bash
bash scripts/linux/run_pipeline.sh --sample
```

Terminal C:

```bash
bash scripts/linux/run_front.sh
```

## 5) Health checks

```bash
curl http://localhost:8001/health
curl http://localhost:11434/api/tags
curl "http://localhost:8080/search?q=Almaty&format=jsonv2&limit=1&countrycodes=kz"
```

## 6) Stop infrastructure

```bash
bash scripts/linux/stop_infra.sh
```

## Optional: pull Ollama models

```bash
ollama pull llama3.2:1b
ollama pull qwen2.5:7b-instruct-q4_K_M
```

Use these env vars for service-specific model selection:

- `PIPELINE_OLLAMA_MODEL` for `pipeline-service`
- `AI_AGENT_OLLAMA_MODEL` for backend analytics agent
