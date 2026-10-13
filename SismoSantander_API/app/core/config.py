from functools import lru_cache
from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parents[2]

class Settings:
    app_name: str = os.getenv("APP_NAME", "SismoSantander API")
    csv_path: Path = Path(os.getenv("SISMOS_CSV", str(BASE_DIR / "data" / "sismos.csv")))
    cors_origins: list[str] = [
        origin.strip()
        for origin in os.getenv("CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173").split(",")
        if origin.strip()
    ]
    nido_lat: float = float(os.getenv("NIDO_LAT", "6.788"))
    nido_lon: float = float(os.getenv("NIDO_LON", "-73.166"))
    nido_max_distance_km: float = float(os.getenv("NIDO_MAX_DISTANCE_KM", "40"))
    nido_min_depth_km: float = float(os.getenv("NIDO_MIN_DEPTH_KM", "110"))
    nido_max_depth_km: float = float(os.getenv("NIDO_MAX_DEPTH_KM", "190"))
    hdbscan_min_cluster_size: int = int(os.getenv("HDBSCAN_MIN_CLUSTER_SIZE", "5"))
    max_records_default: int = int(os.getenv("MAX_RECORDS_DEFAULT", "500"))

@lru_cache
def get_settings() -> Settings:
    return Settings()
