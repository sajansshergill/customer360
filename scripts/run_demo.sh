#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

bash scripts/run_pipeline.sh --profiles 500

echo "Starting API on :8000 and dashboard on :8501 (Ctrl+C to stop)"
export PYTHONPATH="${ROOT}/src:${ROOT}"
# shellcheck disable=SC1091
source .venv/bin/activate

uvicorn api.main:app --host 127.0.0.1 --port 8000 &
API_PID=$!
streamlit run dashboard/app.py --server.port 8501 &
DASH_PID=$!

trap 'kill $API_PID $DASH_PID 2>/dev/null || true' EXIT
wait
