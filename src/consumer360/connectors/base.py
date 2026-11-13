import csv
from pathlib import Path


class BaseConnector:
    def __init__(self, data_dir: Path):
        self.data_dir = Path(data_dir)

    def file_path(self, filename: str) -> Path:
        return self.data_dir / filename

    def read_csv(self, filename: str) -> list[dict]:
        path = self.file_path(filename)
        if not path.exists():
            return []
        with path.open(newline="", encoding="utf-8") as f:
            return list(csv.DictReader(f))

    def validate(self, rows: list[dict], required_cols: list[str]) -> None:
        if not rows:
            return
        keys = set(rows[0].keys())
        missing = [c for c in required_cols if c not in keys]
        if missing:
            raise ValueError(f"Missing required columns: {missing}")

    def extract(self) -> list[dict]:
        raise NotImplementedError
