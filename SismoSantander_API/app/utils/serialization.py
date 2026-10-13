import numpy as np
import pandas as pd

def records(df: pd.DataFrame) -> list[dict]:
    def safe(value):
        if isinstance(value, dict):
            return {str(k): safe(v) for k, v in value.items()}
        if isinstance(value, list):
            return [safe(v) for v in value]
        if isinstance(value, (np.integer,)):
            return int(value)
        if isinstance(value, (np.floating,)):
            return None if not np.isfinite(value) else float(value)
        if isinstance(value, (np.bool_,)):
            return bool(value)
        if pd.isna(value) if not isinstance(value, (dict, list, tuple)) else False:
            return None
        return value
    return [safe(row) for row in df.to_dict(orient="records")]
