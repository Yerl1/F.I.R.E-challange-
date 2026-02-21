# Pipeline Service

DDD-style pipeline service scaffold using LangGraph and Ollama integration points.

## What is implemented now

- Full project structure for a standalone `pipeline-service` repository.
- LangGraph workflow with required branching/join topology.
- Stub node logic with deterministic mock outputs.
- CLI runner for sample ticket processing.
- In-memory + JSON-file persistence stub.
- Smoke test for end-to-end graph execution.

## Run with Docker Compose

```bash
cd pipeline-service
docker-compose up --build
```

The default compose command runs a smoke graph execution.

## Ollama model setup

The service is non-blocking in mock mode (`MOCK_LLM=1`), so it runs even if model is not pulled.

To prepare real model usage:

```bash
docker-compose up -d ollama
docker exec -it fire-ollama ollama pull llama3.2:1b
```

Then disable mock mode:

```bash
MOCK_LLM=0 docker-compose up --build
```

## Local run (without Docker)

```bash
cd pipeline-service
python -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
python -m pipeline_service.main --sample
pytest -q
```

## Where to change logic

- Graph topology: `src/pipeline_service/application/graph/ticket_graph.py`
- Nodes: `src/pipeline_service/application/nodes/`
- Domain entities/value objects: `src/pipeline_service/domain/entities/`
- LLM integration: `src/pipeline_service/infrastructure/llm/ollama_client.py`
- Persistence strategy: `src/pipeline_service/infrastructure/persistence/repository.py`
