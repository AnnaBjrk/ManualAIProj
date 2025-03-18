# fil för alla routers - håller reda på endpoints
from fastapi import APIRouter

from app.api.v1.core.endpoints.general import router as general_router
from app.api.v1.core.endpoints.upload import router as upload_router  # För filuppdatering
from app.api.v1.core.endpoints.authentication import router as auth_router
from app.api.v1.core.endpoints.llm_request import router as llm_router
router = APIRouter()

router.include_router(general_router)
router.include_router(upload_router)  # filuppdatering
router.include_router(auth_router)  # authentication tokens
router.include_router(llm_router)  # llm request
