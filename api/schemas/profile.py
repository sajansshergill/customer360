"""Request/response schemas (Pydantic) for the API - these are the API contract."""
from pydantic import BaseModel
class ProfileOut(BaseModel):
    golden_profile_id: str; first_name: str = ""; last_name: str = ""; email: str = ""
    is_professional: bool = False; marketing_consent: bool = False; order_count: int = 0; total_spend: float = 0.0
