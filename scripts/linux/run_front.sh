#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
FRONT_DIR="${ROOT_DIR}/front"

if [ ! -d "${FRONT_DIR}/node_modules" ]; then
  echo "Missing frontend dependencies. Run: bash scripts/linux/setup_dev.sh"
  exit 1
fi

if [ -f "${ROOT_DIR}/.env" ]; then
  set -a
  source "${ROOT_DIR}/.env"
  set +a
fi

export NEXT_PUBLIC_API_BASE_URL="${NEXT_PUBLIC_API_BASE_URL:-http://localhost:8001}"

cd "${FRONT_DIR}"
exec npm run dev
