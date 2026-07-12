from fastapi import APIRouter

from src.core.config import settings

router = APIRouter(prefix="/system", tags=["System"])


@router.get("/info")
def system_info():
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "environment": settings.app_env,
        "architecture": "enterprise-foundation",
        "modules": [
            "auth",
            "stores",
            "products",
            "analytics",
            "pricing",
            "ai",
            "wildberries",
        ],
    }
