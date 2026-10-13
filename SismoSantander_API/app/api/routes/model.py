from fastapi import APIRouter, Depends, Request, HTTPException
from app.api.dependencies import get_model_service
from app.services.model_service import ModelService

router = APIRouter(tags=["Modelo"])

@router.get("/modelo")
def model_info(service: ModelService = Depends(get_model_service)):
    return service.metadata

@router.post("/recargar")
def reload_model(request: Request):
    service: ModelService = request.app.state.model_service
    service.reload()
    if not service.is_ready:
        raise HTTPException(status_code=400, detail=service.startup_error)
    return {"mensaje": "CSV recargado y modelos entrenados de nuevo", **service.metadata}
