import pandas as pd
from app.services.csv_service import normalize_columns

def test_normalize_year_and_coordinates():
    df = pd.DataFrame(columns=["año", "lat", "long", "municipio"])
    result = normalize_columns(df)
    assert "anio" in result.columns
    assert "latitud" in result.columns
    assert "longitud" in result.columns
