from fastapi import APIRouter, Depends, HTTPException, Query
from app.api.dependencies import get_model_service
from app.services.model_service import ModelService
from app.utils.serialization import records

router = APIRouter(tags=["Municipios"])

@router.get("/niveles")
def levels(service: ModelService = Depends(get_model_service)):
    df = service.municipalities
    rows = []
    for level in service.levels:
        subset = df[df["nivel"] == level]
        if not subset.empty:
            rows.append({
                "nivel": level,
                "color": service.colors[level],
                "municipios": int(len(subset)),
                "indice_medio": round(float(subset["indice_relativo"].mean()), 2),
                "lista_municipios": subset["municipio"].tolist(),
            })
    return {"niveles": rows}

@router.get("/municipios")
def list_municipalities(
    nivel: str | None = None,
    zona_foco: bool | None = None,
    buscar: str | None = None,
    ordenar_por: str = "indice_relativo",
    descendente: bool = True,
    limite: int = Query(100, ge=1, le=1000),
    service: ModelService = Depends(get_model_service),
):
    df = service.municipalities.copy()
    if nivel:
        if nivel not in service.levels:
            raise HTTPException(status_code=400, detail=f"Nivel inválido. Usa: {', '.join(service.levels)}")
        df = df[df["nivel"] == nivel]
    if zona_foco is not None:
        focus = {"bucaramanga", "floridablanca", "girón", "giron", "piedecuesta", "los santos"}
        mask = df["municipio"].str.casefold().isin(focus)
        df = df[mask] if zona_foco else df[~mask]
    if buscar:
        df = df[df["municipio"].str.contains(buscar, case=False, na=False, regex=False)]
    if ordenar_por not in df.columns:
        raise HTTPException(status_code=400, detail=f"Campo de orden inválido: {ordenar_por}")
    df = df.sort_values(ordenar_por, ascending=not descendente).head(limite)
    return {"total": int(len(df)), "municipios": records(df)}

@router.get("/municipios/{nombre_o_codigo}")
def municipality_detail(nombre_o_codigo: str, service: ModelService = Depends(get_model_service)):
    df = service.municipalities
    normalized = service.normalize_name(nombre_o_codigo)
    match = df[df["municipio"].map(service.normalize_name) == normalized]
    if match.empty:
        raise HTTPException(status_code=404, detail={
            "mensaje": "Municipio no encontrado en el CSV",
            "municipios_disponibles": df["municipio"].tolist()[:20],
        })
    row = match.iloc[0].to_dict()
    name = row["municipio"]
    events = service.events[service.events["municipio"] == name]
    row["sismos_recientes"] = records(events.sort_values("magnitud", ascending=False).head(10))
    return service.json_safe(row)

@router.get("/geojson")
def geojson(service: ModelService = Depends(get_model_service)):
    features = []
    for _, row in service.municipalities.iterrows():
        features.append({
            "type": "Feature",
            "geometry": {"type": "Point", "coordinates": [float(row["lon"]), float(row["lat"])]},
            "properties": service.json_safe(row.to_dict()),
        })
    return {
        "type": "FeatureCollection",
        "features": features,
        "nota": "Puntos aproximados a partir de coordenadas medianas; el CSV no contiene polígonos administrativos.",
    }


@router.get("/comparar")
def compare_municipalities(municipios: str, service: ModelService = Depends(get_model_service)):
    names = [name.strip() for name in municipios.split(",") if name.strip()]
    if not names:
        raise HTTPException(status_code=400, detail="Envía municipios separados por coma.")
    output = []
    normalized = {service.normalize_name(name): name for name in names}
    for requested in names:
        norm = service.normalize_name(requested)
        matches = service.municipalities[
            service.municipalities["municipio"].map(service.normalize_name) == norm
        ]
        if matches.empty:
            raise HTTPException(status_code=404, detail={
                "mensaje": f"Municipio no encontrado: {requested}",
                "municipios_disponibles": service.municipalities["municipio"].tolist()[:20],
            })
        row = matches.iloc[0].to_dict()
        output.append(service.json_safe(row))
    return {"total": len(output), "municipios": output}
