"""Consumer360 API (FastAPI). Versioned under /v1 and API-key ready, 
so it can sit behind an API gateway (e.g. Apigee) exactly like the 
JD describes."""

from fastapi import FastAPI
from api.routers import profiles, audiences, activation, kpis

app = FastAPI(title="Consumer360 API", version="1.0.0", description="Profile, audience and activation API for the Consumer360 CDP")
app.include_router(profiles.router);
app.include_router(audiences.router);
app.include_router(activation.router);
app.include_router(kpis.router);
@app.get("/health")
def health():
    return {"ok": True, "service": "consumer360"}