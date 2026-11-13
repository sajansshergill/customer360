from __future__ import annotations

import csv
from pathlib import Path

import duckdb
import yaml

from config.settings import ROOT, Settings, get_settings
from consumer360.ingestion.contracts import validate_contract
from consumer360.ingestion.watermarks import set_watermark
from consumer360.utils.dates import utcnow
from consumer360.utils.logging import get_logger

log = get_logger(__name__)
SAMPLES_DIR = ROOT / "data" / "samples"


def _resolve_file(data_dir: Path, filename: str) -> Path:
    primary = data_dir / filename
    if primary.exists():
        return primary
    sample = SAMPLES_DIR / filename
    if sample.exists():
        return sample
    if filename == "aem_content.csv" and (SAMPLES_DIR / "aem_commerce.csv").exists():
        return SAMPLES_DIR / "aem_commerce.csv"
    return primary


def _load_csv_to_table(
    con: duckdb.DuckDBPyConnection, table: str, file_path: Path, source: str
) -> int:
    if not file_path.exists():
        log.warning("Missing file for %s: %s", source, file_path)
        con.execute(f"CREATE OR REPLACE TABLE {table} AS SELECT * FROM (SELECT 1 WHERE 0=1)")
        return 0

    with file_path.open(newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    validate_contract(source, rows)
    loaded = utcnow()
    con.execute(
        f"""
        CREATE OR REPLACE TABLE {table} AS
        SELECT *, ?::TIMESTAMP AS _loaded_at, ?::VARCHAR AS _source_file
        FROM read_csv_auto(?, header=true)
        """,
        [loaded, file_path.name, str(file_path)],
    )
    count = con.execute(f"SELECT count(*) FROM {table}").fetchone()[0]
    set_watermark(con, source, loaded)
    return count


def load_source_bronze(con: duckdb.DuckDBPyConnection, settings: Settings, source: str) -> int:
    cfg_path = ROOT / "config" / "sources.yaml"
    cfg = yaml.safe_load(cfg_path.read_text())["sources"]
    if source not in cfg:
        raise ValueError(f"Unknown source: {source}")
    meta = cfg[source]
    file_path = _resolve_file(settings.data_dir, meta["file"])
    return _load_csv_to_table(con, meta["table"], file_path, source)


def load_all_bronze(settings: Settings | None = None) -> dict[str, int]:
    settings = settings or get_settings()
    cfg_path = ROOT / "config" / "sources.yaml"
    cfg = yaml.safe_load(cfg_path.read_text())["sources"]
    settings.warehouse_path.parent.mkdir(parents=True, exist_ok=True)
    con = duckdb.connect(str(settings.warehouse_path))
    counts: dict[str, int] = {}
    try:
        for source, meta in cfg.items():
            file_path = _resolve_file(settings.data_dir, meta["file"])
            n = _load_csv_to_table(con, meta["table"], file_path, source)
            counts[source] = n
            log.info("Loaded %s rows into %s from %s", n, meta["table"], file_path)
    finally:
        con.close()
    return counts
