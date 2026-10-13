from fastapi import APIRouter, Depends
from app.api.dependencies import get_model_service
from app.services.model_service import ModelService
from app.utils.serialization import records

router = APIRouter(tags=["Fuentes"])

@router.get("/fuentes")
def list_sources(service: ModelService = Depends(get_model_service)):
    if service.sources.empty:
        return {"total": 0, "fuentes": [], "nota": "No se detectaron grupos distintos del ruido en el CSV."}
    df = service.sources.sort_values("cantidad_sismos", ascending=False)
    return {"total": int(len(df)), "fuentes": records(df)}
