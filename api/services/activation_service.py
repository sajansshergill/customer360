"""Service layer: warehouse queries and business logic behind the API routers."""
from pathlib import Path

from config.settings import get_settings


def activation_file(audience_id: str) -> Path | None:
    p = get_settings().activation_dir / f"{audience_id}.csv"
    return p if p.exists() else None


def list_activation_files() -> list[str]:
    d = get_settings().activation_dir
    if not d.exists():
        return []
    return sorted(p.name for p in d.glob("*.csv"))
