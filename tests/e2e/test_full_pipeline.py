import shutil
import subprocess
import sys
from pathlib import Path

import duckdb

from config.settings import Settings
from consumer360.pipeline import run_pipeline

ROOT = Path(__file__).resolve().parents[2]


def test_full_pipeline_with_synthetic_profiles(tmp_path):
    out_dir = tmp_path / "synthetic"
    out_dir.mkdir()
    db = tmp_path / "consumer360.duckdb"
    act = tmp_path / "activations"
    subprocess.check_call(
        [
            sys.executable,
            str(ROOT / "data" / "synthetic" / "generate.py"),
            "50",
            "--seed",
            "99",
        ],
        cwd=str(ROOT),
        env={**dict(**__import__("os").environ), "PYTHONPATH": f"{ROOT / 'src'}:{ROOT}"},
    )
    generated = ROOT / "data" / "synthetic" / "output"
    for name in [
        "sap_cdc_profiles.csv",
        "sfmc_engagement.csv",
        "ga4_events.csv",
        "aem_content.csv",
        "commerce_orders.csv",
    ]:
        shutil.copy(generated / name, out_dir / name)

    settings = Settings(data_dir=out_dir, warehouse_path=db, activation_dir=act)
    run_pipeline(settings)
    con = duckdb.connect(str(db), read_only=True)
    try:
        golden = con.execute("SELECT count(DISTINCT golden_profile_id) FROM node_golden_map").fetchone()[0]
        assert golden > 0
        summary = con.execute("SELECT count(*) FROM gold_audience_summary").fetchone()[0]
        assert summary == 4
    finally:
        con.close()
