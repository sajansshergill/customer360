"""Run lightweight DuckDB data-quality checks."""
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(_ROOT), str(_ROOT / "src")]

import os
import subprocess
import streamlit as st

from dashboard.bootstrap import ensure_warehouse

st.title("Data Quality")


@st.cache_resource
def _boot():
    return str(ensure_warehouse())


_boot()
if st.button("Run checks"):
    result = subprocess.run(
        [sys.executable, str(_ROOT / "data_quality" / "run_checks.py")],
        capture_output=True,
        text=True,
        cwd=str(_ROOT),
        env={**os.environ, "PYTHONPATH": f"{_ROOT / 'src'}:{_ROOT}"},
    )
    st.code((result.stdout or "") + (result.stderr or ""))
    st.write("Exit code:", result.returncode)
