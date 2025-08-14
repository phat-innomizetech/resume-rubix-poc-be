from fastapi import APIRouter

from rubix.core.config import settings

from rubix.api.routes import health, resume

api_router = APIRouter()
api_router.include_router(health.router)


if settings.ENVIRONMENT == "local":
    api_router.include_router(resume.router)
