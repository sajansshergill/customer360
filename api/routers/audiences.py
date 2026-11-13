"""API router: thin HTTP layer only - all logic lives in api/services/."""
from fastapi import APIRouter, Depends, HTTPException

from api.deps import get_con, require_api_key
from api.services.audience_service import fetch_audiences

router = APIRouter(prefix="/v1/audiences", tags=["audiences"])


@router.get("")
def list_audiences(_=Depends(require_api_key)):
    con = get_con()
    out = fetch_audiences(con)
    con.close()
    return out


@router.get("/{audience_id}/members")
def list_audience_members(audience_id: str, _=Depends(require_api_key)):
    con = get_con()
    try:
        tables = {r[0] for r in con.execute("SHOW TABLES").fetchall()}
        if audience_id not in tables:
            raise HTTPException(404, "audience not found")
        rows = con.execute(
            f"""
            SELECT a.golden_profile_id
            FROM {audience_id} a
            JOIN int_consent_latest c ON c.golden_profile_id = a.golden_profile_id
            WHERE c.marketing_consent = true
            """
        ).fetchall()
        return [{"golden_profile_id": r[0]} for r in rows]
    finally:
        con.close()
