import tempfile
from pathlib import Path

import pandas as pd

from qsbench.storage import write_parquet_shard


def test_write_parquet_shard():
    df = pd.DataFrame({"col1": [1, 2], "col2": ["a", "b"]})
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "test.parquet"
        info = write_parquet_shard(df, path, write_csv=True)
        assert info["rows"] == 2
        assert Path(info["parquet"]).exists()
        assert Path(info["csv"]).exists()