from fastapi import APIRouter

from src.api.v1 import agents, ai, analytics, audit, auth, business, dashboard, products, stores, system

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(auth.router)
api_router.include_router(audit.router)
api_router.include_router(ai.router)
api_router.include_router(analytics.router)
api_router.include_router(stores.router)
api_router.include_router(products.router)
api_router.include_router(agents.router)
api_router.include_router(dashboard.router)
api_router.include_router(business.router)
api_router.include_router(system.router)
