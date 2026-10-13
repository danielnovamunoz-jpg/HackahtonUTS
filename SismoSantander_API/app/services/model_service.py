import unicodedata
import numpy as np
import pandas as pd
from app.services.csv_service import load_csv
from app.services.clustering_service import cluster_sources, aggregate_municipalities

class ModelService:
    levels = ["Muy bajo", "Bajo", "Medio", "Alto", "Muy alto"]
    colors = {
        "Muy bajo": "#22c55e", "Bajo": "#84cc16", "Medio": "#f59e0b",
        "Alto": "#f97316", "Muy alto": "#ef4444",
    }

    def __init__(self, settings):
        self.settings = settings
        self.events = None
        self.municipalities = None
        self.sources = pd.DataFrame()
        self.metadata = {}
        self.startup_error = "CSV aún no cargado."

    @property
    def is_ready(self):
        return self.events is not None and self.municipalities is not None

    @staticmethod
    def normalize_name(value):
        text = unicodedata.normalize("NFKD", str(value).casefold().strip())
        return "".join(ch for ch in text if not unicodedata.combining(ch))

    @staticmethod
    def json_safe(value):
        if isinstance(value, dict):
            return {str(k): ModelService.json_safe(v) for k, v in value.items()}
        if isinstance(value, list):
            return [ModelService.json_safe(v) for v in value]
        if isinstance(value, (np.integer,)):
            return int(value)
        if isinstance(value, (np.floating,)):
            return None if not np.isfinite(value) else float(value)
        if isinstance(value, (np.bool_,)):
            return bool(value)
        if isinstance(value, tuple):
            return [ModelService.json_safe(v) for v in value]
        if value is pd.NA or value is pd.NaT:
            return None
        if isinstance(value, float) and not np.isfinite(value):
            return None
        return value

    def reload(self):
        try:
            data = load_csv(self.settings.csv_path)
            events, sources, source_algorithm = cluster_sources(data, self.settings)
            municipalities, features, k, silhouette = aggregate_municipalities(events, sources, self.settings)
            self.events, self.sources, self.municipalities = events, sources, municipalities
            self.metadata = {
                "csv": str(self.settings.csv_path),
                "filas_validas": int(len(events)),
                "municipios_en_csv": int(municipalities["municipio"].nunique()),
                "municipios_no_es_automaticamente_87": int(municipalities["municipio"].nunique()) != 87,
                "algoritmo_fuentes": source_algorithm,
                "algoritmo_municipios": "K-Means",
                "k_municipios": int(k),
                "silueta_kmeans": silhouette,
                "variables_kmeans": features,
                "variables_hdbscan": ["fuente_id", "es_nido", "es_difuso", "numero_fuentes_cercanas"],
                "nota": "Niveles relativos dentro de los municipios presentes en el CSV; no son pronósticos ni riesgo absoluto.",
            }
            self.startup_error = None
        except Exception as exc:
            self.events = None
            self.municipalities = None
            self.sources = pd.DataFrame()
            self.metadata = {}
            self.startup_error = str(exc)

    def levels_summary(self):
        rows = []
        for level in self.levels:
            subset = self.municipalities[self.municipalities["nivel"] == level]
            if not subset.empty:
                rows.append({
                    "nivel": level, "color": self.colors[level], "municipios": int(len(subset)),
                    "indice_medio": round(float(subset["indice_relativo"].mean()), 2),
                    "lista_municipios": subset["municipio"].tolist(),
                })
        return rows
