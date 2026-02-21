# Pipeline Service

Pipeline service for ticket processing using DDD-style structure and LangGraph orchestration.

## What it does

Given a ticket (JSON or CSV row), the pipeline executes nodes for:

- ingestion and normalization
- OCR extraction from attachment image (if present)
- geodata lookup / fallback
- enriched text construction
- language detection
- sentiment, type, priority
- summary + recommendation
- persistence (stub JSON in `/tmp`)

## Project layout

- `src/pipeline_service/application/graph/ticket_graph.py` - graph topology
- `src/pipeline_service/application/nodes/` - pipeline nodes
- `src/pipeline_service/infrastructure/` - external integrations (LLM, OCR, geo, persistence)
- `tests/` - smoke + unit tests

## Prerequisites

- Python `3.11` or `3.12`
- Docker + Docker Compose (optional, for containerized run)
- Local Ollama installed (optional if `MOCK_LLM=1`)

## 1) Local setup (recommended first)

```bash
cd /home/arsen/F.I.R.E-challange-/pipeline-service
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -U pip setuptools wheel
python -m pip install -e '.[dev]'
```

## 2) Download fastText model (language node)

```bash
cd /home/arsen/F.I.R.E-challange-/pipeline-service
source .venv/bin/activate
make setup_fasttext
```

This downloads:
- `models/lid.176.ftz`

## 3) Configure environment

Environment file is at repo root:
- `/home/arsen/F.I.R.E-challange-/.env`

Current required variables include:

- `MOCK_LLM`
- `OLLAMA_BASE_URL`
- `OLLAMA_MODEL`
- `ENRICH_WITH_LLM`
- `GEOCODER_ENABLED`
- `GEOCODER_BASE_URL`
- `GEO_USE_LLM_NORMALIZATION`
- `GEOCODER_USER_AGENT`
- `FASTTEXT_MODEL_PATH`
- `ATTACHMENTS_DIR`
- `OCR_LANG`
- `OCR_CLEAN_WITH_LLM`
- `SENTIMENT_MODEL_PATH`

Load env into current shell:

```bash
cd /home/arsen/F.I.R.E-challange-/pipeline-service
set -a
source ../.env
set +a
```

Verify:

```bash
echo "$OLLAMA_BASE_URL"
echo "$GEOCODER_BASE_URL"
echo "$FASTTEXT_MODEL_PATH"
```

## 4) Run pipeline on sample built-in ticket

```bash
cd /home/arsen/F.I.R.E-challange-/pipeline-service
source .venv/bin/activate
set -a; source ../.env; set +a
python -m pipeline_service.main --sample
```

## 5) Run pipeline on JSON input

Example input:

```bash
cat > /tmp/ticket.json <<'EOF_JSON'
{
  "ticket_id": "T-1",
  "raw_text": "Проблема с заказом",
  "raw_address": "",
  "country": "KZ",
  "region": "Алматинская",
  "city": "Тургень",
  "street": "Садовая",
  "house": "7",
  "attachments": "/home/arsen/F.I.R.E-challange-/docs/order_error.png"
}
EOF_JSON
```

Run:

```bash
python -m pipeline_service.main --input_type=json --file=/tmp/ticket.json
```

With timing:

```bash
python -m pipeline_service.main --show_timing --input_type=json --file=/tmp/ticket.json
```

## 6) Run pipeline on CSV input

```bash
python -m pipeline_service.main --input_type=csv --file=/absolute/path/to/tickets.csv
```

Each row is processed independently; final state is printed per ticket.

## 7) Test OCR node directly

```bash
cd /home/arsen/F.I.R.E-challange-/pipeline-service
source .venv/bin/activate
set -a; source ../.env; set +a
PYTHONPATH=src python scripts/test_ocr_image.py \
  --image /home/arsen/F.I.R.E-challange-/docs/order_error.png \
  --raw-text "order error screenshot"
```

## 8) Run tests

```bash
cd /home/arsen/F.I.R.E-challange-/pipeline-service
source .venv/bin/activate
python -m pytest -q
```

Targeted tests:

```bash
python -m pytest tests/test_graph_smoke.py -q
python -m pytest tests/test_csv_ingestion.py -q
python -m pytest tests/test_ocr_node.py -q
```

## 9) Docker run

### Option A: from repo root compose

```bash
cd /home/arsen/F.I.R.E-challange-
docker compose up --build
```

### Option B: from service-local compose

```bash
cd /home/arsen/F.I.R.E-challange-/pipeline-service
docker compose up --build
```

## 10) Ollama usage notes

If you want real LLM calls:

```bash
MOCK_LLM=0
```

Ensure local Ollama is running and model is available:

```bash
ollama pull llama3.2:1b
```

If you want pipeline without LLM dependency:

```bash
MOCK_LLM=1
ENRICH_WITH_LLM=0
GEO_USE_LLM_NORMALIZATION=0
OCR_CLEAN_WITH_LLM=0
```

## 11) Geocoder notes

- If running Python on host machine, use:
  - `GEOCODER_BASE_URL=http://localhost:8080`
- If running Python inside compose network, use:
  - `GEOCODER_BASE_URL=http://nominatim:8080`

Quick check:

```bash
curl "$GEOCODER_BASE_URL/search?q=Тургень,Казахстан&format=jsonv2&limit=1&countrycodes=kz"
```

## 12) Common issues

### `make upd_env` did not change env
`make` runs in subshell and does not persist exports in your current shell. Use:

```bash
set -a; source ../.env; set +a
```

### `ModuleNotFoundError: No module named pipeline_service`
Run from `pipeline-service` folder after installing editable package, or use `PYTHONPATH=src`.

### `SENTIMENT model path does not exist`
Set valid local path in `SENTIMENT_MODEL_PATH`.

### OCR returns `ocr_no_text`
- file path may be wrong, or image text is too noisy/small
- test with direct script `scripts/test_ocr_image.py`

### Nominatim 403/406 or empty results
- verify endpoint and headers
- query may be too specific; pipeline already tries broader fallback queries

## 13) Useful make targets

From `pipeline-service/`:

```bash
make install_deps
make setup_fasttext
```

## 14) Main files to customize

- Graph: `src/pipeline_service/application/graph/ticket_graph.py`
- Summary/recommendation: `src/pipeline_service/application/nodes/get_summary_recommendation.py`
- OCR node: `src/pipeline_service/application/nodes/extract_ocr_text.py`
- OCR client: `src/pipeline_service/infrastructure/ocr/paddleocr_client.py`
- Geo node: `src/pipeline_service/application/nodes/get_geo_data.py`
- Sentiment node: `src/pipeline_service/application/nodes/get_sentiment.py`
