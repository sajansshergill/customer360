"""FastAPI dependencies: warehouse connection + API-key check, shared by all routers."""
import duckdb
from fastapi import Header, HTTPException

from config.settings import get_settings


def get_con():
    """Read-only handle so API requests never conflict with each other."""
    return duckdb.connect(str(get_settings().warehouse_path), read_only=True)


def require_api_key(x_api_key: str = Header(default="")):
    # Local default: empty header or "dev-key". Non-empty wrong keys are rejected.
    if x_api_key and x_api_key != "dev-key":
        raise HTTPException(401, "invalid api key")
    return True
