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

This default install is lightweight (no heavy local ML/OCR packages).
If you need full local inference stack, install:

```bash
python -m pip install -e '.[dev,full]'
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
- `TYPE_MODEL_PATH`
- `SPAM_MODEL_PATH`
- `SPAM_THRESHOLD` (optional, default `0.5`)
- `PERSIST_MODE` (`local` or `postgres`)
- `PERSIST_POSTGRES_DSN` (optional, used when `PERSIST_MODE=postgres`)
- `PERF_MODE` (optional)
- `PERF_WARMUP` (optional)
- `TORCH_NUM_THREADS` (optional)
- `TORCH_NUM_INTEROP_THREADS` (optional)
- `OLLAMA_NUM_PREDICT` (optional)
- `OLLAMA_NUM_CTX` (optional)
- `GEOCODER_TIMEOUT_SECONDS` (optional)

Load env into current shell:

```bash
cd /home/arsen/F.I.R.E-challange-/pipeline-service
set -a
source ../.env
set +a
```

Windows PowerShell:

```powershell
cd C:\Users\7ruta\Desktop\fire demo\F.I.R.E-challange-\pipeline-service
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\load_env.ps1
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
ollama pull qwen2.5:7b-instruct-q4_K_M
```

Set one in `.env`:

```bash
OLLAMA_MODEL=llama3.2:1b
# or
OLLAMA_MODEL=qwen2.5:7b-instruct-q4_K_M
```

If Ollama runs in Docker (`ollama` service in compose), pull model inside container:

```bash
cd /home/arsen/F.I.R.E-challange-/pipeline-service
docker compose up -d ollama
docker compose exec ollama ollama pull llama3.2:1b
docker compose exec ollama ollama pull qwen2.5:7b-instruct-q4_K_M
docker compose exec ollama ollama list
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
Set valid local path in `SENTIMENT_MODEL_PATH` (default is `models/sentiment`).

### `TYPE` model path does not exist
Set valid local path in `TYPE_MODEL_PATH` to your custom type-recognition artifacts folder
(for example, `.../type_recognition` with `best_model.pt`, `label_encoder.pkl`, and `xlmr_model/tokenizer.json`).

Inference-only copy (Windows PowerShell):

```powershell
cd C:\Users\7ruta\Desktop\fire demo\F.I.R.E-challange-\pipeline-service
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\prepare_type_model.ps1
```

This script keeps only required inference artifacts in `pipeline-service\models\type_recognition`:
- `best_model.pt` (or `xlmr_final.pt`)
- `label_encoder.pkl`
- `xlmr_model\tokenizer.json`
- `xlmr_model\tokenizer_config.json`

### Spam model artifacts (inference only)
For spam inference node, keep only HF inference artifacts under `pipeline-service/models/spam_detection`:
- `config.json`
- `model.safetensors` (or `pytorch_model.bin`)
- `tokenizer.json`
- `tokenizer_config.json`
- optional tokenizer helper files (`special_tokens_map.json`, `vocab.json`, `merges.txt`)

You can remove training files and datasets from your source folder after copying these artifacts.

### Persist to PostgreSQL instead of local JSON
By default, `persist` node writes JSON files into `PERSIST_DIR`.

To write into PostgreSQL table `ticket_results`:

```powershell
$env:PERSIST_MODE="postgres"
$env:PERSIST_POSTGRES_DSN="postgresql://postgres:postgres@localhost:5432/fire_backend"
```

You can also use `BACKEND_DATABASE_URL` instead of `PERSIST_POSTGRES_DSN`.
If Postgres is unavailable or init fails, pipeline falls back to local JSON persistence.

### `fasttext` wheel build fails on Windows
If you are using Windows with Python 3.12 and see a `Failed building wheel for fasttext` error, reinstall after pulling latest changes. The base install now skips `fasttext` on Windows and language detection falls back to default `RU` when the module is unavailable.

### Docker build fails with `Unsupported compiler -- at least C++17 support is needed!`
This comes from `fasttext` wheel build. Rebuild with the updated `Dockerfile` (it installs `g++` in the image):

```bash
cd /home/arsen/F.I.R.E-challange-/pipeline-service
docker compose build --no-cache pipeline-service
docker compose up
```

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
make install_full_deps
make setup_fasttext
make fix_torch_stack
```

`install_deps` installs a lightweight setup.
`install_full_deps` installs ML/OCR extras.
`fix_torch_stack` is useful if you see `torch`/`torchvision`/`torchaudio` mismatch errors.

## 14) Main files to customize

- Graph: `src/pipeline_service/application/graph/ticket_graph.py`
- Summary/recommendation: `src/pipeline_service/application/nodes/get_summary_recommendation.py`
- OCR node: `src/pipeline_service/application/nodes/extract_ocr_text.py`
- OCR client: `src/pipeline_service/infrastructure/ocr/paddleocr_client.py`
- Geo node: `src/pipeline_service/application/nodes/get_geo_data.py`
- Sentiment node: `src/pipeline_service/application/nodes/get_sentiment.py`

## 15) Performance mode

For lower latency with real LLM calls, use:

```bash
PERF_MODE=1
PERF_WARMUP=1
TORCH_NUM_THREADS=4
TORCH_NUM_INTEROP_THREADS=1
OLLAMA_NUM_PREDICT=96
OLLAMA_NUM_CTX=1024
GEOCODER_TIMEOUT_SECONDS=1.0
```

What it does:
- Reuses HTTP connections for Ollama and Nominatim.
- Uses cached Nominatim results for repeated queries.
- Starts `get_sentiment` in parallel with OCR/geo branch.
- Adds optional model warmup at process start.

Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\scripts\load_env.ps1 -EnvFile "C:\Users\7ruta\Desktop\fire demo\F.I.R.E-challange-\.env"
