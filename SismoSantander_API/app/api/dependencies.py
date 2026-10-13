from fastapi import Request, HTTPException
from app.services.model_service import ModelService

def get_model_service(request: Request) -> ModelService:
    service = getattr(request.app.state, "model_service", None)
    if service is None or not service.is_ready:
        detail = service.startup_error if service else "Servicio de modelo no inicializado."
        raise HTTPException(
            status_code=503,
            detail={
                "mensaje": "La API no tiene datos/modelo disponibles.",
                "error": detail,
                "solucion": "Verifica data/sismos.csv y reinicia o ejecuta POST /recargar.",
            },
        )
    return service
