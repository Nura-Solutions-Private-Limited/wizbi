from app.api.api_v1.endpoints import health
from fastapi import APIRouter

api_router = APIRouter()
api_router.include_router(health.router, prefix="/health", tags=["health"])