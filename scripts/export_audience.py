#!/usr/bin/env python3
"""CLI activation export (uses warehouse + consent filter)."""
import argparse
import sys
from pathlib import Path

import duckdb

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

from config.settings import get_settings
from consumer360.activation.exporter import export_audience


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("audience_id")
    parser.add_argument("--out-dir", type=Path, default=None)
    args = parser.parse_args()
    settings = get_settings()
    out = args.out_dir or settings.activation_dir
    con = duckdb.connect(str(settings.warehouse_path))
    try:
        path = export_audience(con, args.audience_id, out)
    finally:
        con.close()
    print(path)


if __name__ == "__main__":
    main()
