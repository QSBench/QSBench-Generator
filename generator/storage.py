from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

import pandas as pd


def write_parquet_shard(df: pd.DataFrame, path: Path, write_csv: bool = False) -> Dict[str, Any]:
    path.parent.mkdir(parents=True, exist_ok=True)
    # Принудительное использование движка pyarrow
    df.to_parquet(path, compression="zstd", engine="pyarrow")

    csv_path = None
    if write_csv:
        csv_path = path.with_suffix(".csv")
        df.to_csv(csv_path, index=False)

    return {
        "parquet": str(path),
        "csv": str(csv_path) if csv_path else None,
        "rows": int(len(df)),
        "columns": int(len(df.columns)),
    }