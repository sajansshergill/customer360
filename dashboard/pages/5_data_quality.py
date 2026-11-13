"""Streamlit page - run lightweight DQ checks."""
import streamlit as st
import subprocess
import sys
from pathlib import Path

st.title("Data Quality")
root = Path(__file__).resolve().parents[2]
if st.button("Run checks"):
    result = subprocess.run(
        [sys.executable, str(root / "data_quality" / "run_checks.py")],
        capture_output=True,
        text=True,
        cwd=str(root),
        env={**dict(**__import__("os").environ), "PYTHONPATH": f"{root / 'src'}:{root}"},
    )
    st.code((result.stdout or "") + (result.stderr or ""))
    st.write("Exit code:", result.returncode)
