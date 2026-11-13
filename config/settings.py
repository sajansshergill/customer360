"""Part of the Consumer360 CDP - see README for where this file fits."""
import os
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


@dataclass(frozen=True)
class Settings:
    target: str = "local"
    salt: str = "dev-salt"
    data_dir: Path = ROOT / "data" / "synthetic" / "output"
    warehouse_path: Path = ROOT / "data" / "consumer360.duckdb"
    gcp_project: str = ""
    bq_prefix: str = "consumer360"
    activation_dir: Path = ROOT / "output" / "activations"

    def __post_init__(self) -> None:
        object.__setattr__(self, "target", os.getenv("TARGET", self.target))
        object.__setattr__(self, "salt", os.getenv("CONSUMER360_SALT", self.salt))
        object.__setattr__(
            self,
            "data_dir",
            Path(os.getenv("CONSUMER360_DATA_DIR", str(self.data_dir))),
        )
        object.__setattr__(
            self,
            "warehouse_path",
            Path(os.getenv("CONSUMER360_WAREHOUSE", str(self.warehouse_path))),
        )
        object.__setattr__(self, "gcp_project", os.getenv("GCP_PROJECT", self.gcp_project))
        object.__setattr__(self, "bq_prefix", os.getenv("BQ_DATASET_PREFIX", self.bq_prefix))
        object.__setattr__(
            self,
            "activation_dir",
            Path(os.getenv("CONSUMER360_ACTIVATION_DIR", str(self.activation_dir))),
        )

    @property
    def bronze_dataset(self):
        return f"{self.bq_prefix}_bronze"

    @property
    def silver_dataset(self):
        return f"{self.bq_prefix}_silver"

    @property
    def gold_dataset(self):
        return f"{self.bq_prefix}_gold"


def get_settings() -> Settings:
    return Settings()
