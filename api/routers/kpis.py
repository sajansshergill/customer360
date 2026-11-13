"""API router: thin HTTP layer only - all logic lives in api/services/."""
from fastapi import APIRouter, Depends
from api.deps import get_con, require_api_key
router=APIRouter(prefix="/v1/kpis", tags=["kpis"])
@router.get("/daily")
def daily_kpis(_=Depends(require_api_key)):
    con=get_con()
    c=con.execute("select count(*), avg(case when marketing_consent then 1.0 else 0 end) from gold_consumer_360").fetchone()
    p=con.execute("select count(*) from gold_professional_360").fetchone()[0]; con.close()
    return {"consumers":c[0],"professionals":p,"consent_rate":round(c[1],3) if c[1] else 0}
