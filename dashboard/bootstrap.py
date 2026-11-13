"""Shared Streamlit bootstrap: PYTHONPATH + warehouse readiness for local/cloud."""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
for p in (str(ROOT), str(SRC)):
    if p not in sys.path:
        sys.path.insert(0, p)

# Streamlit Community Cloud: ephemeral FS — keep DuckDB under /tmp.
_cloud = (
    os.getenv("STREAMLIT_RUNTIME_ENV") == "cloud"
    or Path("/mount/src").exists()
    or os.getenv("STREAMLIT_SHARING_MODE") == "streamlit"
)
if _cloud:
    os.environ.setdefault("CONSUMER360_WAREHOUSE", "/tmp/consumer360.duckdb")
    os.environ.setdefault("CONSUMER360_ACTIVATION_DIR", "/tmp/activations")
    os.environ.setdefault("CONSUMER360_DATA_DIR", str(ROOT / "data" / "synthetic" / "output"))


def ensure_warehouse(profiles: int = 300) -> Path:
    """Generate synthetic sources (if needed) and run the pipeline once per process."""
    from config.settings import get_settings
    from consumer360.pipeline import run_pipeline

    settings = get_settings()
    if settings.warehouse_path.exists():
        return settings.warehouse_path

    settings.warehouse_path.parent.mkdir(parents=True, exist_ok=True)
    settings.activation_dir.mkdir(parents=True, exist_ok=True)
    settings.data_dir.mkdir(parents=True, exist_ok=True)

    needed = [
        "sap_cdc_profiles.csv",
        "sfmc_engagement.csv",
        "ga4_events.csv",
        "aem_content.csv",
        "commerce_orders.csv",
    ]
    if not all((settings.data_dir / f).exists() for f in needed):
        subprocess.check_call(
            [sys.executable, str(ROOT / "data" / "synthetic" / "generate.py"), str(profiles)],
            cwd=str(ROOT),
            env={**os.environ, "PYTHONPATH": f"{SRC}:{ROOT}"},
        )

    run_pipeline(settings)
    return settings.warehouse_path
