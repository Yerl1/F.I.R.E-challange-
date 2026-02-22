#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

if [ ! -f "${ROOT_DIR}/backend/.venv/bin/activate" ]; then
  echo "Missing backend virtualenv. Run: bash scripts/linux/setup_dev.sh"
  exit 1
fi

source "${ROOT_DIR}/backend/.venv/bin/activate"

if [ -f "${ROOT_DIR}/.env" ]; then
  set -a
  source "${ROOT_DIR}/.env"
  set +a
fi

cd "${ROOT_DIR}"
exec uvicorn backend.app.main:app --host 0.0.0.0 --port 8001
