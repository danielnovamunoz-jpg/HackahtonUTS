from fastapi import APIRouter, Depends
from app.api.dependencies import get_model_service
from app.services.model_service import ModelService
from app.utils.serialization import records

router = APIRouter(tags=["Análisis"])

@router.get("/variables")
def variables(service: ModelService = Depends(get_model_service)):
    return {
        "variables_csv": list(service.events.columns),
        "variables_derivadas_nivel_1": [
            {"nombre": "fuente_id", "descripcion": "Grupo HDBSCAN asignado al sismo; -1 significa ruido/no asignado."},
            {"nombre": "es_nido", "descripcion": "Etiqueta heurística por profundidad y cercanía a la referencia del Nido de Bucaramanga."},
            {"nombre": "es_difuso", "descripcion": "Evento que el agrupamiento no asignó a una fuente."},
        ],
        "variables_municipio_nivel_2": service.metadata.get("variables_kmeans", []),
        "nota": "Clasificación relativa; no es pronóstico ni riesgo absoluto.",
    }

@router.get("/zona-foco")
def focus_zone(service: ModelService = Depends(get_model_service)):
    focus_names = {"bucaramanga", "floridablanca", "girón", "giron", "piedecuesta", "los santos"}
    is_focus = service.municipalities["municipio"].str.casefold().isin(focus_names)
    focus, rest = service.municipalities[is_focus], service.municipalities[~is_focus]
    metrics = ["cantidad_sismos", "magnitud_maxima", "magnitud_media", "porcentaje_nido", "porcentaje_difuso", "indice_relativo"]
    def summary(df):
        return {
            "municipios": int(len(df)),
            "media": {m: round(float(df[m].mean()), 3) if len(df) else None for m in metrics},
            "lista": df["municipio"].tolist(),
        }
    return {"zona_foco": summary(focus), "resto_santander": summary(rest), "nota": "Solo incluye municipios presentes en el CSV."}

@router.get("/validacion")
def validation(service: ModelService = Depends(get_model_service)):
    if "anio" not in service.events.columns or service.events["anio"].notna().sum() == 0:
        return {"disponible": False, "motivo": "El CSV no tiene una columna año utilizable."}
    counts = service.events.groupby("anio").size().reset_index(name="sismos")
    return {
        "disponible": True,
        "anios": [int(service.events["anio"].min()), int(service.events["anio"].max())],
        "filas_por_anio": records(counts),
        "nota": "Resumen temporal descriptivo; no equivale a validación predictiva independiente.",
    }

@router.get("/salidas/resumen")
def summary(service: ModelService = Depends(get_model_service)):
    top = service.municipalities.sort_values("indice_relativo", ascending=False).head(10)
    return {
        "modelo": service.metadata,
        "distribucion_niveles": service.levels_summary(),
        "top_10": records(top),
        "fuentes": records(service.sources.sort_values("cantidad_sismos", ascending=False)) if not service.sources.empty else [],
    }
