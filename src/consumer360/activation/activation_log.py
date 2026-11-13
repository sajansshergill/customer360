from pathlib import Path

import duckdb

from consumer360.utils.dates import utcnow


def ensure_activation_log(con: duckdb.DuckDBPyConnection) -> None:
    con.execute(
        """
        CREATE TABLE IF NOT EXISTS activation_log (
            audience_id VARCHAR,
            row_count INTEGER,
            file_path VARCHAR,
            activated_at TIMESTAMP
        )
        """
    )


def log_activation(
    con: duckdb.DuckDBPyConnection,
    audience_id: str,
    row_count: int,
    file_path: Path,
) -> None:
    ensure_activation_log(con)
    con.execute(
        """
        INSERT INTO activation_log (audience_id, row_count, file_path, activated_at)
        VALUES (?, ?, ?, ?)
        """,
        [audience_id, row_count, str(file_path), utcnow()],
    )
