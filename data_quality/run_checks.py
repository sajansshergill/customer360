#!/usr/bin/env python3
"""Lightweight DuckDB data-quality checks driven by JSON suites."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import duckdb

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

from config.settings import get_settings

SUITE_DIR = Path(__file__).parent / "great_expectations" / "expectations"


def run_expectation(con: duckdb.DuckDBPyConnection, exp: dict) -> tuple[bool, str]:
    kind = exp["expectation_type"]
    table = exp["kwargs"]["table"]
    if kind == "expect_table_row_count_to_be_between":
        n = con.execute(f"select count(*) from {table}").fetchone()[0]
        lo = exp["kwargs"].get("min_value", 0)
        hi = exp["kwargs"].get("max_value", 10**12)
        ok = lo <= n <= hi
        return ok, f"{table} row_count={n} expected [{lo}, {hi}]"
    if kind == "expect_column_values_to_be_unique":
        col = exp["kwargs"]["column"]
        dupes = con.execute(
            f"""
            select {col}, count(*) c from {table}
            group by 1 having count(*) > 1 limit 1
            """
        ).fetchone()
        ok = dupes is None
        return ok, f"{table}.{col} unique={ok}"
    if kind == "expect_column_values_to_not_be_null":
        col = exp["kwargs"]["column"]
        nulls = con.execute(
            f"select count(*) from {table} where {col} is null"
        ).fetchone()[0]
        ok = nulls == 0
        return ok, f"{table}.{col} nulls={nulls}"
    if kind == "expect_compound_columns_to_be_unique":
        cols = ", ".join(exp["kwargs"]["column_list"])
        dupes = con.execute(
            f"select {cols}, count(*) c from {table} group by {cols} having count(*) > 1 limit 1"
        ).fetchone()
        ok = dupes is None
        return ok, f"{table} compound unique on ({cols})={ok}"
    return False, f"unknown expectation {kind}"


def main() -> int:
    settings = get_settings()
    if not settings.warehouse_path.exists():
        print("Warehouse missing — run pipeline first", file=sys.stderr)
        return 1

    con = duckdb.connect(str(settings.warehouse_path), read_only=True)
    failures = 0
    try:
        for suite_path in sorted(SUITE_DIR.glob("*_suite.json")):
            suite = json.loads(suite_path.read_text())
            print(f"Suite: {suite.get('name', suite_path.name)}")
            for exp in suite.get("expectations", []):
                ok, msg = run_expectation(con, exp)
                status = "PASS" if ok else "FAIL"
                print(f"  [{status}] {msg}")
                if not ok:
                    failures += 1
    finally:
        con.close()

    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
