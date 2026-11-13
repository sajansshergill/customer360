"""Request/response schemas (Pydantic) for the API - these are the API contract."""
from pydantic import BaseModel
class AudienceOut(BaseModel):
    audience_id: str; members: int; exported: int
