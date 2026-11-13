import os
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

@dataclass(frozen=True)
class Settings:
    target: str = os.getenv("TARGET", "local")          # local = DuckDB, gcp = BigQuery
    salt: str = os.getenv("CONSUMER360_SALT", "dev-salt")
    data_dir: Path = ROOT / "data" / "synthetic" / "output"
    gcp_project: str = os.getenv("GCP_PROJECT", "")
    bq_prefix: str = os.getenv("BQ_DATASET_PREFIX", "consumer360")

    @property
    def bronze_dataset(self): return f"{self.bq_prefix}_bronze"
    @property
    def silver_dataset(self): return f"{self.bq_prefix}_silver"
    @property
    def gold_dataset(self): return f"{self.bq_prefix}_gold"

def get_settings() -> Settings:
    return Settings()
