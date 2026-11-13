#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
export PYTHONPATH="${ROOT}/src:${ROOT}"

if [[ ! -d .venv ]]; then
  python3 -m venv .venv
  . .venv/bin/activate
  pip install -q -U pip
  pip install -q -r requirements.txt -r requirements-dev.txt
  pip install -q -e .
else
  # shellcheck disable=SC1091
  source .venv/bin/activate
fi

python -m consumer360.cli pipeline "$@"
