"""API router: thin HTTP layer only - all logic lives in api/services/."""
from fastapi import APIRouter, Depends, HTTPException

from api.deps import require_api_key
from api.services.activation_service import activation_file, list_activation_files
from api.schemas.activation import ActivationOut

router = APIRouter(prefix="/v1", tags=["activation"])


@router.post("/audiences/{audience_id}/activate", response_model=ActivationOut)
def activate(audience_id: str, _=Depends(require_api_key)):
    p = activation_file(audience_id)
    if not p:
        raise HTTPException(404, "audience export not found - run the pipeline first")
    # Count data rows (exclude header)
    exported = max(sum(1 for _ in p.open()) - 1, 0)
    return ActivationOut(audience_id=audience_id, exported=exported, status="exported")


@router.get("/activations")
def list_activations(_=Depends(require_api_key)):
    return list_activation_files()
