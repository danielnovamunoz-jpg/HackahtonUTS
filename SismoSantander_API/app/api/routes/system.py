from fastapi import APIRouter, Request

router = APIRouter(tags=["Sistema"])

@router.get("/salud")
def health(request: Request):
    service = getattr(request.app.state, "model_service", None)
    ready = bool(service and service.is_ready)
    return {
        "estado": "ok" if ready else "error",
        "csv_cargado": ready,
        "filas_validas": service.metadata.get("filas_validas") if ready else 0,
        "municipios": service.metadata.get("municipios_en_csv") if ready else 0,
        "error": None if ready else (service.startup_error if service else "Servicio no inicializado"),
    }
