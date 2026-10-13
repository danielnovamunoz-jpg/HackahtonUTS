from pathlib import Path
import numpy as np
import pandas as pd

REQUIRED_COLUMNS = ["municipio", "latitud", "longitud", "profundidad", "magnitud"]
NUMERIC_COLUMNS = [
    "latitud", "longitud", "profundidad", "magnitud", "fases", "Rms(Seg)", "Gap(°)",
    "log_energia_joules", "Error Lat(Km)", "Error Long(Km)", "Error Prof(Km)", "dist_nido_sismico",
    "anio", "mes", "dia", "hora",
]

ALIASES = {
    "año": "anio", "aÃ±o": "anio", "aã±o": "anio", "ano": "anio",
    "lat(°)": "latitud", "lat(Â°)": "latitud", "lat": "latitud",
    "long(°)": "longitud", "long(Â°)": "longitud", "long": "longitud",
    "prof(km)": "profundidad", "mag.": "magnitud", "mag": "magnitud",
    "rms(seg)": "Rms(Seg)", "gap(°)": "Gap(°)",
    "error lat(km)": "Error Lat(Km)", "error long(km)": "Error Long(Km)",
    "error prof(km)": "Error Prof(Km)",
}

def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.columns = [str(c).replace("\ufeff", "").strip() for c in df.columns]
    rename = {}
    for col in df.columns:
        low = col.lower()
        if low in ALIASES:
            rename[col] = ALIASES[low]
    return df.rename(columns=rename)

def to_number(series: pd.Series) -> pd.Series:
    if series.dtype == object:
        series = series.astype(str).str.strip().str.replace(",", ".", regex=False)
        series = series.replace({"": np.nan, "nan": np.nan, "None": np.nan, "NA": np.nan})
    return pd.to_numeric(series, errors="coerce")

def load_csv(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"No se encontró el CSV: {path}. Coloca el archivo en data/sismos.csv.")
    try:
        raw = pd.read_csv(path, encoding="utf-8-sig", sep=None, engine="python")
    except UnicodeDecodeError:
        raw = pd.read_csv(path, encoding="latin-1", sep=None, engine="python")
    raw = normalize_columns(raw)
    missing = [col for col in REQUIRED_COLUMNS if col not in raw.columns]
    if missing:
        raise ValueError(f"Faltan columnas obligatorias: {', '.join(missing)}. Se requieren: {', '.join(REQUIRED_COLUMNS)}.")
    for col in NUMERIC_COLUMNS:
        if col in raw.columns:
            raw[col] = to_number(raw[col])
    raw["municipio"] = raw["municipio"].astype("string").str.strip()
    raw = raw.dropna(subset=["municipio", "latitud", "longitud", "profundidad", "magnitud"])
    raw = raw[
        raw["municipio"].ne("")
        & raw["latitud"].between(-90, 90)
        & raw["longitud"].between(-180, 180)
        & raw["profundidad"].ge(0)
    ].copy()
    raw["municipio"] = raw["municipio"].str.replace(r"\s+", " ", regex=True)
    raw["magnitud"] = raw["magnitud"].clip(lower=0)
    if "log_energia_joules" not in raw.columns or raw["log_energia_joules"].isna().all():
        raw["log_energia_joules"] = 1.5 * raw["magnitud"] + 4.8
    if "anio" not in raw.columns:
        raw["anio"] = np.nan
    if raw.empty:
        raise ValueError("El CSV no contiene filas válidas tras limpiar las columnas obligatorias.")
    return raw.reset_index(drop=True)
