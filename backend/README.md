# FIRE Backend

Backend API that orchestrates the existing `pipeline-service` graph, assigns managers, and stores final ticket results in PostgreSQL.

## Features

- Bootstraps offices/managers from:
  - `docs/business_units.csv`
  - `docs/managers.csv`
- Processes one ticket or whole CSV concurrently using existing pipeline graph
- Manager assignment rules:
  - spam -> no manager
  - unknown/foreign -> 50/50 Astana/Almaty (round-robin toggle)
  - known address -> closest/matching office + least loaded manager
- Persists final results to PostgreSQL

## Run locally

1. Install dependencies:

```bash
pip install -r backend/requirements.txt
```

2. Configure DB URL:

```bash
export BACKEND_DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5432/fire_backend
```

PowerShell:

```powershell
$env:BACKEND_DATABASE_URL="postgresql+psycopg://postgres:postgres@localhost:5432/fire_backend"
```

3. Start API:

```bash
uvicorn backend.app.main:app --host 0.0.0.0 --port 8001
```

## API

- `GET /health`
- `POST /api/v1/bootstrap` - preload offices/managers
- `POST /api/v1/tickets/process-one`
- `POST /api/v1/tickets/process-csv`
- `POST /api/v1/tickets/process-csv-upload` (multipart/form-data, field name: `file`)
- `GET /api/v1/tickets/recent?limit=50`
- `POST /api/v1/analytics/query` - NL analytics -> DSL -> SQL -> chart JSON

Example `process-one` payload:

```json
{
  "payload": {
    "ticket_id": "T-123",
    "raw_text": "Приложение не открывается",
    "segment": "VIP",
    "country": "KZ",
    "region": "Алматинская область",
    "city": "Алматы",
    "street": "Абая",
    "house": "10"
  }
}
```

## AI Analytics Agent

The analytics assistant is implemented inside backend under:

- `backend/app/ai_agent/domain`
- `backend/app/ai_agent/application`
- `backend/app/ai_agent/infrastructure`
- `backend/app/ai_agent/interfaces`

Flow:

1. NL query -> LLM (Ollama) -> strict JSON DSL
2. DSL -> deterministic SQL templates (allowlist fields only)
3. SQL safety checks (SELECT only, single statement, table allowlist)
4. SQL execution with timeout + row limit
5. Vega-Lite chart spec + short summary

### Required env vars

- `OLLAMA_BASE_URL` (default `http://ollama:11434`)
- `AI_AGENT_OLLAMA_MODEL` (recommended `qwen2.5:7b-instruct-q4_K_M`)
- `DEFAULT_DAYS_RANGE` (default `30`)
- `MAX_ROWS` (default `500`)
- `SQL_TIMEOUT_SECONDS` (default `5`)
- `OLLAMA_TIMEOUT_SECONDS` (default `30`)

### Request / Response

`POST /api/v1/analytics/query`

```json
{
  "query": "Покажи распределение типов обращений по городам за 30 дней"
}
```

Response:

```json
{
  "request_id": "uuid",
  "dsl": {},
  "sql": "SELECT ...",
  "data": [],
  "chart_spec": {},
  "summary": "..."
}
```

### cURL examples

```bash
curl -X POST http://localhost:8001/api/v1/analytics/query \
  -H "Content-Type: application/json" \
  -d '{"query":"Покажи распределение типов обращений по городам"}'
```

```bash
curl -X POST http://localhost:8001/api/v1/analytics/query \
  -H "Content-Type: application/json" \
  -d '{"query":"Тренд обращений по дням за последние 2 недели"}'
```

### DSL examples (expected shape)

1. Query: `Покажи распределение типов обращений по городам`

```json
{
  "intent": "distribution",
  "metrics": [{"name":"count","field":"*","as":"tickets"}],
  "dimensions": ["city","ticket_type"],
  "filters": [],
  "time_grain": "null",
  "limit": 100,
  "chart": {"type":"stacked_bar","x":"city","y":"tickets","series":"ticket_type"}
}
```

2. Query: `Тренд обращений по дням за 30 дней`

```json
{
  "intent": "trend",
  "metrics": [{"name":"count","field":"*","as":"tickets"}],
  "dimensions": ["created_at"],
  "filters": [{"field":"created_at","op":">=","value":"<ISO_DATETIME>"}],
  "time_grain": "day",
  "limit": 100,
  "chart": {"type":"line","x":"created_at","y":"tickets","series":null}
}
```

3. Query: `Топ-10 городов по количеству обращений`

```json
{
  "intent": "top_n",
  "metrics": [{"name":"count","field":"*","as":"tickets"}],
  "dimensions": ["city"],
  "filters": [],
  "time_grain": "null",
  "limit": 10,
  "chart": {"type":"bar","x":"city","y":"tickets","series":null}
}
```

4. Query: `Сравни тональность обращений по сегментам`

```json
{
  "intent": "comparison",
  "metrics": [{"name":"count","field":"*","as":"tickets"}],
  "dimensions": ["segment","sentiment"],
  "filters": [],
  "time_grain": "null",
  "limit": 100,
  "chart": {"type":"stacked_bar","x":"segment","y":"tickets","series":"sentiment"}
}
```

5. Query: `Покажи таблицу последних обращений`

```json
{
  "intent": "table",
  "metrics": [],
  "dimensions": ["created_at","city","ticket_type","priority"],
  "filters": [],
  "time_grain": "null",
  "limit": 50,
  "chart": {"type":"table","x":"created_at","y":"priority","series":null}
}
```
