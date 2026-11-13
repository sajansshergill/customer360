from __future__ import annotations

import csv
from pathlib import Path

import duckdb

from consumer360.activation.consent import filter_audience_by_consent
from consumer360.utils.logging import get_logger

log = get_logger(__name__)


def _consent_map(con: duckdb.DuckDBPyConnection) -> dict[str, bool]:
    rows = con.execute(
        "SELECT golden_profile_id, marketing_consent FROM int_consent_latest"
    ).fetchall()
    return {g: bool(c) for g, c in rows}


def export_audience(
    con: duckdb.DuckDBPyConnection, audience_id: str, out_dir: Path
) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    members = [
        r[0]
        for r in con.execute(f"SELECT golden_profile_id FROM {audience_id}").fetchall()
    ]
    consent = _consent_map(con)
    members = filter_audience_by_consent(members, consent)
    if not members:
        path = out_dir / f"{audience_id}.csv"
        with path.open("w", newline="") as f:
            w = csv.writer(f)
            w.writerow(
                ["subscriber_key", "email", "first_name", "last_name", "golden_profile_id"]
            )
        return path

    placeholders = ",".join(["?"] * len(members))
    rows = con.execute(
        f"""
        WITH base AS (
          SELECT * FROM gold_consumer_360
          UNION ALL
          SELECT * FROM gold_professional_360
        )
        SELECT
          coalesce(b.subscriber_key, '') as subscriber_key,
          b.email,
          b.first_name,
          b.last_name,
          b.golden_profile_id
        FROM base b
        JOIN int_consent_latest c ON c.golden_profile_id = b.golden_profile_id
        WHERE b.golden_profile_id IN ({placeholders})
          AND c.marketing_consent = true
        """,
        members,
    ).fetchall()

    path = out_dir / f"{audience_id}.csv"
    with path.open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(
            ["subscriber_key", "email", "first_name", "last_name", "golden_profile_id"]
        )
        w.writerows(rows)
    log.info("Exported %s members to %s", len(rows), path)
    return path
