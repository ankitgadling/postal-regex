import json
import importlib.resources as resources
from pathlib import Path
from typing import Union
import tempfile
import pandas as pd
import pyspark


# ---------- Core JSON Loader ----------
def load_json() -> list[dict]:
    """Load postal codes as a list of dicts (raw JSON)."""
    with (
        resources.files("postal_regex.data")
        .joinpath("postal_codes.json")
        .open("r", encoding="utf-8") as f
    ):
        return json.load(f)


# ---------- Pandas Loader ----------
def load_pandas() -> "pd.DataFrame":
    """Load postal codes into a Pandas DataFrame."""

    return pd.DataFrame(load_json())


# ---------- Spark Loader ----------
def load_spark(spark_session: "pyspark.sql.SparkSession"):
    """Load postal codes into a Spark DataFrame."""
    # Write JSON to temp path (Spark requires a path, not a file-like object)

    data = load_json()
    with tempfile.NamedTemporaryFile(mode="w+", suffix=".json", delete=False) as tmp:
        json.dump(data, tmp)
        tmp_path = tmp.name

    return spark_session.read.json(tmp_path)


# ---------- Parquet Saver ----------
def export_parquet(output_path: Union[str, Path]):
    """Export postal codes to a Parquet file."""

    df = load_pandas()
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(output_path, index=False)
    return output_path
