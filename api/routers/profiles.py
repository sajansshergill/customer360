"""API router: thin HTTP layer only - all logic lives in api/services/."""
from fastapi import APIRouter, Depends, HTTPException
from api.deps import get_con, require_api_key
from api.services.profile_service import fetch_profile
router=APIRouter(prefix="/v1/profiles", tags=["profiles"])
@router.get("/search")
def search_profiles(email: str = "", _=Depends(require_api_key)):
    con=get_con(); rows=con.execute("select golden_profile_id, email from (select * from gold_consumer_360 union all select * from gold_professional_360) where email like ?",[f"%{email}%"]).fetchall(); con.close()
    return [{"golden_profile_id":g,"email":e} for g,e in rows[:50]]
@router.get("/{golden_profile_id}")
def get_profile(golden_profile_id: str, _=Depends(require_api_key)):
    con=get_con(); p=fetch_profile(con, golden_profile_id); con.close()
    if not p: raise HTTPException(404, "profile not found")
    return p
