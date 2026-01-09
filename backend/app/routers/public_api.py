"""
Public API Router - Public endpoints for external integrations
"""
from fastapi import APIRouter, HTTPException, Header, Depends
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

from ..core.task_manager import task_manager
from ..core.cache import cache
from ..core.logging_config import log_info, log_error

router = APIRouter(prefix="/api/public", tags=["public"])

# Simple API key validation (en producción usar DB)
VALID_API_KEYS = set()  # Se puede poblar desde env o DB


def verify_api_key(api_key: Optional[str] = Header(None, alias="X-API-Key")):
    """Dependency to verify API key."""
    if not api_key or api_key not in VALID_API_KEYS:
        raise HTTPException(status_code=401, detail="Invalid or missing API key")
    return api_key


class PublicGenerationRequest(BaseModel):
    qty: int = Field(ge=1, le=50, description="Number of CVs to generate")
    roles: List[str] = Field(default=["any"], description="Target roles")
    genders: List[str] = Field(default=["any"], description="Genders")
    ethnicities: List[str] = Field(default=["any"], description="Ethnicities")
    origins: List[str] = Field(default=["any"], description="Origins")
    age_min: int = Field(default=18, ge=18, le=70)
    age_max: int = Field(default=70, ge=18, le=70)
    expertise_levels: List[str] = Field(default=["any"], description="Expertise levels")
    remote: bool = Field(default=False, description="Include remote work preference")
    profile_model: Optional[str] = None
    cv_model: Optional[str] = None
    image_model: Optional[str] = None


class PublicGenerationResponse(BaseModel):
    batch_id: str
    status: str
    message: str
    estimated_time: Optional[int] = None  # seconds


@router.post("/generate", response_model=PublicGenerationResponse, dependencies=[Depends(verify_api_key)])
async def public_generate(request: PublicGenerationRequest):
    """
    Public API endpoint to generate CVs.
    Requires X-API-Key header.
    """
    try:
        # Check cache first
        cache_key = cache.generate_key("public_generate", **request.dict())
        cached = cache.get(cache_key)
        if cached:
            log_info("Public API: Cache hit", {"cache_key": cache_key})
            return cached
        
        # Create batch request (similar to internal generate)
        batch_request = {
            **request.dict(),
            "smart_category": True,
            "image_size": 100
        }
        
        # Start generation using the same logic as internal endpoint
        from ..core.task_manager import task_manager
        from ..services.batch_service import process_batch, batch_models
        from fastapi import BackgroundTasks
        
        # Create batch
        batch = await task_manager.create_batch(
            qty=request.qty,
            genders=request.genders,
            ethnicities=request.ethnicities,
            origins=request.origins,
            roles=request.roles,
            age_min=request.age_min,
            age_max=request.age_max,
            expertise_levels=request.expertise_levels,
            remote=request.remote
        )
        
        # Store model selections
        batch_models[batch.id] = {
            "profile_model": request.profile_model,
            "cv_model": request.cv_model,
            "image_model": request.image_model
        }
        
        batch_id = batch.id
        
        response = PublicGenerationResponse(
            batch_id=batch_id,
            status="queued",
            message="Generation started",
            estimated_time=request.qty * 30  # Rough estimate
        )
        
        # Cache response for 5 minutes
        cache.set(cache_key, response, ttl=300)
        
        log_info("Public API: Generation started", {"batch_id": batch_id})
        return response
        
    except Exception as e:
        log_error(e, {"endpoint": "/api/public/generate"})
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status/{batch_id}", dependencies=[Depends(verify_api_key)])
async def public_get_status(batch_id: str):
    """Get batch status via public API."""
    try:
        from ..routers.generation import get_batch_status
        status = await get_batch_status(batch_id)
        return status
    except Exception as e:
        log_error(e, {"endpoint": f"/api/public/status/{batch_id}"})
        raise HTTPException(status_code=404, detail="Batch not found")


@router.get("/files", dependencies=[Depends(verify_api_key)])
async def public_list_files():
    """List generated files via public API."""
    try:
        from ..routers.generation import list_files
        files = await list_files()
        return files
    except Exception as e:
        log_error(e, {"endpoint": "/api/public/files"})
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def public_health():
    """Public health check (no auth required)."""
    return {
        "status": "ok",
        "service": "ai-cv-suite-public-api",
        "timestamp": datetime.now().isoformat()
    }
