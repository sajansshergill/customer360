"""Request/response schemas (Pydantic) for the API - these are the API contract."""

from pydantic import BaseModel
class ActivationOut(BaseModel):
    audience_id: str;
    exported: int;
    status: str = "exported"