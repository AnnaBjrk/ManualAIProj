# fil för alla routers - håller reda på endpoints
from fastapi import APIRouter

from app.api.v1.core.endpoints.general import router as general_router
from app.api.v1.core.endpoints.upload import router as upload_router  # För filuppdatering

router = APIRouter()

router.include_router(general_router)
router.include_router(upload_router)  # filuppdatering




