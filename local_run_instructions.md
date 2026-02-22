# Local Run Instructions (Windows)

This setup runs only infrastructure in Docker and keeps app services local for faster iteration:

- Docker: `postgres`, `ollama`, `nominatim`
- Local (venv/node): `backend` (includes `ai_agent`), `pipeline-service`, `front`

## 1) Start infra in Docker

From repo root:

```powershell
docker compose up -d postgres ollama nominatim
```

Check:

```powershell
docker compose ps
```

## 2) Prepare env in current PowerShell session

From repo root:

```powershell
$env:BACKEND_DATABASE_URL="postgresql+psycopg://postgres:postgres@localhost:5432/fire_backend"
$env:PERSIST_MODE="postgres"
$env:PERSIST_POSTGRES_DSN="postgresql://postgres:postgres@localhost:5432/fire_backend"

$env:OLLAMA_BASE_URL="http://localhost:11434"
$env:GEOCODER_BASE_URL="http://localhost:8080"

$env:PIPELINE_OLLAMA_MODEL="llama3.2:1b" # pipeline-service/ticket pipeline model
$env:AI_AGENT_OLLAMA_MODEL="qwen2.5:7b-instruct-q4_K_M" # analytics agent model
$env:MOCK_LLM="0"

$env:TYPE_MODEL_PATH="C:\Users\7ruta\Desktop\fire demo\F.I.R.E-challange-\pipeline-service\models\type_recognition"
$env:SPAM_MODEL_PATH="C:\Users\7ruta\Desktop\fire demo\F.I.R.E-challange-\pipeline-service\models\spam_detection"
$env:SENTIMENT_MODEL_PATH="C:\Users\7ruta\Desktop\fire demo\F.I.R.E-challange-\pipeline-service\models\sentiment"
```

Do not override global `OLLAMA_MODEL` when both run in one environment.
Use the two dedicated vars above.

## 3) Run backend locally (includes ai_agent)

Open Terminal A, repo root:

```powershell
python -m pip install -r .\backend\requirements.txt
uvicorn backend.app.main:app --host 0.0.0.0 --port 8001
```

Notes:
- `ai_agent` is already mounted in backend app via router.
- API docs: `http://localhost:8001/docs`
- Analytics endpoint: `POST /api/v1/analytics/query`

Optional bootstrap reference data:

```powershell
curl -X POST http://localhost:8001/api/v1/bootstrap
```

## 4) Run pipeline-service locally

Open Terminal B:

```powershell
cd .\pipeline-service
python -m pip install -e ".[dev]"
python -m pipeline_service.main --sample --show_timing
```

CSV run:

```powershell
python -m pipeline_service.main --show_timing --input_type=csv --file="C:\full\path\to\tickets.csv"
```

## 5) Run frontend locally

Open Terminal C:

```powershell
cd .\front
```

If PowerShell blocks `npm.ps1`, run through `cmd`:

```powershell
cmd /c npm install
setx NEXT_PUBLIC_API_BASE_URL "http://localhost:8001"
cmd /c npm run dev
```

Or for current session only:

```powershell
$env:NEXT_PUBLIC_API_BASE_URL="http://localhost:8001"
cmd /c npm run dev
```

Frontend URL:
- `http://localhost:3000`

## 6) Quick health checks

```powershell
curl http://localhost:8001/health
curl http://localhost:11434/api/tags
curl "http://localhost:8080/search?q=Алматы&format=jsonv2&limit=1&countrycodes=kz"
```

## 7) Stop everything

Stop local terminals with `Ctrl+C`.

Stop Docker infra:

```powershell
docker compose down
```

Keep DB data (default). To remove volumes too:

```powershell
docker compose down -v
```
