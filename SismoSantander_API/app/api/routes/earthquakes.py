from fastapi import APIRouter, Depends, HTTPException, Query
import pandas as pd
from app.api.dependencies import get_model_service
from app.services.model_service import ModelService
from app.utils.serialization import records

router = APIRouter(tags=["Sismos"])

@router.get("/sismos")
def list_earthquakes(
    mag_min: float = Query(0, ge=0, le=10),
    municipio: str | None = None,
    fuente_tipo: str | None = None,
    limite: int = Query(500, ge=1, le=10000),
    periodo: str = "todos",
    service: ModelService = Depends(get_model_service),
):
    df = service.events.copy()
    df = df[df["magnitud"] >= mag_min]
    if municipio:
        df = df[df["municipio"].str.contains(municipio, case=False, na=False, regex=False)]
    if fuente_tipo:
        if fuente_tipo.casefold() == "difusa":
            df = df[df["fuente_id"] == -1]
        elif not service.sources.empty:
            ids = service.sources.loc[
                service.sources["tipo"].str.contains(fuente_tipo, case=False, regex=False), "fuente_id"
            ]
            df = df[df["fuente_id"].isin(ids)]
        else:
            df = df.iloc[0:0]
    if periodo not in {"todos", "variables", "objetivo"}:
        raise HTTPException(status_code=400, detail="periodo debe ser todos, variables u objetivo")
    if periodo != "todos":
        if "anio" not in df.columns or df["anio"].isna().all():
            raise HTTPException(status_code=400, detail="El CSV no tiene año utilizable.")
        years = pd.to_numeric(df["anio"], errors="coerce")
        cutoff = years.quantile(.6)
        df = df[years <= cutoff] if periodo == "variables" else df[years > cutoff]
    df = df.sort_values("magnitud", ascending=False).head(limite)
    return {
        "total": int(len(df)),
        "filtros": {"mag_min": mag_min, "municipio": municipio, "fuente_tipo": fuente_tipo, "periodo": periodo},
        "sismos": records(df),
    }
