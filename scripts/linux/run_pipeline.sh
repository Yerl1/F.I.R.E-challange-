#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

if [ ! -f "${ROOT_DIR}/pipeline-service/.venv/bin/activate" ]; then
  echo "Missing pipeline virtualenv. Run: bash scripts/linux/setup_dev.sh"
  exit 1
fi

source "${ROOT_DIR}/pipeline-service/.venv/bin/activate"

if [ -f "${ROOT_DIR}/.env" ]; then
  set -a
  source "${ROOT_DIR}/.env"
  set +a
fi

cd "${ROOT_DIR}/pipeline-service"
exec python -m pipeline_service.main "$@"
