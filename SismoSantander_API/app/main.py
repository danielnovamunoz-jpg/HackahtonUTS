from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router
from app.core.config import get_settings
from app.services.model_service import ModelService

settings = get_settings()
model_service = ModelService(settings)

@asynccontextmanager
async def lifespan(app: FastAPI):
    model_service.reload()
    app.state.model_service = model_service
    yield

app = FastAPI(
    title=settings.app_name,
    description=(
        "API modular para análisis descriptivo de sismicidad a partir de un CSV. "
        "HDBSCAN agrupa eventos en fuentes y K-Means agrupa municipios en niveles relativos."
    ),
    version="2.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)

@app.get("/", tags=["Sistema"])
def root():
    return {
        "nombre": settings.app_name,
        "estado": "ok" if model_service.is_ready else "esperando_csv",
        "documentacion": "/docs",
        "version": "2.0.0",
    }
