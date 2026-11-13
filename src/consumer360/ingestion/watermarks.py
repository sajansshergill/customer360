from datetime import datetime

import duckdb


def ensure_watermarks_table(con: duckdb.DuckDBPyConnection) -> None:
    con.execute(
        """
        CREATE TABLE IF NOT EXISTS ingestion_watermarks (
            source VARCHAR PRIMARY KEY,
            watermark TIMESTAMP
        )
        """
    )


def get_watermark(con: duckdb.DuckDBPyConnection, source: str) -> datetime | None:
    ensure_watermarks_table(con)
    row = con.execute(
        "SELECT watermark FROM ingestion_watermarks WHERE source = ?", [source]
    ).fetchone()
    return row[0] if row else None


def set_watermark(con: duckdb.DuckDBPyConnection, source: str, watermark: datetime) -> None:
    ensure_watermarks_table(con)
    con.execute("DELETE FROM ingestion_watermarks WHERE source = ?", [source])
    con.execute(
        "INSERT INTO ingestion_watermarks (source, watermark) VALUES (?, ?)",
        [source, watermark],
    )
