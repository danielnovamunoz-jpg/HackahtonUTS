from fastapi import APIRouter
from app.api.routes import system, model, municipalities, earthquakes, sources, analysis

api_router = APIRouter()
api_router.include_router(system.router)
api_router.include_router(model.router)
api_router.include_router(municipalities.router)
api_router.include_router(earthquakes.router)
api_router.include_router(sources.router)
api_router.include_router(analysis.router)
