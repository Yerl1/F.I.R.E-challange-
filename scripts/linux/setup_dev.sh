#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

if ! command -v python3 >/dev/null 2>&1; then
  echo "python3 is required."
  exit 1
fi

if ! command -v npm >/dev/null 2>&1; then
  echo "npm is required."
  exit 1
fi

echo "[1/3] Setup backend virtualenv"
python3 -m venv "${ROOT_DIR}/backend/.venv"
source "${ROOT_DIR}/backend/.venv/bin/activate"
python -m pip install -U pip
python -m pip install -r "${ROOT_DIR}/backend/requirements.txt"
deactivate

echo "[2/3] Setup pipeline-service virtualenv"
python3 -m venv "${ROOT_DIR}/pipeline-service/.venv"
source "${ROOT_DIR}/pipeline-service/.venv/bin/activate"
python -m pip install -U pip setuptools wheel
python -m pip install -e "${ROOT_DIR}/pipeline-service[dev]"
deactivate

echo "[3/3] Install frontend dependencies"
cd "${ROOT_DIR}/front"
if [ -f package-lock.json ]; then
  npm ci
else
  npm install
fi

echo "Development setup complete."
