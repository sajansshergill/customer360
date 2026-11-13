import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

from config.settings import Settings
from consumer360.pipeline import run_pipeline


@pytest.fixture
def tmp_settings(tmp_path, monkeypatch):
    db = tmp_path / "warehouse.duckdb"
    data_dir = ROOT / "data" / "samples"
    act = tmp_path / "activations"
    monkeypatch.setenv("CONSUMER360_WAREHOUSE", str(db))
    monkeypatch.setenv("CONSUMER360_DATA_DIR", str(data_dir))
    monkeypatch.setenv("CONSUMER360_ACTIVATION_DIR", str(act))
    settings = Settings(
        data_dir=data_dir,
        warehouse_path=db,
        activation_dir=act,
    )
    # Re-apply after __post_init__ env reads in case defaults were used
    object.__setattr__(settings, "data_dir", data_dir)
    object.__setattr__(settings, "warehouse_path", db)
    object.__setattr__(settings, "activation_dir", act)
    return settings


@pytest.fixture
def seeded_warehouse(tmp_settings, monkeypatch):
    run_pipeline(tmp_settings)
    monkeypatch.setattr("config.settings.get_settings", lambda: tmp_settings)
    monkeypatch.setattr("api.deps.get_settings", lambda: tmp_settings)
    yield tmp_settings
