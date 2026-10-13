import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score

try:
    import hdbscan
except ImportError:
    hdbscan = None

def haversine_km(lat1, lon1, lat2, lon2):
    radius = 6371.0088
    p1, p2 = np.radians(lat1), np.radians(lat2)
    dp, dl = np.radians(lat2 - lat1), np.radians(lon2 - lon1)
    a = np.sin(dp / 2) ** 2 + np.cos(p1) * np.cos(p2) * np.sin(dl / 2) ** 2
    return 2 * radius * np.arcsin(np.sqrt(np.clip(a, 0, 1)))

def cluster_sources(events: pd.DataFrame, settings):
    data = events.copy()
    lat0, lon0 = float(data["latitud"].median()), float(data["longitud"].median())
    data["x_km"] = (data["longitud"] - lon0) * 111.32 * np.cos(np.radians(lat0))
    data["y_km"] = (data["latitud"] - lat0) * 110.574
    xyz = data[["x_km", "y_km", "profundidad"]].to_numpy(dtype=float)
    if hdbscan is not None and len(data) >= 20:
        min_size = max(settings.hdbscan_min_cluster_size, min(30, int(round(len(data) * 0.005))))
        clusterer = hdbscan.HDBSCAN(
            min_cluster_size=min_size,
            min_samples=max(3, min(10, min_size // 2)),
            metric="euclidean",
            cluster_selection_method="eom",
        )
        data["fuente_id"] = clusterer.fit_predict(xyz)
        data["confianza_fuente"] = getattr(clusterer, "probabilities_", np.ones(len(data)))
        algorithm = "HDBSCAN"
    else:
        from sklearn.cluster import DBSCAN
        data["fuente_id"] = DBSCAN(eps=12, min_samples=max(3, min(8, len(data) // 10 or 3))).fit_predict(xyz)
        data["confianza_fuente"] = (data["fuente_id"] != -1).astype(float)
        algorithm = "DBSCAN (respaldo; instala hdbscan y usa al menos 20 filas)"
    source_rows = []
    for index, source_id in enumerate(sorted(i for i in data["fuente_id"].unique() if i != -1), start=1):
        group = data[data["fuente_id"] == source_id]
        depth = float(group["profundidad"].median())
        lat, lon = float(group["latitud"].median()), float(group["longitud"].median())
        distance = float(haversine_km(lat, lon, settings.nido_lat, settings.nido_lon))
        if settings.nido_min_depth_km <= depth <= settings.nido_max_depth_km and distance <= settings.nido_max_distance_km:
            source_type = "Nido de Bucaramanga (heurístico)"
        elif depth < 70:
            source_type = "Cortical (por profundidad)"
        else:
            source_type = "Intermedia (por profundidad)"
        source_rows.append({
            "fuente_id": int(source_id), "codigo": f"F{index}", "tipo": source_type,
            "lat": lat, "lon": lon, "profundidad_mediana_km": depth,
            "magnitud_maxima": float(group["magnitud"].max()), "cantidad_sismos": int(len(group)),
            "confianza_media": float(group["confianza_fuente"].mean()),
            "distancia_referencia_nido_km": distance,
        })
    sources = pd.DataFrame(source_rows)
    data["es_difuso"] = data["fuente_id"] == -1
    if sources.empty:
        data["es_nido"] = False
    else:
        nido_ids = sources.loc[sources["tipo"].str.startswith("Nido"), "fuente_id"].tolist()
        data["es_nido"] = data["fuente_id"].isin(nido_ids)
    return data, sources, algorithm

def aggregate_municipalities(events: pd.DataFrame, sources: pd.DataFrame, settings):
    records = []
    for name, group in events.groupby("municipio", sort=True):
        n = len(group)
        valid_sources = group.loc[group["fuente_id"] != -1, "fuente_id"]
        record = {
            "municipio": name, "cantidad_sismos": int(n),
            "lat": float(group["latitud"].median()), "lon": float(group["longitud"].median()),
            "profundidad_mediana_km": float(group["profundidad"].median()),
            "profundidad_maxima_km": float(group["profundidad"].max()),
            "magnitud_media": float(group["magnitud"].mean()),
            "magnitud_maxima": float(group["magnitud"].max()),
            "magnitud_p95": float(group["magnitud"].quantile(.95)),
            "tasa_m3": float((group["magnitud"] >= 3).sum()),
            "tasa_m4": float((group["magnitud"] >= 4).sum()),
            "log_energia_media": float(group["log_energia_joules"].mean()),
            "porcentaje_nido": float(group["es_nido"].mean() * 100),
            "porcentaje_difuso": float(group["es_difuso"].mean() * 100),
            "numero_fuentes_cercanas": int(valid_sources.nunique()),
            "dist_nido_sismico_km": float(group["dist_nido_sismico"].median()) if "dist_nido_sismico" in group and group["dist_nido_sismico"].notna().any() else float(haversine_km(group["latitud"].median(), group["longitud"].median(), settings.nido_lat, settings.nido_lon)),
        }
        optional = {"fases": "fases_media", "Rms(Seg)": "rms_medio", "Gap(°)": "gap_medio"}
        for source_col, target_col in optional.items():
            record[target_col] = float(group[source_col].mean()) if source_col in group and group[source_col].notna().any() else None
        error_cols = [c for c in ["Error Lat(Km)", "Error Long(Km)", "Error Prof(Km)"] if c in group]
        record["error_localizacion_medio_km"] = float(pd.concat([group[c] for c in error_cols]).mean()) if error_cols else None
        records.append(record)
    municipalities = pd.DataFrame(records)
    if municipalities.empty:
        raise ValueError("No hay municipios válidos para entrenar K-Means.")
    score_cols = ["cantidad_sismos", "magnitud_maxima", "magnitud_p95", "log_energia_media"]
    ranked = pd.DataFrame(index=municipalities.index)
    for col in score_cols:
        ranked[col] = municipalities[col].rank(pct=True)
    ranked["superficialidad"] = (-municipalities["profundidad_mediana_km"]).rank(pct=True)
    ranked["fraccion_nido"] = municipalities["porcentaje_nido"].rank(pct=True)
    ranked["fraccion_difusa"] = municipalities["porcentaje_difuso"].rank(pct=True)
    ranked["distancia"] = (-municipalities["dist_nido_sismico_km"]).rank(pct=True)
    municipalities["indice_relativo"] = (ranked.mean(axis=1) * 100).round(2)
    features = [
        "cantidad_sismos", "profundidad_mediana_km", "magnitud_media", "magnitud_maxima",
        "magnitud_p95", "tasa_m3", "tasa_m4", "log_energia_media", "porcentaje_nido",
        "porcentaje_difuso", "numero_fuentes_cercanas", "dist_nido_sismico_km",
    ]
    x = municipalities[features].replace([np.inf, -np.inf], np.nan)
    x = x.fillna(x.median(numeric_only=True)).fillna(0)
    scaler = StandardScaler()
    scaled = scaler.fit_transform(x)
    count = len(municipalities)
    k = min(5, count)
    if count >= 2:
        km = KMeans(n_clusters=k, random_state=42, n_init=20)
        labels = km.fit_predict(scaled)
        municipalities["grupo_kmeans"] = labels.astype(int)
        group_scores = municipalities.groupby("grupo_kmeans")["indice_relativo"].mean().sort_values()
        mapping = {int(label): ["Muy bajo", "Bajo", "Medio", "Alto", "Muy alto"][min(i, 4)] for i, label in enumerate(group_scores.index)}
        municipalities["nivel"] = municipalities["grupo_kmeans"].map(mapping)
        silhouette = float(silhouette_score(scaled, labels)) if 1 < len(set(labels)) < count else None
    else:
        municipalities["grupo_kmeans"] = 0
        municipalities["nivel"] = "Sin clasificar"
        silhouette = None
    colors = {"Muy bajo": "#22c55e", "Bajo": "#84cc16", "Medio": "#f59e0b", "Alto": "#f97316", "Muy alto": "#ef4444"}
    municipalities["color"] = municipalities["nivel"].map(colors)
    municipalities["perfil_mixto"] = False
    if count > 1:
        order = {level: i for i, level in enumerate(["Muy bajo", "Bajo", "Medio", "Alto", "Muy alto"])}
        score_order = municipalities["indice_relativo"].rank(method="average", pct=True)
        municipalities["nivel_indice"] = pd.cut(score_order, bins=[0, .2, .4, .6, .8, 1.000001], labels=list(order), include_lowest=True).astype(str)
        municipalities["perfil_mixto"] = municipalities.apply(
            lambda row: abs(order.get(row["nivel"], 0) - order.get(row["nivel_indice"], 0)) >= 2, axis=1
        )
    else:
        municipalities["nivel_indice"] = municipalities["nivel"]
    return municipalities, features, k, silhouette
